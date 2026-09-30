# PROJECTS_AND_EXTRACTION_LINT_PLAN.md — Rendszerarchitektúra Terv

> **Státusz:** Architektúra és Rendszerterv (Kódolás nélküli tervezési specifikáció)  
> **Szabvány:** GP3 Medical Research Pipeline · CTM BoostR Standard (`Data_extraction_template_v9.xlsx`) · Cochrane Handbook v6.5  
> **Dátum:** 2026-09-30  
> **Fájl elérési út:** `PROJECTS_AND_EXTRACTION_LINT_PLAN.md`  
> **Kanonikus szabályzatok:** `AGENTS.md` §3.4, §5.10 · `GEMINI.md` Rule 10, Rule 11 (Adat-integritási és forrástisztasági mandátum)

---

# RÉSZ A: `projects/` Gyűjtőmappa Bevezetése

Jelenleg a repozitóriumban a projektek adatai széttagoltan, több gyökérszintű mappában helyezkednek el:
- A `meta_hyperglycaemia` adatai a gyökérszintű `meta_hyperglycaemia/` mappában és a `data/wiki/meta_hyperglycaemia/` alatt találhatók.
- A `neonatal_antibiotics` adatai szét vannak szórva a `data/pdfs/neonatal_antibiotics/`, `results/neonatal_antibiotics/`, `data/wiki/neonatal_antibiotics/` és a gyökérszintű `data/Data_extraction_neonatal_antibiotics_v9.xlsx` fájl között.
- A `balasko` jelenleg csak a `.gitignore`-ban létezik könyvtárként, a fájlrendszerben még nincs inicializálva.

A cél egy egységes, skálázható **`projects/`** gyűjtőmappa kialakítása, amely megszünteti a gyökérszintű mappák szaporodását, miközben tiszteletben tartja a GP3 tudásbázis (`data/wiki/`) és a futtatási eredmények határait.

---

## A.1 Célstruktúra és Mappahierarchia Tervezése

Két lehetséges integrációs modell mutatkozik:

### Modell 1: Teljesen Egységbe Zárt Projektek (Self-Contained Project Folders)
Minden projekt egyetlen mappába tömöríti a saját PDF-jeit, Excel kivonatait, futtatási eredményeit és wiki-dossziéit:
```
projects/
├── meta_hyperglycaemia/
│   ├── data/                           # Keresési CSV-k, Excel extrakció (Data_extraction_template_v9_HIE.xlsx)
│   ├── pdfs/                           # Kiadói PDF-ek (helyi letöltések)
│   ├── results/                        # R-metafor kimenetek, forest plotok, táblázatok
│   ├── wiki/                           # studies/*.md dossziék, plausibility_ranges.json, _resolutions/
│   ├── PROTOCOL.md                     # Jóváhagyott protokoll
│   └── PROTOCOL_AMENDMENTS.md          # Helyi módosítási napló
│
├── neonatal_antibiotics/
│   ├── data/                           # Data_extraction_neonatal_antibiotics_v9.xlsx, keresési listák
│   ├── pdfs/                           # ~130 letöltött cikk PDF
│   ├── results/                        # forest plotok, subgroup képek, táblázatok
│   └── wiki/                           # 97 db cohort dosszié
│
└── balasko/
    ├── data/
    ├── pdfs/
    └── results/
```

### Modell 2: Hibrid Mappastruktúra (Central Wiki Layer + Projects Storage)
A `data/wiki/` megmarad központi tudásbázisnak (mivel az ágensek a `data/wiki/methodology/` és `data/wiki/<project>/studies/` útvonalakra vannak kalibrálva), míg a nehéz kutatási nyersanyagok (adatok, PDF-ek, futtatási képek) kerülnek a `projects/` alá:
```
projects/
├── meta_hyperglycaemia/
│   ├── data/
│   ├── pdfs/
│   └── results/
├── neonatal_antibiotics/
│   ├── data/
│   ├── pdfs/
│   └── results/
└── balasko/

data/wiki/                              # Központi módszertani és dosszié réteg (változatlan helyen)
├── methodology/
├── meta_hyperglycaemia/studies/
└── neonatal_antibiotics/studies/
```

> **Értékelés és Javaslat:** A **Modell 1** hosszú távon sokkal tisztább, mert egy projekt archiválása vagy megosztása egyetlen mappa mozgatásával megoldható. Ugyanakkor a `data/wiki/` áthelyezése a Modell 1-ben érinti az ágensek wiki-olvasási mechanizmusait. A döntést a Nyitott Kérdések fejezetben kell meghozni.

---

## A.2 Tényleges Hardkódolt Útvonal-Hivatkozások Auditja (`src/`, `.agent/`, `docs/`)

A kódbázis tételes átvizsgálása alapján az alábbi scriptek és dokumentumok tartalmaznak közvetlen sztring-hivatkozást a jelenlegi útvonalakra:

### 1. `meta_hyperglycaemia` Hivatkozások (Összesen: 21 találat, 9 fájl)
- **`src/download_all_databases.py`** (29. sor):  
  `OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "meta_hyperglycaemia")` ➔ frissítendő: `projects/meta_hyperglycaemia/data`
- **`src/full_text_adjudicator.py`** (737. sor):  
  `in_path = os.path.join(WORKSPACE_DIR, "meta_hyperglycaemia", "screening_decisions_review.csv")` ➔ frissítendő: `projects/meta_hyperglycaemia/...`
- **`src/extraction_assistant.py`** (436–437. sorok):  
  Help leírások és Markdown badge linkek: `data/wiki/meta_hyperglycaemia/...`
- **`src/generate_hyperglycaemia_wiki.py`**:  
  Több ponton közvetlenül a gyökérszintű `meta_hyperglycaemia/` mappából olvassa a CSV-ket.
- **`.agent/workflows/generate-study-wiki.md`** (33. sor):  
  Példaparanccs: `python src/generate_study_wiki.py --project meta_hyperglycaemia`
- **`.agent/ARCHITECTURE.md`** (129. sor):  
  Fájlfa leírásban: `├── meta_hyperglycaemia/`
- **`meta_hyperglycaemia/` belső scriptek** (további 12 belső segédscript):  
  `automated_screening.py`, `prisma_pipeline_v3.py`, `feasibility_screen.py` stb. közvetlen lokális relatív fájlneveket használnak (pl. `'screening_library.csv'`), így ha magát a mappát mozgatjuk, ezek belsőleg nem törnek el, ha a munkakönyvtár a projekt mappája.

### 2. `neonatal_antibiotics` Hivatkozások (Összesen: 151 találat, 74 fájl)
A legfontosabb kategóriák:
- **`results/neonatal_antibiotics/` hivatkozások (26 fájl):**
  - `src/run_meta_analysis.py` (164. sor: `out_dir = 'results/neonatal_antibiotics'`)
  - `src/run_subgroup_analysis.py` (181. sor: `out_dir = 'results/neonatal_antibiotics'`)
  - `src/run_extended_meta_analysis.py` (103. sor: `out_dir = 'results/neonatal_antibiotics'`)
  - `src/screen_downloaded_fulltexts.py` (121–122. sorok: `df.to_excel('results/neonatal_antibiotics/...')`)
  - `src/match_downloaded_pdfs.py`, `src/build_master_audit_workbook.py`, `src/run_antibiotics_search.py` stb.
- **`data/pdfs/neonatal_antibiotics/` hivatkozások (24 fájl):**
  - `src/screen_downloaded_fulltexts.py` (5. sor: `PDF_DIR = os.path.join('data', 'pdfs', 'neonatal_antibiotics')`)
  - `src/refine_dossier_names.py` (14. sor: `pdf_dir = os.path.join('data', 'pdfs', 'neonatal_antibiotics')`)
  - `src/match_batch1_pdfs.py` – `match_batch6_pdfs.py` (glob útvonalak: `'data/pdfs/neonatal_antibiotics/*.pdf'`)
  - `src/parse_batch1_details.py` – `parse_batch6_details.py`
- **`data/Data_extraction_neonatal_antibiotics_v9.xlsx` hivatkozások (15 fájl):**
  - `src/run_meta_analysis.py`, `src/run_subgroup_analysis.py`, `src/run_extended_meta_analysis.py`, `src/validate_extraction_integrity.py`, `src/update_master_extraction_with_demographics.py`, `src/test_audit_load.py`.
- **`data/wiki/neonatal_antibiotics/studies/` hivatkozások:**
  - `src/write_batch2_dossiers.py` – `write_batch4_dossiers.py`, `src/match_downloaded_pdfs.py`, `src/plan_wiki_cleanup.py`.

### 3. `balasko` Hivatkozások (0 találat a forráskódban)
- Sem a `src/`, sem az `.agent/`, sem a `docs/` nem tartalmaz aktív kódot vagy fájlhivatkozást a `balasko` projektre. Kizárólag a `.gitignore` 30. sorában szerepel.

---

## A.3 A `data/project_state.json` és `src/check_phase_gate.py` Auditja

### Elemzési Eredmény:
1. **`data/project_state.json`:**
   - **NEM TARTALMAZ FÁJLÚTVONALAKAT.**
   - A JSON kizárólag a projekt azonosító kulcsát (`"meta_hyperglycaemia"`, `"neonatal_antibiotics"`), a fázis-állapotokat, PICO szövegeket, SHA-256 hash-eket és az Oversight Loop módosítási naplóját tárolja.
   - Következmény: A fájlok `projects/` mappába mozgatása a `data/project_state.json` tartalmát **közvetlenül egyetlen ponton sem érvényteleníti**, a kulcsok változatlanok maradhatnak.
2. **`src/check_phase_gate.py`:**
   - A kapuellenőrző determinisztikus script mindössze két rögzített gyökérszintű fájlt kezel:
     - `DEFAULT_STATE_FILE = os.path.join(WORKSPACE_DIR, "data", "project_state.json")`
     - `DEFAULT_AMENDMENTS_FILE = os.path.join(WORKSPACE_DIR, "PROTOCOL_AMENDMENTS.md")`
   - A kapuk vizsgálatakor (`check_phase_3`, `check_phase_4`, `check_amendment`) a script a `--project <slug>` paraméterrel kapott kulcsot keresi a `project_state.json`-ban. Nem nyit meg sem PDF-eket, sem Excel táblázatokat közvetlenül merev útvonalon.
   - Következmény: A `check_phase_gate.py` a projektmappák mozgatása után is **100%-ban működőképes marad**, feltéve, hogy a jövőbeli kiegészítések (pl. a Part B-ben tervezett adatlinter) paraméterezhető útvonalat kapnak.

---

## A.4 A `.gitignore` Szabályainak Átalakulása

Jelenlegi `.gitignore` szabályok (sorok 28–39):
```gitignore
# 1. Saját kutatási alprojektek könyvtárai
meta_hyperglycaemia/
balasko/
results/
garami_publications/
hegyi_publications/
TM/

# 2. Egyedi tanulmány dossziék (a methodology, templates és resources marad!)
data/wiki/*/studies/
data/wiki/neonatal_antibiotics/
data/wiki/meta_hyperglycaemia/
```

### Javasolt Új `.gitignore` Minta a `projects/` Mappához:

Ha a projektek a `projects/<project_slug>/` gyűjtőmappába kerülnek:
1. **Egységes kizárás:** A különálló `meta_hyperglycaemia/`, `balasko/`, `results/` sorok helyett egyetlen univerzális szabály alkalmazható:
   ```gitignore
   # Kutatási projektek nyers anyagai (nagyméretű PDF-ek, nyers adatok és ábrák kizárása)
   projects/*/pdfs/
   projects/*/results/
   projects/*/data/*.pdf
   projects/*/data/*.xlsx
   projects/*/data/*.csv
   projects/*/annotated_pdfs/
   ```
2. **Értékes projekt-metaadatok verziózása (Whitelist):**
   Ha azt szeretnénk, hogy a projektek protokolljai, döntésnaplói és konfigurációi megmaradjanak a Gitben, de a többszáz megabájtos PDF-ek és Excel táblák ne:
   ```gitignore
   # Kizárjuk a projektek nehéz adatait
   projects/*/pdfs/
   projects/*/results/
   projects/*/*.xlsx
   projects/*/*.pdf
   
   # De MEGŐRIZZÜK a protokollokat, konfigurációkat és döntésnaplókat:
   !projects/*/PROTOCOL.md
   !projects/*/PROTOCOL_AMENDMENTS.md
   !projects/*/plausibility_ranges.json
   !projects/*/_resolutions/
   !projects/*/_resolutions/**
   ```
Ez a megoldás radikálisan letisztítja a `.gitignore`-t, és automatikusan működni fog bármilyen újonnan létrehozott projektre (`projects/új_projekt/`), anélkül hogy a `.gitignore`-t újra kellene szerkeszteni.

---

## A.5 Rész A — Nyitott Kérdések a Kutatói Döntéshez

1. **Struktúra Választás:** A Modell 1 (teljes önálló projektmappa: `projects/<slug>/wiki/studies/`) vagy a Modell 2 (hibrid: `projects/<slug>/` csak az adatoknak/eredményeknek, míg a `data/wiki/` marad a központi tudásréteg) mellett döntsünk?
2. **Historikus Scriptek Sorsa:** A `src/` mappában lévő ~40 db régebbi batch-scriptben (amiket a P0 szabályok miatt már tilos futtatni az adatkinyerésre) javítsuk-e a hardkódolt útvonalakat `projects/`-re, vagy mozgassuk át őket egy `archive/legacy_batch_scripts/` mappába a rend fenntartása érdekében?
3. **`balasko` Projekt Inicializálás:** Létrehozzuk-e a `projects/balasko/` alapmappát az üres sablonokkal (`data/`, `pdfs/`, `results/`), vagy maradjon csak egy lehetséges jövőbeli slug?

---
---

# RÉSZ B: `src/validate_extraction_data.py` — CTM BoostR Adatlinter

A GP3 szisztematikus áttekintések metaanalízisének megalapozásához kötelező a [CTM Template v9](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/07_data_extraction_and_boostr.md) adattisztítási szabványának (BoostR Standard) maradéktalan teljesítése.

A jelenlegi pipeline-ban van egy `src/validate_extraction_integrity.py`, de az kizárólag a `data/Data_extraction_neonatal_antibiotics_v9.xlsx` fájlra van hardkódolva, nem univerzális, és hiányoznak belőle a strukturált CTM BoostR ellenőrző kapuk.

Az új **`src/validate_extraction_data.py`** egy általános célú, determinisztikus linter lesz, amely bármely megadott Excel munkafüzeten képes lefutni.

---

## B.1 A CTM BoostR Szabályok Determinisztikus Logikája

A linter az `AGENTS.md` §3.4 Rule 5 alapján az alábbi 5 determinisztikus kaput ellenőrzi:

### Gate 1: Numeric-Only Mandate (Szigorú Számformátum)
- **Kritérium:** A statisztikai adatmezőkben KIZÁRÓLAG valós számértékek (`int` vagy `float`) szerepelhetnek.
- **Detektált hibák:**
  - Szöveges helyettesítők: `"N/A"`, `"NA"`, `"-"`, `"nil"`, `"missing"`, `"nem ismert"`.
  - Szöveggel kevert számok: `"kb. 12"`, `"12 (26%)"`, `">180"`, `"<0.001"`, `"[1.2-3.4]"`.
  - Formázási anomáliák: Pont helyett vesszővel írt tizedes tört szövegként tárolva (`"38,6"` a `38.6` helyett).
- **Megengedett kivétel:** Ha egy cella üres, és a mező nem kötelező.

### Gate 2: Mandatory Cells Integrity (Kötelező Mezők Sértetlensége)
- **Kritérium:** Egy kitöltött sor sem hagyhat üresen fundamentális azonosítókat és matematikai párokat.
- **Detektált hibák:**
  - Hiányzó `Author_Year`, `Study_ID` vagy `Outcome_Name`.
  - Aszimmetrikus 2x2 dichotomous adatok: meg van adva az `events_E`, de hiányzik a `total_E`.
  - Matematikai érvénytelenség: `events_E > total_E` vagy `events_C > total_C` (több esemény, mint a csoportlétszám).

### Gate 3: Unique Author_Year & Disaggregation Integrity
- **Kritérium:** Egy primer tanulmány ugyanarra a kimenetelre csak egyszer szerepelhet a fő elemzésben (ökológiai duplikáció tilalma), kivéve, ha explicit alcsoport/kar bontás van jelen.
- **Detektált hibák:**
  - Teljesen azonos `Author_Year` + `Outcome_Name` kombinációk több sorban alcsoport-jelölés nélkül.
  - Helyes forma: `Ali 2024 (Mild TH)` és `Ali 2024 (Severe TH)` külön karokként engedélyezett, ha a mintanagyságok nem átfedőek.

### Gate 4: Homogeneous Outcome Taxonomy (Egységes Kimenetel-Taxonómia)
- **Kritérium:** Egy adott metaanalízisben tilos azonos biológiai végpontokat eltérő elnevezésekkel szétszórni.
- **Detektált hibák:**
  - Szinonimák keveredése ugyanabban az oszlopban: pl. sor 3-ban `"Mortality"`, sor 7-ben `"Death"`, sor 12-ben `"In-hospital death"` ➔ a linter kötelező egységesítési hibát jelez.

### Gate 5: Unit Conversion Isolation & Wan/Higgins Flag
- **Kritérium:** A mértékegységeknek és a transzformációs jelölőknek szigorúan izolált oszlopban kell lenniük.
- **Detektált hibák:**
  - Mértékegység beírása a szám mellé: pl. `"3320 g"` vagy `"10.2 mmol/L"` a numerikus cellában.
  - Medián/IQR értékek átlagként/szórásként való feltüntetése a kötelező konverziós zászló (`Is_Wan_Converted = True`) nélkül.

---

## B.2 Bemenet és Kimenet Specifikációja

### Bemenet:
A script CLI argumentumként kapja meg a vizsgálandó fájlt:
```powershell
python src/validate_extraction_data.py --file projects/meta_hyperglycaemia/data/Data_extraction_template_v9_HIE.xlsx
```
- **Beolvasott Munkalapok:**
  1. `ORs - RRs`: Dichotomous hatásméretek (eseményszámok, crude OR, aOR, CI határok).
  2. `Mean Difference` & `Simple mean`: Folytonos kimenetek (átlag, SD, N).
  3. `Regression coefficient`: Korrigált regressziós együtthatók és kovariánsok.
  4. `Basic layout`: Kohorsz alapjellemzők és demográfia.
  5. `QUIPS` / `RoB2`: Torzításkockázati doménértékek (Low / Moderate / High / Unclear formátum-ellenőrzés).

### Kimenet (Strukturált Audit Riport a `validate_protocol.py` mintájára):
A terminálon és kérésre JSON formátumban megjelenő jelentés:

```
════════════════════════════════════════════════════════════════════════════
  CTM BOOSTR DATA EXTRACTION LINTER REPORT
  Fájl: projects/meta_hyperglycaemia/data/Data_extraction_template_v9_HIE.xlsx
════════════════════════════════════════════════════════════════════════════

  [GATE 1] Numeric-Only Mandate:              20 / 25 pont  ⚠️
  [GATE 2] Mandatory Cells Integrity:          20 / 20 pont  ✅
  [GATE 3] Unique Author_Year & Arms:          15 / 15 pont  ✅
  [GATE 4] Outcome Taxonomy Consistency:       10 / 20 pont  ❌
  [GATE 5] Unit Isolation & Wan/Higgins:       20 / 20 pont  ✅
  ────────────────────────────────────────────────────────────────────────
  ÖSSZPONTSZÁM:                                85 / 100 pont [PASS]

DETEKTÁLT HIBÁK ÉS CELLAHIVATKOZÁSOK:
----------------------------------------------------------------------------
1. [GATE 1][NON_NUMERIC_VALUE] Munkalap: 'ORs - RRs', Cella: E14 (Sor 14)
   Oszlop: 'total_E' | Talált érték: 'approx 56'
   Hiba: Szöveges módosító numerikus oszlopban. Elvárt: 56.

2. [GATE 4][TAXONOMY_DISCREPANCY] Munkalap: 'ORs - RRs', Cella: C8 vs C12
   Oszlop: 'Outcome_Name' | 'Death before discharge' vs 'Mortality'
   Hiba: Szinonimák használata azonos elsődleges végpontra. Standardizálás szükséges.
════════════════════════════════════════════════════════════════════════════
```

- **Kilépési Kódok (Exit Codes):**
  - `0`: PASS (Pontszám $\ge 85$ és nincsenek kritikus Gate 1/Gate 2 blokkoló hibák).
  - `1`: FAIL (Pontszám $< 85$ vagy kritikus cellahiba jelenléte).

---

## B.3 Workflow Integráció és a `check_phase_gate.py` Döntési Pont

### Használati Módok:
1. **Önálló Eszközként (Ad-hoc Researcher Tool):**
   A kutató vagy az adatkinyerést végző ágens bármikor meghívhatja a kitöltés alatt, hogy ellenőrizze az Excel állapotát, mielőtt továbbhaladna.
2. **Phase 3 ➔ Phase 4 Fáziskapu Feltételként (`check_phase_gate.py`):**
   - **Kérdés:** Legyen-e kötelező feltétel a Phase 4-be (Mentori Bírálat) lépéshez, hogy a `validate_extraction_data.py` kilépési kódja `0` legyen?
   - **Módszertani indoklás:** Prof. Hegyi és Dr. Garami mentori értékelése nem kezdődhet meg olyan adathalmazon, amelyben kevert mértékegységek vagy hibás nevezők vannak.
   - ⚠️ **KUTATÓI JÓVÁHAGYÁSI PONT:** Ennek beépítése a `src/check_phase_gate.py` módosítását igényli. A jelenlegi szabályzat értelmében a kapuellenőrző szigorúan védett, így ez **kizárólag explicit felhasználói engedéllyel aktiválható**.

---

## B.4 Biztonságos Tesztelési Stratégia (Nulla Szintetikus Adat Kockázat)

A korábbi incidens (szintetikus PDF generálása) tanulságaként **szigorúan TILOS kitalált kutatási adatokat valódiként kezelni**. A linter tesztelésére az alábbi két tiszta módszer tervezett:

### 1. Módszer: Valódi, Meglévő Történeti Munkafüzetek Auditja (Arany Standard)
- Tesztelés a már a repozitóriumban lévő, valódi adatokon:
  - `data/Data_extraction_neonatal_antibiotics_v9.xlsx` (145 valós sor)
  - `meta_hyperglycaemia/Data_extraction_template_v9_HIE.xlsx` (19 valós sor)
- A lintert ezeken futtatjuk le **kizárólag olvasási módban**. Ez azonnal megmutatja a valódi kutatási adatokban lévő esetleges formázási hibákat anélkül, hogy bármilyen új adatot kellene generálni.

### 2. Módszer: Kifejezett és Izolált Egységteszt Fixture (`tests/fixtures/`)
- Ha szándékos hibákat (pl. betűk a számok között) kell tesztelni a linter hibadetektáló képességének igazolására:
  - Létrehozunk egy `tests/fixtures/fixture_ctm_linter_bad_syntax.xlsx` állományt.
  - A fájl nevében, fejlécében és minden munkalapján **hatalmas, félreérthetetlen figyelmeztetés szerepel**:  
    `[MOCK UNIT TEST FIXTURE — INTENTIONAL FORMATTING ERRORS FOR REGRESSION TESTING ONLY — NOT REAL EVIDENCE]`.
  - A tesztelt tanulmányok nevei kizárólag: `DummyAuthor_2099_Test_A`, `MockStudy_2099_Test_B`.
  - Ez a fájl szigorúan a `tests/` mappában él, soha nem kerülhet a `data/` vagy `projects/` mappákba, és semmilyen metaanalízis nem olvashatja be.

---

## B.5 Rész B — Nyitott Kérdések a Kutatói Döntéshez

1. **Gate Integráció a `check_phase_gate.py`-ba:** Jóváhagyod-e, hogy az adatkinyerési linter sikeres lefutása (Pass) kötelező determinisztikus feltétele legyen a Phase 4-be (Mentori Bírálat) történő belépésnek a `check_phase_gate.py`-ban?
2. **Szigorúsági Küszöb:** Megfelel-e a $\ge 85/100$ pontos jóváhagyási küszöb, azzal a feltétellel, hogy egyetlen Numeric-Only (szöveg a számok között) hiba is azonnali automatikus elutasítást (FAIL) von maga után?
3. **Munkalap Hatókör:** A jelenlegi 5 fő munkalapon (`ORs - RRs`, `Mean Difference`, `Simple mean`, `Regression coefficient`, `Basic layout`) felül vizsgálja-e a linter a RoB táblákat (`RoB2`, `QUIPS`) is, vagy azok maradjanak külön minőségbiztosítási körben?

---

*Tervdokumentum elkészült: 2026-09-30 · GP3 Architecture and Linting Plan v1.0*
