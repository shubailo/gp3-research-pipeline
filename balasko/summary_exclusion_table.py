# -*- coding: utf-8 -*-
"""
summary_exclusion_table.py
--------------------------
Egyéni kizárási hatás: minden jelölt állat esetén kiszámítja,
hogy HA CSAK ŐT zárjuk ki, mennyit változik a csoport SEM és átlag.
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent

# === KIZÁRÁSRA JELÖLT ÁLLATOK (mindkét elemzés alapján) ===
# (sheet, animal_id, outlier_param, outlier_value, group_mean, group_std, z_score, reason)
CANDIDATES = [
    # NF12_Control – 4 erős metabolikus outlier
    ('NF12_Control', '6545.2', 'VO2',  7.42,  12.266, 1.710, -2.83, 'VO2 drámaian alacsony'),
    ('NF12_Control', '6546.3', 'RQ',   1.029,  0.910, 0.044, +2.74, 'RQ > 1.0 – fizikailag értelmezhetetlen'),
    ('NF12_Control', '6547.1', 'dVO2', -6.689, -0.435, 2.349, -2.66, 'dVO2 drámaian alacsony'),
    ('NF12_Control', '6548.1', 'VO2',  8.502, 12.266, 1.710, -2.20, 'VO2 alacsony'),
    # NF12_aMSH
    ('NF12_aMSH', '7208.1', 'VO2', 9.772, 16.205, 2.288, -2.81, 'VO2 nagyon alacsony + PG− komment'),
    # TR12_Control
    ('TR12_Control', '7247', 'RQ', 0.677, 0.817, 0.061, -2.29, 'RQ alacsony + szétcsúszott kanül'),
    # NF12_Leptin
    ('NF12_Leptin', '7247', 'RQ', 0.677, 0.826, 0.057, -2.60, 'RQ alacsony (ugyanaz az állat, Leptin lapon)'),
    # TR12_aMSH
    ('TR12_aMSH', '7675', 'HLI', 0.743, 0.078, 0.172, +5.06, 'HLI extrém magas – PG véletlenül beadva'),
    ('TR12_aMSH', '7375', 'dTc', -0.574, 0.174, 0.302, -2.48, 'dTc alacsony + szétcsúszott'),
    ('TR12_aMSH', '7243', 'Tc',  38.205, 37.415, 0.370, +2.14, 'Tc magas + oxy nincs'),
    ('TR12_aMSH', '7240', 'Tc',  36.558, 37.415, 0.370, -2.32, 'Tc alacsony + oxy nincs'),
    # CR12_Control
    ('CR12_Control', '7204', 'Tc', 35.579, 36.789, 0.556, -2.18, 'Tc alacsony + PG− komment'),
    # CR12_aMSH
    ('CR12_aMSH', '7340', 'Tc', 35.968, 37.344, 0.462, -2.98, 'Tc nagyon alacsony + szétcsúszott'),
    # CR12_Leptin
    ('CR12_Leptin', '7346', 'dVCO2', -4.268, -0.764, 1.042, -3.36, 'dVCO2 extrém alacsony'),
    ('CR12_Leptin', '7347', 'dVO2',  -4.611, -0.450, 1.124, -3.70, 'dVO2 extrém alacsony'),
    ('CR12_Leptin', '7430', 'Tc',    38.300, 37.153, 0.559, +2.05, 'Tc magas + PG− komment'),
    ('CR12_Leptin', '7438', 'dTc',    0.947,  0.129, 0.347, +2.36, 'dTc magas + gennyes fej'),
]

TARGET_PARAMS = ['VO2', 'VCO2', 'RQ', 'EE', 'dVO2', 'dVCO2']


def sem(arr):
    if len(arr) < 2:
        return np.nan
    return np.std(arr, ddof=1) / np.sqrt(len(arr))


def get_animal_means_for_param(xls, sheet_name, param_name):
    """
    Visszaadja: {animal_id_str: mean_post_injection} az adott paraméterhez.
    """
    try:
        df = pd.read_excel(xls, sheet_name=sheet_name, header=0)
    except:
        return {}

    time_col, time_idx = None, None
    for i, col in enumerate(df.columns):
        if 'Time' in str(col):
            time_col = col
            time_idx = i
            break
    if time_col is None:
        return {}

    param_col = None
    for col in df.columns[:time_idx]:
        if 'Param' in str(col):
            param_col = col
            break

    df['_t'] = pd.to_numeric(df[time_col], errors='coerce')
    df_post = df[df['_t'] >= 0].copy()

    animal_cols = []
    for col in df.columns[time_idx + 1:]:
        base = str(col).split('.')[0]
        try:
            float(base)
            animal_cols.append(col)
        except ValueError:
            pass

    result = {}

    if param_col:
        for param, pdata in df_post.groupby(param_col):
            if param_name.lower() not in str(param).lower():
                continue
            for ac in animal_cols:
                vals = pd.to_numeric(pdata[ac], errors='coerce').dropna()
                if len(vals) >= 2:
                    result[str(ac).strip()] = vals.mean()
        return result
    else:
        for ac in animal_cols:
            vals = pd.to_numeric(df_post[ac], errors='coerce').dropna()
            if len(vals) >= 2:
                result[str(ac).strip()] = vals.mean()
        return result


def compute_individual_impact(xls, sheet, animal_id, param):
    """
    Kiszámolja a SEM-változást, ha EGY állatot kizárunk.
    """
    means = get_animal_means_for_param(xls, sheet, param)
    if not means or len(means) < 3:
        return None

    all_vals = np.array(list(means.values()))
    animal_id_str = str(animal_id).strip()

    if animal_id_str not in means:
        return None

    animal_val = means[animal_id_str]
    clean_vals = np.array([v for k, v in means.items() if k != animal_id_str])

    sem_all = sem(all_vals)
    sem_clean = sem(clean_vals)
    mean_all = all_vals.mean()
    mean_clean = clean_vals.mean() if len(clean_vals) > 0 else np.nan

    sem_change_pct = (sem_clean - sem_all) / sem_all * 100 if sem_all > 0 else np.nan

    return {
        'n_all': len(all_vals),
        'n_clean': len(clean_vals),
        'mean_all': round(mean_all, 3),
        'mean_clean': round(mean_clean, 3),
        'sem_all': round(sem_all, 4),
        'sem_clean': round(sem_clean, 4),
        'sem_change_pct': round(sem_change_pct, 1),
        'animal_val': round(animal_val, 3),
    }


def main():
    xls = pd.ExcelFile(BASE_DIR / "animaldata_metabolism.xlsx")

    rows = []

    print(f"\n{'='*90}")
    print("ÖSSZESÍTŐ KIZÁRÁSI TÁBLÁZAT")
    print(f"{'='*90}")
    print(f"{'ID':>10} | {'Csoport':<16} | {'Kiugró paraméter & érték':<40} | {'SEM változás'}")
    print('-'*90)

    for (sheet, animal_id, param, aval, gmean, gstd, z, reason) in CANDIDATES:
        impact = compute_individual_impact(xls, sheet, animal_id, param)

        if impact:
            sem_pct = impact['sem_change_pct']
            sem_icon = f"✅ {sem_pct:+.1f}%" if sem_pct < -5 else (
                       f"⚠️ {sem_pct:+.1f}%" if sem_pct > 5 else f"≈ {sem_pct:+.1f}%")
            impact_str = f"{param} SEM: {impact['sem_all']:.4f}→{impact['sem_clean']:.4f} ({sem_icon})"
        else:
            sem_pct = None
            impact_str = "Nincs elég adat a lapon"

        print(f"{animal_id:>10} | {sheet:<16} | {param}: {aval:.3f} (z={z:+.2f}) | {impact_str}")

        rows.append({
            'Állat ID': animal_id,
            'Csoport': sheet,
            'Kiugró paraméter': param,
            'Állat értéke': aval,
            'Csoport átlag': gmean,
            'Csoport SD': gstd,
            'z-score': z,
            'OK (komment)': reason,
            'n előtte': impact['n_all'] if impact else None,
            'SEM előtte': impact['sem_all'] if impact else None,
            'n utána': impact['n_clean'] if impact else None,
            'SEM utána': impact['sem_clean'] if impact else None,
            'SEM változás %': sem_pct,
            'Átlag előtte': impact['mean_all'] if impact else None,
            'Átlag utána': impact['mean_clean'] if impact else None,
        })

    xls.close()

    # CSV
    df = pd.DataFrame(rows)
    df.to_csv(BASE_DIR / "exclusion_summary_table.csv", index=False, encoding='utf-8-sig')

    # Markdown
    with open(BASE_DIR / "exclusion_summary_table.md", 'w', encoding='utf-8') as f:
        f.write("# Kizárási összesítő táblázat\n\n")
        f.write("> Egyéni hatás: ha csak az adott állatot zárjuk ki, mennyit változik a csoport SEM és átlag.\n\n")
        f.write("| Állat ID | Kategória/Csoport | Kiugró érték (ok) | SEM előtte → utána | SEM Δ% | Átlag előtte → utána |\n")
        f.write("|---------|-----------------|-------------------|-------------------|-------|--------------------|\n")

        for r in rows:
            sem_icon = ""
            if r['SEM változás %'] is not None:
                p = r['SEM változás %']
                sem_icon = f"✅ {p:+.1f}%" if p < -5 else (f"⚠️ {p:+.1f}%" if p > 5 else f"≈ {p:+.1f}%")
            else:
                sem_icon = "—"

            outlier_str = (f"{r['Kiugró paraméter']}={r['Állat értéke']:.3f} "
                           f"(z={r['z-score']:+.2f}) – {r['OK (komment)']}")

            sem_str = (f"{r['SEM előtte']:.4f} → {r['SEM utána']:.4f}"
                       if r['SEM előtte'] is not None else "—")
            mean_str = (f"{r['Átlag előtte']:.3f} → {r['Átlag utána']:.3f}"
                        if r['Átlag előtte'] is not None else "—")

            f.write(f"| **{r['Állat ID']}** | {r['Csoport']} | {outlier_str} | "
                    f"{sem_str} | {sem_icon} | {mean_str} |\n")

    print(f"\n✅  CSV: {BASE_DIR / 'exclusion_summary_table.csv'}")
    print(f"✅  MD:  {BASE_DIR / 'exclusion_summary_table.md'}")


if __name__ == '__main__':
    main()
