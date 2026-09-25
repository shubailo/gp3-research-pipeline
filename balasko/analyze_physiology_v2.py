import pandas as pd
import numpy as np
from scipy import stats
import itertools
import os

def analyze_file(filename):
    print(f"Analyzing {filename}...")
    xls = pd.ExcelFile(filename)
    sheets = [s for s in xls.sheet_names if s not in ['Summary', 'Animal_metadata']]
    
    all_data = []
    for sheet in sheets:
        df = pd.read_excel(filename, sheet_name=sheet)
        
        parts = sheet.split('_')
        diet = parts[0].replace('12', '') 
        treatment = parts[1] 
        
        time_col = None
        for i, col in enumerate(df.columns):
            if 'Time' in str(col):
                time_col = col
                time_col_idx = i
                break
                
        if time_col is None:
            continue
            
        animal_cols = [c for c in df.columns[time_col_idx+1:] if str(c).replace('.0','').isdigit()]
        
        for idx, row in df.iterrows():
            t = row[time_col]
            param_name = row['Parameter']
            for animal in animal_cols:
                val = row[animal]
                if pd.notna(val) and isinstance(val, (int, float)):
                    all_data.append({
                        'File': filename,
                        'Parameter': param_name,
                        'Diet': diet,
                        'Treatment': treatment,
                        'Time': t,
                        'Animal': str(animal),
                        'Value': float(val)
                    })
                    
    df_raw = pd.DataFrame(all_data)
    
    # Identify Biological Outliers / Technical Failures
    # Tc < 33, VO2 < 5. We will apply this based on parameter name.
    df_raw['Is_Failed'] = False
    
    def is_failed(row):
        val = row['Value']
        p = str(row['Parameter'])
        # Only filter absolute Tc, not dTc
        if p.startswith('Tc') and val < 33:
            return True
        # Only filter absolute VO2, not dVO2
        if p == 'VO2' and val < 5:
            return True
        return False
        
    df_raw['Is_Failed'] = df_raw.apply(is_failed, axis=1)
    
    failed_list = df_raw[df_raw['Is_Failed']].to_dict('records')
    
    df_clean = df_raw[~df_raw['Is_Failed']]
    
    # Calculate AUC for each animal (Time >= 0)
    # We will compute AUC using trapezoidal rule
    auc_data = []
    for (param, diet, treatment, animal), group in df_clean[df_clean['Time'] >= 0].groupby(['Parameter', 'Diet', 'Treatment', 'Animal']):
        group = group.sort_values('Time')
        if len(group) > 1:
            auc = np.trapezoid(group['Value'], group['Time'])
            auc_data.append({
                'Parameter': param,
                'Diet': diet,
                'Treatment': treatment,
                'Animal': animal,
                'AUC': auc
            })
            
    df_auc = pd.DataFrame(auc_data)
    
    return df_clean, df_auc, failed_list

def run_stats(data_subset, group_col, val_col):
    groups = data_subset[group_col].unique()
    if len(groups) < 2:
        return np.nan, {}
        
    group_arrays = [data_subset[data_subset[group_col] == g][val_col].values for g in groups]
    group_arrays = [a for a in group_arrays if len(a) > 1]
    
    if len(group_arrays) < 2:
        return np.nan, {}
        
    try:
        f_stat, p_anova = stats.f_oneway(*group_arrays)
    except:
        p_anova = np.nan
        
    pairwise = {}
    for g1, g2 in itertools.combinations(groups, 2):
        a1 = data_subset[data_subset[group_col] == g1][val_col].values
        a2 = data_subset[data_subset[group_col] == g2][val_col].values
        if len(a1) > 1 and len(a2) > 1:
            try:
                t_stat, p_t = stats.ttest_ind(a1, a2, equal_var=False)
                pairwise[f"{g1}_vs_{g2}"] = p_t
            except:
                pairwise[f"{g1}_vs_{g2}"] = np.nan
                
    return p_anova, pairwise

def main():
    df_clean_t, df_auc_t, fails_t = analyze_file('animaldata_temperature.xlsx')
    df_clean_m, df_auc_m, fails_m = analyze_file('animaldata_metabolism.xlsx')
    
    df_clean = pd.concat([df_clean_t, df_clean_m])
    df_auc = pd.concat([df_auc_t, df_auc_m])
    fails = fails_t + fails_m
    
    # 1. AUC Statistics
    auc_results = []
    for param in df_auc['Parameter'].unique():
        df_p = df_auc[df_auc['Parameter'] == param]
        
        # Diet effect per Treatment
        for treatment in df_p['Treatment'].unique():
            df_sub = df_p[df_p['Treatment'] == treatment]
            p_anova, pairs = run_stats(df_sub, 'Diet', 'AUC')
            auc_results.append({'Parameter': param, 'Comparison': f"Diet effect in {treatment}", 'Type': 'ANOVA', 'P_Value': p_anova})
            for k, p in pairs.items():
                auc_results.append({'Parameter': param, 'Comparison': f"{k} in {treatment}", 'Type': 'T-test', 'P_Value': p})
                
        # Treatment effect per Diet
        for diet in df_p['Diet'].unique():
            df_sub = df_p[df_p['Diet'] == diet]
            p_anova, pairs = run_stats(df_sub, 'Treatment', 'AUC')
            auc_results.append({'Parameter': param, 'Comparison': f"Treatment effect in {diet}", 'Type': 'ANOVA', 'P_Value': p_anova})
            for k, p in pairs.items():
                auc_results.append({'Parameter': param, 'Comparison': f"{k} in {diet}", 'Type': 'T-test', 'P_Value': p})
                
    df_auc_results = pd.DataFrame(auc_results)
    df_auc_results.to_csv('statistical_results_AUC.csv', index=False)
    
    # 2. Timepoint Statistics
    time_results = []
    for param in df_clean['Parameter'].unique():
        df_p = df_clean[df_clean['Parameter'] == param]
        for t in sorted(df_p['Time'].unique()):
            df_time = df_p[df_p['Time'] == t]
            
            # Diet effect per Treatment
            for treatment in df_time['Treatment'].unique():
                df_sub = df_time[df_time['Treatment'] == treatment]
                p_anova, pairs = run_stats(df_sub, 'Diet', 'Value')
                if not pd.isna(p_anova) and p_anova < 0.05:
                    time_results.append({'Parameter': param, 'Time': t, 'Comparison': f"Diet effect in {treatment}", 'Type': 'ANOVA', 'P_Value': p_anova})
                    for k, p in pairs.items():
                        if not pd.isna(p) and p < 0.05:
                            time_results.append({'Parameter': param, 'Time': t, 'Comparison': f"{k} in {treatment}", 'Type': 'T-test', 'P_Value': p})
                            
            # Treatment effect per Diet
            for diet in df_time['Diet'].unique():
                df_sub = df_time[df_time['Diet'] == diet]
                p_anova, pairs = run_stats(df_sub, 'Treatment', 'Value')
                if not pd.isna(p_anova) and p_anova < 0.05:
                    time_results.append({'Parameter': param, 'Time': t, 'Comparison': f"Treatment effect in {diet}", 'Type': 'ANOVA', 'P_Value': p_anova})
                    for k, p in pairs.items():
                        if not pd.isna(p) and p < 0.05:
                            time_results.append({'Parameter': param, 'Time': t, 'Comparison': f"{k} in {diet}", 'Type': 'T-test', 'P_Value': p})
                            
    df_time_results = pd.DataFrame(time_results)
    df_time_results.to_csv('statistical_results_timepoints_significant_only.csv', index=False)
    
    # Write Markdown
    artifacts_dir = r"C:\Users\shuba\.gemini\antigravity-ide\brain\193e6dd7-b967-442b-835b-7573e565a974"
    
    with open(os.path.join(artifacts_dir, 'research_protocol_results.md'), 'w', encoding='utf-8') as f:
        f.write("# Proper Dataset Analysis Results\n\n")
        f.write(f"We identified {len(fails)} technical failures (e.g. impossible values like Tc < 33).\n")
        
        f.write("## 1. Area Under the Curve (AUC) Significant Findings\n")
        f.write("Calculated for Time >= 0. P-values < 0.05.\n\n")
        f.write("| Parameter | Comparison | Type | P-value |\n")
        f.write("|---|---|---|---|\n")
        for _, row in df_auc_results[df_auc_results['P_Value'] < 0.05].iterrows():
            f.write(f"| {row['Parameter']} | {row['Comparison']} | {row['Type']} | {row['P_Value']:.4f} |\n")
            
        f.write("\n## 2. Timepoint-by-Timepoint Significant Findings\n")
        f.write("Only showing P-values < 0.05.\n\n")
        f.write("| Parameter | Time | Comparison | Type | P-value |\n")
        f.write("|---|---|---|---|---|\n")
        for _, row in df_time_results.iterrows():
            f.write(f"| {row['Parameter']} | {row['Time']} | {row['Comparison']} | {row['Type']} | {row['P_Value']:.4f} |\n")

if __name__ == '__main__':
    main()
