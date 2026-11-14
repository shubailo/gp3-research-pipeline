---
description: "Hibrid 2-szintű NLP és LLM szisztematikus absztrakt-szűrés (Rayyan-szerű ranking + Tier 2 LLM audit a false-negative hibák kizárására)."
---

# /screening-nlp — Hibrid NLP & LLM Absztrakt-Szűrés

> **Fázis:** Phase 2 (Irodalomkutatás & Szűrés) / CTM PRISMA Screening  
> **Vezető Ágens:** `lit-reviewer` (Systematic Search & Screening Specialist)  
> **Szabvány:** Cochrane Handbook v6.5 Ch. 4 · PRISMA 2020 · CTM 21-Step Workflow Step 6  
> **Eszköz:** `python src/ai_screener.py --project <slug> [--threshold 0.15]`

---

## 1. Célkitűzés & Módszertani Elv

A szisztematikus áttekintésekben a legnagyobb metodológiai kockázat a **téves kizárás (false negative bias)**: amikor egy klinikailag releváns tanulmány véletlenül a több ezer kizárt tétel (`EXCLUDE`) közé keveredik.

Ez a workflow egy Rayyan-szerű, 2-lépcsős aktív tanulási modellt valósít meg:
1. **Tier 1 (Determinisztikus TF-IDF motor):** A már biztosan beválogatott (`INCLUDE`) tanulmányok szövegeiből képez súlyozott profilvektort (centroidot), és koszinusz-hasonlóság alapján rangsorolja az összes kizárt rekordot.
2. **Tier 2 (AI/LLM közvetlen felülvizsgálat):** A kutató / Antigravity LLM közvetlenül elolvassa a határesetek (`score >= threshold`) absztraktját, kizárva a vak automatizációt, és pontosítja a döntést vagy indoklást.

---

## 2. Műveleti Lépések (Operational Flow)

### 1. Lépés: Tier 1 Rangsorolás Futtatása

Futtasd a projekt screening adatbázisára a modellt:

```bash
# Alapértelmezett küszöbérték (0.10 - konzervatív, teljes határeset-lefedettség):
python src/ai_screener.py --project <project_slug> --threshold 0.10

# Szigorúbb fókusz (0.20 feletti magas prioritású határesetek):
python src/ai_screener.py --project <project_slug> --threshold 0.20
```

**Kimenetek a `scratch/` mappában:**
- `ranked_exclude_candidates.csv`: Minden kizárt rekord hasonlósági sorrendben
- `tier2_review_queue.csv`: Kizárólag a küszöbérték feletti határesetek

---

### 2. Lépés: Tier 2 LLM Határeset-Audit (Slow & Steady)

Az LLM / kutató tételesen áttekinti a várólistát (`tier2_review_queue.csv`):
- **Cím és absztrakt vizsgálata a projekt PICO/PECO kritériumai alapján.**
- Ha az absztrakt nem zárja ki egyértelműen a bevonást (pl. nem derül ki a hipotermia státusz) ➔ **`MAYBE (Kérdőjel)`** kategóriába mozgatás full-text ellenőrzésre (*in dubio pro inclusione*).
- Ha egyértelműen kizárandó ➔ `EXCLUDE` marad, de az indoklást orvosilag precízen rögzíteni kell (copy-paste szövegek eliminálása).

---

### 3. Lépés: Adatbázis & PRISMA Frissítés

Ha módosítás történik:
1. A projekt kanonikus CSV állományának frissítése (`projects/<project>/data/CTM_Screening_Decisions_*.csv`).
2. Az Excel döntési segédlet szinkronizálása:
   ```bash
   python scratch/sync_excel_after_tier2.py
   ```
3. A PRISMA Flow Report számainak frissítése (`projects/<project>/results/PRISMA_FLOW_REPORT_*.md`).

---

## 3. Determinisztikus Verifikáció & Kapu-Ellenőrzés

A szűrési revízió után kötelező a protokoll validátor és fáziskapu futtatása:

```bash
python src/validate_protocol.py projects/<project>/data/meta_analysis_protocol_PROSPERO.md
```

- **Elvárt eredmény:** 100/100 APPROVED, a PICO és PRISMA számok konzisztensek maradnak.

