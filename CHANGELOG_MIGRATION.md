# CHANGELOG_MIGRATION.md — Rendszer-konszolidációs és Migrációs Változásnapló

> **Dátum:** 2026-09-25  
> **Verzió:** GP3 v2.0-canonical  
> **Feladat:** A fragmentált szabályrendszer és mentori struktúra konszolidálása, elérési utak javítása, redundáns ágensek archiválása.  
> **Jóváhagyó:** Felhasználói döntések a `MIGRATION_PLAN.md` alapján (1A, 2A, 3A, 4A, 5B + kiegészítések).

---

## 1. LÉTREHOZOTT KANONIKUS DOKUMENTUMOK

### 📄 `AGENTS.md` (Kanonikus Ágens Architektúra és Szabályzat)
- **Helye:** `c:\Users\shuba\Desktop\Researcher - Dóri\AGENTS.md`
- **Fő tartalmi elemek:**
  - **A Kanonikus 5-Fázisú Kutatási Workflow:**
    - Phase 1: Bed-to-Bench Hipotézis & Szenvedés Narratíva (`research-sage`)
    - Phase 2: Irodalmi Szigor & 3-Lépcsős Keresőkulcs Építés (`lit-reviewer`)
    - Phase 3: Megvalósíthatósági & Biostatisztikai Kapuk (`feasibility-judge` + `meta-analyzer`)
    - Phase 4: Független Kettős Mentori Bírálat & Rekonciliáció (`mentor-hegyi` + `mentor-garami`)
    - Phase 5: Protokoll Kompiláció & Determinisztikus Linter (`documentation-writer` + `validate_protocol.py`)
  - **A 6 Mag Kutatási Ágens Szabályzata:**
    - `research-sage`: PICO/PEO/CoCoPop/PIRD framing, kötelező PICO Címformula (*"Investigating the effect of [E] on [O] in [P]"*), 3-as Szenvedés Narratíva (Beteg, Család, Klinikai Remény), T1–T4 besorolás.
    - `lit-reviewer`: 6-pontos háttérellenőrzés, 3-lépcsős keresőkulcs, 5–10 korábbi metaanalízis precedenselemzése (**KIKÖTÉS:** <10 precedens esetén explicit szakirodalmi korlát indoklás kötelező), abszolút Boole 'NOT' tilalom, PROSPERO ellenőrzés, CitationChaser standard.
    - `feasibility-judge`: Hiányzó kovariánsok auditja (<70% riportolás esetén tilos a meta-regresszió), ökológiai torzítás tilalma, PROSPERO időzítési kapu.
    - `meta-analyzer`: Poolability Gate (legalább 3 primer cikk azonos elsődleges végponttal), RoB 2 / ROBINS-I / QUIPS eszközök, kötelező Confounder Matrix, Multilevel RVE modell, CTM BoostR adattisztítási standard (`Data_extraction_template_v9.xlsx`).
    - `orchestrator`: Szigorú ágenshatár-védelem (Boundary Enforcement), fázisok közötti kontextusátadás.
    - `documentation-writer`: 10-pontos CTM és PROSPERO-kompatibilis protokoll megírása.
  - **A 7 GP3 Protokoll Megfelelőségi Kapu (`src/validate_protocol.py`):**
    - Gate 1: PICO Címformula & PICO-szigor (formai definíció a linterben)
    - Gate 2: Szenvedés Narratíva (Patient, Family, Hope)
    - Gate 3: 6-pontos számszerűsített háttér
    - Gate 4: 3-domén keresési szintaxis & precedens indoklás
    - Gate 5: Poolozhatósági Kapu (≥3 tanulmány)
    - Gate 6: QUIPS / RoB 2 + Confounder Matrix + Multilevel RVE + Termális intervencióknál kötelező Cooling Index (COIN) ellenőrzés
    - Gate 7: T1–T4 transzlációs stádium és elkerülhető mortalitás
  - **Szabályzati Prioritási Lánc:** P0 (GEMINI.md) > P1 (AGENTS.md & MENTORS.md) > P2 (TM/ & Cochrane) > P3 (Workflows).

---

### 📄 `MENTORS.md` (Kanonikus Mentori Rendszer és Értékelési Szabályzat)
- **Helye:** `c:\Users\shuba\Desktop\Researcher - Dóri\MENTORS.md`
- **Fő tartalmi elemek:**
  - **Független Kettős Bírálat & Rekonciliáció Modellje:**
    - **1. Lépés: Független Vakbírálat (Independent Score Lock):** Hegyi és Garami egymástól szigorúan elzártan, külön kontextusban értékeli a kutatást. A kezdeti 1–10-es pontszámok azonnal zárolásra kerülnek (nem írhatók át utólag).
    - **2. Lépés: Explicit Rekonciliációs Kör (Reconciliation Round):** A mentorok megismerik egymás bírálatát, és reflektálnak a felmerült feszültségre. Ha véleményük finomodik, azt kizárólag Revíziós Addendumként rögzíthetik, explicit indoklással.
    - **3. Lépés: Szókratészi Kapu a Kutató számára:** 2–3 blokkoló kérdés feloldása a kutató által a Phase 5 megkezdése előtt.
  - **Mentor Hegyi (Transzlációs Medicina):**
    - Bedside First, Transzlációs Medicina Ciklus (Nature Med 2021), PubMed Paradoxon & Medicina GPS (J Clin Med 2020), Single Attackable Problem (SAP), Suffering Narrative, Üres Review megvetése.
    - **Kanonikus 4D Klinikai Mátrix:** 1. Hasznosság (Clinical Utility), 2. Megvalósíthatóság (Operational Feasibility), 3. Újszerűség (Novelty & Gap Filling), 4. Problémamegoldás (Problem-Solving Power). *(A PICO-szigort a linter kapu auditálja).*
  - **Mentor Garami (Élettan és Méréstan):**
    - Mechanizmus Mindenek Felett (Szolcsányi iskola), Sensor-Pathway-Effector Triád, Láz vs Hyperthermia, Kontrollcsoportok és környezeti hőmérséklet (Ta) szigora, Visszamelegítési sebesség (Rewarming Velocity).
    - **Kanonikus 4D Módszertani Mátrix:** 1. Mechanisztikus Megalapozottság (Mechanistic Plausibility), 2. Mérési Minőség és Standardizáció (Measurement Quality), 3. Heterogenitási Kockázatkezelés (Heterogeneity Risk Mitigation), 4. Torzítási Kockázat (Risk of Bias Exposure). *(A COIN dózist a linter kapu auditálja).*

---

## 2. MÓDOSÍTOTT RENDSZERFÁJLOK

### ✏️ `.agent/rules/GEMINI.md`
- **Változás:** Eltávolításra került a korábbi duplikált TIER 1 és TIER 2 szabályzat, és helyette közvetlen kanonikus hivatkozás került be az `AGENTS.md` és `MENTORS.md` fájlokra.
- **Session Start Protocol:** Kötelezővé teszi a `PROJECT.md` és az `AGENTS.md` & `MENTORS.md` beolvasását minden kutatási munkamenet elején.
- **Hierarchia:** Formalizálta a P0–P3 prioritási láncot.

### ✏️ `src/medbuddy.py`
- **Hiba:** Korábban a relatív gyökérből (`"hegyi_agent_profile.json"`) próbálta betölteni a profilokat, ami futásidejű `FileNotFoundError`-t okozott.
- **Javítás:** Beépítésre került a dinamikus, abszolút gyökérkönyvtár-képzés (`BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`), amely a valós `data/profiles/` almappából tölti be a profilokat.

### ✏️ `src/multi_agent_service.py` & `src/hegyi_rag_service.py`
- **Hiba:** A LangChain és Chroma konfiguráció relatív útvonalai hibára futottak más mappából való indításkor.
- **Javítás:** A `_get_config()` és a konfigurációs konstansok átálltak a script helyzetéhez viszonyított abszolút elérési útra a `data/profiles/` és a Chroma adatbázisok (`hegyi_chroma`, `garami_chroma`) eléréséhez.

---

## 3. ARCHIVÁLT FÁJLOK ÉS KÖNYVTÁRAK (NEM TÖRLÉS)

### 📦 Gyökér `agents/` könyvtár átmozgatása
- **Forrás:** `c:\Users\shuba\Desktop\Researcher - Dóri\agents\` (26 darab `.md` fájl)
- **Új Célhely:** `c:\Users\shuba\Desktop\Researcher - Dóri\.agent\archive\legacy-agents\`
- **Indoklás:** Megszüntette az elavult fájlokkal való párhuzamosságot és eltávolította a szoftverfejlesztési ágenseket (`frontend-specialist`, `backend-specialist`, `game-developer`, `database-architect`, `penetration-tester`, stb.) a gyökérből, megőrizve az összes korábbi leírást az archívumban.

---

## 4. SZÁNDÉKOSAN ÉRINTETLENÜL HAGYOTT TERÜLETEK (OUT OF SCOPE)

A felhasználói megbízásnak megfelelően az alábbi területekhez és fájlokhoz **egyáltalán nem nyúltunk**:
1. **`scratch/` könyvtár:** A 134 darab ad-hoc kísérleti Python script, teszt és lekérdezés-ablatió érintetlen maradt.
2. **`PROTOCOL.md`:** A gyökérben lévő integrált kutatási protokoll nem módosult.
3. **`meta_hyperglycaemia/` könyvtár:** A folyamatban lévő HIE-hiperglikémia metaanalízis protokoll-tervezete (`meta_analysis_protocol_PROSPERO.md`), az adatextrakciós Excel munkafüzetek és szűrési adatbázisok teljes mértékben változatlanok maradtak.
4. **`balasko/` könyvtár:** Az állatkísérletes metabolizmus- és hőmérséklet-elemzések érintetlenek maradtak.
5. **`results/` könyvtár:** Az eddigi szűrési eredmények és nyers adatbázis-exportok (pl. `neonatal_antibiotics/`) változatlanok maradtak.
