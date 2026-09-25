---
description: Phase 5 workflow — Protocol Compilation & Deterministic Linter. 10-chapter compilation, citation verification, compliance linting (score >= 70), and PRISMA-trAIce reporting.
---

# /phase-5-protocol — Protokoll Kompiláció & Determinisztikus Linter

> **Fázis:** Phase 5 a Kanonikus 5-Fázisú Kutatási Folyamatban  
> **Vezető Ágens:** `documentation-writer` (Lead Protocol Author)  
> **Kanonikus Szabályzat:** [AGENTS.md 3.5. & 4. Fejezet](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md)  
> **Releváns Módszertani Wiki Fejezetek:**  
> • [05. Protokoll Tervezés & PROSPERO Regisztráció](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/05_protocol_and_prospero.md)  
> • [10. GRADE Bizonyítékértékelés & 6-Mondatos Storytelling](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/10_grade_and_storytelling.md)  
> • [12. Cochrane Handbook v6.5 Részletes Referencia](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/12_cochrane_handbook_v6_5_reference.md)

---

## 1. Célkitűzés & Ágenshatárok

A Phase 5 feladata a korábbi négy fázis eredményeinek egységes, 10 fejezetből álló, nemzetközi folyóiratba benyújtható `PROTOCOL.md` vagy PROSPERO tervezetté formálása, determinisztikus kódokkal történő minőségellenőrzése és formális verziózása (`v1.0`).
- **Vezető felelős:** `documentation-writer` (orvosi szakírás, strukturálás, formázás).
- ⛔ **Ágenshatár:** A `documentation-writer` NEM változtathatja meg a Phase 4-ben zárolt PICO elemeket vagy a statisztikai tervet; az előző fázisok jóváhagyott adataiból dolgozik.

---

## 2. Műveleti Sorrend (Operational Steps)

1. **A 10 Fejezetes Protokoll Kompilációja:**
   - A végleges dokumentum összeállítása az [AGENTS.md 3.5](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) fejezeti struktúrája szerint:
     `1. Cím & PICO | 2. Racionálé & 3-as Szenvedés | 3. Célkitűzés | 4. Beválogatás/Kizárás | 5. Keresési Stratégia | 6. Válogatás & Adatkinyerés | 7. RoB Eszközök | 8. Szintézis & RVE | 9. GRADE | 10. Adminisztráció & Mentori Ellenjegyzés`.

2. **PMID Halucináció- és Idézettség Ellenőrzés:**
   - A protokollban szereplő hivatkozások valóságtartalmának ellenőrzése a PubMed API-val:
     ```bash
     python src/citation_verifier.py <elérési_út/PROTOCOL.md>
     ```
   - Minden hivatkozott PMID-nek valósnak és tematikailag illeszkedőnek kell lennie.

3. **Determinisztikus Protokoll Linter Futtatása:**
   - A dokumentum pontozása a 7 Kanonikus Megfelelőségi Kapu szerint:
     ```bash
     python src/validate_protocol.py <elérési_út/PROTOCOL.md>
     ```
   - ⚠️ **Megfelelőségi Küszöb:** A protokoll kötelezően el kell érje a **$\ge 70/100$ pontot** a release-hez az [AGENTS.md 4. Fejezet](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) kapurendszere szerint. Ha a pontszám alacsonyabb, a hibás kapuk javítása kötelező.

4. **PRISMA-trAIce Riport Létrehozása:**
   - Az AI felhasználás transzparens naplózása a PRISMA 2020 irányelvek szerint:
     ```bash
     python src/prisma_trace_reporter.py <elérési_út/PROTOCOL.md>
     ```

5. **Projekt Lezárása & Verziózás (`v1.0`):**
   - A végleges állapot és verziószám rögzítése a `data/project_state.json` állományban.

---

## 3. Záró Kapu & Determinisztikus Verifikáció

A kutatási protokoll elfogadása és élesítése az alábbi parancs hibátlan kimenetével válik hivatalossá:

```bash
python src/check_phase_gate.py --project <slug> --status
```

- **Siker feltétele:** Kilépési kód: `0` (Minden fázis [PASS], Linter $\ge 70$, hash érintetlen).
- **Végleges Termék:** Publikációkész `PROTOCOL.md` (v1.0).
