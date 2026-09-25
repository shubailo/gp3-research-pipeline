# -*- coding: utf-8 -*-
"""
before_after_stats.py
---------------------
Összehasonlítja a csoportátlagokat és SEM értékeket:
  - ELŐTTE: minden állat benne van
  - UTÁNA: a kizárt állatok nélkül

Kizártak listája: az előző elemzések alapján (komment + statisztikai outlier).
Struktúra: oszlop = állat, sor = időpont×paraméter
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent

# ============================================================
# KIZÁRT ÁLLATOK LISTÁJA
# (az előző cross-validate + metabolism_outliers elemzések alapján)
# ============================================================
EXCLUDED = {
    # Hőmérséklet + metabolikus (mindkét adatbázisban outlier)
    'TR12_aMSH':    ['7675', '7375', '7243', '7240', '7318', '7328'],
    'TR12_Control': ['7247'],
    'TR12_Leptin':  [],  # Nincs erős kizárandó ebben a csoportban
    'NF12_Control': ['6545.2', '6546.3', '6547.1', '6548.1'],
    'NF12_aMSH':    ['7208.1'],
    'NF12_Leptin':  ['7247'],
    'CR12_Control': ['7204'],
    'CR12_aMSH':    ['7340'],
    'CR12_Leptin':  ['7675', '7346', '7347', '7430', '7438'],
}

TARGET_PARAMS = ['VO2', 'VCO2', 'RQ', 'EE', 'dVO2', 'dVCO2']


def sem(arr):
    """Standard error of the mean."""
    if len(arr) < 2:
        return np.nan
    return np.std(arr, ddof=1) / np.sqrt(len(arr))


def analyze_sheet(xls, sheet_name, excluded_ids):
    """
    Egy lap elemzése. Visszaad egy listát dict-ekből:
    {param, n_all, mean_all, sem_all, n_clean, mean_clean, sem_clean, ...}
    """
    try:
        df = pd.read_excel(xls, sheet_name=sheet_name, header=0)
    except Exception as e:
        print(f"  Hiba ({sheet_name}): {e}")
        return []

    # Időoszlop
    time_col, time_idx = None, None
    for i, col in enumerate(df.columns):
        if 'Time' in str(col):
            time_col = col
            time_idx = i
            break
    if time_col is None:
        return []

    # Paraméter oszlop
    param_col = None
    for col in df.columns[:time_idx]:
        if 'Param' in str(col):
            param_col = col
            break

    # Post-injekciós adatok (t >= 0)
    df['_t'] = pd.to_numeric(df[time_col], errors='coerce')
    df_post = df[df['_t'] >= 0].copy()

    # Állatoszlopok azonosítása
    all_animal_cols = []
    for col in df.columns[time_idx + 1:]:
        base = str(col).split('.')[0]
        try:
            float(base)
            all_animal_cols.append(col)
        except ValueError:
            pass

    if not all_animal_cols:
        return []

    # Kizárt oszlopok azonosítása
    excluded_ids_norm = [str(e).strip() for e in excluded_ids]
    excluded_cols = []
    kept_cols = []
    for col in all_animal_cols:
        col_str = str(col).strip()
        if col_str in excluded_ids_norm:
            excluded_cols.append(col)
        else:
            kept_cols.append(col)

    results = []

    def get_animal_means(cols, df_sub, param_col, param):
        """Minden állat post-injekciós átlaga egy adott paraméternél."""
        means = []
        for c in cols:
            vals = pd.to_numeric(df_sub[c], errors='coerce').dropna()
            if len(vals) >= 2:
                means.append(vals.mean())
        return np.array(means)

    if param_col:
        groups = df_post.groupby(param_col)
    else:
        groups = [('overall', df_post)]

    for param, pdata in groups:
        param_str = str(param).strip()
        if TARGET_PARAMS and not any(tp.lower() in param_str.lower() for tp in TARGET_PARAMS):
            continue

        arr_all   = get_animal_means(all_animal_cols, pdata, param_col, param_str)
        arr_clean = get_animal_means(kept_cols, pdata, param_col, param_str)

        if len(arr_all) < 2:
            continue

        sem_all   = sem(arr_all)
        sem_clean = sem(arr_clean) if len(arr_clean) >= 2 else np.nan
        mean_all   = arr_all.mean()
        mean_clean = arr_clean.mean() if len(arr_clean) >= 1 else np.nan

        # Változás mértéke
        sem_change_pct = ((sem_clean - sem_all) / sem_all * 100) if sem_all > 0 and not np.isnan(sem_clean) else np.nan
        mean_change    = mean_clean - mean_all if not np.isnan(mean_clean) else np.nan

        results.append({
            'sheet': sheet_name,
            'param': param_str,
            'kizárt_oszlopok': ', '.join(str(c) for c in excluded_cols),
            'n_all': len(arr_all),
            'mean_all': round(mean_all, 4),
            'sem_all': round(sem_all, 4),
            'n_clean': len(arr_clean),
            'mean_clean': round(mean_clean, 4) if not np.isnan(mean_clean) else None,
            'sem_clean': round(sem_clean, 4) if not np.isnan(sem_clean) else None,
            'mean_delta': round(mean_change, 4) if not np.isnan(mean_change) else None,
            'sem_change_pct': round(sem_change_pct, 1) if not np.isnan(sem_change_pct) else None,
        })

    return results


def main():
    xls = pd.ExcelFile(FILE := BASE_DIR / "animaldata_metabolism.xlsx")
    sheets = [s for s in xls.sheet_names if s not in ['Summary', 'Animal_metadata']]

    all_results = []

    for sheet in sheets:
        excl = EXCLUDED.get(sheet, [])
        print(f"\n--- {sheet} | Kizárva: {excl if excl else 'senki'} ---")
        res = analyze_sheet(xls, sheet, excl)
        all_results.extend(res)

        for r in res:
            sem_arrow = ""
            if r['sem_change_pct'] is not None:
                if r['sem_change_pct'] < -5:
                    sem_arrow = f"✅ −{abs(r['sem_change_pct']):.1f}%"
                elif r['sem_change_pct'] > 5:
                    sem_arrow = f"⚠️ +{r['sem_change_pct']:.1f}%"
                else:
                    sem_arrow = f"≈ {r['sem_change_pct']:+.1f}%"

            print(f"  {r['param']:>8} | "
                  f"ELŐTTE: n={r['n_all']:>2}, mean={r['mean_all']:>8.3f}, SEM={r['sem_all']:>7.4f} | "
                  f"UTÁNA: n={r['n_clean']:>2}, mean={r['mean_clean']:>8.3f}, SEM={r['sem_clean']:>7.4f} | "
                  f"SEM {sem_arrow}")

    xls.close()

    # ---- CSV ----
    df_out = pd.DataFrame(all_results)
    out_csv = BASE_DIR / "before_after_stats.csv"
    df_out.to_csv(out_csv, index=False, encoding='utf-8-sig')

    # ---- MARKDOWN ----
    out_md = BASE_DIR / "before_after_stats.md"
    with open(out_md, 'w', encoding='utf-8') as f:
        f.write("# Csoportátlagok és SEM: Kizárás előtt vs. után\n\n")
        f.write("> Egy oszlop = egy állat. Post-injekciós átlagok (t ≥ 0 min).\n\n")

        for sheet in sheets:
            sub = df_out[df_out['sheet'] == sheet]
            if sub.empty:
                continue
            excl = EXCLUDED.get(sheet, [])
            f.write(f"## {sheet}\n")
            if excl:
                f.write(f"> Kizárt állatok: **{', '.join(excl)}**\n\n")
            else:
                f.write("> Kizárás: **nincs** (nincs erős outlier)\n\n")

            f.write("| Paraméter | n (előtte) | Átlag (előtte) | SEM (előtte) | n (utána) | Átlag (utána) | SEM (utána) | Átlag Δ | SEM változás |\n")
            f.write("|-----------|-----------|--------------|------------|----------|-------------|-----------|---------|-------------|\n")

            for _, r in sub.iterrows():
                sem_pct = r['sem_change_pct']
                if sem_pct is not None:
                    if sem_pct < -5:
                        sem_icon = f"✅ {sem_pct:+.1f}%"
                    elif sem_pct > 5:
                        sem_icon = f"⚠️ {sem_pct:+.1f}%"
                    else:
                        sem_icon = f"≈ {sem_pct:+.1f}%"
                else:
                    sem_icon = "—"

                f.write(f"| {r['param']} | {r['n_all']} | {r['mean_all']:.4f} | {r['sem_all']:.4f} | "
                        f"{r['n_clean']} | {r['mean_clean']:.4f} | {r['sem_clean']:.4f} | "
                        f"{r['mean_delta']:+.4f} | {sem_icon} |\n")
            f.write("\n")

    print(f"\n✅  CSV: {out_csv}")
    print(f"✅  Markdown: {out_md}")


if __name__ == '__main__':
    main()
