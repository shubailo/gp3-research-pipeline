# -*- coding: utf-8 -*-
"""
generate_cleaned_uniform_figures.py
-----------------------------------
Újragenerálja az összes folyamatábrát (időgörbét) a KIZÁRÁSOK UTÁNI tiszta adatokból,
szigorúan egységesített és biológiailag optimális skálákkal, hogy azonnal és könnyen
összehasonlíthatóak legyenek mind a diéták (NF vs. CR vs. TR), mind a kezelések (aMSH vs. Leptin) között!

Tartalom:
1. Egyedi ábrák generálása a 'figures/' mappába (Control vs. Treatment, hibasávval, t=0 jelöléssel)
2. Mester 3-paneles összehasonlító ábrák (NF - CR - TR egymás mellett azonos Y-tengelyen!)
3. Összefoglaló PDF riport generálása: 'Ábrák_Tisztított_Egységes.pdf'
4. PowerPoint diasor frissítése: 'Physiology_Presentation_v4_Cleaned.pptx'
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

# Beállítások
BASE_DIR = Path(r"C:\Users\shuba\Desktop\Researcher - Dóri\balasko")
FIG_DIR = BASE_DIR / "figures"
FIG_DIR.mkdir(exist_ok=True)

# Betöltjük az időpont-szintű tiszta adatbázisokat
df_tc_temp = pd.read_csv(BASE_DIR / "timecourses_homerseklet.csv")
df_tc_metab = pd.read_csv(BASE_DIR / "timecourses_metabolizmus.csv")

# Egyesített adatkeret
df_all = pd.concat([df_tc_temp, df_tc_metab], ignore_index=True)

# Sheet bontás: Diet és Treatment
def parse_sheet(sheet_name):
    parts = str(sheet_name).split('_')
    diet = parts[0][:2]  # TR, NF, CR
    treatment = parts[1] # Control, aMSH, Leptin
    return diet, treatment

df_all['Diet'] = df_all['Sheet'].apply(lambda s: parse_sheet(s)[0])
df_all['Treatment'] = df_all['Sheet'].apply(lambda s: parse_sheet(s)[1])

# Paraméternevek tisztítása és egységesítése
param_name_map = {
    'Tc': 'Tc (°C)',
    'dTc': 'ΔTc (°C)',
    'Ts': 'Ts (°C)',
    'dTs': 'ΔTs (°C)',
    'HLI': 'HLI',
    'VO2': 'VO2 (ml/min/kg^0.75)',
    'dVO2': 'ΔVO2 (ml/min/kg^0.75)',
    'RQ': 'RQ',
    'EE': 'EE (kcal/nap/kg^0.75)'
}

df_all['Param_Display'] = df_all['Param'].map(lambda p: param_name_map.get(p, p))

# ==============================================================================
# EGYSÉGES, OPTIMÁLIS SKÁLÁK (GLOBAL Y-AXIS LIMITS)
# ==============================================================================
# Szigorúan azonos határok minden összehasonlításhoz!
UNIFIED_LIMITS = {
    'Tc': (35.8, 38.2),
    'dTc': (-1.2, 1.4),
    'Ts': (22.5, 29.5),
    'dTs': (-1.0, 4.0),
    'HLI': (-0.12, 0.32),
    'VO2': (10.0, 22.0),
    'dVO2': (-4.5, 2.0),
    'RQ': (0.72, 1.10),
    'EE': (75.0, 155.0)
}

# Színpaletta (Publikációs stílus: élénk, de letisztult)
COLORS = {
    'Control': '#3182ce', # Kék
    'aMSH': '#e53e3e',    # Piros
    'Leptin': '#38a169'   # Zöld
}

# Matplotlib globális stílus
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#4a5568'
plt.rcParams['axes.linewidth'] = 1.0

# ==============================================================================
# 1. EGYEDI ÁBRÁK GENERÁLÁSA (Diet x Treatment x Paraméter)
# ==============================================================================
saved_fig_paths = {}

target_plot_params = ['Tc', 'dTc', 'HLI', 'VO2', 'dVO2', 'RQ']
diets = ['NF', 'CR', 'TR']
treatments = ['aMSH', 'Leptin']

print("Generáljuk az egyedi folyamatábrákat...")

for diet in diets:
    for trt in treatments:
        for p in target_plot_params:
            ylim = UNIFIED_LIMITS.get(p)
            disp_name = param_name_map.get(p, p)
            
            fig, ax = plt.subplots(figsize=(6, 4.2), dpi=150)
            
            # Kontroll görbe
            sub_c = df_all[(df_all['Diet'] == diet) & (df_all['Treatment'] == 'Control') & (df_all['Param'] == p)].sort_values('Time')
            if not sub_c.empty:
                n_c = sub_c.iloc[0]['n_after']
                lbl_c = f"Kontroll (n={n_c})"
                ax.plot(sub_c['Time'], sub_c['mean_after'], color=COLORS['Control'], linewidth=2.2, label=lbl_c, marker='o', markersize=4.5)
                ax.fill_between(sub_c['Time'], 
                                sub_c['mean_after'] - sub_c['sem_after'], 
                                sub_c['mean_after'] + sub_c['sem_after'], 
                                color=COLORS['Control'], alpha=0.18)
                                
            # Kezelt görbe
            sub_t = df_all[(df_all['Diet'] == diet) & (df_all['Treatment'] == trt) & (df_all['Param'] == p)].sort_values('Time')
            if not sub_t.empty:
                n_t = sub_t.iloc[0]['n_after']
                lbl_t = f"{trt} (n={n_t})"
                ax.plot(sub_t['Time'], sub_t['mean_after'], color=COLORS[trt], linewidth=2.4, label=lbl_t, marker='s', markersize=4.5)
                ax.fill_between(sub_t['Time'], 
                                sub_t['mean_after'] - sub_t['sem_after'], 
                                sub_t['mean_after'] + sub_t['sem_after'], 
                                color=COLORS[trt], alpha=0.22)
            
            # Segédvonalak
            ax.axvline(x=0, color='#718096', linestyle='--', linewidth=1.2, label='Injekció (t=0)' if diet=='NF' and p=='dTc' else "")
            if p in ['dTc', 'dTs', 'dVO2', 'HLI']:
                ax.axhline(y=0, color='#a0aec0', linestyle=':', linewidth=1.0)
            if p == 'RQ':
                ax.axhline(y=1.0, color='#cbd5e0', linestyle='--', linewidth=0.8) # CH oxidáció
                ax.axhline(y=0.7, color='#cbd5e0', linestyle='--', linewidth=0.8) # Zsír oxidáció
                
            ax.set_xlim(-35, 185)
            if ylim:
                ax.set_ylim(ylim)
                
            ax.set_xlabel("Idő (perc)", fontsize=11, fontweight='bold', labelpad=6)
            ax.set_ylabel(disp_name, fontsize=11, fontweight='bold', labelpad=6)
            ax.set_title(f"{diet} Csoport: {trt} vs. Kontroll", fontsize=12, fontweight='bold', pad=10)
            
            # Legend & rács
            ax.legend(loc='best', frameon=True, framealpha=0.9, facecolor='white', edgecolor='#e2e8f0', fontsize=9.5)
            ax.grid(True, linestyle='-', alpha=0.15, color='#cbd5e0')
            ax.set_axisbelow(True)
            
            plt.tight_layout()
            
            fname = f"{diet}_{trt}_{p}.png"
            fpath = FIG_DIR / fname
            plt.savefig(fpath, dpi=200)
            plt.close(fig)
            saved_fig_paths[f"{diet}_{trt}_{p}"] = fpath

print(f"OK: {len(saved_fig_paths)} egyedi abra sikeresen elmentve!")

# ==============================================================================
# 2. MESTER 3-PANELES ÖSSZEHASONLÍTÓ ÁBRÁK (NF - CR - TR egy ábrán)
# ==============================================================================
print("Generáljuk a 3-paneles mester összehasonlító ábrákat...")
master_figs = []

for trt in ['aMSH', 'Leptin']:
    for p in ['dTc', 'Tc', 'dVO2', 'VO2', 'HLI']:
        ylim = UNIFIED_LIMITS.get(p)
        disp_name = param_name_map.get(p, p)
        
        fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), sharey=True, dpi=200)
        fig.suptitle(f"{trt} hatása a különböző diétás csoportokban: {disp_name} (Egységes skála)", 
                     fontsize=15, fontweight='bold', y=0.98)
        
        diet_titles = {
            'NF': 'Normál táplált (Normal Fed)',
            'CR': 'Kalóriamegszorított (Caloric Restr.)',
            'TR': 'Tréningezett (Trained)'
        }
        
        for idx, diet in enumerate(['NF', 'CR', 'TR']):
            ax = axes[idx]
            
            # Kontroll
            sub_c = df_all[(df_all['Diet'] == diet) & (df_all['Treatment'] == 'Control') & (df_all['Param'] == p)].sort_values('Time')
            if not sub_c.empty:
                n_c = sub_c.iloc[0]['n_after']
                ax.plot(sub_c['Time'], sub_c['mean_after'], color=COLORS['Control'], linewidth=2.2, label=f"Kontroll (n={n_c})", marker='o', markersize=4)
                ax.fill_between(sub_c['Time'], 
                                sub_c['mean_after'] - sub_c['sem_after'], 
                                sub_c['mean_after'] + sub_c['sem_after'], 
                                color=COLORS['Control'], alpha=0.18)
                                
            # Kezelt
            sub_t = df_all[(df_all['Diet'] == diet) & (df_all['Treatment'] == trt) & (df_all['Param'] == p)].sort_values('Time')
            if not sub_t.empty:
                n_t = sub_t.iloc[0]['n_after']
                ax.plot(sub_t['Time'], sub_t['mean_after'], color=COLORS[trt], linewidth=2.4, label=f"{trt} (n={n_t})", marker='s', markersize=4)
                ax.fill_between(sub_t['Time'], 
                                sub_t['mean_after'] - sub_t['sem_after'], 
                                sub_t['mean_after'] + sub_t['sem_after'], 
                                color=COLORS[trt], alpha=0.22)
                                
            ax.axvline(x=0, color='#718096', linestyle='--', linewidth=1.2)
            if p in ['dTc', 'dTs', 'dVO2', 'HLI']:
                ax.axhline(y=0, color='#a0aec0', linestyle=':', linewidth=1.0)
                
            ax.set_xlim(-35, 185)
            if ylim:
                ax.set_ylim(ylim)
                
            ax.set_title(diet_titles[diet], fontsize=12, fontweight='bold', pad=8)
            ax.set_xlabel("Idő (perc)", fontsize=11, fontweight='bold')
            if idx == 0:
                ax.set_ylabel(disp_name, fontsize=12, fontweight='bold')
            ax.grid(True, linestyle='-', alpha=0.15, color='#cbd5e0')
            ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9, fontsize=9.5)
            
        plt.tight_layout()
        master_fname = f"Master_{trt}_{p}.png"
        master_path = FIG_DIR / master_fname
        plt.savefig(master_path, dpi=200)
        plt.close(fig)
        master_figs.append(master_path)

print(f"OK: {len(master_figs)} mester osszehasonlito abra elmentve!")

# ==============================================================================
# 3. ÖSSZEFOGLALÓ PDF RIPORT GENERÁLÁSA
# ==============================================================================
pdf_path = BASE_DIR / "Ábrák_Tisztított_Egységes.pdf"
print(f"Generáljuk a PDF összefoglalót: {pdf_path.name}...")

with PdfPages(pdf_path) as pdf:
    # 1. Oldal: aMSH 3-paneles ábrák
    for master_f in [f for f in master_figs if 'aMSH' in f.name]:
        fig, ax = plt.subplots(figsize=(11, 4), dpi=150)
        img = plt.imread(master_f)
        ax.imshow(img)
        ax.axis('off')
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)
        
    # 2. Oldal: Leptin 3-paneles ábrák
    for master_f in [f for f in master_figs if 'Leptin' in f.name]:
        fig, ax = plt.subplots(figsize=(11, 4), dpi=150)
        img = plt.imread(master_f)
        ax.imshow(img)
        ax.axis('off')
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

print("OK: PDF jelentes elmentve!")

# ==============================================================================
# 4. POWERPOINT PREZENTÁCIÓ GENERÁLÁSA (v4_Cleaned)
# ==============================================================================
pptx_path = BASE_DIR / "Physiology_Presentation_v4_Cleaned.pptx"
print(f"Generáljuk a frissített prezentációt: {pptx_path.name}...")

prs = Presentation()
blank_layout = prs.slide_layouts[6]
title_layout = prs.slide_layouts[0]

# Címdia
slide0 = prs.slides.add_slide(title_layout)
slide0.shapes.title.text = "Metabolikus és Termoregulációs Válaszok\n(Tisztított Adatok & Egységes Skálák)"
slide0.placeholders[1].text = "Normal Fed, Calorie Restricted és Trained Csoportok Elemzése\naMSH és Leptin Centrális Hatására"

def add_diet_slide(prs, diet_code, diet_full_name, trt, key_note):
    slide = prs.slides.add_slide(blank_layout)
    
    # Cím
    tx = slide.shapes.add_textbox(Inches(0.6), Inches(0.2), Inches(12), Inches(0.8))
    tf = tx.text_frame
    p = tf.add_paragraph()
    p.text = f"{diet_full_name} – {trt} Kezelés Hatása (Tisztított Adatok)"
    p.font.size = Pt(24)
    p.font.bold = True
    from pptx.dml.color import RGBColor
    p.font.color.rgb = RGBColor(40, 50, 70)
    
    # Képek beillesztése: Felső sor = Metabolizmus (VO2, dVO2), Alsó sor = Termoreguláció (Tc, dTc, HLI)
    f_vo2 = saved_fig_paths.get(f"{diet_code}_{trt}_VO2")
    f_dvo2 = saved_fig_paths.get(f"{diet_code}_{trt}_dVO2")
    f_tc = saved_fig_paths.get(f"{diet_code}_{trt}_Tc")
    f_dtc = saved_fig_paths.get(f"{diet_code}_{trt}_dTc")
    f_hli = saved_fig_paths.get(f"{diet_code}_{trt}_HLI")
    
    # Felső sor (Metabolizmus: 2 ábra egymás mellett)
    if f_vo2 and f_vo2.exists():
        slide.shapes.add_picture(str(f_vo2), Inches(0.6), Inches(1.1), width=Inches(4.4))
    if f_dvo2 and f_dvo2.exists():
        slide.shapes.add_picture(str(f_dvo2), Inches(5.3), Inches(1.1), width=Inches(4.4))
        
    # Alsó sor (Hőmérséklet: 3 ábra egymás mellett)
    if f_tc and f_tc.exists():
        slide.shapes.add_picture(str(f_tc), Inches(0.6), Inches(4.3), width=Inches(3.0))
    if f_dtc and f_dtc.exists():
        slide.shapes.add_picture(str(f_dtc), Inches(3.8), Inches(4.3), width=Inches(3.0))
    if f_hli and f_hli.exists():
        slide.shapes.add_picture(str(f_hli), Inches(7.0), Inches(4.3), width=Inches(3.0))
        
    slide.notes_slide.notes_text_frame.text = key_note

# 1. aMSH blokk
add_diet_slide(prs, "NF", "Normál táplált állapot (NF)", "aMSH", 
               "Normál táplált állapotban az aMSH mérsékelt VO2 emelkedést és kb. 0.4-0.5 °C maghőmérséklet emelkedést (dTc) vált ki. A HLI enyhén emelkedik a késői fázisban.")
add_diet_slide(prs, "CR", "Kalóriamegszorított állapot (CR)", "aMSH", 
               "CR állapotban a bazális VO2 és Tc alacsonyabb. Az aMSH hatására a láz kialakul, de a HLI és a perifériás hőleadás jelentős ingadozást mutat.")
add_diet_slide(prs, "TR", "Fizikailag tréningezett állapot (TR)", "aMSH", 
               "Tréningezett állatokban az aMSH hatása rendkívül kifejezett: a testhőmérséklet emelkedés stabil, a hibasáv szűk, a metabolikus válasz robusztus.")

# Átvezető dia: Leptin
slide_trans = prs.slides.add_slide(title_layout)
slide_trans.shapes.title.text = "Leptin Centrális Hatásai"
slide_trans.placeholders[1].text = "Ugyanazokon az egységesített skálákon vizsgálva a leptin hatásmechanizmusát"

# 2. Leptin blokk
add_diet_slide(prs, "NF", "Normál táplált állapot (NF)", "Leptin", 
               "A leptin hatása normál táplált állatokban jóval mérsékeltebb, mint az aMSH-é. Az egységes skálán világosan látszik a két peptiderg mechanizmus amplitúdó-különbsége.")
add_diet_slide(prs, "CR", "Kalóriamegszorított állapot (CR)", "Leptin", 
               "A tisztított adatok alapján CR-ben a leptin-indukált dVO2 szórása lecsökkent, a görbe lefutása megbízható és sima.")
add_diet_slide(prs, "TR", "Fizikailag tréningezett állapot (TR)", "Leptin", 
               "Tréningezett állapotban a leptin nem képes olyan drasztikus lázat és VO2 kiugrást produkálni, mint az aMSH, ami igazolja a melanocortin és leptin jelátvitel szétválását.")

# 3. Mester 3-paneles dia
slide_master = prs.slides.add_slide(blank_layout)
tx = slide_master.shapes.add_textbox(Inches(0.6), Inches(0.2), Inches(12), Inches(0.8))
tx.text_frame.text = "Összehasonlító Mester Ábra: aMSH Lázválasz és dVO2 Diéták Szerint"
f_m1 = FIG_DIR / "Master_aMSH_dTc.png"
f_m2 = FIG_DIR / "Master_aMSH_dVO2.png"
if f_m1.exists():
    slide_master.shapes.add_picture(str(f_m1), Inches(0.6), Inches(1.1), width=Inches(8.8))
if f_m2.exists():
    slide_master.shapes.add_picture(str(f_m2), Inches(0.6), Inches(4.3), width=Inches(8.8))

prs.save(pptx_path)
print(f"OK: Prezentacio sikeresen elmentve: {pptx_path.name}")
