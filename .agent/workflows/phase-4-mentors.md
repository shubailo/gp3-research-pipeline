---
description: Phase 4 workflow — Independent Dual Mentor Review & Reconciliation. Hegyi 4D Matrix, Garami 4D Matrix, Single-Context Ban enforcement, Socratic questions, and SHA-256 state locking.
---

# /phase-4-mentors — Független Kettős Mentori Bírálat & Rekonciliáció

> **Fázis:** Phase 4 a Kanonikus 5-Fázisú Kutatási Folyamatban  
> **Vezető Mentorok:** `mentor-hegyi` (Klinikai Transzláció) & `mentor-garami` (Élettani Méréstan)  
> **Kanonikus Szabályzat:** [MENTORS.md](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/MENTORS.md) és [AGENTS.md 5.3 & 5.4. Fejezet](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md)  
> **Releváns Módszertani Wiki Fejezetek:**  
> • [01. A Transzlációs Medicina Modellje](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/01_translational_medicine_model.md)  
> • [11. A CTM 22-Lépéses Mester Munkafolyamat & Moodle](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/11_ctm_22_step_master_workflow.md)

---

## 1. ⛔ P0 Alapszabály: Egymenetes Mentori Szimuláció Tilalma (Single-Context Mentor Ban)

Szigorúan tilos a Phase 4-et egyetlen csevegési ablakban, szimulált párbeszédként lefolytatni!
A két mentor független bírálata **fizikailag két külön Antigravity chat-fülön** futtatandó:
- **Hegyi Chat Fül:** Prompt: [`docs/mentor_prompts/hegyi_task_prompt.md`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/docs/mentor_prompts/hegyi_task_prompt.md)
- **Garami Chat Fül:** Prompt: [`docs/mentor_prompts/garami_task_prompt.md`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/docs/mentor_prompts/garami_task_prompt.md)

---

## 2. Műveleti Sorrend (Operational Steps)

1. **1. Lépés: Független, Zárolt Pontozás (Independent Locked Scoring):**
   - Mindkét mentor önállóan értékeli a kutatást a [MENTORS.md 2. és 3. Fejezete](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/MENTORS.md) szerinti saját 4D mátrixában (1–10 skála doménenként):
     - **Mentor Hegyi 4D:** Klinikai Hasznosság, Megvalósíthatóság, Újszerűség, Problémamegoldó Képesség.
     - **Mentor Garami 4D:** Élettani Mechanizmus, Mérés Minősége, Heterogenitás-védelem, Torzítás elleni Védelem.
   - A pontok zárolásra kerülnek a `data/project_state.json` állományban (`hegyi_score_locked = true`, `garami_score_locked = true`).

2. **2. Lépés: Explicit Rekonciliációs Kör:**
   - A mentorok kölcsönösen megismerik egymás értékelését és reflexiót fogalmaznak meg a [MENTORS.md 4. Fejezete](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/MENTORS.md) szerint.
   - ⚠️ A kezdeti pontszámok utólag NEM írhatók át; kizárólag szakmai konszenzus vagy fenntartás rögzíthető.

3. **3. Lépés: Blokkoló Szókratészi Kérdések Megválaszolása:**
   - A mentorok által feltett 2–3 nehéz klinikai/módszertani kérdésre a kutatónak érdemi, részletes választ kell adnia. A válaszok bekerülnek a jegyzőkönyvbe.

4. **4. Lépés: SHA-256 Állapot-Zár (Locked Hypothesis Hash):**
   - A bírálat jóváhagyásakor a PICO és a primer kimenetel kriptográfiai lenyomata (`locked_hypothesis_hash`) rögzítésre kerül az [AGENTS.md 5.4](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) szerint. Bármilyen utólagos módosítás azonnal érvényteleníti a Phase 4 jóváhagyást.

---

## 3. Záró Kapu & Determinisztikus Verifikáció

A fázis lezárása és a protokoll-írás megkezdése KIZÁRÓLAG a determinisztikus kapu sikere után engedélyezett:

```bash
python src/check_phase_gate.py --project <slug> --target-phase 5
```

- **Siker feltétele:** Kilépési kód: `0` (Hegyi és Garami pontok zárolva, rekonciliáció kész, szókratészi válaszok megadva, hash egyezik).
- **Kimeneti dokumentum:** `mentor_evaluation_and_reconciliation.md`.
- **Következő lépés:** [`/phase-5-protocol`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/.agent/workflows/phase-5-protocol.md) indítása.
