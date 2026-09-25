# -*- coding: utf-8 -*-
"""
export_dual_analysis_results.py
--------------------------------
Generálja a végleges, részletes statisztikai jelentést és CSV-ket:
1. balasko/kizarasok_homerseklet.csv
2. balasko/kizarasok_metabolizmus.csv
3. balasko/statisztika_homerseklet_elotte_utana.csv
4. balasko/statisztika_metabolizmus_elotte_utana.csv
5. Artifact: kizarasok_elemzes.md (tiszta, strukturált összefoglaló)
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(r"C:\Users\shuba\Desktop\Researcher - Dóri\balasko")
ARTIFACT_DIR = Path(r"C:\Users\shuba\.gemini\antigravity-ide\brain\f32e32a9-2c9f-49a7-a653-8184932bce67")

from generate_final_stats import (
    analyze_temperature, analyze_metabolism, compute_impact, clean_id
)

# 1. Hőmérséklet
df_temp, temp_excl, t_sheets, t_params = analyze_temperature()
df_t_impact = compute_impact(df_temp, temp_excl, t_sheets, t_params)

# 2. Metabolizmus
df_metab, metab_excl, m_sheets, m_params = analyze_metabolism()
df_m_impact = compute_impact(df_metab, metab_excl, m_sheets, m_params)

# Részletes kizárási lista Hőmérsékletre
t_excl_rows = []
for sheet, aids in temp_excl.items():
    sub = df_temp[df_temp['Sheet'] == sheet]
    for aid in aids:
        aid_s = str(aid).strip()
        match = sub[sub['Col'].apply(clean_id) == aid_s]
        if not match.empty:
            r = match.iloc[0]
            # legmagasabb abs z-score
            top_z = sorted(r['Z_scores'].items(), key=lambda x: abs(x[1]), reverse=True)[0]
            t_excl_rows.append({
                "Tábla": "animaldata_temperature.xlsx",
                "Csoport": sheet,
                "Állat_ID": str(r['Col']),
                "Komment": r['Comment'],
                "Legfőbb_kiugrás": f"{top_z[0]}: z={top_z[1]:+.2f}",
                "Érték": f"{r['Means'].get(top_z[0], np.nan):.3f}",
                "Csoport_átlag": f"{r['Grp_stats'][top_z[0]]['mean']:.3f} ± {r['Grp_stats'][top_z[0]]['std']:.3f}",
                "Indoklás": "Technikai hiba + adatkiugrás" if r['Comment'] else "Súlyos adat-outlier / mérési műhiba"
            })
df_t_excl = pd.DataFrame(t_excl_rows)
df_t_excl.to_csv(BASE_DIR / "kizarasok_homerseklet.csv", index=False, encoding='utf-8-sig')
df_t_impact.to_csv(BASE_DIR / "statisztika_homerseklet_elotte_utana.csv", index=False, encoding='utf-8-sig')

# Részletes kizárási lista Metabolizmusra
m_excl_rows = []
for sheet, aids in metab_excl.items():
    sub = df_metab[df_metab['Sheet'] == sheet]
    for aid in aids:
        aid_s = str(aid).strip()
        match = sub[sub['Col'].apply(clean_id) == aid_s]
        if not match.empty:
            r = match.iloc[0]
            top_z = sorted(r['Z_scores'].items(), key=lambda x: abs(x[1]), reverse=True)[0]
            m_excl_rows.append({
                "Tábla": "animaldata_metabolism.xlsx",
                "Csoport": sheet,
                "Állat_ID": str(r['Col']),
                "Komment": r['Comment'],
                "Legfőbb_kiugrás": f"{top_z[0]}: z={top_z[1]:+.2f}",
                "Érték": f"{r['Means'].get(top_z[0], np.nan):.3f}",
                "Csoport_átlag": f"{r['Grp_stats'][top_z[0]]['mean']:.3f} ± {r['Grp_stats'][top_z[0]]['std']:.3f}",
                "Indoklás": "Technikai hiba + adatkiugrás" if r['Comment'] else "Súlyos adat-outlier / mérési műhiba"
            })
df_m_excl = pd.DataFrame(m_excl_rows)
df_m_excl.to_csv(BASE_DIR / "kizarasok_metabolizmus.csv", index=False, encoding='utf-8-sig')
df_m_impact.to_csv(BASE_DIR / "statisztika_metabolizmus_elotte_utana.csv", index=False, encoding='utf-8-sig')

print("OK: CSV fajlok sikeresen elmentve!")
print(f"  - Homerseklet kizartak: {len(df_t_excl)} allat")
print(f"  - Metabolizmus kizartak: {len(df_m_excl)} allat")
