# MIGRATION_PLAN.md — Konszolidációs és Migrációs Terv

> **Státusz:** Jóváhagyásra váró tervezet (LÉPÉS 1)  
> **Szabályzat:** Nincs törlés vagy felülírás a jóváhagyásig. A `scratch/`, `PROTOCOL.md` és `meta_hyperglycaemia/` területek érintetlenek maradnak.  
> **Dátum:** 2026-09-25  
> **Cél:** A fragmentált szabályok és mentori logikák egységesítése a kanonikus `AGENTS.md` és `MENTORS.md` fájlokba, valamint a duplikált fájlstruktúra megtisztítása.

---

## 1. TARTALMI TÉRKÉP (CONTENT MAP)

Az alábbi táblázat pontosan rögzíti, hogy a meglévő szétszórt fájlok mely tartalmi elemei hova kerülnek át a migráció során.

| Forrásfájl és Elérési Út | Tartalmi Elem / Szabályzat | Célfájl | Indoklás & Művelet |
|---|---|---|---|
| `.agent/rules/GEMINI.md` | Globális protokollok, Request Classifier, Socratic Gate, Universal Rules. | **`GEMINI.md` (karcsúsítva)** | Megmarad a belépési kapunak, de a mentori és kutatási szabályokat nem duplikálja, hanem linkeli az `AGENTS.md` és `MENTORS.md` felé. |
| `.agent/ARCHITECTURE.md` | A 6 kutatási ágens definíciója, 7 compliance kapu, CTM prioritási lánc. | **`AGENTS.md`** | Alapvető referencia az orvosi kutatási pipeline architektúrájához. |
| `.agent/agents/research-sage.md` | PI szerepkör, PICO címformula, Szenvedés Narratíva, FINER, T1-T4 audit. | **`AGENTS.md`** | A Principal Investigator ágens kanonikus specifikációja. |
| `.agent/agents/lit-reviewer.md` | 6-pontos háttérellenőrzés, 3-lépcsős keresőkulcs, 'NOT' tilalom, CitationChaser. | **`AGENTS.md`** | A szisztematikus keresési szakértő kanonikus szabályai. |
| `.agent/agents/feasibility-judge.md` | Hiányzó változók (<70%), ökológiai torzítás tilalma, PROSPERO előzetes szűrés. | **`AGENTS.md`** | A megvalósíthatósági szakértő szabályrendszere. |
| `.agent/agents/meta-analyzer.md` | Poolability Gate (≥3 azonos végpontú tanulmány), Confounder Matrix, RoB eszközök, Multilevel RVE, CTM BoostR tisztítási szabályok. | **`AGENTS.md`** | A biostatisztikus és szintézis ágens kanonikus szabályrendszere. |
| `.agent/agents/orchestrator.md` | Fázis-átmenetek, ágenshatárok védelme (Boundary Enforcement), szintézis. | **`AGENTS.md`** | Az orkesztrátor vezérlési szabályai és hatásköre. |
| `.agent/agents/mentor-hegyi.md` | Prof. Hegyi autentikus perszónája, Bedside First, SAP, PubMed Paradoxon, T1-T4, 1-10 Klinikai Mátrix. | **`MENTORS.md`** | Mentor Hegyi kanonikus definíciója és mentori szabályai. |
| `.agent/agents/mentor-garami.md` | Dr. Garami autentikus perszónája, Thermal Logic, Sensor-Pathway-Effector triád, COIN index, Ta kontroll, 1-10 Módszertani Mátrix. | **`MENTORS.md`** | Mentor Garami kanonikus definíciója és élettani szabályai. |
| `notebook_sources/hegyi_persona.md` & `hegyi_workflow.md` | Szókratészi stílusjegyek, tipikus kérdések, 5-fázisú PhD hallgatói munkafolyamat. | **`MENTORS.md`** | Integrálva Hegyi mentorálási és kérdezési protokolljába. |
| `notebook_sources/garami_persona.md` & `garami_workflow.md` | Fogalmi szigor (láz vs hyperthermia), effektorvázlat tervezés, hallgatói lépések. | **`MENTORS.md`** | Integrálva Garami élettani és módszertani protokolljába. |
| `notebook_sources/hegyi_rubric.md` | Transzlációs kör táblázat, hallgatói feladatsablon. | **`MENTORS.md`** | A mentori rubrikák és értékelő sablonok fejezetbe kerül. |
| `notebook_sources/garami_rubric.md` | Élettani mechanizmus sablon, COIN számítási szabályok. | **`MENTORS.md`** | A mentori rubrikák és élettani ellenőrző listák közé kerül. |
| `data/profiles/hegyi_agent_profile.json` & `garami_agent_profile.json` | JSON értékelési dimenziók, kulcsszavak, absztrakt kontextusok. | **`MENTORS.md`** (és frissített JSON) | A pontozási definíciók beépülnek a `MENTORS.md`-be, a JSON fájlok a helyükön maradnak a Python RAG számára. |
| `notebook_sources/scientific_workflow.md` | A kutatástervezés 4-fázisú alapelve és kritikus standardjai. | **`AGENTS.md`** | Az ágensek együttműködési protokolljának törzse. |
| `PROJECT.md` (1–22. és 317–337. sor) | Állapotkezelési kötelezettség, Globális szabályok emlékeztetője (P0–P3 prioritási lánc, PROSPERO kötelezettség, Poolability). | **`AGENTS.md` & `PROJECT.md`** | A szabályok beépülnek az `AGENTS.md`-be, a `PROJECT.md` megtartja tiszta állapotkezelő funkcióját. |

---

## 2. KONFLIKTUSLISTA (DÖNTÉST IGÉNYLŐ PONTOK)

Az audit során 5 konkrét helyen találtunk eltérő vagy ellentmondó definíciókat a fájlok között. Ezeket **nem oldjuk fel önhatalmúlag**, kérjük a felhasználó választását:

### ❓ Konfliktus 1: Mentor Hegyi Értékelő Mátrix Dimenziói
- **Változat A (4 Dimenziós CTM Mátrix):**  
  *Forrás:* `.agent/agents/mentor-hegyi.md`, `.agent/workflows/research.md`, `notebook_sources/hegyi_rubric.md`  
  *Dimenziók:*
  1. Hasznosság / Klinikai Hasznosság (Utility)
  2. Megvalósíthatóság (Feasibility)
  3. Újszerűség (Novelty & Gap Filling)
  4. Problémamegoldó erő / Guideline hatás (Problem Solving)
- **Változat B (5 Dimenziós Profil Mátrix):**  
  *Forrás:* `data/profiles/hegyi_agent_profile.json`, `docs/claude_assessment.md`  
  *Dimenziók:*
  1. Klinikai relevancia
  2. **PICO Szigor / Precizitás** *(Önálló pontozott dimenzióként)*
  3. Tudományos rés (Novelty)
  4. Transzlációs érték (T0–T4)
  5. Adatminőség és megvalósíthatóság
- 👉 **Kérdés:** A 4 dimenziós standard CTM mátrixot tartsuk meg a `MENTORS.md`-ben (Változat A), VAGY az 5 dimenziós változatot, amely külön pontozza a PICO szigort (Változat B)?

---

### ❓ Konfliktus 2: Mentor Garami Értékelő Mátrix Dimenziói
- **Változat A (4 Dimenziós Módszertani Mátrix):**  
  *Forrás:* `.agent/agents/mentor-garami.md`, `.agent/workflows/research.md`  
  *Dimenziók:*
  1. Élettani / Mechanisztikus Megalapozottság (Mechanistic Plausibility)
  2. Mérési Minőség és Standardizáció (Measurement Quality - telemetria, Ta kontroll)
  3. Heterogenitási Kockázatkezelés (Heterogeneity Risk Mitigation - I² védelem)
  4. Torzítási Kockázat (Risk of Bias Exposure - kontrollcsoport, hiányzó adatok)
- **Változat B (5 Dimenziós Profil Mátrix):**  
  *Forrás:* `data/profiles/garami_agent_profile.json`  
  *Dimenziók:*
  1. Élettani alapozottság
  2. Módszertani precizitás
  3. **Terápiás relevancia (COIN dózis)** *(Önálló pontozott dimenzióként)*
  4. Innováció mechanizmusban
  5. Kutatási realitás / megvalósíthatóság
- 👉 **Kérdés:** Dr. Garami mátrixában a 4 dimenziós szigorú biostatisztikai/élettani mátrixot alkalmazzuk (Változat A), VAGY az 5 dimenziós, COIN-fókuszú profilt (Változat B)?

---

### ❓ Konfliktus 3: Mentorok Viszonya: Dialektikus Cross-Talk vs. Független Bírálat
- **Változat A (Független Kettős Bírálat - Ajánlott):**  
  *Forrás:* `notebook_sources/scientific_workflow.md`  
  *Működés:* Hegyi és Garami **egymástól függetlenül, külön kontextusban** értékeli a kutatási tervet. Egyikük sem látja a másik pontszámait a saját értékelése előtt. A felmerülő ellentmondásokat (pl. klinikai sürgősség vs. mérési precizitás) nem ők játsszák el egymás között, hanem kérdésként intézik a kutatóhoz/hallgatóhoz, akinek szintézist kell alkotnia.
- **Változat B (Szimulált Dialektikus Vita / Cross-Talk):**  
  *Forrás:* `.agent/workflows/research.md` (Phase 4), `.agent/agents/mentor-hegyi.md`  
  *Működés:* Megmarad a 2-fordulós koreografált vita: Round 1 (Hegyi klinikai vízió vs Garami élettani szigor), Round 2 (Hegyi és Garami közvetlen vitája egymással: *"András, nézd a klinikai realitást..."*).
- 👉 **Kérdés:** Melyik modellt rögzítsük kanonikusként a `MENTORS.md`-ben: a valódi független kettős bírálatot (Változat A), vagy a szimulált dialektikus párbeszédet (Változat B)?

---

### ❓ Konfliktus 4: A Munkafolyamat Fázisszámozása: 4-Fázisú vs. 5-Fázisú
- **Változat A (5-Fázisú Modell - Ajánlott):**  
  *Forrás:* `.agent/ARCHITECTURE.md`, `.agent/workflows/research.md`  
  *Struktúra:*
  - Phase 1: Hipotézis & Szenvedés Narratíva (`research-sage`)
  - Phase 2: Keresési Stratégia & 3-Step Search Key (`lit-reviewer`)
  - Phase 3: Megvalósíthatóság & Poolozhatóság (`feasibility-judge` + `meta-analyzer`)
  - Phase 4: Mentori Értékelés & Szókratészi Kapuk (`mentor-hegyi` + `mentor-garami`)
  - **Phase 5: Protokoll Kompiláció & Linter Ellenőrzés** (`documentation-writer` + `validate_protocol.py`)
- **Változat B (4-Fázisú Modell):**  
  *Forrás:* `notebook_sources/scientific_workflow.md`  
  *Struktúra:* A protokoll-összeállítás nem képez önálló fázist, hanem a Phase 4 (Socratic Gates) záró aktusa.
- 👉 **Kérdés:** Az 5-fázisú modellt rögzítsük kanonikusként az `AGENTS.md`-ben, ahol a protokoll összeállítása és linteres validálása önálló Phase 5-ként szerepel?

---

### ❓ Konfliktus 5: Keresési Precedensek Minimális Száma
- **Változat A (Szigorú: ≥10 metaanalízis):**  
  *Forrás:* `.agent/agents/lit-reviewer.md` (32. sor), `.agent/workflows/plan.md` (46. sor)  
  *Szabály:* Kötelező legalább 10 korábban publikált metaanalízis keresőkulcsát elemezni az új keresési kulcs felépítése előtt.
- **Változat B (Megengedő: 5–10 metaanalízis):**  
  *Forrás:* `.agent/workflows/research.md` (71. sor), `.agent/workflows/feasibility.md` (42. sor)  
  *Szabály:* Legalább 5–10 korábbi metaanalízis keresőkulcsának áttekintése elegendő.
- 👉 **Kérdés:** Mi legyen a kötelező CTM minimum a `lit-reviewer` számára: szigorúan legalább 10 metaanalízis (Változat A), vagy a ritkább szakterületeken életszerűbb 5–10 metaanalízis (Változat B)?

---

## 3. REDUNDANCIA-LISTA ÉS ARCHIVÁLÁSI TERV

### A Jelenlegi Helyzet Elemzése
- A gyökérben lévő `agents/` mappa (26 darab `.md` fájl) párhuzamosan létezik a `.agent/agents/` mappával (14 darab `.md` fájl).
- A gyökér `agents/` mappa az alábbi felesleges szoftverfejlesztési ágenseket tartalmazza, amelyek nem tartoznak a transzlációs orvosi kutatástervezéshez:
  - `backend-specialist.md`, `frontend-specialist.md`, `database-architect.md`
  - `game-developer.md`, `mobile-developer.md`
  - `penetration-tester.md`, `security-auditor.md`, `seo-specialist.md`
  - `test-engineer.md`, `qa-automation-engineer.md`, `performance-optimizer.md`, `devops-engineer.md`
- Továbbá a gyökér `agents/` mappában lévő `lit-reviewer.md` és `meta-analyzer.md` elavult, régebbi verzió, ami hiányos utasításokat tartalmaz a `.agent/agents/` verziókhoz képest.

### Végrehajtási Javaslat a 2. Lépésben (NEM TÖRLÉS, HANEM ARCHIVÁLÁS):
1. Létrehozzuk a `.agent/archive/legacy-agents/` könyvtárat.
2. A teljes gyökér `agents/` mappát **átmozgatjuk** a `.agent/archive/legacy-agents/` mappába.
3. Így semmilyen adat vagy korábbi prompt nem vész el, de a gyökér könyvtár letisztul, és az AI ágensrendszer nem fog tévesen elavult szoftverfejlesztői ágensleírásokat betölteni.

---

## 4. ELÉRÉSI ÚT HIBA ÉS JAVÍTÁSI TERV (PYTHON RAG & CLI)

### A Hiba Leírása
A `src/medbuddy.py` (45–48. sor) és a `src/multi_agent_service.py` (70. és 75. sor) a relatív gyökérből próbálja betölteni a profilokat:
```python
# JELENLEGI HIBÁS KÓD:
paths = {
    "hegyi": "hegyi_agent_profile.json",
    "garami": "garami_agent_profile.json"
}
```
Mivel ezek a fájlok a valóságban a `data/profiles/` mappában találhatók (`data/profiles/hegyi_agent_profile.json` és `data/profiles/garami_agent_profile.json`), a scriptek indításkor `FileNotFoundError` hibát dobnak.

### Javasolt Javítás (2. Lépésben, jóváhagyás után)

A scriptekben robusztus, abszolút fájlútvonal-képzést alkalmazunk a script helyzetéhez (`__file__`) viszonyítva:

#### 1. Javítás a `src/medbuddy.py`-ban:
```python
# JAVÍTOTT KÓD:
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES_DIR = os.path.join(BASE_DIR, "data", "profiles")

paths = {
    "hegyi": os.path.join(PROFILES_DIR, "hegyi_agent_profile.json"),
    "garami": os.path.join(PROFILES_DIR, "garami_agent_profile.json")
}
```

#### 2. Javítás a `src/multi_agent_service.py`-ban:
```python
# JAVÍTOTT KÓD:
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES_DIR = os.path.join(BASE_DIR, "data", "profiles")

def _get_config(self, agent_id):
    configs = {
        "hegyi": {
            "name": "Prof. Hegyi Péter",
            "profile_file": os.path.join(PROFILES_DIR, "hegyi_agent_profile.json"),
            "vector_db": os.path.join(BASE_DIR, "hegyi_chroma")
        },
        "garami": {
            "name": "Dr. Garami András",
            "profile_file": os.path.join(PROFILES_DIR, "garami_agent_profile.json"),
            "vector_db": os.path.join(BASE_DIR, "garami_chroma")
        }
    }
    return configs.get(agent_id, configs["hegyi"])
```

---

## 5. MIT NEM ÉRINT EZ A LÉPÉS (ÉRINTETLEN TERÜLETEK)

A feladat meghatározása szerint a következő elemek szigorúan érintetlenek maradnak:
1. **`scratch/` könyvtár:** A benne lévő 134 kísérleti Python scripthez, teszthez és lekérdezés-ablatióhoz nem nyúlunk.
2. **`PROTOCOL.md`:** A gyökérben lévő integrált kutatási protokoll nem módosul.
3. **`meta_hyperglycaemia/` könyvtár:** Az aktív metaanalízis protokollja (`meta_analysis_protocol_PROSPERO.md`), szűrési adatai (`screening_decisions_review.xlsx`) és extrakciós táblái teljes egészében érintetlenek maradnak.
4. **`balasko/` könyvtár:** Az állatkísérletes metabolizmus- és hőmérséklet-adatok érintetlenek maradnak.
5. **`results/` könyvtár:** Az eddigi szűrési és irodalomkeresési kimenetek (pl. `neonatal_antibiotics/`) változatlanok maradnak.

---

## 6. A JÓVÁHAGYÁSRA VÁRÓ DÖNTÉSI MÁTRIX

Kérjük a felhasználót, hogy az alábbi 5 pontban jelölje meg a döntését a végrehajtás (LÉPÉS 2) előtt:

| Konfliktus Pont | Választható Opció 1 | Választható Opció 2 | Javaslat |
|---|---|---|---|
| **1. Hegyi Mátrix** | **Opció 1A:** 4 dimenziós CTM (Utility, Feasibility, Novelty, Problem Solving) | **Opció 1B:** 5 dimenziós JSON (Relevancia, PICO Szigor, Gap, Transzláció, Feasibility) | **Opció 1A** (Összhangban a CTM standarddal) |
| **2. Garami Mátrix** | **Opció 2A:** 4 dimenziós módszertani (Mechanisztikus ok, Mérésminőség, Heterogenitás, Torzítás) | **Opció 2B:** 5 dimenziós JSON (Élettan, Módszertan, COIN dózis, Innováció, Realitás) | **Opció 2A** (Szigorúbb biostatisztikai védelem) |
| **3. Mentorok Viszonya** | **Opció 3A:** Független kettős vakbírálat (külön kontextus, nincs előreírt párbeszéd) | **Opció 3B:** Dialektikus vita (Hegyi és Garami színpadias dialógusa egymással) | **Opció 3A** (Megszünteti a kontextustorzulást) |
| **4. Munkafolyamat Fázisai** | **Opció 4A:** 5-Fázisú modell (önálló Phase 5 protokoll kompilációval és linterrel) | **Opció 4B:** 4-Fázisú modell (a protokollírás a Phase 4 része) | **Opció 4A** (Egyértelmű felelősség és kapu) |
| **5. Precedens Szám** | **Opció 5A:** Szigorú minimum 10 korábbi metaanalízis | **Opció 5B:** Életszerűbb 5–10 korábbi metaanalízis | **Opció 5B** (Megvalósíthatóbb szűk témáknál) |

> 🛑 **KÖVETKEZŐ LÉPÉS:**  
> A fenti 1–5. pontok jóváhagyása és kiválasztása után indulhat a **LÉPÉS 2: VÉGREHAJTÁS** (az `AGENTS.md` és `MENTORS.md` létrehozása, a `GEMINI.md` frissítése, a gyökér `agents/` archiválása, és a Python elérési utak javítása).
