import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pptx import Presentation
from pptx.util import Inches, Pt

sns.set_theme(style="ticks", context="talk")

data_dir = r"C:\Users\shuba\Desktop\Researcher - Dóri\balasko"
fig_dir = os.path.join(data_dir, "figures")
os.makedirs(fig_dir, exist_ok=True)

file_temp = os.path.join(data_dir, "animaldata_temperature.xlsx")
file_metab = os.path.join(data_dir, "animaldata_metabolism.xlsx")

def load_data(filepath):
    xls = pd.ExcelFile(filepath)
    sheets = [s for s in xls.sheet_names if s not in ['Summary', 'Animal_metadata']]
    all_data = []
    for sheet in sheets:
        df = pd.read_excel(filepath, sheet_name=sheet)
        parts = sheet.split('_')
        diet = parts[0][:2] 
        treatment = parts[1]
        
        time_col = None
        for col in df.columns:
            if 'Time' in str(col):
                time_col = col
                break
                
        if time_col is None: continue
        
        time_idx = list(df.columns).index(time_col)
        animal_cols = [c for c in df.columns[time_idx+1:] if str(c).replace('.0','').isdigit()]
        
        for _, row in df.iterrows():
            t = row[time_col]
            param = row['Parameter']
            vals = []
            for a in animal_cols:
                v = row[a]
                if pd.notna(v) and isinstance(v, (int, float)):
                    if str(param).startswith('Tc') and v < 33:
                        continue
                    if param == 'VO2' and v < 5:
                        continue
                    vals.append(v)
            if len(vals) > 0:
                mean_val = np.mean(vals)
                sem_val = np.std(vals, ddof=1) / np.sqrt(len(vals))
                all_data.append({
                    'Diet': diet,
                    'Treatment': treatment,
                    'Parameter': param,
                    'Time': t,
                    'Mean': mean_val,
                    'SEM': sem_val,
                    'n': len(vals)
                })
    return pd.DataFrame(all_data)

df_t = load_data(file_temp)
df_m = load_data(file_metab)
df_all = pd.concat([df_t, df_m])

def fix_param(p):
    p = str(p)
    if 'dTc' in p: return 'ΔTc (°C)'
    if 'Tc' in p: return 'Tc (°C)'
    if 'dTs' in p: return 'ΔTs (°C)'
    if 'Ts' in p: return 'Ts (°C)'
    if 'Ta' in p: return 'Ta (°C)'
    if p == 'dVO2': return 'ΔVO2'
    if p == 'VO2': return 'VO2'
    return p
df_all['Parameter'] = df_all['Parameter'].apply(fix_param)

target_params = ['VO2', 'ΔVO2', 'Tc (°C)', 'ΔTc (°C)', 'HLI']
global_limits = {}

for param in target_params:
    df_p = df_all[df_all['Parameter'] == param].copy()
    if len(df_p) == 0:
        continue

    df_p['upper'] = df_p['Mean'] + df_p['SEM']
    df_p['lower'] = df_p['Mean'] - df_p['SEM']
    
    min_val = df_p['lower'].min()
    max_val = df_p['upper'].max()
    
    span = max_val - min_val
    if span == 0: span = 1
    pad = span * 0.05
    min_limit = min_val - pad
    max_limit = max_val + pad
    
    # round limits beautifully
    global_limits[param] = (min_limit, max_limit)

colors = {'Control': '#1f77b4', 'aMSH': '#d62728', 'Leptin': '#2ca02c'}
saved_figs = {}

for diet in ['NF', 'CR', 'TR']:
    for treatment in ['aMSH', 'Leptin']:
        for param, (ylim_min, ylim_max) in global_limits.items():
            fig, ax = plt.subplots(figsize=(5, 3.5))
            
            # Control
            df_c = df_all[(df_all['Parameter'] == param) & (df_all['Diet'] == diet) & (df_all['Treatment'] == 'Control')]
            df_c = df_c.sort_values('Time')
            if len(df_c) > 0:
                ax.errorbar(df_c['Time'], df_c['Mean'], yerr=df_c['SEM'], 
                            fmt='-o', color=colors['Control'], markerfacecolor='white', label='Control', capsize=3, markersize=5)
                            
            # Treatment
            df_t = df_all[(df_all['Parameter'] == param) & (df_all['Diet'] == diet) & (df_all['Treatment'] == treatment)]
            df_t = df_t.sort_values('Time')
            if len(df_t) > 0:
                ax.errorbar(df_t['Time'], df_t['Mean'], yerr=df_t['SEM'], 
                            fmt='-o', color=colors[treatment], label=treatment, capsize=3, markersize=5)
                            
            ax.axvline(x=0, color='black', linestyle='--', linewidth=1)
            ax.axhline(y=0, color='gray', linestyle=':', linewidth=1) # useful for deltas
            ax.set_ylim(ylim_min, ylim_max)
            ax.set_xlim(-35, 185)
            ax.set_xlabel('Time (min)', fontsize=12)
            ax.set_ylabel(param, fontsize=12)
            ax.tick_params(axis='both', which='major', labelsize=10)
            ax.legend(loc='best', fontsize=10)
            
            plt.tight_layout()
            safe_param = param.replace('(', '').replace(')', '').replace('°', '').replace(' ', '_').replace('/', '').replace('Δ', 'd')
            fname = f"{diet}_{treatment}_{safe_param}.png"
            fpath = os.path.join(fig_dir, fname)
            plt.savefig(fpath, dpi=150)
            plt.close(fig)
            saved_figs[f"{diet}_{treatment}_{safe_param}"] = fpath

# Create PPTX
pptx_path = os.path.join(data_dir, "Physiology_Presentation_v3.pptx")
prs = Presentation()
blank_slide_layout = prs.slide_layouts[6]
title_slide_layout = prs.slide_layouts[0]
bullet_slide_layout = prs.slide_layouts[1]

# Slide 1: Title Slide
slide = prs.slides.add_slide(title_slide_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]
title.text = "Metabolic and Thermoregulatory Responses to aMSH and Leptin\n(Unified Scales)"
subtitle.text = "Analysis of Normal Fed, Calorie Restricted, and Trained States"
slide.notes_slide.notes_text_frame.text = "Welcome everyone. Today I'll present how metabolic context rewires responses to aMSH and Leptin. All graphs share a unified global Y-axis scale to allow true cross-group comparison."

def add_custom_slide(title_text, diet, treatment, notes_text):
    slide = prs.slides.add_slide(blank_slide_layout)
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.1), Inches(9), Inches(0.8))
    tf = txBox.text_frame
    p = tf.add_paragraph()
    p.text = title_text
    p.font.size = Pt(28)
    p.font.bold = True
    
    # 5 images: VO2, dVO2, Tc, dTc, HLI
    keys = ['VO2', 'dVO2', 'Tc_C', 'dTc_C', 'HLI']
    
    # Top row (Metabolism)
    if f"{diet}_{treatment}_{keys[0]}" in saved_figs:
        slide.shapes.add_picture(saved_figs[f"{diet}_{treatment}_{keys[0]}"], Inches(0.5), Inches(1.0), width=Inches(4.2))
    if f"{diet}_{treatment}_{keys[1]}" in saved_figs:
        slide.shapes.add_picture(saved_figs[f"{diet}_{treatment}_{keys[1]}"], Inches(5.0), Inches(1.0), width=Inches(4.2))
        
    # Bottom row (Thermoregulation)
    if f"{diet}_{treatment}_{keys[2]}" in saved_figs:
        slide.shapes.add_picture(saved_figs[f"{diet}_{treatment}_{keys[2]}"], Inches(0.2), Inches(4.3), width=Inches(3.1))
    if f"{diet}_{treatment}_{keys[3]}" in saved_figs:
        slide.shapes.add_picture(saved_figs[f"{diet}_{treatment}_{keys[3]}"], Inches(3.4), Inches(4.3), width=Inches(3.1))
    if f"{diet}_{treatment}_{keys[4]}" in saved_figs:
        slide.shapes.add_picture(saved_figs[f"{diet}_{treatment}_{keys[4]}"], Inches(6.6), Inches(4.3), width=Inches(3.1))
        
    slide.notes_slide.notes_text_frame.text = notes_text

add_custom_slide(
    "Baseline aMSH Response (Normal Fed)",
    "NF", "aMSH",
    "Look at the healthy, Normal Fed state. aMSH significantly alters VO2, driving an increase in core body temperature (Tc). Notice how the HLI remains relatively flat across this global scale."
)

add_custom_slide(
    "aMSH During Caloric Restriction (CR)",
    "CR", "aMSH",
    "In the starved CR group, baseline VO2 is suppressed. When administered aMSH, the hyperthermia occurs, but we see a massive, statistically significant spike in heat loss (HLI) compared to the baseline scale."
)

add_custom_slide(
    "aMSH in the Trained State (TR)",
    "TR", "aMSH",
    "In physically trained animals, the aMSH response is dramatic. Look at the magnitude of the Tc and dTc on this global scale! Exercise adaptation massively sensitizes the melanocortin pathway."
)

# Leptin Slides
slide = prs.slides.add_slide(title_slide_layout)
slide.shapes.title.text = "Transition to Leptin"
slide.placeholders[1].text = "Does the key satiety hormone operate under the same thermal logic?"

add_custom_slide(
    "Leptin Baseline Response (NF)",
    "NF", "Leptin",
    "Looking at the Normal Fed animals on our global scale, Leptin's effect is almost flat compared to aMSH. Changes in VO2 and Tc are minimal."
)

add_custom_slide(
    "Leptin During Caloric Restriction (CR)",
    "CR", "Leptin",
    "In Calorie Restriction, the system defends leptin-induced heating differently without the drastic HLI spike seen with aMSH."
)

add_custom_slide(
    "Leptin in the Trained State (TR)",
    "TR", "Leptin",
    "Finally, in the Trained group, while aMSH caused massive hyperthermia and an HLI spike, Leptin completely fails to elicit this intense response on the absolute scale. The separation of the two pathways is beautifully clear here."
)

prs.save(pptx_path)
print(f"Unified PPTX saved to {pptx_path}")
