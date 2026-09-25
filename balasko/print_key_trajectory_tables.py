# -*- coding: utf-8 -*-
"""
print_key_trajectory_tables.py
------------------------------
Készít egy tömör, olvasható táblázatot az időgörbék legfontosabb pontjairól:
Időpontok: -30, 0, 30, 60, 90, 120, 150, 180 min
A leginkább érintett csoportokra.
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(r"C:\Users\shuba\Desktop\Researcher - Dóri\balasko")

df_t = pd.read_csv(BASE_DIR / "timecourses_homerseklet.csv")
df_m = pd.read_csv(BASE_DIR / "timecourses_metabolizmus.csv")

key_times = [-30, 0, 30, 60, 90, 120, 150, 180]

print("=== HŐMÉRSÉKLET: KULCS IDŐPONTOK LEFUTÁSA ===")
for sheet, param in [('CR12_aMSH', 'Tc'), ('CR12_aMSH', 'dTc'), ('TR12_Control', 'dTc'), ('TR12_Leptin', 'Tc'), ('CR12_Leptin', 'Tc')]:
    sub = df_t[(df_t['Sheet'] == sheet) & (df_t['Param'] == param) & (df_t['Time'].isin(key_times))]
    print(f"\n--- {sheet} | {param} ---")
    print(f"{'Time':>5} | {'Mean (elotte)':>12} | {'SEM (elotte)':>12} | {'Mean (utana)':>12} | {'SEM (utana)':>12} | {'SEM Delta%':>10}")
    for _, r in sub.iterrows():
        print(f"{int(r['Time']):5d} | {r['mean_before']:12.3f} | {r['sem_before']:12.4f} | {r['mean_after']:12.3f} | {r['sem_after']:12.4f} | {r['sem_pct']:+7.1f}%")

print("\n\n=== METABOLIZMUS: KULCS IDŐPONTOK LEFUTÁSA ===")
for sheet, param in [('TR12_Leptin', 'dVO2'), ('CR12_Leptin', 'dVO2'), ('NF12_Control', 'VO2'), ('NF12_aMSH', 'VO2'), ('NF12_aMSH', 'RQ')]:
    sub = df_m[(df_m['Sheet'] == sheet) & (df_m['Param'] == param) & (df_m['Time'].isin(key_times))]
    print(f"\n--- {sheet} | {param} ---")
    print(f"{'Time':>5} | {'Mean (elotte)':>12} | {'SEM (elotte)':>12} | {'Mean (utana)':>12} | {'SEM (utana)':>12} | {'SEM Delta%':>10}")
    for _, r in sub.iterrows():
        print(f"{int(r['Time']):5d} | {r['mean_before']:12.3f} | {r['sem_before']:12.4f} | {r['mean_after']:12.3f} | {r['sem_after']:12.4f} | {r['sem_pct']:+7.1f}%")
