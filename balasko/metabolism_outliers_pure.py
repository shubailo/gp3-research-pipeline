# -*- coding: utf-8 -*-
"""
metabolism_outliers_pure.py
---------------------------
Tisztán adat-alapú outlier detekció az animaldata_metabolism.xlsx fájlban.
Kommenttől FÜGGETLENÜL keres kiugró értékeket minden állatnál.

Módszer:
- Minden csoportlapon (pl. NF12_aMSH) minden állatnál kiszámítja a
  post-injekciós átlagot (t >= 0) paraméterenként
- IQR módszer (1.5x) és z-score (|z| > 2.0) alapján azonosítja az outliereket
- Mindkét módszerrel kiugró állatokat jelöli ERŐS outliernek
- Csak az egyiknél kiugrót jelöli GYENGE outliernek
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent
FILE = BASE_DIR / "animaldata_metabolism.xlsx"

# Metabolikus paraméterek, amiket vizsgálunk
TARGET_PARAMS = ['VO2', 'VCO2', 'RQ', 'EE', 'dVO2', 'dVCO2']

Z_THRESH = 2.0
IQR_MULTIPLIER = 1.5


def is_outlier_zscore(val, mean, std):
    if std == 0 or np.isnan(std):
        return False, 0.0
    z = (val - mean) / std
    return abs(z) > Z_THRESH, round(z, 2)


def is_outlier_iqr(val, q1, q3):
    iqr = q3 - q1
    if iqr == 0:
        return False
    return val < (q1 - IQR_MULTIPLIER * iqr) or val > (q3 + IQR_MULTIPLIER * iqr)


def analyze_sheet(xls, sheet_name):
    """
    Egy csoport-lapot elemez. Visszaad egy listát:
    [{'param', 'animal_id', 'mean_value', 'group_mean', 'group_std',
      'z_score', 'iqr_outlier', 'z_outlier', 'strength'}]
    """
    try:
        df = pd.read_excel(xls, sheet_name=sheet_name, header=0)
    except Exception as e:
        print(f"  Hiba: {e}")
        return []

    # Időoszlop keresése
    time_col = None
    time_idx = None
    for i, col in enumerate(df.columns):
        if 'Time' in str(col) or 'time' in str(col.lower()):
            time_col = col
            time_idx = i
            break

    if time_col is None:
        return []

    # Paraméter oszlop keresése
    param_col = None
    for col in df.columns[:time_idx]:
        if 'Param' in str(col) or 'param' in str(col).lower():
            param_col = col
            break

    # Post-injekciós adatok (t >= 0)
    df['_time_num'] = pd.to_numeric(df[time_col], errors='coerce')
    df_post = df[df['_time_num'] >= 0].copy()

    # Állatoszlopok azonosítása (numerikus ID fejléccel)
    animal_cols = []
    for col in df.columns[time_idx + 1:]:
        col_str = str(col).strip()
        base = col_str.split('.')[0]
        try:
            float(base)
            animal_cols.append(col)
        except ValueError:
            continue

    if not animal_cols:
        return []

    results = []

    # Csoportosítás paraméterenként
    if param_col:
        param_groups = df_post.groupby(param_col)
    else:
        param_groups = [('overall', df_post)]

    for param, pdata in param_groups:
        param_str = str(param).strip()

        # Csak célparamétereket vizsgálunk
        if TARGET_PARAMS and not any(tp.lower() in param_str.lower() for tp in TARGET_PARAMS):
            continue

        # Minden állat post-injekciós átlaga
        animal_means = {}
        for ac in animal_cols:
            vals = pd.to_numeric(pdata[ac], errors='coerce').dropna()
            if len(vals) >= 2:  # Legalább 2 mérési pont kell
                animal_means[ac] = vals.mean()

        if len(animal_means) < 3:  # Legalább 3 állat kell a stat-hoz
            continue

        arr = np.array(list(animal_means.values()))
        gmean = arr.mean()
        gstd = arr.std()
        q1 = np.percentile(arr, 25)
        q3 = np.percentile(arr, 75)

        for animal_id, animal_mean in animal_means.items():
            z_out, z_val = is_outlier_zscore(animal_mean, gmean, gstd)
            iqr_out = is_outlier_iqr(animal_mean, q1, q3)

            if z_out or iqr_out:
                if z_out and iqr_out:
                    strength = "ERŐS"
                elif z_out:
                    strength = "z-score"
                else:
                    strength = "IQR"

                results.append({
                    'sheet': sheet_name,
                    'param': param_str,
                    'animal_id': str(animal_id).strip(),
                    'mean_post': round(animal_mean, 3),
                    'group_mean': round(gmean, 3),
                    'group_std': round(gstd, 3),
                    'z_score': z_val,
                    'iqr_outlier': iqr_out,
                    'z_outlier': z_out,
                    'strength': strength,
                    'direction': 'MAGAS' if animal_mean > gmean else 'ALACSONY',
                })

    return results


def main():
    if not FILE.exists():
        print(f"Nem található: {FILE}")
        return

    xls = pd.ExcelFile(FILE)
    sheets = [s for s in xls.sheet_names if s not in ['Summary', 'Animal_metadata']]
    print(f"Lapok: {sheets}\n")

    all_results = []

    for sheet in sheets:
        print(f"Elemzés: {sheet}...")
        res = analyze_sheet(xls, sheet)
        all_results.extend(res)
        if res:
            print(f"  → {len(res)} outlier bejegyzés")
        else:
            print(f"  → Nincs outlier")

    xls.close()

    if not all_results:
        print("\nNem találtam metabolikus outliert.")
        return

    df = pd.DataFrame(all_results)

    # ---- NYOMTATÁS ----
    print(f"\n{'='*70}")
    print("METABOLIKUS OUTLIEREK – ÖSSZESÍTŐ")
    print(f"{'='*70}\n")

    # Csak az ERŐS outliereket emeljük ki
    strong = df[df['strength'] == 'ERŐS']
    weak = df[df['strength'] != 'ERŐS']

    print(f"🔴 ERŐS outlierek (z > {Z_THRESH} ÉS IQR): {len(strong.drop_duplicates(['sheet','param','animal_id']))}")
    print(f"🟡 Gyenge outlierek (csak z VAGY csak IQR): {len(weak.drop_duplicates(['sheet','param','animal_id']))}\n")

    # Csoportonként
    for sheet in sheets:
        sub = df[df['sheet'] == sheet]
        if sub.empty:
            continue
        print(f"\n--- {sheet} ---")
        for _, r in sub.drop_duplicates(['param','animal_id']).sort_values('strength').iterrows():
            icon = "🔴" if r['strength'] == 'ERŐS' else "🟡"
            print(f"  {icon} ID={r['animal_id']:>8} | {r['param']:>8} | "
                  f"Állat={r['mean_post']:>8.3f} | Csoport={r['group_mean']:>8.3f}±{r['group_std']:.3f} "
                  f"| z={r['z_score']:>+6.2f} | {r['direction']} | {r['strength']}")

    # ---- CSV ----
    out_csv = BASE_DIR / "metabolism_outliers_pure.csv"
    df.to_csv(out_csv, index=False, encoding='utf-8-sig')

    # ---- MARKDOWN ----
    out_md = BASE_DIR / "metabolism_outliers_pure.md"
    with open(out_md, 'w', encoding='utf-8') as f:
        f.write("# Metabolikus outlierek – Tisztán adat-alapú elemzés\n\n")
        f.write(f"> Z-score küszöb: **{Z_THRESH}** | IQR szorzó: **{IQR_MULTIPLIER}x** | Post-injekciós adatok (t ≥ 0 min)\n\n")
        f.write("Vizsgált paraméterek: " + ", ".join(TARGET_PARAMS) + "\n\n")

        for strength_label, strength_key in [("🔴 ERŐS outlierek (z > 2.0 ÉS IQR)", "ERŐS"),
                                              ("🟡 Gyenge outlierek (z > 2.0 VAGY IQR)", None)]:
            if strength_key:
                sub_df = df[df['strength'] == strength_key]
            else:
                sub_df = df[df['strength'] != 'ERŐS']

            if sub_df.empty:
                continue

            f.write(f"## {strength_label}\n\n")
            f.write("| Csoport | ID | Paraméter | Állat átlaga | Csoport átlaga | SD | z-score | Irány |\n")
            f.write("|---------|-----|-----------|-------------|----------------|-----|---------|-------|\n")

            for _, r in sub_df.drop_duplicates(['sheet','param','animal_id']).sort_values(['sheet','animal_id']).iterrows():
                f.write(f"| {r['sheet']} | **{r['animal_id']}** | {r['param']} | "
                        f"{r['mean_post']:.3f} | {r['group_mean']:.3f} | {r['group_std']:.3f} | "
                        f"{r['z_score']:+.2f} | {r['direction']} |\n")
            f.write("\n")

    print(f"\n✅  CSV: {out_csv}")
    print(f"✅  Markdown: {out_md}")


if __name__ == '__main__':
    main()
