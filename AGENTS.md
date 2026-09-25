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
│ • Sensor-Pathway-Effector triád & Termális Dózis (COIN) ellenőrzés     │
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
│ PHASE 5: Protokoll Kompiláció & Determinisztikus Linter                │
│ Vezető ágens: documentation-writer                                     │
│ • 10 fejezetes, publikációkész PROTOCOL.md / PROSPERO tervezet         │
│ • Determinisztikus ellenőrzés: `python src/validate_protocol.py`       │
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

---

### 3.5 Támogató Ágensek
- **`orchestrator`:** Koordinálja az 5 fázis lefutását, érvényesíti az ágenshatárokat (Agent Boundary Enforcement: a `lit-reviewer` nem számol statisztikát, a `meta-analyzer` nem ír klinikai bevezetőt), és biztosítja a kontextus átadását a fázisok között.
- **`documentation-writer`:** A Phase 5-ben összeállítja a végleges, 10 fejezetből álló `PROTOCOL.md` dokumentumot, integrálva a korábbi fázisok számszerű adatait, mentori pontjait és szókratészi válaszait.

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
| **Gate 6** | **Módszertani Szigor, Confounder Matrix & COIN Dózis:** QUIPS / RoB 2 + Confounder Matrix + Multilevel RVE + Termális intervencióknál kötelező Cooling Index (COIN) ellenőrzés | 15 pont |
| **Gate 7** | **Transzlációs Hatás:** Explicit T1–T4 stádium + Kerülhető Mortalitás számai | 10 pont |

- **Jóváhagyási küszöb:** **≥ 70 pont** = APPROVED (Elfogadva)  
- **Elutasítás:** **< 70 pont** = REJECTED (Javítás szükséges a hibás kapuk mentén)

---

## 5. SZABÁLYZATI PRIORITÁSI LÁNC ÉS MINŐSÉGBIZTOSÍTÁS

### 5.1 Szabályzati Hierarchia
Bármilyen módszertani konfliktus esetén a prioritás szigorúan a következő:
1. **P0:** Globális rendszerbiztonsági és munkamenet-szabályok (`.agent/rules/GEMINI.md`)
2. **P1:** Kanonikus Ágens- és Mentor-specifikációk (`AGENTS.md` és `MENTORS.md`)
3. **P2:** CTM módszertani iránymutatások (`TM/` könyvtár és Cochrane Handbook v6.5)
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

