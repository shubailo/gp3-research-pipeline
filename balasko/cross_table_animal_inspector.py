# -*- coding: utf-8 -*-
"""
cross_table_animal_inspector.py
-------------------------------
Minden kérdéses állatot megkeres MINDKÉT fájlban, és összehasonlítja:
- Szerepel-e a Temperature fájlban? (Ha igen: melyik lapon, mi az adata, mi a z-score)
- Szerepel-e a Metabolism fájlban? (Ha igen: melyik lapon, mi az adata, mi a z-score)
- Mi a kommentje a metaadatban?
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(r"C:\Users\shuba\Desktop\Researcher - Dóri\balasko")

def clean_id(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s

def load_data(filename, params):
    filepath = BASE_DIR / filename
    xl = pd.ExcelFile(filepath)
    df_meta = xl.parse("Animal_metadata")
    sheets = [s for s in xl.sheet_names if s not in ['Summary', 'Animal_metadata']]
    
    animals_dict = {}
    
    for sheet in sheets:
        df = xl.parse(sheet)
        time_col = [c for c in df.columns if 'Time' in str(c)][0]
        time_idx = list(df.columns).index(time_col)
        param_col = [c for c in df.columns if 'Param' in str(c)][0]
        animal_cols = list(df.columns)[time_idx+1:]
        
        df_post = df[pd.to_numeric(df[time_col], errors='coerce') >= 0].copy()
        df_post['_param_clean'] = df_post[param_col].astype(str).str.strip()
        
        # Átlagok
        col_means = {}
        for col in animal_cols:
            means = {}
            for p in params:
                sub = df_post[df_post['_param_clean'].str.startswith(p)]
                if not sub.empty:
                    vals = pd.to_numeric(sub[col], errors='coerce').dropna()
                    if len(vals) > 0:
                        means[p] = vals.mean()
            col_means[col] = means
            
        # Csoport statisztika
        grp_stats = {}
        for p in params:
            vals = [col_means[c].get(p, np.nan) for c in animal_cols]
            vals = [v for v in vals if not np.isnan(v)]
            if vals:
                grp_stats[p] = {"mean": np.mean(vals), "std": np.std(vals, ddof=1) if len(vals) > 1 else 0.0}
                
        for col in animal_cols:
            aid = clean_id(col)
            # metadata
            m = df_meta[df_meta['Animal_ID'].astype(str) == aid]
            comm = str(m.iloc[0]['Comment']).strip() if not m.empty and pd.notna(m.iloc[0]['Comment']) else ""
            
            z_scores = {}
            for p, val in col_means[col].items():
                st = grp_stats.get(p)
                if st and st['std'] > 0:
                    z_scores[p] = (val - st['mean']) / st['std']
                    
            key = (aid, sheet)
            animals_dict[key] = {
                "aid": aid,
                "col": col,
                "sheet": sheet,
                "comment": comm,
                "means": col_means[col],
                "z_scores": z_scores,
                "grp_stats": grp_stats
            }
            
    return animals_dict

temp_dict = load_data("animaldata_temperature.xlsx", ['Tc', 'dTc', 'Ts', 'dTs', 'Ta', 'HLI'])
metab_dict = load_data("animaldata_metabolism.xlsx", ['VO2', 'dVO2', 'VCO2', 'dVCO2', 'RQ', 'EE'])

# Nézzük meg az összes állatot, aki valaha felmerült
candidate_ids = [
    '6919', '7675', '7375', '7380', '7245', '7243', '7237', '7240', '7246', '7247',
    '7318', '7328', '7340', '7336', '7337', '7338', '7339', '7345', '7346', '7347',
    '7430', '7438', '7441.1', '7565', '7566', '7567', '7569', '7570',
    '6545.2', '6547.1', '6546.3', '6548.1', '7208.1', '7209', '7204', '6905'
]

print(f"{'ID':<10} | {'Sheet':<14} | {'In Temp?':<9} | {'Temp z-score / hiba':<35} | {'In Metab?':<9} | {'Metab z-score / hiba':<35}")
print("-" * 125)

for cid in candidate_ids:
    # Keresünk temp-ben
    t_matches = [v for k, v in temp_dict.items() if k[0] == cid or clean_id(v['col']) == cid]
    m_matches = [v for k, v in metab_dict.items() if k[0] == cid or clean_id(v['col']) == cid]
    
    # Ha több lapban is van
    sheets = set([x['sheet'] for x in t_matches] + [x['sheet'] for x in m_matches])
    if not sheets:
        sheets = ["-"]
        
    for sh in sheets:
        t_obj = [x for x in t_matches if x['sheet'] == sh]
        m_obj = [x for x in m_matches if x['sheet'] == sh]
        
        t_info = "NINCS a táblában"
        if t_obj:
            o = t_obj[0]
            zs = o['z_scores']
            top_z = sorted(zs.items(), key=lambda x: abs(x[1]), reverse=True)
            top_str = f"{top_z[0][0]}: z={top_z[0][1]:+.2f}" if top_z else "n/a"
            comm = f" [{o['comment'][:15]}]" if o['comment'] else ""
            t_info = f"{top_str}{comm}"
            
        m_info = "NINCS a táblában"
        if m_obj:
            o = m_obj[0]
            zs = o['z_scores']
            top_z = sorted(zs.items(), key=lambda x: abs(x[1]), reverse=True)
            top_str = f"{top_z[0][0]}: z={top_z[0][1]:+.2f}" if top_z else "n/a"
            comm = f" [{o['comment'][:15]}]" if o['comment'] else ""
            m_info = f"{top_str}{comm}"
            
        print(f"{cid:<10} | {sh:<14} | {'IGEN' if t_obj else 'NEM':<9} | {t_info:<35} | {'IGEN' if m_obj else 'NEM':<9} | {m_info:<35}")
