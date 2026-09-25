---
description: Phase 2 workflow — Systematic Search & 3-Step Search Key Building. Precedent analysis, query syntax, Boolean rules, live PubMed verification, and PROSPERO screening.
---

# /phase-2-search — Irodalmi Szigor & Keresőkulcs Építés

> **Fázis:** Phase 2 a Kanonikus 5-Fázisú Kutatási Folyamatban  
> **Vezető Ágens:** `lit-reviewer` (Systematic Search Expert)  
> **Kanonikus Szabályzat:** [AGENTS.md 3.2. Fejezet (`lit-reviewer`)](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md)  
> **Releváns Módszertani Wiki Fejezet:**  
> • [04. Szisztematikus Keresési Stratégia & Keresőkulcs Építés (CTM Guide v2.6)](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/04_systematic_search_key_guide.md)

---

## 1. Célkitűzés & Ágenshatárok

A Phase 2 feladata a szakterület szakirodalmi feltérképezése, a publikált precedens metaanalízisek keresőkulcsainak szisztematikus bányászata, a kanonikus keresési stringek megépítése és a fehér folt (white spot) élő bizonyítása.
- **Vezető felelős:** `lit-reviewer` (keresési stratégia, adatbázis-szintaxis, szűrés).
- ⛔ **Ágenshatár:** A `lit-reviewer` NEM ír klinikai bevezetőt és NEM dönt biostatisztikai poolozhatóságról (ez a Phase 1 és Phase 3 feladata).

---

## 2. Műveleti Sorrend (Operational Steps)

1. **6-Pontos Számszerűsített Háttérellenőrzés:**
   - A betegség epidemiológiájának, mortalitásának és a tudományos fehér foltnak a számszerű feltárása az [AGENTS.md 3.2.1](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) kötelező pontjai alapján.

2. **Precedens Metaanalízisek Elemzése (1. Lépés):**
   - Legalább 5–10 korábbi releváns metaanalízis keresőkulcsának begyűjtése és elemzése (MeSH/Emtree és szabadszavas kifejezések) az [AGENTS.md 3.2.2](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) szerint.  
   *(⚠️ Ha az elemzett precedensek száma < 10, kötelező az explicit indoklás rögzítése).*

3. **3-Lépcsős Keresőkulcs Felépítése (2–3. Lépés):**
   - A kanonikus 3 domén (`1. Populáció AND 2. Expozíció/Intervenció AND 3. Terápia/Kontextus`) szintaktikai megépítése a [Wiki 04. Fejezet (CTM Guide v2.6)](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/04_systematic_search_key_guide.md) szerint.
   - ⛔ **Boole 'NOT' Ellenőrzés:** A `NOT` operátor teljes hiányának kötelező ellenőrzése az [AGENTS.md 3.2.3](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) szerint.

4. **Élő PubMed Keresés & Eredmények Naplózása:**
   - A keresőkulcs futtatása a helyi keresőmotorral:
     ```bash
     python src/literature_search.py "<KERESŐKULCS>" --analyze --max-results 100 --years 5
     ```
   - Eredmények mentése és szűrése a `src/screen_literature.py` segítségével.

5. **PROSPERO Duplikáció-Szűrés & CitationChaser Tervezés:**
   - Annak igazolása a PROSPERO-ban, hogy nincs folyamatban lévő azonos protokoll; a CitationChaser másodlagos keresés előírása az [AGENTS.md 3.2.4](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) szerint.

6. **Projekt Állapot Frissítése:**
   - Keresőkulcsok, találati számok és precedensek rögzítése a `data/project_state.json` állományban.

---

## 3. Záró Kapu & Determinisztikus Verifikáció

A fázis lezárása és a továbblépés KIZÁRÓLAG a determinisztikus ellenőrzés sikere után engedélyezett:

```bash
python src/check_phase_gate.py --project <slug> --target-phase 3
```

- **Siker feltétele:** Kilépési kód: `0` (Gate 3 és Gate 4 PASS).
- **Kimeneti dokumentum:** `search_strategy_and_white_spot.md` az artifact könyvtárban.
- **Következő lépés:** [`/phase-3-feasibility`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/.agent/workflows/phase-3-feasibility.md) indítása.
