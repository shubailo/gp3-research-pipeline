import pandas as pd
import numpy as np
from scipy import stats
import warnings
import itertools
import os

warnings.filterwarnings('ignore')

def get_outliers_iqr(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers_mask = (series < lower_bound) | (series > upper_bound)
    return outliers_mask

def analyze_file(filename, param_name):
    print(f"Analyzing {filename}...")
    xls = pd.ExcelFile(filename)
    sheets = [s for s in xls.sheet_names if s not in ['Summary', 'Animal_metadata']]
    
    # Extract data
    all_data = []
    for sheet in sheets:
        df = pd.read_excel(filename, sheet_name=sheet)
        
        # Determine group and treatment from sheet name (e.g. TR12_Control)
        parts = sheet.split('_')
        diet = parts[0].replace('12', '') # TR, NF, CR
        treatment = parts[1] # Control, aMSH, Leptin
        
        # Raw data columns are those after the 5th column
        # Columns: MEAN, SEM, n, Parameter, Time (min), then animal IDs
        time_col = None
        for i, col in enumerate(df.columns):
            if 'Time' in str(col):
                time_col = col
                time_col_idx = i
                break
                
        if time_col is None:
            print(f"Could not find Time column in {sheet}")
            continue
            
        animal_cols = df.columns[time_col_idx+1:]
        
        for idx, row in df.iterrows():
            t = row[time_col]
            for animal in animal_cols:
                val = row[animal]
                if pd.notna(val) and isinstance(val, (int, float)):
                    all_data.append({
                        'Parameter': param_name,
                        'Diet': diet,
                        'Treatment': treatment,
                        'Time': t,
                        'Animal': animal,
                        'Value': float(val)
                    })
                    
    df_raw = pd.DataFrame(all_data)
    
    # 1. Identify Outliers
    outliers_list = []
    df_raw['Is_Outlier'] = False
    
    # Group by Diet, Treatment, and Time to find outliers in that specific cluster
    for (diet, treatment, t), group in df_raw.groupby(['Diet', 'Treatment', 'Time']):
        mask = get_outliers_iqr(group['Value'])
        if mask.any():
            outlier_indices = group[mask].index
            df_raw.loc[outlier_indices, 'Is_Outlier'] = True
            for idx in outlier_indices:
                outliers_list.append(df_raw.loc[idx].to_dict())
                
    # 2. Statistical Testing (With and Without Outliers)
    results = []
    times = sorted(df_raw['Time'].unique())
    
    def test_effect(data_subset, group_col):
        groups = data_subset[group_col].unique()
        if len(groups) < 2:
            return None, {}
            
        group_arrays = [data_subset[data_subset[group_col] == g]['Value'].values for g in groups]
        group_arrays = [a for a in group_arrays if len(a) > 1]
        
        if len(group_arrays) < 2:
            return None, {}
            
        try:
            f_stat, p_anova = stats.f_oneway(*group_arrays)
        except:
            p_anova = np.nan
            
        pairwise = {}
        for g1, g2 in itertools.combinations(groups, 2):
            a1 = data_subset[data_subset[group_col] == g1]['Value'].values
            a2 = data_subset[data_subset[group_col] == g2]['Value'].values
            if len(a1) > 1 and len(a2) > 1:
                try:
                    t_stat, p_t = stats.ttest_ind(a1, a2, equal_var=False)
                    pairwise[f"{g1}_vs_{g2}"] = p_t
                except:
                    pairwise[f"{g1}_vs_{g2}"] = np.nan
                    
        return p_anova, pairwise

    for t in times:
        df_time = df_raw[df_raw['Time'] == t]
        
        # Test Diet effect per Treatment
        for treatment in df_time['Treatment'].unique():
            df_sub = df_time[df_time['Treatment'] == treatment]
            df_sub_clean = df_sub[~df_sub['Is_Outlier']]
            
            p_anova_all, pair_all = test_effect(df_sub, 'Diet')
            p_anova_clean, pair_clean = test_effect(df_sub_clean, 'Diet')
            
            results.append({
                'Parameter': param_name,
                'Time': t,
                'Comparison': f"Diet effect in {treatment}",
                'Type': 'ANOVA',
                'P_All': p_anova_all,
                'P_Clean': p_anova_clean
            })
            
            for k in pair_all.keys():
                results.append({
                    'Parameter': param_name,
                    'Time': t,
                    'Comparison': f"{k} in {treatment}",
                    'Type': 'T-test',
                    'P_All': pair_all[k],
                    'P_Clean': pair_clean.get(k, np.nan)
                })

        # Test Treatment effect per Diet
        for diet in df_time['Diet'].unique():
            df_sub = df_time[df_time['Diet'] == diet]
            df_sub_clean = df_sub[~df_sub['Is_Outlier']]
            
            p_anova_all, pair_all = test_effect(df_sub, 'Treatment')
            p_anova_clean, pair_clean = test_effect(df_sub_clean, 'Treatment')
            
            results.append({
                'Parameter': param_name,
                'Time': t,
                'Comparison': f"Treatment effect in {diet}",
                'Type': 'ANOVA',
                'P_All': p_anova_all,
                'P_Clean': p_anova_clean
            })
            
            for k in pair_all.keys():
                results.append({
                    'Parameter': param_name,
                    'Time': t,
                    'Comparison': f"{k} in {diet}",
                    'Type': 'T-test',
                    'P_All': pair_all[k],
                    'P_Clean': pair_clean.get(k, np.nan)
                })
                
    return outliers_list, results

def main():
    outliers_temp, res_temp = analyze_file('animaldata_temperature.xlsx', 'Temperature')
    outliers_met, res_met = analyze_file('animaldata_metabolism.xlsx', 'VO2')
    
    all_outliers = outliers_temp + outliers_met
    df_outliers = pd.DataFrame(all_outliers)
    df_outliers.to_csv('outliers_identified.csv', index=False)
    
    all_res = res_temp + res_met
    df_res = pd.DataFrame(all_res)
    
    def check_change(row):
        p1 = row['P_All']
        p2 = row['P_Clean']
        if pd.isna(p1) or pd.isna(p2):
            return "No Change"
        sig1 = p1 < 0.05
        sig2 = p2 < 0.05
        if sig1 and not sig2:
            return "Lost Significance"
        elif not sig1 and sig2:
            return "Gained Significance"
        else:
            return "No Change"
            
    df_res['Significance_Impact'] = df_res.apply(check_change, axis=1)
    df_res.to_csv('statistical_results_comparison.csv', index=False)
    
    changed = df_res[df_res['Significance_Impact'] != "No Change"]
    changed.to_csv('significant_changes_only.csv', index=False)
    
    artifacts_dir = r"C:\Users\shuba\.gemini\antigravity-ide\brain\d51ee855-4ed2-467b-869e-8981f305b41b"
    
    with open(os.path.join(artifacts_dir, 'outliers_list.md'), 'w', encoding='utf-8') as f:
        f.write("# Identified Statistical Outliers\n\n")
        f.write("The following data points were identified as outliers using the 1.5 * IQR method.\n\n")
        
        for param in df_outliers['Parameter'].unique():
            f.write(f"## {param}\n")
            sub = df_outliers[df_outliers['Parameter'] == param]
            for t in sorted(sub['Time'].unique()):
                sub_t = sub[sub['Time'] == t]
                f.write(f"### Time: {t} min\n")
                f.write("| Diet | Treatment | Animal | Value |\n")
                f.write("|---|---|---|---|\n")
                for _, row in sub_t.iterrows():
                    f.write(f"| {row['Diet']} | {row['Treatment']} | {row['Animal']} | {row['Value']:.3f} |\n")
                f.write("\n")
                
    with open(os.path.join(artifacts_dir, 'significance_impact.md'), 'w', encoding='utf-8') as f:
        f.write("# Impact of Outlier Removal on Significance\n\n")
        f.write("This table lists ONLY the statistical comparisons where removing the outliers changed the conclusion (i.e., crossing the p=0.05 threshold).\n\n")
        
        f.write("| Parameter | Time | Comparison | Type | P-value (All) | P-value (Cleaned) | Impact |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for _, row in changed.iterrows():
            p_all = f"{row['P_All']:.4f}" if not pd.isna(row['P_All']) else "NaN"
            p_clean = f"{row['P_Clean']:.4f}" if not pd.isna(row['P_Clean']) else "NaN"
            f.write(f"| {row['Parameter']} | {row['Time']} | {row['Comparison']} | {row['Type']} | {p_all} | {p_clean} | **{row['Significance_Impact']}** |\n")
            
        f.write("\n\n*Note: 'Gained Significance' means the result was NOT significant before, but became significant after outliers were removed. 'Lost Significance' means the opposite.*\n")

    print(f"Generated {len(all_outliers)} outliers.")
    print(f"Found {len(changed)} comparisons where significance changed.")
    
if __name__ == '__main__':
    main()
