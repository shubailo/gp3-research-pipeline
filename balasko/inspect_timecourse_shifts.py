# -*- coding: utf-8 -*-
"""
inspect_timecourse_shifts.py
----------------------------
Kiszámítja, hogy az egyes időgörbéknél:
1. Átlagosan mennyit javult a SEM a 22 időpont mentén?
2. Hol voltak a legnagyobb elmozdulások (peak, baseline, late)?
3. Milyen a görbék lefutása a leginkább érintett csoportoknál?
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(r"C:\Users\shuba\Desktop\Researcher - Dóri\balasko")

df_t = pd.read_csv(BASE_DIR / "timecourses_homerseklet.csv")
df_m = pd.read_csv(BASE_DIR / "timecourses_metabolizmus.csv")

print("================================================================================")
print("HŐMÉRSÉKLET IDŐGÖRBÉK (-30 - 180 perc): ÁTLAGOS SEM VÁLTOZÁS CSOPORTONKÉNT")
print("================================================================================")

for (sheet, param), grp in df_t.groupby(['Sheet', 'Param']):
    if param in ['Tc', 'dTc']:
        sem_mean_pct = grp['sem_pct'].mean()
        max_sem_drop = grp['sem_pct'].min()
        max_sem_drop_t = grp.loc[grp['sem_pct'].idxmin(), 'Time']
        max_delta = grp['mean_delta'].abs().max()
        max_delta_t = grp.loc[grp['mean_delta'].abs().idxmax(), 'Time']
        print(f"{sheet:15s} | {param:4s} | Átl. SEM változás: {sem_mean_pct:+6.1f}% | Legnagyobb SEM javulás: {max_sem_drop:+6.1f}% (t={max_sem_drop_t:3d} min) | Max görbe-eltolódás: {max_delta:.3f} °C (t={max_delta_t:3d} min)")

print("\n================================================================================")
print("METABOLIZMUS IDŐGÖRBÉK (-30 - 180 perc): ÁTLAGOS SEM VÁLTOZÁS CSOPORTONKÉNT")
print("================================================================================")

for (sheet, param), grp in df_m.groupby(['Sheet', 'Param']):
    if param in ['VO2', 'dVO2', 'RQ']:
        sem_mean_pct = grp['sem_pct'].mean()
        max_sem_drop = grp['sem_pct'].min()
        max_sem_drop_t = grp.loc[grp['sem_pct'].idxmin(), 'Time']
        max_delta = grp['mean_delta'].abs().max()
        max_delta_t = grp.loc[grp['mean_delta'].abs().idxmax(), 'Time']
        print(f"{sheet:15s} | {param:4s} | Átl. SEM változás: {sem_mean_pct:+6.1f}% | Legnagyobb SEM javulás: {max_sem_drop:+6.1f}% (t={max_sem_drop_t:3d} min) | Max görbe-eltolódás: {max_delta:.3f} (t={max_delta_t:3d} min)")
