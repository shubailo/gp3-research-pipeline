# -*- coding: utf-8 -*-
"""
analyze_timecourses.py
-----------------------
Kiszámítja az időgörbék (folyamatábrák) pontjait (-30-tól 180 percig, 10 percenként, 22 időpont):
- Minden csoportra (TR12, NF12, CR12 x Control, aMSH, Leptin)
- Minden kulcsparaméterre (Tc, dTc, Ts a hőmérsékletnél; VO2, dVO2, RQ a metabolizmusnál)
- ELŐTTE (minden állat) vs. UTÁNA (kizártak nélkül)
- Időpontonként: N, Átlag, SEM, ΔÁtlag, % SEM változás
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(r"C:\Users\shuba\Desktop\Researcher - Dóri\balasko")

from generate_final_stats import clean_id, calc_sem

# Betöltjük a végleges kizárási listákat a CSV-kből
df_t_excl = pd.read_csv(BASE_DIR / "kizarasok_homerseklet.csv")
df_m_excl = pd.read_csv(BASE_DIR / "kizarasok_metabolizmus.csv")

temp_excl = {}
for sheet, group in df_t_excl.groupby('Csoport'):
    temp_excl[sheet] = [clean_id(x) for x in group['Állat_ID'].tolist()]

metab_excl = {}
for sheet, group in df_m_excl.groupby('Csoport'):
    metab_excl[sheet] = [clean_id(x) for x in group['Állat_ID'].tolist()]

print("Hőmérséklet kizárások:", temp_excl)
print("Metabolizmus kizárások:", metab_excl)

def process_file_timecourses(filename, exclusions_dict, target_params):
    filepath = BASE_DIR / filename
    xl = pd.ExcelFile(filepath)
    sheets = [s for s in xl.sheet_names if s not in ['Summary', 'Animal_metadata']]
    
    records = []
    
    for sheet in sheets:
        df = xl.parse(sheet)
        time_col = [c for c in df.columns if 'Time' in str(c)][0]
        time_idx = list(df.columns).index(time_col)
        param_col = [c for c in df.columns if 'Param' in str(c)][0]
        animal_cols = list(df.columns)[time_idx+1:]
        
        excl_list = exclusions_dict.get(sheet, [])
        clean_cols = [c for c in animal_cols if clean_id(c) not in excl_list and str(c).strip() not in excl_list]
        
        df['_param_clean'] = df[param_col].astype(str).str.strip()
        
        # Végigmegyünk a releváns paramétereken
        for p in target_params:
            sub = df[df['_param_clean'].str.startswith(p)].copy()
            if sub.empty:
                continue
                
            sub_sorted = sub.sort_values(by=time_col)
            
            for _, row in sub_sorted.iterrows():
                t = int(row[time_col])
                
                # Értékek előtte (minden állat)
                vals_before = [row[c] for c in animal_cols if pd.notna(row[c]) and isinstance(row[c], (int, float))]
                # Értékek utána (tisztított állatok)
                vals_after = [row[c] for c in clean_cols if pd.notna(row[c]) and isinstance(row[c], (int, float))]
                
                n_b = len(vals_before)
                m_b = np.mean(vals_before) if n_b > 0 else np.nan
                s_b = calc_sem(vals_before) if n_b > 1 else np.nan
                
                n_a = len(vals_after)
                m_a = np.mean(vals_after) if n_a > 0 else np.nan
                s_a = calc_sem(vals_after) if n_a > 1 else np.nan
                
                m_delta = (m_a - m_b) if (not np.isnan(m_a) and not np.isnan(m_b)) else np.nan
                sem_pct = ((s_a - s_b) / s_b * 100.0) if (s_b and not np.isnan(s_b) and s_b > 0) else np.nan
                
                records.append({
                    "File": filename,
                    "Sheet": sheet,
                    "Param": p,
                    "Time": t,
                    "n_before": n_b,
                    "mean_before": m_b,
                    "sem_before": s_b,
                    "n_after": n_a,
                    "mean_after": m_a,
                    "sem_after": s_a,
                    "mean_delta": m_delta,
                    "sem_pct": sem_pct
                })
                
    return pd.DataFrame(records)

df_tc_temp = process_file_timecourses("animaldata_temperature.xlsx", temp_excl, ['Tc', 'dTc', 'Ts', 'dTs'])
df_tc_metab = process_file_timecourses("animaldata_metabolism.xlsx", metab_excl, ['VO2', 'dVO2', 'RQ', 'EE'])

df_tc_temp.to_csv(BASE_DIR / "timecourses_homerseklet.csv", index=False, encoding='utf-8-sig')
df_tc_metab.to_csv(BASE_DIR / "timecourses_metabolizmus.csv", index=False, encoding='utf-8-sig')

print("OK: Időgörbe adatok elmentve CSV-be!")
print(f"Hőmérséklet sorok száma: {len(df_tc_temp)}")
print(f"Metabolizmus sorok száma: {len(df_tc_metab)}")
