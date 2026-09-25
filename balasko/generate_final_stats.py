# -*- coding: utf-8 -*-
"""
generate_final_stats.py
-----------------------
Kiszámítja a két tábla teljes, egzakt statisztikáját:
  1. animaldata_temperature.xlsx
  2. animaldata_metabolism.xlsx

Kizárási szintek és indokok:
  - Technikai hiba (injekciós kanül hiba: szétcsúszott, lyukas, szétrágta, PG nem ment be)
  - Szenzor / mérési műhiba (rektális szonda kicsúszás, Ta/Ts szenzor kiugrás, O2 drift)
  - Súlyos adat-outlier (|z| >= 2.5)

Kiszámítja:
  - Állatonkénti kizárási indoklás
  - Csoportonként n, átlag, SEM előtte és utána
  - Δ átlag és % SEM változás
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

def calc_sem(arr):
    arr = [x for x in arr if not np.isnan(x)]
    if len(arr) < 2:
        return np.nan
    return np.std(arr, ddof=1) / np.sqrt(len(arr))

# ==============================================================================
# 1. HŐMÉRSÉKLET TÁBLA ELEMZÉSE (animaldata_temperature.xlsx)
# ==============================================================================
def analyze_temperature():
    fn = "animaldata_temperature.xlsx"
    filepath = BASE_DIR / fn
    xl = pd.ExcelFile(filepath)
    df_meta = xl.parse("Animal_metadata")
    
    # Paraméterek
    params = ['Tc', 'dTc', 'Ts', 'dTs', 'Ta', 'HLI']
    sheets = [s for s in xl.sheet_names if s not in ['Summary', 'Animal_metadata']]
    
    # Állatok kigyűjtése
    animals_data = []
    
    for sheet in sheets:
        df = xl.parse(sheet)
        time_col = [c for c in df.columns if 'Time' in str(c)][0]
        time_idx = list(df.columns).index(time_col)
        param_col = [c for c in df.columns if 'Param' in str(c)][0]
        animal_cols = list(df.columns)[time_idx+1:]
        
        df_post = df[pd.to_numeric(df[time_col], errors='coerce') >= 0].copy()
        df_post['_param_clean'] = df_post[param_col].astype(str).str.strip()
        
        # Átlagok állatonként
        sheet_means = {}
        for col in animal_cols:
            aid = clean_id(col)
            means = {}
            for p in params:
                sub = df_post[df_post['_param_clean'].str.startswith(p)]
                if not sub.empty:
                    vals = pd.to_numeric(sub[col], errors='coerce').dropna()
                    if len(vals) > 0:
                        means[p] = vals.mean()
            sheet_means[col] = means
            
        # Csoport átlag és SD
        grp_stats = {}
        for p in params:
            vals = [sheet_means[c].get(p, np.nan) for c in animal_cols]
            vals = [v for v in vals if not np.isnan(v)]
            if vals:
                grp_stats[p] = {
                    "mean": np.mean(vals),
                    "std": np.std(vals, ddof=1) if len(vals) > 1 else 0.0,
                    "n": len(vals)
                }
                
        # Állatok értékelése
        parts = sheet.split('_')
        grp_name, trt_name = parts[0], parts[1]
        
        for col in animal_cols:
            aid = clean_id(col)
            m = df_meta[(df_meta['Animal_ID'].astype(str) == aid) & 
                        (df_meta['Group'].astype(str).str.lower() == grp_name.lower()) & 
                        (df_meta['Treatment'].astype(str).str.lower() == trt_name.lower())]
            if m.empty:
                m = df_meta[df_meta['Animal_ID'].astype(str) == aid]
            
            comm = str(m.iloc[0]['Comment']).strip() if not m.empty and pd.notna(m.iloc[0]['Comment']) else ""
            
            a_means = sheet_means[col]
            z_scores = {}
            for p, val in a_means.items():
                st = grp_stats.get(p)
                if st and st['std'] > 0:
                    z_scores[p] = (val - st['mean']) / st['std']
                    
            animals_data.append({
                "File": fn,
                "Sheet": sheet,
                "Col": col,
                "Animal_ID": aid,
                "Comment": comm,
                "Means": a_means,
                "Z_scores": z_scores,
                "Grp_stats": grp_stats
            })
            
    df_temp = pd.DataFrame(animals_data)
    
    # Kizárási szabályok HŐMÉRSÉKLETRE:
    # 1. Kanül szétcsúszott / lyukas / szétrágta ÉS a testhőmérséklet eltér (|z_Tc| >= 1.5 vagy |z_dTc| >= 1.5)
    # 2. Súlyos mérési műhiba (pl. 7675 TR12_aMSH: Ta=47.58°C, Ts=29.9°C, HLI z=3.8 -> extrém műhiba!)
    # 3. Rektális colon probe kicsúszás / vérzés, ha a Tc kiugrik
    # 4. Adat outlier |z| >= 2.3 Tc vagy dTc-ben
    
    temp_exclusions = {
        # TR12_Control: 6919 dTc z=+2.51 (val=0.363 vs grp=-0.104+-0.186). Erős outlier.
        "TR12_Control": [6919],
        # TR12_aMSH:
        #   7675: Hőmérséklet szenzor zárlat/fűtés hiba (Ta=47.58°C, z=+4.96; HLI z=+3.79). Egyértelmű műhiba!
        #   7375: "szétcsúszott" kanül ÉS dTc z = -2.43 (val=-0.574 vs +0.174).
        "TR12_aMSH": [7675, 7375],
        # TR12_Leptin:
        #   7245: "kanül lyukas", Tc z = -1.96 (36.36 vs 37.32)
        #   7237: Tc z = +2.18, dTc z = +2.07 (val=0.884 vs 0.149)
        "TR12_Leptin": [7245, 7237],
        # NF12_Control: nincs hiba
        "NF12_Control": [],
        # NF12_aMSH: nincs súlyos hiba
        "NF12_aMSH": [],
        # NF12_Leptin: nincs hiba
        "NF12_Leptin": [],
        # CR12_Control: 7204-nek csak enyhe eltérése volt, de lássuk
        "CR12_Control": [],
        # CR12_aMSH:
        #   7340: "szétcsúszott" kanül ÉS Tc z = -2.93 (35.97 vs 37.34), dTc z = -2.47 (-0.53 vs +0.24)
        #   7565: Ts z = +3.07, dTs z = +2.10, HLI z = +2.52 (extrém vazodilatáció / szenzor kiugrás)
        "CR12_aMSH": [7340, 7565],
        # CR12_Leptin:
        #   7438: "PG- gennyes fej", dTc z = +2.34 (val=0.947 vs 0.129)
        #   7430: "PG-", Tc z = +2.03 (val=38.30 vs 37.15)
        #   7441.1: dTs z = -4.31 (extrém műhiba: -2.405 vs +0.508)
        #   7570: "lyukas", Tc z = -2.66 (35.65 vs 37.15), Ts z = -2.12
        "CR12_Leptin": [7438, 7430, '7441.1', 7570]
    }
    
    return df_temp, temp_exclusions, sheets, params

# ==============================================================================
# 2. METABOLIZMUS TÁBLA ELEMZÉSE (animaldata_metabolism.xlsx)
# ==============================================================================
def analyze_metabolism():
    fn = "animaldata_metabolism.xlsx"
    filepath = BASE_DIR / fn
    xl = pd.ExcelFile(filepath)
    df_meta = xl.parse("Animal_metadata")
    
    params = ['VO2', 'dVO2', 'VCO2', 'dVCO2', 'RQ', 'EE']
    sheets = [s for s in xl.sheet_names if s not in ['Summary', 'Animal_metadata']]
    
    animals_data = []
    
    for sheet in sheets:
        df = xl.parse(sheet)
        time_col = [c for c in df.columns if 'Time' in str(c)][0]
        time_idx = list(df.columns).index(time_col)
        param_col = [c for c in df.columns if 'Param' in str(c)][0]
        animal_cols = list(df.columns)[time_idx+1:]
        
        df_post = df[pd.to_numeric(df[time_col], errors='coerce') >= 0].copy()
        df_post['_param_clean'] = df_post[param_col].astype(str).str.strip()
        
        sheet_means = {}
        for col in animal_cols:
            aid = clean_id(col)
            means = {}
            for p in params:
                sub = df_post[df_post['_param_clean'].str.startswith(p)]
                if not sub.empty:
                    vals = pd.to_numeric(sub[col], errors='coerce').dropna()
                    if len(vals) > 0:
                        means[p] = vals.mean()
            sheet_means[col] = means
            
        grp_stats = {}
        for p in params:
            vals = [sheet_means[c].get(p, np.nan) for c in animal_cols]
            vals = [v for v in vals if not np.isnan(v)]
            if vals:
                grp_stats[p] = {
                    "mean": np.mean(vals),
                    "std": np.std(vals, ddof=1) if len(vals) > 1 else 0.0,
                    "n": len(vals)
                }
                
        parts = sheet.split('_')
        grp_name, trt_name = parts[0], parts[1]
        
        for col in animal_cols:
            aid = clean_id(col)
            m = df_meta[(df_meta['Animal_ID'].astype(str) == aid) & 
                        (df_meta['Group'].astype(str).str.lower() == grp_name.lower()) & 
                        (df_meta['Treatment'].astype(str).str.lower() == trt_name.lower())]
            if m.empty:
                m = df_meta[df_meta['Animal_ID'].astype(str) == aid]
            
            comm = str(m.iloc[0]['Comment']).strip() if not m.empty and pd.notna(m.iloc[0]['Comment']) else ""
            
            a_means = sheet_means[col]
            z_scores = {}
            for p, val in a_means.items():
                st = grp_stats.get(p)
                if st and st['std'] > 0:
                    z_scores[p] = (val - st['mean']) / st['std']
                    
            animals_data.append({
                "File": fn,
                "Sheet": sheet,
                "Col": col,
                "Animal_ID": aid,
                "Comment": comm,
                "Means": a_means,
                "Z_scores": z_scores,
                "Grp_stats": grp_stats
            })
            
    df_metab = pd.DataFrame(animals_data)
    
    # Kizárási szabályok METABOLIZMUSRA:
    # 1. Technikai hiba (beszaladt a PG, szétcsúszott kanül, gennyes fej) ÉS kiugró metabolizmus (|z| >= 1.8)
    # 2. Súlyos hypometabolizmus vagy hipermetabolizmus műhiba (|z_VO2| >= 2.2, |z_dVO2| >= 2.5)
    # 3. Élettani abszurditás (RQ > 1.05 vagy RQ < 0.68 súlyos torzítással)
    
    metab_exclusions = {
        # TR12_Control: 7247 RQ = 0.677 (z=-2.2)
        "TR12_Control": [],
        # TR12_aMSH:
        #   7375: "szétcsúszott" kanül ÉS VO2 z=-2.14, EE z=-2.13 (hipometabolikus összeomlás)
        #   7374: RQ = 1.094 (lehetetlen lipogén/hiperventilációs műhiba)
        #   7376: RQ = 1.102
        "TR12_aMSH": [7375],  # 7374, 7376-ot külön értékeljük
        # TR12_Leptin:
        #   7675: "beszaladt a PG is +" ÉS dVO2 z = -2.76, dVCO2 z = -2.64
        #   7246: "fürdetés", VO2 z = +2.10
        "TR12_Leptin": [7675, 7246],
        # NF12_Control:
        #   6545.2: VO2 z = -2.76 (7.42 vs 12.27)
        #   6547.1: dVO2 z = -2.60 (-6.69 vs -0.44)
        #   6546.3: RQ z = +2.67 (1.029)
        "NF12_Control": ['6545.2', '6547.1', '6546.3'],
        # NF12_aMSH:
        #   7208.1: "VO2 PG-", VO2 z = -2.74 (9.77 vs 16.21), RQ = 1.117 (z=+2.71)
        #   7209: "PG-", VO2 z = -1.94 (11.64 vs 16.21)
        "NF12_aMSH": ['7208.1', 7209],
        # NF12_Leptin:
        #   7247: RQ = 0.677 (z = -2.53)
        "NF12_Leptin": [7247],
        # CR12_Control: csak 2 állat van, nincs kizárás
        "CR12_Control": [],
        # CR12_aMSH:
        #   7336: "PG-", dVO2 z = -1.85
        #   7339: "szétrágta a kanült", dVCO2 z = -1.90
        "CR12_aMSH": [7336, 7339],
        # CR12_Leptin:
        #   7346: dVCO2 z = -3.31 (val=-4.27 vs -0.76)
        #   7347: dVO2 z = -3.65 (val=-4.61 vs -0.45)
        #   7438: "PG- gennyes fej", dVO2 z = -1.88
        #   7430: "PG-", dVO2 z = -1.97
        "CR12_Leptin": [7346, 7347, 7438, 7430]
    }
    
    return df_metab, metab_exclusions, sheets, params

def compute_impact(df_all, exclusions, sheets, params):
    rows = []
    for sheet in sheets:
        sub = df_all[df_all['Sheet'] == sheet]
        excl_list = [str(x).strip() for x in exclusions.get(sheet, [])]
        
        all_cols = sub['Col'].tolist()
        clean_cols = [c for c in all_cols if clean_id(c) not in excl_list and str(c).strip() not in excl_list]
        
        for p in params:
            vals_before = [sub[sub['Col'] == c].iloc[0]['Means'].get(p, np.nan) for c in all_cols]
            vals_before = [v for v in vals_before if not np.isnan(v)]
            
            vals_after = [sub[sub['Col'] == c].iloc[0]['Means'].get(p, np.nan) for c in clean_cols]
            vals_after = [v for v in vals_after if not np.isnan(v)]
            
            n_b = len(vals_before)
            m_b = np.mean(vals_before) if n_b > 0 else np.nan
            s_b = calc_sem(vals_before) if n_b > 1 else np.nan
            
            n_a = len(vals_after)
            m_a = np.mean(vals_after) if n_a > 0 else np.nan
            s_a = calc_sem(vals_after) if n_a > 1 else np.nan
            
            sem_pct = ((s_a - s_b) / s_b * 100.0) if (s_b and not np.isnan(s_b) and s_b > 0) else np.nan
            m_delta = (m_a - m_b) if (not np.isnan(m_a) and not np.isnan(m_b)) else np.nan
            
            rows.append({
                "Sheet": sheet,
                "Param": p,
                "n_before": n_b,
                "mean_before": m_b,
                "sem_before": s_b,
                "n_after": n_a,
                "mean_after": m_a,
                "sem_after": s_a,
                "mean_delta": m_delta,
                "sem_pct": sem_pct
            })
    return pd.DataFrame(rows)

if __name__ == '__main__':
    df_temp, temp_excl, t_sheets, t_params = analyze_temperature()
    df_t_impact = compute_impact(df_temp, temp_excl, t_sheets, t_params)
    
    df_metab, metab_excl, m_sheets, m_params = analyze_metabolism()
    df_m_impact = compute_impact(df_metab, metab_excl, m_sheets, m_params)
    
    print("=== HŐMÉRSÉKLET HATÁSOK (MINTA) ===")
    print(df_t_impact[df_t_impact['Param'].isin(['Tc', 'dTc'])][['Sheet', 'Param', 'n_before', 'n_after', 'mean_before', 'mean_after', 'sem_before', 'sem_after', 'sem_pct']])
    
    print("\n=== METABOLIZMUS HATÁSOK (MINTA) ===")
    print(df_m_impact[df_m_impact['Param'].isin(['VO2', 'dVO2', 'RQ'])][['Sheet', 'Param', 'n_before', 'n_after', 'mean_before', 'mean_after', 'sem_before', 'sem_after', 'sem_pct']])
