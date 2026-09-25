---
description: Phase 1 workflow — Bed-to-Bench Hypothesis & Suffering Narrative. Defines framework, canonical title, 3-part suffering narrative, and translation stage.
---

# /phase-1-hypothesis — Bed-to-Bench Hipotézis & Szenvedés

> **Fázis:** Phase 1 a Kanonikus 5-Fázisú Kutatási Folyamatban  
> **Vezető Ágens:** `research-sage` (Principal Investigator & Lead Scientist)  
> **Kanonikus Szabályzat:** [AGENTS.md 3.1. Fejezet (`research-sage`)](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md)  
> **Releváns Módszertani Wiki Fejezetek:**  
> • [01. A Transzlációs Medicina Modellje](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/01_translational_medicine_model.md)  
> • [02. Témaválasztás & A FINER Keretrendszer](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/02_topic_selection_finer.md)  
> • [03. Klinikai Kérdés Keretrendszerek & Tanulmánytervezés](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/03_clinical_question_frameworks.md)

---

## 1. Célkitűzés & Ágenshatárok

A Phase 1 feladata a klinikai probléma transzlációs hipotézissé formálása, a betegközpontú szenvedés számszerűsítése és a formális vizsgálati architektúra rögzítése.
- **Vezető felelős:** `research-sage` (tanulmánytervezés, hipotézisalkotás).
- ⛔ **Ágenshatár:** A `research-sage` ebben a fázisban NEM futtat bonyolult irodalmi keresést és NEM végez biostatisztikai kalkulációt (ezek a Phase 2 és Phase 3 feladatai).

---

## 2. Műveleti Sorrend (Operational Steps)

1. **Klinikai Kérdés Feltárása & Keretrendszer Kiválasztása:**
   - A kutatói ötlet besorolása a kérdés jellege alapján a 7 kanonikus keretrendszer egyikébe (PICO, PECO, PEO, PFO, CoCoPop, PCC, PICo) a [Wiki 03. Fejezet](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/03_clinical_question_frameworks.md) alapján.
   - A komponensek tételes rögzítése az [AGENTS.md 3.1.1](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) szabályai szerint.

2. **Kanonikus Címformula Generálása:**
   - A PICO elemekből képzett cím megfogalmazása szigorúan az [AGENTS.md 3.1.2](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) kötelező címformulája szerint.

3. **A 3-as Szenvedés Narratíva Kidolgozása:**
   - A klinikai hatás bemutatása a három kötelező dimenzióban (1. Beteg egyéni szenvedése és morbiditása, 2. Családi/társadalmi teher, 3. Klinikai remény és mérhető haszon) az [AGENTS.md 3.1.3](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) előírásai szerint.

4. **Transzlációs Stádium & Kerülhető Mortalitás:**
   - A kutatás besorolása a T1–T4 transzlációs skálán, valamint a kérdés megválaszolásával megelőzhető elhalálozások / szövődmények becslése az [AGENTS.md 3.1.4](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) és a [Wiki 01. Fejezet](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/01_translational_medicine_model.md) szerint.

5. **Projekt Állapot Rögzítése:**
   - A validált PICO és hipotézis elemek mentése a `data/project_state.json` állományba a `phase_1` blokk alá.

---

## 3. Záró Kapu & Determinisztikus Verifikáció

A fázis lezárása és a továbblépés KIZÁRÓLAG a determinisztikus linter sikeres lefutása után engedélyezett:

```bash
python src/check_phase_gate.py --project <slug> --target-phase 2
```

- **Siker feltétele:** Kilépési kód: `0` (Gate 1 és Gate 2 PASS).
- **Kimeneti dokumentum:** `hypothesis_and_suffering.md` az artifact könyvtárban.
- **Következő lépés:** [`/phase-2-search`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/.agent/workflows/phase-2-search.md) indítása.
