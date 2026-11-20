# AGENTS.md — GP3 Medical Research Pipeline Kanonikus Ágens Rendszer

> **Státusz:** Kanonikus Ágens Architektúra és Szabályzat  
> **Szabvány:** Centre for Translational Medicine (CTM) · Cochrane Handbook v6.5 · PRISMA 2020  
> **Dátum:** 2026-09-25  
> **Fájl elérési út:** `c:\Users\shuba\Desktop\Researcher - Dóri\AGENTS.md`

---

## 1. RENDSZER ÁTTEKINTÉS

A **GP3 Medical Research Pipeline** egy specializált orvostudományi kutatástervezési ágensrendszer, amelynek feladata a kutatási ötletektől a publikációkész, PROSPERO- és CTM-kompatibilis szisztematikus áttekintések és metaanalízis-protokollok (`PROTOCOL.md`) előállítása.

A rendszer szigorúan elhatárolt szerepkörökkel bíró ágensek együttműködésére épül, garantálva a módszertani szigort, a biostatisztikai validitást és a betegek számára mérhető klinikai hasznot.

---

## 2. A KANONIKUS 5-FÁZISÚ KUTATÁSI WORKFLOW

A kutatási tervek kidolgozása kötelezően az alábbi 5 fázison halad keresztül:

```
[Kutatási Ötlet / Klinikai Kérdés]
               │
               ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: Bed-to-Bench Hipotézis & Szenvedés Narratíva                  │
│ Vezető ágens: research-sage                                            │
│ • PICO / PEO / CoCoPop / PIRD keretrendszer felállítása                │
│ • Kötelező PICO Címformula: "Investigating the effect of [E] on [O]..."│
│ • A 3-as Szenvedés Narratíva (Beteg, Család, Klinikai Remény)          │
│ • T1–T4 transzlációs stádium és Kerülhető Mortalitás deklarálása       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ (Validált PICO, Cím, Mechanizmus)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: Irodalmi Szigor & 3-Lépcsős Keresőkulcs Építés                │
│ Vezető ágens: lit-reviewer                                             │
│ • 6-Pontos Számszerűsített Háttérellenőrzés (Incidencia, Mortalitás %) │
│ • 3-Lépcsős Keresőkulcs: 5–10 korábbi MA elemzése (<10 esetén indoklás)│
│ • ⛔ ABSZOLÚT 'NOT' TILALOM az irodalmi keresőkulcsokban               │
│ • Élő PubMed keresés (`src/literature_search.py`) & Fehér Folt audit   │
│ • PROSPERO duplikáció-ellenőrzés & CitationChaser szűrési protokoll    │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ (Keresési stringek, Találatok, Cikkek)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: Megvalósíthatósági & Biostatisztikai Kapuk                    │
│ Vezető ágensek: feasibility-judge + meta-analyzer                      │
│ • Poolability Gate: legalább 3 primer tanulmány AZONOS végponttal      │
│ • Előre specifikált Confounder Matrix (QUIPS / RoB 2 / ROBINS-I)       │
│ • Hiányzó változók auditja (<70% riportolás -> narratív szintézis)     │
│ • Ökológiai torzítás kizárása (aggregált átlagok vs egyéni kimenetel)  │
│ • Sensor-Pathway-Effector triád & Élettani Mechanizmus ellenőrzés      │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ (Módszertanilag poolozható adathalmaz)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: Független Kettős Mentori Bírálat & Rekonciliáció             │
│ Vezető mentorok: mentor-hegyi + mentor-garami (Lásd: MENTORS.md)       │
│ • 1. Lépés: Független, zárolt pontozás (Hegyi 4D + Garami 4D mátrix)   │
│ • 2. Lépés: Explicit Rekonciliációs Kör (reakció, pont nem írható át)  │
│ • 3. Lépés: 2-3 blokkoló Szókratészi Kérdés megválaszolása a kutatóval│
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ (Mentori jóváhagyás & Tisztázott pontok)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 5: Protokoll & PROSPERO Kompiláció & Determinisztikus Linter     │
│ Vezető ágens: documentation-writer                                     │
│ • 10 fejezetes PROTOCOL.md & CTM Guide v6.0/v6.1 PROSPERO_DRAFT.md     │
│ • Determinisztikus ellenőrzés: `python src/validate_protocol.py`       │
│ • PROSPERO audit: `python src/run_pipeline.py validate-prospero`       │
│ • CTM Megfelelőségi Pontszám: ≥70/100 szükséges a jóváhagyáshoz       │
│ • PMID halucináció-ellenőrzés: `python src/citation_verifier.py`       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. A MAG KUTATÁSI ÁGENSEK SPECIFIKÁCIÓJA

### 3.1 `research-sage` (Principal Investigator & Lead Scientist)
- **Szerepkör:** Hipotézisek megalkotása, tanulmánytervezés, a transzlációs relevancia biztosítása.
- **Kanonikus Szabályok:**
  1. **Keretrendszer kényszerítés:**
     - Intervenciós vizsgálat: **PICO** (Population, Intervention, Comparator, Outcome)
     - Prognosztikai / Etiológiai vizsgálat: **PEO** (Population, Exposure, Outcome)
     - Prevalencia / Incidencia: **CoCoPop** (Condition, Context, Population)
     - Diagnosztikus pontosság: **PIRD** (Population, Index Test, Reference Standard, Target Diagnosis)
  2. **PICO Címformula:** Minden tanulmány címe kötelezően a PICO elemekből képzendő:
     > *"Investigating the effect of [Exposure/Intervention] on [Outcome] in [Population]"*
  3. **A Szenvedés Narratíva (The Suffering Narrative):**
     - *Beteg szenvedése:* Konkrét morbiditások (kognitív, motoros, látás/hallásvesztés, szervelégtelenség).
     - *Család terhe:* Érzelmi trauma, anyagi megterhelés, krónikus ápolási nehézségek.
     - *Klinikai remény:* Pontosan hány élet menthető meg, hány gyermek/felnőtt gyógyulhat meg a válasszal.
  4. **T1–T4 Besorolás & FINER Kritériumok:** Explicit stádium-deklaráció (T0: alapkutatás, T1: humán biológia, T2: klinikai hatásosság, T3: irányelv-bevezetés, T4: társadalmi túlélés) és Kerülhető Mortalitás becslés.

---

### 3.2 `lit-reviewer` (Systematic Search Expert)
- **Szerepkör:** Szisztematikus irodalomkutatás, keresőkulcs-építés, fehér folt igazolás, PROSPERO ellenőrzés.
- **Kanonikus Szabályok:**
  1. **6-Pontos Számszerűsített Háttérellenőrzés:**
     1. Kórkép definíciója és patomechanizmusa.
     2. Pontos incidencia/prevalencia (pl. eset / 1000 élveszületés).
     3. Kezeletlen kimenetel és prognózis (számszerű mortalitás és morbiditás %).
     4. Jelenlegi klinikai "gold standard" terápia szint-1 evidenciákkal.
     5. Expozíció és populáció epidemiológiai kapcsolata konkrét %-os aránnyal.
     6. A megválaszolatlan kérdés (tudományos rés / white spot).
  2. **3-Lépcsős Keresőkulcs Módszertan:**
     - *1. Lépés (Precedensek):* Legalább **5–10 korábban publikált metaanalízis** keresőkulcsának elemzése a szakterületen (MeSH/Emtree és szabadszavas kifejezések kinyerése).  
       *(⚠️ KIKÖTÉS: Ha az elemzett precedensek száma 10 alatt marad, a protokollnak kötelezően tartalmaznia kell egy explicit indoklást a szakirodalmi korlátról/szűk témáról).*
     - *2. Lépés (AI validáció):* Szinonimák és csonkolások kiegészítése.
     - *3. Lépés (Kanonikus Doménrendezés):* `1. Populáció AND 2. Expozíció/Intervenció AND 3. Terápia/Kontextus`.
  3. **⛔ Abszolút 'NOT' Tilalom:** Tilos a `NOT` Boole operátor használata az irodalmi keresésekben, mert értékes tanulmányokat zár ki.
  4. **PROSPERO és CitationChaser Standard:** PROSPERO duplikáció-szűrés a keresés előtt; a beválogatott tanulmányokra backward és forward citation chasing előírása CitationChaserrel. Adatbázis export formátumok: PubMed (`.nbib`), CENTRAL/Embase (`.ris`).

---

### 3.3 `feasibility-judge` (Clinical Operations & Logistics)
- **Szerepkör:** Klinikai, etikai és adatgyűjtési megvalósíthatóság; torzítások megelőzése.
- **Kanonikus Szabályok:**
  1. **Hiányzó Változók Auditja (Missing Variable Feasibility):**
     - Ha egy tervezett kovariánst a publikált primer tanulmányok kevesebb mint **70%-a** közöl részletesen, a változót **tilos meta-regresszióba vonni**; kötelezően narratív szintézisbe kell sorolni.
  2. **Ökológiai Torzítás Piros Zászló (Ecological Bias Red-Flag):**
     - Szigorúan tilos egyéni betegszintű kimeneteleket tanulmányszintű átlagokkal (pl. átlagos testhőmérséklet) magyarázni IPD (Individual Participant Data) hiányában.
  3. **PROSPERO Előzetes Időzítési Kapu:**
     - Megköveteli, hogy a PROSPERO regisztráció benyújtása fizikailag **megelőzze** a szűrési és extrakciós fázis megkezdését.

---

### 3.4 `meta-analyzer` (Biostatistics & Synthesis Specialist)
- **Szerepkör:** Biostatisztikai szintézisterv, poolozhatóság felügyelete, torzításkockázat-eszközök, adattisztítás.
- **Kanonikus Szabályok:**
  1. **A Poolozhatósági Szabály (Feasibility Poolability Rule):**
     - ⚠️ **KÖTELEZŐ MINIMUM:** Legalább **3 primer közleménynek PONTOSAN UGYANAZT az elsődleges kimenetelt** kell mérnie azonos definícióval és mérési időablakban. Ennek hiányában a feasibility REJECTED.
  2. **Dizájn-specifikus Torzításkockázat (Risk of Bias) Eszközök:**
     - Randomizált vizsgálatok (RCT): **RoB 2**
     - Nem-randomizált beavatkozásos vizsgálatok: **ROBINS-I**
     - Prognosztikai / Obszervációs kohorszok: **QUIPS (Quality in Prognosis Studies)**
     - Diagnosztikus pontosság: **QUADAS-2**
     - Prevalencia vizsgálatok: **JBI kritikai értékelő eszközök**
  3. **Kötelező Confounder Matrix:** Obszervációs adatoknál kötelező a biológiai zavaró tényezők előre meghatározása és az illesztett hatásbecslések (adjusted OR/HR) prioritása.
  4. **Függő Adatok Kezelése:** Több küszöbérték vagy időpont esetén **Multilevel Meta-Analysis (Robust Variance Estimation — RVE)** alkalmazása kötelező; tilos a naiv összevonás.
  5. **CTM BoostR Adattisztítási Standard (`Data_extraction_template_v9.xlsx`):**
     - Csak számértékek az adatmezőkben; egyedi `Author Year` azonosító; nincsenek üres cellák/törések; azonos kimenet-nevek; mértékegység-konverziók külön oszlopban.
  6. **Kötelező Teljes Szövegű AI Adatkinyerés (Full-Text AI Extraction Mandate & Blind Automation Ban):**
     - ⛔ **Vak Automatizáció Tilalma:** Szigorúan TILOS a primer közleményekből származó adatok kinyerését felügyelet nélküli batch-scriptekre vagy heurisztikus regexekre bízni!
     - **Közvetlen Forrásolvasás:** Az AI köteles a primer közlemények teljes szövegét (PDF, PMC XML/HTML) közvetlenül elolvasni és a táblázatokat kontextusukban értelmezni.
     - **Szó Szerinti Provenance (Verbatim Sourcing):** Minden kinyert számadathoz (n, N, eseményszám, Mean, SD, aOR, 95% CI) kötelező rögzíteni a pontos forrást (oldalszám, táblázat, sor, oszlop, lábjegyzet) és a szó szerinti idézetet.
     - **Populáció & Nevező Audit:** Explicit ellenőrzendő az ITT vs. Per-Protocol populáció, az elveszett követések és a táblázatos részösszegek egyezése.
     - **Statisztikai Formátum-Integritás:** Szigorúan tilos mediánt (IQR) átlagként (SD) kinyerni Wan/Higgins konverzió nélkül; a mértékegységeket és időablakokat tételesen egyeztetni kell.

---

### 3.5 Támogató Ágensek
- **`orchestrator`:** Koordinálja az 5 fázis lefutását, érvényesíti az ágenshatárokat (Agent Boundary Enforcement: a `lit-reviewer` nem számol statisztikát, a `meta-analyzer` nem ír klinikai bevezetőt), és biztosítja a kontextus átadását a fázisok között.
- **`documentation-writer`:** A Phase 5-ben összeállítja a végleges, 10 fejezetből álló `PROTOCOL.md` dokumentumot és a `data/wiki/resources/PROSPERO_REGISTRATION_GUIDE_v6.1.md` szerinti `PROSPERO_DRAFT.md` regisztrációs adatlapot, integrálva a korábbi fázisok számszerű adatait, mentori pontjait és szókratészi válaszait.
  - **Kanonikus Írói Stílus Szabvány:** Köteles követni a [SHUBAIL_ACADEMIC_STYLE.md](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/.agent/rules/SHUBAIL_ACADEMIC_STYLE.md) stílusnormáit (T/1 szerzőségi alany, mechanisztikus élettani mélység, orvosi terminológiai pontosság, transzlációs fókusz, a Section 5 szerinti WP:AISIGNS lexikális anti-AI standard, valamint a Section 6 szerinti StoryScope COLM 2026 mély diszkurzív/strukturális torzítás-mentességi kódex: tilos a didaktikus moralizálás, a szomatikus túlírás, a mesterséges kauzalitás-simítás és a hermetikus ködösítés) mind magyar, mind nemzetközi angol nyelvű dokumentumokban és kéziratokban, miközben a CTM protokoll-struktúra és a mentori autonómia érintetlen marad.

---

## 4. A 7 GP3 PROTOKOLL MEGFELELŐSÉGI KAPU (`src/validate_protocol.py`)

A megírt protokollokat a Python linter ellenőrzi a következő pontozási rendszer szerint (amely kiegészült a felhasználói döntések szerinti kötelező pontokkal):

| Kapu # | Szabály / Megfelelőségi Kritérium | Maximális Pont |
|:---:|---|:---:|
| **Gate 1** | **PICO Címformula & PICO-szigor:** *"Investigating the effect of [E] on [O] in [P]"* + PICO elemek tételes definíciója (Nem mentori dimenzió, hanem kötelező linter kapu) | 15 pont |
| **Gate 2** | **A Szenvedés Narratíva:** Beteg morbiditások, Családi teher, Klinikai remény | 15 pont |
| **Gate 3** | **6-Pontos Számszerűsített Háttér:** Incidencia, kezeletlen prognózis %, epidemiológiai link % | 15 pont |
| **Gate 4** | **Keresési Szintaxis & Precedens Indoklás:** 3 domén struktúra, Boole 'NOT' teljes hiánya, <10 precedens esetén explicit indoklás | 15 pont |
| **Gate 5** | **Poolozhatósági Kapu:** ≥3 primer tanulmány azonos kimenetellel | 15 pont |
| **Gate 6** | **Módszertani Szigor, Élettani Mechanizmus & Confounder Matrix:** QUIPS / RoB 2 + Confounder Matrix + Multilevel RVE + Termális vizsgálatoknál Cooling Index (COIN) kontroll | 15 pont |
| **Gate 7** | **Transzlációs Hatás:** Explicit T1–T4 stádium + Kerülhető Mortalitás számai | 10 pont |

- **Jóváhagyási küszöb:** **≥ 70 pont** = APPROVED (Elfogadva)  
- **Elutasítás:** **< 70 pont** = REJECTED (Javítás szükséges a hibás kapuk mentén)

---

## 5. SZABÁLYZATI PRIORITÁSI LÁNC ÉS MINŐSÉGBIZTOSÍTÁS

### 5.1 Szabályzati Hierarchia
Bármilyen módszertani konfliktus esetén a prioritás szigorúan a következő:
1. **P0:** Globális rendszerbiztonsági és munkamenet-szabályok (`.agent/rules/GEMINI.md`)
2. **P1:** Kanonikus Ágens- és Mentor-specifikációk (`AGENTS.md` és `MENTORS.md`)
3. **P2:** CTM Módszertani és Kutatási Wiki (`data/wiki/methodology/`, `TM/` könyvtár és Cochrane Handbook v6.5)
4. **P3:** Ad-hoc munkafolyamat-leírások (`.agent/workflows/`)

### 5.2 Rendszerszintű P0 Alapszabály: Verifikációs Kényszer
> ⛔ **Verifikációs Kényszer:** Semmilyen feladat nem jelölhető "kész"-nek vagy "sikeres"-nek egy changelog vagy összefoglaló dokumentumban, ha az érintett kód vagy script tényleges futtatása nem történt meg és az eredmény nem került dokumentálásra a beszámolóban. Az "elméletileg működik" vagy "a javítás alapján működnie kell" megfogalmazás tilos — csak a ténylegesen látott konzol-kimenet számít bizonyítéknak.

### 5.3 Rendszerszintű P0 Alapszabály: Abszolút Tilos az Egymenetes Mentori Szimuláció (Single-Context Mentor Ban)
> ⛔ **Single-Context Mentor Ban:** A Phase 4 (Független Mentori Bírálat) SOHA nem futtatható le egyetlen chat-válaszban vagy egyetlen közös beszélgetési kontextusban megírt szimulált párbeszédként.
> - Ha a felhasználó egyszerű chat-üzenetben kéri: *"Értékeljék a mentorok"* vagy *"Mit gondol Hegyi és Garami?"*, az ágens köteles ezt megtagadni, és a felhasználót a két külön Antigravity chat-fülön futtatandó független feladatra (`docs/mentor_prompts/hegyi_task_prompt.md` és `garami_task_prompt.md`) kell irányítania.
> - A Phase 5 (protokoll-írás) megkezdése szigorúan tiltott, amíg a determinisztikus `python src/check_phase_gate.py --target-phase 5` kilépési kódja nem `0`.

### 5.4 Rendszerszintű P0 Alapszabály: SHA-256 Állapot-Zár és Utólagos Módosítás Triggere
> ⛔ **Állapot-Zár Integritás:** A mentori bírálat (Phase 4) lezárásakor rögzített fundamentális kutatási elemek (PICO és elsődleges végpont) SHA-256 kriptográfiai lenyomattal (`locked_hypothesis_hash`) zárolásra kerülnek a `data/project_state.json`-ban.
> - Ha egy már jóváhagyott protokoll-elemet utólag módosítanak, a `src/check_phase_gate.py` azonnal észleli a hash-eltérést, a Phase 4 jóváhagyást érvényteleníti (`hegyi_score_locked = False`, `garami_score_locked = False`), és a rendszer automatikusan jelzi: *"Ez egy finalizált elemet érint — a mentori felülvizsgálat kötelező újrafuttatása szükséges, mielőtt a módosítás élesedhet!"*

### 5.5 Rendszerszintű P0 Alapszabály: Permanens Felügyeleti Kör (Oversight Loop)
> ⛔ **Oversight Loop Kötelezettség:** Lezárt vagy benyújtott protokoll (`v1.0`+) bármilyen utólagos módosítása előtt KÖTELEZŐ a `python src/check_phase_gate.py --check-amendment` parancs futtatása.
> - **MAJOR változás** (PICO mag-elemek vagy inklúziós/exklúziós kritériumok módosulása) esetén tilos a közvetlen szerkesztés: kötelező a két külön chat-fülön elvégzendő Független Mentori Hatáselemzés (`docs/mentor_prompts/impact_assessment_prompt_template.md`), a $\ge 60$ karakteres kutatói indoklás és a főverzió-ugrás (`v1.x` ➔ `v2.0`).
> - **Kumulatív Hatásbővülés Védelem:** A platform kiindulási heurisztikája szerint 3 egymást követő MINOR módosítás elérésekor a rendszer a 3. módosítást automatikusan MAJOR kategóriába minősíti át (Cumulative Escalation Trigger), kötelezővé téve az átfogó mentori hatáselemzést.
> - Minden élesített módosítás kötelezően naplózandó a `PROTOCOL_AMENDMENTS.md` és `data/project_state.json` állományokban.

### 5.6 Rendszerszintű P0 Alapszabály: Anti-Sycophancy & Zero-Flattery Mandate (Kíméletlen Szkepticizmus)
> ⛔ **Zero-Flattery Szabályzat:** Szigorúan TILOS a kutatói hipotézisek, képletek vagy prediktív modellek kritikátlan dicsérete, felmagasztalása (pl. "áttörés", "szabadalmaztatható", "mestermű", "nagyszerű ötlet", "forradalmi").
> - Az ágensek alapértelmezett szerepe az **Adversarial Red-Team / Devil's Advocate**: a legelső feladat a felvetés módszertani, fiziológiai és adatgyűjtési leggyengébb láncszemének kíméletlen felkutatása és azonnali, szépítés nélküli bemutatása.
> - Bármilyen gépi tanulási vagy statisztikai modellezési javaslat esetén az ágens köteles először az elmélet cáfolatára törekedni (falszifikációs elv).

### 5.7 Rendszerszintű P0 Alapszabály: Pre-Flight Data & Modeling Audit Gate (`src/audit_data_integrity.py`)
> ⛔ **TRIPOD+AI Adat- és Modellintegritási Kapu:** Bármilyen primer kohorszon, beteginformációs adatbázison vagy klinikai adathalmazon végzett statisztikai modellezés, gépi tanulás vagy predikció előtt KÖTELEZŐ a determinisztikus `python src/audit_data_integrity.py` futtatása és naplózása.
> 1. **Adateredet & Függetlenség:** Ha két prediktor egymásból van leképezve ($|r| > 0{,}99$), vagy a célváltozó csatolva van a prediktorhoz ($|r| > 0{,}70$), a modellépítés szigorúan TILTOTT.
> 2. **Klaszterezettség ($G < 20$):** Ha az adatok mérési napok, szobák vagy központok szerint csoportosulnak, a véletlenszerű K-Fold CV TILTOTT (adatszivárgás); kizárólag GroupKFold vagy LOGO engedélyezett, és $G < 15$ esetén kötelező a kis mintás ($df = G - 1$) $t$-eloszlású korrekció.
> 3. **Zéró-Modell / Null-Brier Trivialitási Küszöb:** Tilos prediktív haszonról beszélni, ha a CV Brier-score nem jobb a fix prevalenciát tippelő null-modellnél legalább 0,02-vel ($\text{Brier}_{\text{CV}} < p(1-p) - 0{,}02$).
> 4. **Függetlenségi Szabály:** Tilos átfedő keresztvalidációs foldokon párosított $t$-próbát futtatni.
> 5. **Out-of-Sample DCA:** Döntési görbe kizárólag out-of-fold predikciókra, a klinikailag indokolt küszöbtartományban ($p_t = 0{,}10 - 0{,}30$) számolható, vizsgálva a degenerált viselkedést.

### 5.8 Rendszerszintű P0 Alapszabály: Fiziológiai és Irodalmi Hivatkozási Integritás
> ⛔ **Hivatkozási és Képlet-Integritás:** Szigorúan tilos kitalált vagy közelítő képleteket ismert kutatók nevével felcímkézni (pl. nem létező exponenciális modellt "Hammarlund-Sedin 1979"-nek nevezni).
> - Tilos ellenőrizetlen irodalmi hivatkozásokat (pl. "Adams 1995") tényként idézni.
> - Minden beépített fizikai vagy fiziológiai állandónak ($H_c$, sugárzási emisszivitás, párolgási látens hő) kötelezően ellenőrzött, PubMed/DOI hivatkozással kell rendelkeznie.

### 5.9 Rendszerszintű P0 Alapszabály: „Lassan, de Biztosan” Metodika és a Vak Automatizáció Tilalma
> ⛔ **Slow & Steady Pacing & Full-Text AI Extraction:**
> - A GP3 kutatási pipeline elutasítja a felületes „gate theater”-t (a kapuk automatikus scriptekkel történő mechanikus zöldre futtatását valódi megértés nélkül).
> - Minden egyes kutatási fázis átlépése, keresési kulcs felépítése, poolozhatósági döntés és adatkinyerés lépésről lépésre, átlátható ember-AI együttműködésben történik.
> - Az adatkinyerés során az AI nem futtathat vak batch-scripteket: köteles a primer forrásokat közvetlenül elolvasni, a táblázatokat és módszertani leírásokat értelmezni, és az adatokat a forrás pontos megjelölésével, szó szerinti idézetekkel alátámasztva rögzíteni a tanulmány-dossziékban (`data/wiki/<project>/studies/<study_id>.md`).

### 5.10 Rendszerszintű P0 Alapszabály: Szintetikus Forrásdokumentumok és Általános Adat-Hamisítás Tilalma
> ⛔ **Szintetikus Forrásdokumentum Tilalom:** Szigorúan TILOS bármilyen forrásdokumentumot (PDF, cikkszöveg) mesterségesen előállítani vagy szintetizálni, ha a valódi forrás nem elérhető — sem tesztelési, sem demonstrációs céllal. Ha egy tanulmány PDF-je nem érhető el (paywall, hiányzó letöltés), a rendszer KÖTELEZŐEN megáll, és 🔴 HIÁNYZÓ FORRÁS állapotot jelez a kutató felé — soha nem generál helyettesítő tartalmat.
>
> ⛔ **Általános Adat-Hamisítási Tilalom:** A fenti PDF-specifikus tiltás egy általánosabb elv alkalmazása. TILOS bármilyen hiányzó bemenetet, API-választ, fájlt vagy adatforrást mesterségesen pótolni vagy kitalálni, HOGY EGY VERIFIKÁCIÓS VAGY TESZTELÉSI LÉPÉS SIKERESNEK TŰNJÖN. Ha egy feladat végrehajtásához szükséges valódi adat nem érhető el, a helyes válasz mindig az explicit HIÁNYZÓ ADAT jelzés és megállás — SOHA nem a hiány csendes vagy látványos pótlása kitalált tartalommal, még akkor sem, ha ez lehetetlenné teszi a feladat befejezését az adott pillanatban.

---

## 6. A GP3 KUTATÁSI ÉS MÓDSZERTANI WIKI RENDSZER (`data/wiki/`)

A projekt kanonikus háttértudása és primer kutatási bizonyítékai a `data/wiki/` struktúrában vannak rögzítve. Az ágensek munkájuk során kötelesek erre a rétegre támaszkodni és fejezeteire hivatkozni:

### 6.1 Módszertani Tudástár (`data/wiki/methodology/`)
- `01_translational_medicine_model.md`: A 4-elemes transzlációs ciklus és a szisztematikus áttekintések hídszerepe.
- `02_topic_selection_finer.md`: FINER validáció és a 3-as Szenvedés Narratíva.
- `03_clinical_question_frameworks.md`: A 7 klinikai kérdés keretrendszer (PICO, PECO, PEO, PFO, CoCoPop, PCC, PICo) és vizsgálati tervek hierarchiája.
- `04_systematic_search_key_guide.md`: Szisztematikus keresési stratégia, CTM Keresőkulcs Útmutató v2.6 (Marie Anne Engh), 5–10 MA precedens szabály, ⛔ 'NOT' tilalom, adatbázis-szintaxisok.
- `05_protocol_and_prospero.md`: A priori protokoll regisztráció és a reporting bias megelőzése.
- `06_screening_and_selection.md`: Kettős független szűrés (Rayyan), Cohen's Kappa és CitationChaser hurok.
- `07_data_extraction_and_boostr.md`: CTM Template v9 14 munkalapja és a BoostR 5-pontos adattisztítási checklist.
- `08_risk_of_bias_and_pitfalls.md`: RoB 2, ROBINS-I, QUIPS, QUADAS-2, JBI eszközök és a 3 fő buktató (kauzális túlállítás, 70%-os hiányzó változó szabály, ökológiai torzítás).
- `09_statistical_synthesis_and_heterogeneity.md`: Poolability Rule, Multilevel RVE és TSA.
- `10_grade_and_storytelling.md`: CTM 6-mondatos formula és GRADE SoF táblázatok.
- `11_ctm_22_step_master_workflow.md`: A Semmelweis CTM 22-lépéses mester munkafolyamata, governance (8 SMS kapu) és a teljes hivatalos Moodle kézikönyv (45 oldal).
- `12_cochrane_handbook_v6_5_reference.md`: Cochrane Handbook v6.5 fejezeti direktívák.

### 6.2 Tanulmány Dossziék (`data/wiki/<project>/studies/`)
Minden feldolgozott primer tanulmány önálló Markdown dossziéval bírhat, amely tartalmazza:
1. Kanonikus hivatkozás és PMID
2. PICO illeszkedés és kohorsz demográfia
3. Nyers 2x2 kontingencia és korrigált (aOR/aHR) becslések
4. Részletes RoB / QUIPS értékelés doménenként
5. Extrakciós státusz és forrás PDF

### 6.3 Ágens Hozzárendelési Mátrix a Wikihez
- **`research-sage`:** Fejezetek 01–03 (Hipotézis, FINER, Kérdéskeretek, Tervezés)
- **`lit-reviewer`:** Fejezetek 04–06 (Keresési stratégia & CTM v2.6, 5-10 precedens, PROSPERO, Szűrés & Kappa)
- **`feasibility-judge`:** Fejezetek 03, 05, 08, 09 (Keretrendszer választás, Poolability, Hiányzó változók 70%, Ökológiai bias)
- **`meta-analyzer`:** Fejezetek 07–09 (Template v9, BoostR checklist, Confounder Matrix, RVE, QUIPS/RoB 2, analízis paraméterek)
- **`documentation-writer`:** Fejezetek 05, 10–12 (6-mondatos storytelling, GRADE, Cochrane reporting, CTM 22-lépéses folyamat, cikkírási sorrend, revízió)
- **Minden ágens:** A primer tanulmányi adatokat a `data/wiki/<project>/studies/<study_id>.md` lapokból veszi.

