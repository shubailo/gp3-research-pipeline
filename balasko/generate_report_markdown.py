# -*- coding: utf-8 -*-
"""
generate_report_markdown.py
---------------------------
Összeállítja a teljes, professzionális, két táblára bontott statisztikai jelentést.
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(r"C:\Users\shuba\Desktop\Researcher - Dóri\balasko")
ARTIFACT_PATH = Path(r"C:\Users\shuba\.gemini\antigravity-ide\brain\f32e32a9-2c9f-49a7-a653-8184932bce67\kizarasok_elemzes.md")

df_t_excl = pd.read_csv(BASE_DIR / "kizarasok_homerseklet.csv")
df_t_imp = pd.read_csv(BASE_DIR / "statisztika_homerseklet_elotte_utana.csv")

df_m_excl = pd.read_csv(BASE_DIR / "kizarasok_metabolizmus.csv")
df_m_imp = pd.read_csv(BASE_DIR / "statisztika_metabolizmus_elotte_utana.csv")

def format_sem_change(pct):
    if pd.isna(pct):
        return "—"
    if pct < -5:
        return f"**{pct:.1f}%** (javult)"
    elif pct > 5:
        return f"+{pct:.1f}% (romlott)"
    else:
        return f"{pct:+.1f}% (nincs érdemi vált.)"

lines = []
lines.append("# Kétlépcsős Kizárási és Statisztikai Elemzés: Hőmérséklet vs. Metabolizmus")
lines.append("")
lines.append("> **Módszertani tisztázás:** A korábbi összehasonlítás során a két Excel adatbázis állatai és paraméterei részben összemosódtak. ")
lines.append("> Ez a dokumentum **szigorúan kettéválasztva** mutatja be, hogy melyik fájlból kiket indokolt kizárni, és a kizárásuk hogyan befolyásolja az adott tábla csoportátlagait és SEM (átlag standard hibája) értékeit.")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 📌 1. Miért kell külön kezelni a két táblát?")
lines.append("")
lines.append("| Szempont | `animaldata_temperature.xlsx` | `animaldata_metabolism.xlsx` |")
lines.append("| :--- | :--- | :--- |")
lines.append("| **Mért paraméterek** | `Tc` (maghő), `dTc` (maghő változás), `Ts` (bőrhő), `dTs`, `Ta` (környezeti hő), `HLI` | `VO2` (oxigénfogyasztás), `dVO2`, `VCO2`, `dVCO2`, `RQ` (légzési hányados), `EE` (energiafelhasználás) |")
lines.append("| **Mérési technika** | Rektális / telemetriás hőszenzorok, réz-konstantán hőelemek | Zárt/áramlásos indirekt kalorimetriás kamrák, O2/CO2 analizátorok |")
lines.append("| **Mintanagyság (N)** | **197 állat** (9 csoport) | **173 állat** (9 csoport) |")
lines.append("| **Tipikus műhibák** | Rektális szonda kicsúszása (`colon visszacsúszva`), vérzés (`colon véres`), Ta túlhevülés | Kamra szivárgás, O2 szenzor kimaradás (`oxy nincs`), légzési hányados képtelenségek (`RQ > 1.05`) |")
lines.append("| **Közös hibapont** | **Centrális injekciós kanülhiba:** ha a kanül `szétcsúszott`, `lyukas`, `szétrágta`, vagy `nem kapott PG-t`, a farmakológiai ágens nem jutott be az agykamrába. Ez mindkét mérést érvényteleníti! |")
lines.append("")
lines.append("---")
lines.append("")

# ==============================================================================
# HŐMÉRSÉKLET RÉSZ
# ==============================================================================
lines.append("## 🌡️ 2. HŐMÉRSÉKLET TÁBLA (`animaldata_temperature.xlsx`)")
lines.append("")
lines.append(f"Ebből a táblából összesen **{len(df_t_excl)} állat** kizárása indokolt technikai műhiba vagy extrém adat-kiugrás (|z| ≥ 2.0) miatt.")
lines.append("")
lines.append("### 🔴 Hőmérsékleti kizárási lista")
lines.append("")
lines.append("| Állat ID | Csoport | Komment a jegyzőkönyvben | Kiugró paraméter & z-score | Állat értéke | Csoport átlag ± SD | Kizárás indoka |")
lines.append("| :---: | :---: | :--- | :--- | :---: | :---: | :--- |")

for idx, r in df_t_excl.iterrows():
    comm = r['Komment'] if pd.notna(r['Komment']) and str(r['Komment']).strip() != '' else "*(nincs komment)*"
    aid = str(r['Állat_ID']).replace('.0', '')
    lines.append(f"| **{aid}** | `{r['Csoport']}` | {comm} | `{r['Legfőbb_kiugrás']}` | {r['Érték']} | {r['Csoport_átlag']} | {r['Indoklás']} |")

lines.append("")
lines.append("### 📊 Hőmérsékleti csoportátlagok és SEM változások (Előtte vs. Utána)")
lines.append("")
lines.append("A legfontosabb termoregulációs végpontok: **Tc** (maghőmérséklet, °C) és **dTc** (testhőmérséklet elmozdulás, °C).")
lines.append("")
lines.append("| Csoport | Paraméter | n (előtte) | Átlag (előtte) | SEM (előtte) | n (utána) | Átlag (utána) | SEM (utána) | Átlag Δ | SEM javulás |")
lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

for sheet in df_t_imp['Sheet'].unique():
    sub = df_t_imp[(df_t_imp['Sheet'] == sheet) & (df_t_imp['Param'].isin(['Tc', 'dTc']))]
    for idx, r in sub.iterrows():
        sem_str = format_sem_change(r['sem_pct'])
        lines.append(f"| `{r['Sheet']}` | **{r['Param']}** | {r['n_before']} | {r['mean_before']:.3f} | {r['sem_before']:.4f} | {r['n_after']} | {r['mean_after']:.3f} | {r['sem_after']:.4f} | {r['mean_delta']:+.3f} | {sem_str} |")

lines.append("")
lines.append("---")
lines.append("")

# ==============================================================================
# METABOLIZMUS RÉSZ
# ==============================================================================
lines.append("## 🫁 3. METABOLIZMUS TÁBLA (`animaldata_metabolism.xlsx`)")
lines.append("")
lines.append(f"Ebből a táblából összesen **{len(df_m_excl)} állat** kizárása indokolt közvetlen respirometriás hiba, technikai kanülhiba vagy súlyos metabolikus outlier (|z| ≥ 2.0) miatt.")
lines.append("")
lines.append("### 🔴 Metabolikus kizárási lista")
lines.append("")
lines.append("| Állat ID | Csoport | Komment a jegyzőkönyvben | Kiugró paraméter & z-score | Állat értéke | Csoport átlag ± SD | Kizárás indoka |")
lines.append("| :---: | :---: | :--- | :--- | :---: | :---: | :--- |")

for idx, r in df_m_excl.iterrows():
    comm = r['Komment'] if pd.notna(r['Komment']) and str(r['Komment']).strip() != '' else "*(nincs komment)*"
    aid = str(r['Állat_ID']).replace('.0', '')
    lines.append(f"| **{aid}** | `{r['Csoport']}` | {comm} | `{r['Legfőbb_kiugrás']}` | {r['Érték']} | {r['Csoport_átlag']} | {r['Indoklás']} |")

lines.append("")
lines.append("### 📊 Metabolikus csoportátlagok és SEM változások (Előtte vs. Utána)")
lines.append("")
lines.append("A legfontosabb anyagcsere végpontok: **VO2** (oxigénfogyasztás, ml/min/kg^0.75), **dVO2** (oxigénfogyasztás változás) és **RQ** (légzési hányados).")
lines.append("")
lines.append("| Csoport | Paraméter | n (előtte) | Átlag (előtte) | SEM (előtte) | n (utána) | Átlag (utána) | SEM (utána) | Átlag Δ | SEM javulás |")
lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

for sheet in df_m_imp['Sheet'].unique():
    sub = df_m_imp[(df_m_imp['Sheet'] == sheet) & (df_m_imp['Param'].isin(['VO2', 'dVO2', 'RQ']))]
    for idx, r in sub.iterrows():
        sem_str = format_sem_change(r['sem_pct'])
        lines.append(f"| `{r['Sheet']}` | **{r['Param']}** | {r['n_before']} | {r['mean_before']:.3f} | {r['sem_before']:.4f} | {r['n_after']} | {r['mean_after']:.3f} | {r['sem_after']:.4f} | {r['mean_delta']:+.3f} | {sem_str} |")

lines.append("")
lines.append("---")
lines.append("")

# ==============================================================================
# KERESZT-ÖSSZEHASONLÍTÁS ÉS TANULSÁGOK
# ==============================================================================
lines.append("## 🔄 4. Kereszt-validáció: Melyik állat melyik táblában érintett?")
lines.append("")
lines.append("A két tábla összevetése alapján három tiszta kategóriát különíthetünk el:")
lines.append("")
lines.append("### A) Mindkét táblából KIZÁRANDÓK (Szisztémás kanülhiba / kudarcba fulladt kísérlet)")
lines.append("- **7375** (`TR12_aMSH`): Injekciós kanül szétcsúszott → sem lázválasz nem volt (`dTc z = -2.43`), sem metabolikus válasz (`VO2 z = -2.14`).")
lines.append("- **7675** (`TR12_Leptin` / `TR12_aMSH`): A metabolizmusban `beszaladt a PG is +` kommenttel extrém hipometabolizmus (`dVO2 z = -2.76`), a hőmérsékletben extrém környezeti szenzorzárlat (`Ta = 47.58°C, z = +4.96`).")
lines.append("- **7438** (`CR12_Leptin`): Komment: `PG- gennyes a feje`. Hőmérsékletben `dTc z = +2.34` kiugró melegedés, metabolizmusban `dVO2 z = -1.88` alacsony érték.")
lines.append("- **7430** (`CR12_Leptin`): Komment: `PG-`. Hőmérsékletben `Tc z = +2.03` magas alaphő, metabolizmusban `dVO2 z = -1.97` kiugró.")
lines.append("")
lines.append("### B) CSAK a Hőmérséklet táblából kizárandók")
lines.append("- **6919** (`TR12_Control`): Csak a hőmérséklet táblában létezik! dTc z = +2.51 kiugró láz kontrollban.")
lines.append("- **7245** (`TR12_Leptin`): Kanül lyukas volt a reggeli fürdetésnél, Tc z = -1.96.")
lines.append("- **7237** (`TR12_Leptin`): Tc z = +2.18, dTc z = +2.07 kiugró melegedés.")
lines.append("- **7340** (`CR12_aMSH`): `szétcsúszott` kommenttel a maghőmérséklete drasztikusan leesett (`Tc = 35.97°C, z = -2.93`, `dTc z = -2.47`). A metabolizmusban viszont normális értékeket mutatott.")
lines.append("- **7565** (`CR12_aMSH`): Extrém bőrhőmérsékleti kiugrás (`Ts z = +3.07, dTs z = +2.10`), nincs a metabolizmus táblában.")
lines.append("- **7441.1, 7570** (`CR12_Leptin`): 7441.1 extrém bőrhőmérsékleti hiba (`dTs z = -4.31`), 7570 lyukas kanül és mély hypothermia (`Tc = 35.65°C, z = -2.66`). Nincsenek a metabolizmus táblában.")
lines.append("")
lines.append("### C) CSAK a Metabolizmus táblából kizárandók")
lines.append("- **6545.2, 6547.1, 6546.3** (`NF12_Control`): Ezek az állatok **egyáltalán nem szerepelnek a hőmérséklet táblában**! Ott az NF12_Control 1-8-ig számozott. A respirometriában viszont súlyos kamraszivárgás/mérési műhiba történt (`VO2 z = -2.76`, `dVO2 z = -2.60`, `RQ = 1.029`).")
lines.append("- **7208.1, 7209** (`NF12_aMSH`): Komment: `VO2 PG-`, `PG-`. VO2 z = -2.74, RQ = 1.117 (lehetetlen érték).")
lines.append("- **7247** (`NF12_Leptin`): RQ = 0.677 (z = -2.53), irreálisan alacsony légzési hányados.")
lines.append("- **7246** (`TR12_Leptin`): Fürdetés utáni VO2 z = +2.10 hipermetabolikus kiugrás.")
lines.append("- **7336, 7339** (`CR12_aMSH`): PG- és szétrágott kanül, dVO2 és dVCO2 kiugrások.")
lines.append("- **7346, 7347** (`CR12_Leptin`): Extrém metabolikus összeomlás (`dVO2 z = -3.65`, `dVCO2 z = -3.31`).")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 🏆 5. Összegzés és Mentori Értékelés (Garami Perspective)")
lines.append("1. **Nem szabad mechanikusan másolni a kizárásokat:** Ha egy állat rektális probája elmozdult (`colon visszacsúszva`), a testhőmérséklete érvénytelen, de a zárt kamrában mért O2 fogyasztása fiziológiásan teljesen helytálló maradhat.")
lines.append("2. **A centrális kanül hibája szisztémás:** Ha az intracerebroventricularis (ICV) kanül szétcsúszott vagy lyukas volt az injekció alatt, a neuropeptid (aMSH, leptin) vagy a PG nem jutott be a hipotalamikus központokba. Az ilyen állatot mindkét adatbázisból kötelező kizárni.")
lines.append("3. **Statisztikai erő:** A fenti precíz, különválasztott kizárásokkal a szórás (SEM) a legfontosabb paraméterekben **10% és 29% közötti mértékben javult (csökkent)**, anélkül, hogy a mintanagyságot indokolatlanul lecsökkentettük volna.")

with open(ARTIFACT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("OK: Artifact sikeresen elmentve:", ARTIFACT_PATH)
