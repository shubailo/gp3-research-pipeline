import pandas as pd
import numpy as np
import scipy.stats as stats
import warnings
warnings.filterwarnings('ignore')

file_path = r'C:\Users\shuba\Desktop\Researcher - Dóri\animaldata_temperature.xlsx'
xls = pd.ExcelFile(file_path)

sheets = ['TR12_Control', 'TR12_aMSH', 'TR12_Leptin', 'NF12_Control', 'NF12_aMSH', 'NF12_Leptin', 'CR12_Control', 'CR12_aMSH', 'CR12_Leptin']

all_data = []

for sheet in sheets:
    df = pd.read_excel(file_path, sheet_name=sheet)
    
    baseline_df = df[df['Time (min)'] <= 0]
    response_df = df[df['Time (min)'] > 0]
    
    animal_cols = [c for c in df.columns if str(c).isdigit()]
    
    for animal in animal_cols:
        baseline_tc = baseline_df[animal].mean()
        
        # calculate max change from baseline or average change
        mean_response = response_df[animal].mean() - baseline_tc
        
        # calculate the AUC using trapezoidal rule for the change from baseline
        # we need to subtract baseline from each timepoint
        temp_diff = df[df['Time (min)'] > 0][animal].values - baseline_tc
        times = df[df['Time (min)'] > 0]['Time (min)'].values
        
        if len(times) > 0:
            auc = np.trapezoid(temp_diff, times)
        else:
            auc = np.nan
        
        parts = sheet.split('_')
        condition = parts[0][:2] # TR, NF, CR
        treatment = parts[1] # Control, aMSH, Leptin
        
        all_data.append({
            'Animal': animal,
            'Condition': condition,
            'Treatment': treatment,
            'Baseline_Tc': baseline_tc,
            'Mean_Delta_Tc': mean_response,
            'AUC': auc
        })

df_all = pd.DataFrame(all_data)
print('--- OVERALL STATS ---')
print(df_all.groupby(['Condition', 'Treatment']).agg({
    'Baseline_Tc': ['mean', 'sem', 'count'],
    'AUC': ['mean', 'sem']
}))

print('\n--- ANOVA within Conditions (AUC) ---')
for cond in ['NF', 'CR', 'TR']:
    print(f'Condition: {cond}')
    c_data = df_all[df_all['Condition'] == cond]
    ctrl = c_data[c_data['Treatment'] == 'Control']['AUC'].dropna()
    amsh = c_data[c_data['Treatment'] == 'aMSH']['AUC'].dropna()
    lept = c_data[c_data['Treatment'] == 'Leptin']['AUC'].dropna()
    
    f_val, p_val = stats.f_oneway(ctrl, amsh, lept)
    print(f'  ANOVA: F={f_val:.2f}, p={p_val:.4f}')
    
    # post hoc t-tests vs control
    t, p_amsh = stats.ttest_ind(ctrl, amsh)
    t, p_lept = stats.ttest_ind(ctrl, lept)
    print(f'  Control vs aMSH: p={p_amsh:.4f}')
    print(f'  Control vs Leptin: p={p_lept:.4f}')

print('\n--- BASELINE ANOVA between Conditions ---')
ctrl_data = df_all[df_all['Treatment'] == 'Control']
nf_b = ctrl_data[ctrl_data['Condition'] == 'NF']['Baseline_Tc'].dropna()
cr_b = ctrl_data[ctrl_data['Condition'] == 'CR']['Baseline_Tc'].dropna()
tr_b = ctrl_data[ctrl_data['Condition'] == 'TR']['Baseline_Tc'].dropna()
f_val, p_val = stats.f_oneway(nf_b, cr_b, tr_b)
print(f'  ANOVA on Baseline Tc: F={f_val:.2f}, p={p_val:.4f}')
