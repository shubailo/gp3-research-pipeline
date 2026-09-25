# GATE_ENFORCEMENT_PLAN.md — Antigravity-Natív Kapurendszer és Mentori Függetlenség Terve

> **Státusz:** Tervezet (Jóváhagyásra vár, kódmódosítás nélkül)  
> **Környezet:** Kizárólag Antigravity belső funkciók + meglévő Google Gemini Pro előfizetés  
> **Kizárt technológiák:** LangGraph, külső felhős orkesztrátorok, Claude / Anthropic API  
> **Dátum:** 2026-09-25  
> **Fájl elérési út:** `c:\Users\shuba\Desktop\Researcher - Dóri\GATE_ENFORCEMENT_PLAN.md`

---

## 1. DETERMINISZTIKUS GATE-CHECKER SCRIPT (`src/check_phase_gate.py`)

### 1.1 Célkitűzés & Alapelv
A kutatási fázisok (Phase 1–5) közötti átlépést nem az LLM jóindulatára vagy szubjektív ítéletére bízzuk. Ehelyett egy **tisztán determinisztikus, Python standard library-re épülő** ellenőrző scriptet vezetünk be.

- **0 db LLM API hívás** ➔ 100%-ban ingyenes, azonnali (<0.1 mp lefutás).
- **Konzol kilépési kódok (Exit Codes):**
  - `0`: Minden feltétel maradéktalanul teljesült ➔ **APPROVED (A fázisváltás engedélyezve)**.
  - `1`: Legalább egy feltétel hiányzik vagy sérült ➔ **BLOCKED (A fázisváltás letiltva + konkrét teendő-lista)**.

### 1.2 Bemeneti Állapotmodell (`data/project_state.json`)
A determinisztikus script a `data/project_state.json` állapotleíróból vagy a `PROJECT.md` strukturált YAML/Markdown blokkjaiból olvassa ki az objektív tényeket:

```json
{
  "project_id": "meta_hyperglycaemia",
  "current_phase": 3,
  "locked_hypothesis_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "phase_gates": {
    "gate_1_pico": {
      "pico_defined": true,
      "title_formula_valid": true,
      "suffering_narrative_present": true
    },
    "gate_2_literature": {
      "precedent_count": 8,
      "precedent_limit_justification": true,
      "boolean_not_used": false,
      "pubmed_verified": true
    },
    "gate_3_poolability": {
      "primary_outcome_name": "mortality_or_severe_disability",
      "identical_outcome_study_count": 4,
      "confounder_matrix_defined": true,
      "missing_covariates_under_30_pct": true
    },
    "gate_4_dual_mentor": {
      "hegyi_score_locked": true,
      "hegyi_timestamp": "2026-09-25T07:15:00Z",
      "garami_score_locked": true,
      "garami_timestamp": "2026-09-25T07:16:30Z",
      "reconciliation_round_completed": true,
      "socratic_questions_answered": true
    },
    "gate_5_protocol": {
      "protocol_file_exists": true,
      "linter_score": 85,
      "citation_verified": true
    }
  }
}
```

### 1.3 A Kapuk Szigorú Logikai Ellenőrzési Szabályai

| Célfázis | Fázisátlépés | Determinisztikus Logikai Feltételek (`Exit 0` követelmény) |
|---|---|---|
| **Phase 2** | 1 ➔ 2 | `pico_defined == True` ÉS `title_formula_valid == True` ÉS `suffering_narrative_present == True` |
| **Phase 3** | 2 ➔ 3 | `precedent_count >= 10` VAGY (`precedent_count >= 5` ÉS `precedent_limit_justification == True`) ÉS `boolean_not_used == False` |
| **Phase 4** | 3 ➔ 4 | **Poolability Gate:** `identical_outcome_study_count >= 3` ÉS `confounder_matrix_defined == True` ÉS `missing_covariates_under_30_pct == True` |
| **Phase 5** | 4 ➔ 5 | **Mentori Zárolási Kapu:** `hegyi_score_locked == True` ÉS `garami_score_locked == True` ÉS `reconciliation_round_completed == True` ÉS `socratic_questions_answered == True` |
| **Release** | 5 ➔ Kész | `linter_score >= 70` ÉS `citation_verified == True` |

### 1.4 CLI Interfész és Példa Kimenetek

```bash
# Futtatás terminálból:
python src/check_phase_gate.py --target-phase 4
```

- **Sikertelen futás kimenete (Kilépési kód: 1):**
  ```text
  ======================================================================
  🛑 GP3 PHASE GATE CHECK FAILED: Transition to Phase 4 is BLOCKED
  ======================================================================
  [FAIL] Gate 3.1 (Poolability): Identical outcome study count is 2 (Required: >= 3).
         Magyarázat: Legalább 3 primer tanulmánynak kell pontosan ugyanazt a végpontot mérnie.
  [PASS] Gate 3.2 (Confounders): Confounder Matrix is defined in protocol.
  [FAIL] Gate 3.3 (Missing Data): Covariate 'maternal_diabetes' reporting rate is 55% (< 70%).
         Teendő: Sorold át a változót narratív szintézisbe, tilos meta-regresszióba tenni!
  ======================================================================
  A rendszer nem léphet a Phase 4-be (Mentori bírálat). Javítsd a fenti pontokat!
  ```

- **Sikeres futás kimenete (Kilépési kód: 0):**
  ```text
  ======================================================================
  ✅ GP3 PHASE GATE CHECK PASSED: Transition to Phase 4 APPROVED
  ======================================================================
  Minden biostatisztikai és poolozhatósági feltétel teljesült.
  A Phase 4 (Független Kettős Mentori Bírálat) megkezdhető.
  ```

---

## 2. MENTOR-FÜGGETLENSÉG AZ ANTIGRAVITY MANAGER-BEN

### 2.1 A Probléma: Miért tarthatatlan az egymenetes LLM-szimuláció?
Amikor egyetlen Antigravity chat-ablakban kérjük az ágenstől, hogy: *"Most bírálja el Hegyi és Garami"*, a modell elkerülhetetlenül egyetlen összefüggő szövegfolyamot generál. 
- Garami szövegének generálásakor az LLM kontextus-ablakában már ott van Hegyi véleménye.
- Emiatt a modell szimulált egyetértést vagy teátrális párbeszédet gyárt, megszűnik a valódi függetlenség, és a biostatisztikai/élettani hibák átcsúsznak.

### 2.2 Az Antigravity-Natív Független Mentori Architektúra

```
                     [Phase 1-3 Állapot & Protokoll Kivonat]
                                       │
                  ┌────────────────────┴────────────────────┐
                  ▼                                         ▼
      ┌───────────────────────┐                 ┌───────────────────────┐
      │   TASK A: HEGYI TASK  │                 │  TASK B: GARAMI TASK  │
      │  (Teljesen izolált    │                 │ (Teljesen izolált     │
      │   Gemini kontextus)   │                 │  Gemini kontextus)    │
      │                       │                 │                       │
      │ • CSAK Hegyi perszóna │                 │ • CSAK Garami perszóna│
      │ • CSAK 4D CTM Mátrix  │                 │ • CSAK 4D Méréstan    │
      │ • Phase 1-3 Bemenet   │                 │ • Phase 1-3 Bemenet   │
      └───────────┬───────────┘                 └───────────┬───────────┘
                  │                                         │
                  ▼                                         ▼
      [data/reviews/hegyi.json]                 [data/reviews/garami.json]
         (ZÁROLT PONTSZÁM)                         (ZÁROLT PONTSZÁM)
                  │                                         │
                  └────────────────────┬────────────────────┘
                                       ▼
                      ┌─────────────────────────────────┐
                      │    ORCHESTRATOR / MANAGER       │
                      │  • Beolvassa mindkét fájlt      │
                      │  • Összefűzi a Rekonciliációhoz │
                      │  • Létrehozza a Szókratészi     │
                      │    kérdéseket a kutatónak       │
                      └─────────────────────────────────┘
```

### 2.3 Két Megvalósítási Út Antigravity-n Belül

#### Opció 1: Teljesen Automatikus Párhuzamos Háttér-Taskok (`run_command` + Python CLI)
Egyetlen parancs futtatásával az Orchestrator a háttérben elindít két különálló Python folyamatot a meglévő Gemini API kulcs használatával (`google.genai` / `gemini-2.0-flash`):
1. `python src/run_blind_mentor.py --mentor hegyi --input data/phase3_summary.json --output data/reviews/hegyi_locked.json`
2. `python src/run_blind_mentor.py --mentor garami --input data/phase3_summary.json --output data/reviews/garami_locked.json`

- **Miért 100%-ig független?** Két külön operációs rendszer szintű Python processz indul el, külön API hívással. Egyik sem látja a másik kimenetét.
- Mindkét script lefutása után JSON formátumban elmenti a 4 dimenziós pontszámot (1–10) és a szöveges indoklást a `data/reviews/` mappába.

#### Opció 2: Interaktív, Kézi Két-Task Indítás az Antigravity Chat Felületén
Ha a felhasználó az Antigravity UI-n belül, közvetlen chat-interakcióban szeretné a mentorokat futtatni:
1. **Lépés 1:** Nyiss egy **ÚJ chat-fülét (Task 1)** az Antigravity-ben.
   - Másold be a **Mentor Hegyi Minta-Promptot** (lásd 2.4).
   - A Hegyi task kiadja a pontokat, és elmenti a `data/reviews/hegyi_locked.json` fájlba.
2. **Lépés 2:** Ezzel párhuzamosan nyiss egy **MÁSIK független chat-fülét (Task 2)**.
   - Másold be a **Mentor Garami Minta-Promptot** (lásd 2.4).
   - A Garami task kiadja a pontokat, és elmenti a `data/reviews/garami_locked.json` fájlba.
3. **Lépés 3:** A fő Orchestrator szálban kiadott parancs:
   - *"Mindkét mentori bírálat lezárult. Indítsd a Rekonciliációs Kört a két mentori fájl alapján!"*

---

### 2.4 Konkrét Minta-Promptok a Független Taskokhoz

#### 🔴 Minta-Prompt A: Mentor Hegyi Task
```markdown
Szerepköröd: Prof. Dr. Hegyi Péter (Transzlációs Medicina Mentora).
Szabályzatod: Kizárólag a MENTORS.md 2. fejezete és a kanonikus 4D CTM Mátrix.
Korlátozás: Teljesen vakon bírálsz. Nem tudsz más bíráló véleményéről.

Feladatod: Értékeld az alábbi kutatási tervet a 4 kanonikus klinikai dimenzió mentén (1–10 skála):
1. Hasznosság (Clinical Utility)
2. Megvalósíthatóság (Operational Feasibility)
3. Újszerűség (Novelty & Gap Filling)
4. Problémamegoldás (Problem-Solving Power)

Kutatási Terv (Phase 1–3 Kivonat):
[IDE JÖN A PROTOKOLL / PROJECT.MD KIVONAT]

Kimeneti formátum:
Adj szigorú szöveges indoklást mind a 4 pontra, fogalmazz meg EGYETLEN kulcsfontosságú klinikai kérdést a kutatónak, majd zárd a választ az alábbi szigorú JSON blokkal:
```json
{
  "mentor": "hegyi",
  "scores": {
    "clinical_utility": <1-10>,
    "operational_feasibility": <1-10>,
    "novelty": <1-10>,
    "problem_solving": <1-10>
  },
  "overall_verdict": "APPROVED | REVISION_NEEDED | REJECTED",
  "socratic_question": "...",
  "locked": true
}
```
```

#### 🟡 Minta-Prompt B: Mentor Garami Task
```markdown
Szerepköröd: Dr. Garami András (Élettan és Méréstan Mentora).
Szabályzatod: Kizárólag a MENTORS.md 3. fejezete és a kanonikus 4D Módszertani Mátrix.
Korlátozás: Teljesen vakon bírálsz. Nem tudsz más bíráló véleményéről.

Feladatod: Értékeld az alábbi kutatási tervet a 4 kanonikus élettani dimenzió mentén (1–10 skála):
1. Mechanisztikus Megalapozottság (Sensor-Pathway-Effector triád)
2. Mérési Minőség és Standardizáció (Measurement Quality & Ta kontroll)
3. Heterogenitási Kockázatkezelés (Heterogeneity Risk Mitigation)
4. Torzítási Kockázat (Risk of Bias Exposure)

Kutatási Terv (Phase 1–3 Kivonat):
[IDE JÖN A PROTOKOLL / PROJECT.MD KIVONAT]

Kimeneti formátum:
Adj szigorú szöveges indoklást mind a 4 pontra, fogalmazz meg EGYETLEN kulcsfontosságú élettani/méréstani kérdést a kutatónak, majd zárd a választ az alábbi szigorú JSON blokkal:
```json
{
  "mentor": "garami",
  "scores": {
    "mechanistic_plausibility": <1-10>,
    "measurement_quality": <1-10>,
    "heterogeneity_mitigation": <1-10>,
    "risk_of_bias": <1-10>
  },
  "overall_verdict": "APPROVED | REVISION_NEEDED | REJECTED",
  "socratic_question": "...",
  "locked": true
}
```
```

---

## 3. GEMINI.md ÉS AGENTS.md SZABÁLY-KIEGÉSZÍTÉS

A szabályrendszerbe az alábbi kötelező tiltó és irányító szabályt fogalmazzuk meg:

### ⛔ Szabályszöveg-tervezet:
> ### ⛔ ABSZOLÚT TILOS AZ EGYMENETES MENTORI SZIMULÁCIÓ (SINGLE-CONTEXT MENTOR BAN)
>
> 1. **Tilos a szerepjátékos szimuláció:** A Phase 4 (Mentori Bírálat) SOHA, semmilyen körülmények között nem futtatható le egyetlen chat-válaszban, egyetlen beszélgetési kontextusban vagy közös üzenetváltásban "eljátszott" mentori párbeszédként.
> 2. **Kikényszerített elutasítás chatben:** Ha a felhasználó egy chat-üzenetben azt kéri: *"Bíráld el a tervet Hegyi és Garami szemével"*, az ágens köteles ezt **megtagadni**, és a következő szabványos választ adni:
>    > *"A CTM és GP3 minőségbiztosítási szabályzat értelmében a mentori bírálat nem szimulálható egyetlen kontextusban. Kérlek, futtasd a független bírálati folyamatot a két izolált párhuzamos taskban (CLI: `python src/run_blind_mentor.py` vagy a két külön Antigravity chat-fülön), hogy a bírálók ne befolyásolhassák egymást."*
> 3. **Determinisztikus előfeltétel:** A Phase 5 (protokoll-írás) megkezdése előtt KÖTELEZŐ lefutnia a `python src/check_phase_gate.py --target-phase 5` parancsnak. Ha a kilépési kód nem `0`, az ágens fizikailag nem írhat meg protokoll-tervezetet.

---

## 4. UTÓLAGOS PROTOKOLL-MÓDOSÍTÁS AUTOMATIKUS TRIGGERE

### 4.1 A Probléma
Gyakori hiba a kutatásokban: a kutató megkapja a mentori jóváhagyást a Phase 4-ben, majd a Phase 5 során csendben módosítja az elsődleges kimenetelt, szűkíti a populációt, vagy átírja a PICO-t — így a végleges cikk már nem arra az anyagra vonatkozik, amit a mentorok láttak.

### 4.2 A Megoldás: Determinisztikus Állapot-Hash (State Lock Hashing)
1. **Hash Képzés a Phase 4 Zárolásakor:**
   Amikor mindkét mentor lezárja a bírálatát, a `src/check_phase_gate.py` script kiszámítja a fundamentális kutatási definíciók SHA-256 lenyomatát:
   $$Hash = \text{SHA256}(\text{PICO} + \text{Elsődleges Kimenetel} + \text{Inklúziós Feltételek})$$
   Ez a lenyomat elmentésre kerül a `data/project_state.json` `locked_hypothesis_hash` mezőjébe.

2. **Automatikus Trigger Utólagos Módosításkor:**
   Bármikor, amikor a felhasználó vagy egy ágens módosítani kívánja a `PROJECT.md`-t vagy a `PROTOCOL.md`-t:
   - A `check_phase_gate.py` script ellenőrzi a jelenlegi szöveg hash-ét a mentett `locked_hypothesis_hash`-sel.
   - Ha a lenyomat **eltér**, a script azonnal **invalidálja a Phase 4 állapotot** (`hegyi_score_locked = False`, `garami_score_locked = False`), és a következő üzenettel blokkol:

> ⚠️ **KRITIKUS VÁLTOZTATÁSI RIASZTÁS:**  
> *"Ez a módosítás a korábban mentori jóváhagyást kapott fundamentális elemet (PICO / Elsődleges Kimenetel) érinti! A változtatás miatt a meglévő mentori pontszámok érvényüket vesztették. A módosítás élesítéséhez kötelező a Phase 4 független kettős bírálat (Hegyi + Garami) újbóli lefutása."*

3. **Beépítés a GEMINI.md-be:**
   A rendszer-utasítás rögzíti: az ágens semmilyen Phase 5-ös szerkesztést nem hajthat végre, ha a hash-ellenőrzés integritási hibát jelez.

---

## 5. ERŐFORRÁS- ÉS KÖLTSÉGBECSLÉS

| Elem | Szükséges Eszköz / API | Költség / Erőforrás-igény | Magyarázat |
|---|---|---|---|
| **Gate-Checker Script** (`check_phase_gate.py`) | Python 3 standard library | **0 Ft (Ingyenes)** | Semmilyen hálózati kérést vagy AI-t nem használ; azonnali futás. |
| **Párhuzamos Mentor Bírálat** | Meglévő Google Gemini Pro / Flash | **0 Ft extra költség** | A felhasználó meglévő előfizetési kvótáján belül fut, az Antigravity IDE beépített modell-hozzáférésével vagy ingyenes AI Studio kulccsal. |
| **Állapot-kezelés & Hashing** | JSON fájlok a `data/` mappában | **0 Ft (Lokális tárhely)** | Semmilyen külső adatbázis vagy felhős állapotkezelő (pl. LangSmith, Redis) nem szükséges. |
| **Külső API igény** | Anthropic / OpenAI / LangGraph | **NEM SZÜKSÉGES (0 db)** | A teljes architektúra 100%-ban zártan, az Antigravity ökoszisztémán belül marad. |

---

## 6. ÖSSZEFOGLALÓ JAVASLAT ÉS JÓVÁHAGYÁSI DÖNTÉSI PONTOK

Kérlek, vizsgáld meg a fenti tervet, és jelezd az alábbi döntéseket:
1. **Gate-checker formátum:** Elfogadod-e a `data/project_state.json` alapú állapot-követést a `check_phase_gate.py`-hoz?
2. **Mentor-futtatási mód preferenciája:**
   - **Opció 1:** Automatikus háttér-CLI futtatás (egyetlen parancs indítja mindkét mentort izoláltan a háttérben a Gemini API-val).
   - **Opció 2:** Kézi indítás két különálló Antigravity chat-fülön a minta-promptok bemásolásával.
3. **Szabályzat és Hash-zár:** Jóváhagyod-e a `Single-Context Mentor Ban` szabály beépítését a `GEMINI.md`-be és az SHA-256 állapot-zár bevezetését?
