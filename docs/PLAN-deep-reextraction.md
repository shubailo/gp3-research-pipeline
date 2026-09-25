# PLAN: Mélyextrakció – 41 beválogatott tanulmány teljes adatkinyerése

## 1. Probléma összefoglaló

Az eddigi adatkinyerés **felületes és hiányos** volt:

| Probléma | Részletek |
|----------|-----------|
| **PDF→text konverzió** | `PyPDF2` csak nyers szöveget nyer ki → **táblázatok széttörnek**, ábrák teljesen elvesznek |
| **Hiányzó dózisadatok** | `Dose_mg_kg_Agent_1`: csak 5/44 tanulmányban kitöltve, holott szinte minden RCT közli a dózisokat |
| **Risk of Bias: 0/0** | A `9_RISK_OF_BIAS` sheet teljesen üres – meta-analízis nem végezhető el nélküle |
| **Secondary Outcomes: 0/0** | A `7_OUTCOMES_SECONDARY` sheet teljesen üres |
| **Nincs N/A jelölés** | Ha egy adat nem volt a cikkben, egyszerűen üresen hagytuk ahelyett, hogy `N/A` vagy `CHECK` jelölés lenne |
| **Üres oszlopok** | ~80 oszlop a 130-ból teljesen üres |

### Jelenlegi kitöltöttségi állapot

```
Sheet 01 (Study ID):        ~90% kitöltött (de DOI, Language hiányzik)
Sheet 02 (Characteristics): ~20% kitöltött (Randomization, Blinding, Funding üres)
Sheet 03 (Population):      ~40% kitöltött (GA_SD, Male%, Inclusion/Exclusion criteria üres)
Sheet 04 (Intervention):    ~30% kitöltött (Dose, Frequency, Duration részleges)
Sheet 05 (Comparator):      ~30% kitöltött (Details, Co-interventions üres)
Sheet 06 (Primary Outcomes): ~50% kitöltött (Effect measure, CI, P-value üres)
Sheet 07 (Secondary):        0% – TELJESEN ÜRES
Sheet 08 (Subgroup):         2 sor van összesen
Sheet 09 (Risk of Bias):     0% – TELJESEN ÜRES
```

---

## 2. Célkitűzés

**Minden beválogatott tanulmányhoz (41 db) teljes adatkinyerés**:
- Minden oszlopban legyen **érték**, **N/A** (nem közölt), vagy **CHECK** (ellenőrzést igényel)
- Risk of Bias értékelés minden tanulmányra
- Pontos dózisok, gyakoriságok, időtartamok
- Primary és Secondary outcome adatok számszerű értékekkel (events/N, OR/RR, 95% CI, p-érték)

---

## 3. Módszertani változások

### 3.1 PDF feldolgozás javítása

| Régi módszer | Új módszer |
|---|---|
| `PyPDF2` text extraction | **`pdfplumber`** (táblázatok megtartása) + **`PyMuPDF/fitz`** (ábrák kinyerése) |
| Szöveges .txt fájl kimenet | Strukturált .txt **+ ábra képfájlok** (PNG) tanulmányonként külön mappában |
| Ábrák elvesznek | Ábrák mentése → vizuális ellenőrzés lehetséges |

#### Új munkafolyamat:
```
PDF → pdfplumber (szöveg + táblák) → study_text.md
PDF → PyMuPDF (ábrák) → study_figures/fig_p1.png, fig_p2.png...
study_text.md + study_figures/ → AI olvasás → Excel sorok feltöltése
```

### 3.2 Értékjelölési rendszer

| Jelölés | Jelentés |
|---|---|
| **(tényleges érték)** | Az adat megtalálható a cikkben |
| **N/A** | Az adat **nem szerepel** a cikkben (ellenőrizve) |
| **CHECK** | Az adat **valószínűleg létezik** de nem volt egyértelmű → kézi ellenőrzés szükséges |
| **NR** | Not Reported – a cikk kifejezetten nem közölte |
| **CALC** | Számolt érték (pl. events/N-ből kiszámolt %) |

### 3.3 Tanulmányonkénti feldolgozási protokoll

Minden tanulmányhoz az alábbi lépések:

1. **PDF feldolgozás** (pdfplumber + fitz)
2. **Szöveg olvasása** – minden szekció átvizsgálása (Abstract, Methods, Results, Tables, Figures)
3. **Sheet 01-05 kitöltése/frissítése** – minden üres cellát N/A-val vagy tényleges adattal tölt
4. **Sheet 06 (Primary Outcomes) kitöltése** – számszerű adatok (events, N, effect size, CI, p)
5. **Sheet 07 (Secondary Outcomes) kitöltése** – halálozás, NEC, hospitalizáció, stb.
6. **Sheet 09 (Risk of Bias) kitöltése** – RoB 2 (RCT-khez) vagy ROBINS-I (nem-RCT-khez)
7. **Sheet 08 (Subgroup) kitöltése** – ha releváns alcsoportelemzés van

---

## 4. Oszloplista – mi kell kitölteni

### Sheet 02: Study_characteristics (most hiányzó mezők)
- `Randomization_Method` → pl. "computer-generated", "coin flip", "block randomization"
- `Allocation_Concealment` → "sealed envelopes", "central", "none described"
- `Blinding_Participants` / `Blinding_Assessors` / `Blinding_Outcome_Assessment`
- `Study_Duration_Months`
- `Funding_Source` / `Commercial_Funding`
- `Trial_Registration` / `Registration_ID`
- `Ethics_Approval` / `Informed_Consent`

### Sheet 03: Population (most hiányzó mezők)
- `GA_SD` → szórás a gesztációs korhoz
- `Birth_Weight_SD`
- `Male_Percent` / `Female_Percent`
- `Inclusion_Criteria_Summary` / `Exclusion_Criteria_Summary`
- `Baseline_Comparability` → "Yes - balanced" / "No - imbalance in X"

### Sheet 04: Intervention (KRITIKUS hiányok)
- `Dose_mg_kg_Agent_1` / `_Agent_2` / `_Agent_3` → pl. "25 mg/kg", "4 mg/kg"
- `Frequency_Agent_1` / `_Agent_2` → pl. "q12h", "q8h"
- `Route_Administration` → "IV", "IM", "PO"
- `Duration_Planned_Days` / `Duration_Median_Days`
- `De_escalation_Protocol`

### Sheet 06: Primary Outcomes (számszerű adatok)
- `Effect_Measure_Type` → "RR", "OR", "RD", "HR"
- `Effect_Estimate` → tényleges szám
- `CI_95_Lower` / `CI_95_Upper`
- `P_Value`
- `Analysis_Population` → "ITT", "per-protocol"

### Sheet 09: Risk of Bias (TELJESEN ÜRES – kitöltendő)
RCT-khez (RoB 2 tool):
- `RoB2_D1_Bias_Process` → Low / Some concerns / High
- `RoB2_D2_Deviations` → Low / Some concerns / High
- `RoB2_D3_Missing` → Low / Some concerns / High
- `RoB2_D4_Measurement` → Low / Some concerns / High
- `RoB2_D5_Reporting` → Low / Some concerns / High
- `RoB2_Overall` → Low / Some concerns / High

---

## 5. Végrehajtási terv

### Fázis 1: Technikai előkészítés
- [ ] `pdfplumber` és `PyMuPDF` telepítése
- [ ] Új `deep_extract_pdf.py` script írása (szöveg + táblák + ábrák)
- [ ] Pilot futtatás 1 tanulmányra (pl. Metsvaht 2010 – jól strukturált RCT)

### Fázis 2: Mélyextrakció – 41 tanulmány feldolgozása
- [ ] Tanulmányonként: PDF újrafeldolgozás → teljes adatkinyerés → Excel frissítés
- [ ] 5-ös adagokban, mint eddig, de most **minden oszlopot kitöltünk**
- [ ] Minden adag után összefoglaló a felhasználónak

### Fázis 3: Risk of Bias értékelés
- [ ] RoB 2 értékelés minden RCT-re (kb. 30 tanulmány)
- [ ] ROBINS-I értékelés quasi-RCT-kre és kohorsz tanulmányokra

### Fázis 4: Minőségellenőrzés
- [ ] Véletlenszerű 5 tanulmány manuális ellenőrzése (user által)
- [ ] "CHECK" jelölésű cellák átvizsgálása
- [ ] Összesített kitöltöttségi statisztika futtatása

---

## 6. Becslések

| Fázis | Becsült idő | Output |
|---|---|---|
| Fázis 1 (tech prep) | ~15 perc | Script + pilot |
| Fázis 2 (41 tanulmány) | ~3-4 óra | Teljesen kitöltött Excel |
| Fázis 3 (RoB) | ~1 óra | RoB sheet kitöltve |
| Fázis 4 (QC) | ~30 perc | Validált dataset |

---

## 7. Szókratészi kérdések (döntéshozatalhoz)

> [!IMPORTANT]
> Az alábbi kérdésekre válaszolj, mielőtt elkezdjük a végrehajtást:

1. **Outcome prioritás**: Melyik a legfontosabb primary outcome ehhez a meta-analízishez? (pl. mortalitás, treatment failure, szepszis arány, antibiotikum-rezisztencia)?

2. **A kizárt tanulmányokat is újra kell vizsgálni?** Eddig 10 tanulmányt zártunk ki – érdemes ezeket is újra ellenőrizni az új módszerrel, vagy maradjunk a 41 beválogatottnál?

3. **Mennyi manuális ellenőrzést szeretnél végezni?** A Fázis 4-ben javasolt 5 tanulmány elég, vagy többet szeretnél kézzel átnézni?
