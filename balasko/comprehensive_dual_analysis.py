# -*- coding: utf-8 -*-
"""
comprehensive_dual_analysis.py
-------------------------------
Külön-külön, precízen elemzi a két független adatbázist:
  1. animaldata_temperature.xlsx (Tc, dTc, Ts, dTs, Ta, HLI)
  2. animaldata_metabolism.xlsx (VO2, dVO2, VCO2, dVCO2, RQ, EE)
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(r"C:\Users\shuba\Desktop\Researcher - Dóri\balasko")

PROBLEM_KEYWORDS = [
    "szétcsúszott", "szétrágta", "lyukas", "nehezen megy be",
    "nem kap pg", "nem kap pg-t", "pg nincs", "oxy nincs",
    "pg-", "gennyes", "véres", "visszafordulva", "visszacsúszott",
    "fürdetés", "ül", "magas tc", "beszaladt a pg"
]

def clean_id(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s

def has_problem(comment_str):
    if not comment_str or pd.isna(comment_str):
        return False, []
    comm = str(comment_str).lower().strip()
    found = []
    for kw in PROBLEM_KEYWORDS:
        if kw in comm:
            found.append(kw)
    return len(found) > 0, found

def load_file_metadata(filepath):
    xl = pd.ExcelFile(filepath)
    df_meta = xl.parse("Animal_metadata")
    records = []
    for idx, r in df_meta.iterrows():
        aid = clean_id(r.get("Animal_ID"))
        grp = str(r.get("Group")).strip() if pd.notna(r.get("Group")) else ""
        trt = str(r.get("Treatment")).strip() if pd.notna(r.get("Treatment")) else ""
        comm = str(r.get("Comment")).strip() if pd.notna(r.get("Comment")) else ""
        has_p, kws = has_problem(comm)
        records.append({
            "Animal_ID": aid,
            "Group": grp,
            "Treatment": trt,
            "Comment": comm,
            "HasProblem": has_p,
            "Keywords": kws
        })
    return pd.DataFrame(records)

def calc_sem(arr):
    arr = np.array([x for x in arr if not np.isnan(x)])
    if len(arr) < 2:
        return np.nan
    return np.std(arr, ddof=1) / np.sqrt(len(arr))

def run_analysis():
    datasets = [
        {
            "filename": "animaldata_temperature.xlsx",
            "name": "HŐMÉRSÉKLET (temperature)",
            "params": ["Tc", "dTc", "Ts", "dTs", "Ta", "HLI"],
            "primary_params": ["Tc", "dTc"]
        },
        {
            "filename": "animaldata_metabolism.xlsx",
            "name": "METABOLIZMUS (metabolism)",
            "params": ["VO2", "dVO2", "VCO2", "dVCO2", "RQ", "EE"],
            "primary_params": ["VO2", "dVO2", "RQ"]
        }
    ]

    all_file_summaries = {}

    for ds in datasets:
        fn = ds["filename"]
        target_params = ds["params"]
        filepath = BASE_DIR / fn
        xl = pd.ExcelFile(filepath)
        df_meta = load_file_metadata(filepath)
        sheets = [s for s in xl.sheet_names if s not in ['Summary', 'Animal_metadata']]

        print(f"\n{'='*90}")
        print(f"ELEMEZZÜK: {fn} ({ds['name']})")
        print(f"{'='*90}")

        evaluated_animals = []

        for sheet in sheets:
            df = xl.parse(sheet)
            time_col = None
            time_idx = None
            for i, col in enumerate(df.columns):
                if 'Time' in str(col) or 'time' in str(col):
                    time_col = col
                    time_idx = i
                    break
            if time_col is None:
                continue

            param_col = None
            for col in df.columns[:time_idx]:
                if 'Parameter' in str(col) or 'Param' in str(col):
                    param_col = col
                    break

            animal_cols = [c for c in df.columns[time_idx + 1:]]

            # t >= 0
            df['_t'] = pd.to_numeric(df[time_col], errors='coerce')
            df_post = df[df['_t'] >= 0].copy()
            df_post['_param_clean'] = df_post[param_col].astype(str).str.strip()

            parts = sheet.split('_')
            grp_name = parts[0] if len(parts) > 0 else ""
            trt_name = parts[1] if len(parts) > 1 else ""

            # 1. Minden állat átlaga
            sheet_animal_means = {}
            for col in animal_cols:
                aid_str = clean_id(col)
                a_means = {}
                for p in target_params:
                    matching_rows = df_post[df_post['_param_clean'].str.startswith(p)]
                    if not matching_rows.empty:
                        vals = pd.to_numeric(matching_rows[col], errors='coerce').dropna()
                        if len(vals) > 0:
                            a_means[p] = vals.mean()
                sheet_animal_means[col] = a_means

            # 2. Csoport statisztika
            sheet_grp_stats = {}
            for p in target_params:
                vals = [sheet_animal_means[col].get(p, np.nan) for col in animal_cols]
                vals = [v for v in vals if not np.isnan(v)]
                if len(vals) > 0:
                    q1 = np.percentile(vals, 25) if len(vals) >= 4 else np.nan
                    q3 = np.percentile(vals, 75) if len(vals) >= 4 else np.nan
                    sheet_grp_stats[p] = {
                        "mean": np.mean(vals),
                        "std": np.std(vals, ddof=1) if len(vals) > 1 else 0.0,
                        "n": len(vals),
                        "q1": q1,
                        "q3": q3,
                        "iqr": q3 - q1 if not np.isnan(q1) else 0.0
                    }

            # 3. Z-score és komment párosítás
            for col in animal_cols:
                aid_str = clean_id(col)
                # metadata keresés
                meta_matches = df_meta[
                    (df_meta['Animal_ID'] == aid_str) & 
                    (df_meta['Group'].str.lower() == grp_name.lower()) & 
                    (df_meta['Treatment'].str.lower() == trt_name.lower())
                ]
                if meta_matches.empty:
                    meta_matches = df_meta[df_meta['Animal_ID'] == aid_str]

                comm = ""
                has_p = False
                kws = []
                if not meta_matches.empty:
                    comm = meta_matches.iloc[0]['Comment']
                    has_p = meta_matches.iloc[0]['HasProblem']
                    kws = meta_matches.iloc[0]['Keywords']

                a_means = sheet_animal_means[col]
                z_scores = {}
                outlier_details = []

                for p, val in a_means.items():
                    st = sheet_grp_stats.get(p)
                    if st and st['std'] > 0:
                        z = (val - st['mean']) / st['std']
                        z_scores[p] = round(z, 2)
                        is_iqr = False
                        if st['iqr'] > 0:
                            is_iqr = (val < st['q1'] - 1.5 * st['iqr']) or (val > st['q3'] + 1.5 * st['iqr'])
                        
                        if abs(z) >= 2.0 or is_iqr:
                            outlier_details.append(f"{p}: z={z:+.2f} (val={val:.3f}, grp={st['mean']:.3f}±{st['std']:.3f})")

                max_z = max([abs(z) for z in z_scores.values()]) if z_scores else 0.0

                # Döntési szabály:
                # 1. KIZÁRANDÓ:
                #    A) Technikai hiba (komment: szétcsúszott, lyukas, szétrágta, véres, colon vissza stb.) ÉS |z| >= 1.8 bármely paraméterre
                #    B) Extrém adat-outlier (|z| >= 2.5) még ha nincs komment sem
                #    C) Biológiai képtelenség (pl. RQ > 1.05 vagy RQ < 0.65)
                # 2. MEGTARTHATÓ:
                #    Mindenki más.
                verdict = "MEGTARTHATÓ"
                reason = "Normális határokon belüli adat"
                
                is_rq_extreme = False
                if 'RQ' in a_means:
                    if a_means['RQ'] > 1.05 or a_means['RQ'] < 0.65:
                        is_rq_extreme = True

                if has_p and max_z >= 1.8:
                    verdict = "KIZÁRANDÓ"
                    reason = f"Technikai hiba ({comm}) + kiugró adat (|z|={max_z:.2f})"
                elif max_z >= 2.5:
                    verdict = "KIZÁRANDÓ"
                    reason = f"Súlyos statisztikai outlier (|z|={max_z:.2f})"
                elif is_rq_extreme:
                    verdict = "KIZÁRANDÓ"
                    reason = f"Fizikailag/biológiailag lehetetlen RQ ({a_means['RQ']:.3f})"
                elif has_p and max_z < 1.8:
                    verdict = "MEGTARTHATÓ"
                    reason = f"Van komment ('{comm}'), de az adat normális (|z|={max_z:.2f} < 1.8)"

                evaluated_animals.append({
                    "File": fn,
                    "Sheet": sheet,
                    "Col": col,
                    "Animal_ID": aid_str,
                    "Comment": comm,
                    "HasProblem": has_p,
                    "Max_Z": max_z,
                    "Z_Scores": z_scores,
                    "OutlierDetails": "; ".join(outlier_details),
                    "Verdict": verdict,
                    "Reason": reason,
                    "Means": a_means
                })

        df_eval = pd.DataFrame(evaluated_animals)

        # Kizártak listája sheetenként
        exclusions_per_sheet = {}
        for sheet in sheets:
            sub = df_eval[df_eval['Sheet'] == sheet]
            excl = sub[sub['Verdict'] == 'KIZÁRANDÓ']['Col'].tolist()
            exclusions_per_sheet[sheet] = excl

        # 4. ELŐTTE / UTÁNA statisztikák kiszámítása
        before_after_rows = []
        for sheet in sheets:
            sub = df_eval[df_eval['Sheet'] == sheet]
            excl_cols = exclusions_per_sheet[sheet]
            all_cols = sub['Col'].tolist()
            clean_cols = [c for c in all_cols if c not in excl_cols]

            for p in target_params:
                # Előtte
                vals_all = [sub[sub['Col'] == c].iloc[0]['Means'].get(p, np.nan) for c in all_cols]
                vals_all = [v for v in vals_all if not np.isnan(v)]
                # Utána
                vals_clean = [sub[sub['Col'] == c].iloc[0]['Means'].get(p, np.nan) for c in clean_cols]
                vals_clean = [v for v in vals_clean if not np.isnan(v)]

                n_all = len(vals_all)
                mean_all = np.mean(vals_all) if n_all > 0 else np.nan
                sem_all = calc_sem(vals_all) if n_all > 1 else np.nan

                n_clean = len(vals_clean)
                mean_clean = np.mean(vals_clean) if n_clean > 0 else np.nan
                sem_clean = calc_sem(vals_clean) if n_clean > 1 else np.nan

                sem_pct = ((sem_clean - sem_all) / sem_all * 100.0) if (sem_all and not np.isnan(sem_all) and sem_all > 0) else np.nan
                mean_delta = (mean_clean - mean_all) if (not np.isnan(mean_clean) and not np.isnan(mean_all)) else np.nan

                before_after_rows.append({
                    "File": fn,
                    "Sheet": sheet,
                    "Param": p,
                    "n_all": n_all,
                    "mean_all": mean_all,
                    "sem_all": sem_all,
                    "n_clean": n_clean,
                    "mean_clean": mean_clean,
                    "sem_clean": sem_clean,
                    "mean_delta": mean_delta,
                    "sem_pct": sem_pct
                })

        df_ba = pd.DataFrame(before_after_rows)
        all_file_summaries[fn] = {
            "eval": df_eval,
            "ba": df_ba,
            "exclusions": exclusions_per_sheet
        }

        # Kiírás a konzolra
        print(f"\n--- KIZÁRANDÓ ÁLLATOK EBBŐL A TÁBLÁBÓL ({fn}) ---")
        excl_total = df_eval[df_eval['Verdict'] == 'KIZÁRANDÓ']
        print(f"Összesen kizárandó: {len(excl_total)} állat")
        for idx, r in excl_total.iterrows():
            print(f"  [{r['Sheet']:15s}] ID={r['Animal_ID']:>7} | max|z|={r['Max_Z']:4.2f} | Ok: {r['Reason']} | Részletek: {r['OutlierDetails']}")

    return all_file_summaries

if __name__ == '__main__':
    summaries = run_analysis()
