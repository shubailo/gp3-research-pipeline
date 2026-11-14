---
description: Phase 6 workflow — Multi-Database Search Deduplication & PRISMA 2020 Calculator. Merges PubMed, Embase, Cochrane exports, removes duplicates via the Bramer method, and generates flow metrics.
---

# /phase-6-dedup — Többadatbázisos Keresési Deduplikáció & PRISMA 2020 Folyamatszámítás

> **Fázis:** Phase 6 a Bővített Kutatási Folyamatban  
> **Vezető Ágensek:** `lit-reviewer` (Irodalmi és Adatbázis Felelős) + `meta-analyzer` (Módszertani Adatintegritás)  
> **Szabvány:** Cochrane Handbook v6.5 §4.6.2 · PRISMA 2020 Statement · Bramer Deduplication Method (2016)  
> **Releváns Módszertani Wiki Fejezet:**  
> • [04. Szisztematikus Keresési Stratégia & Keresőkulcs Építés (CTM Guide v2.6)](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/04_systematic_search_key_guide.md)  
> • [06. Válogatás, Szűrés & Cohen's Kappa](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/06_screening_and_selection.md)

---

## 1. Célkitűzés & Ágenshatárok

A Phase 6 feladata a szisztematikus irodalomkutatás során letöltött többezres bibliográfiai exportállományok (PubMed, Embase, Cochrane CENTRAL, Scopus, ClinicalTrials.gov) beolvasása, szabványos összefűzése, szisztematikus és determinisztikus deduplikációja, valamint a **PRISMA 2020 folyamatábra pontos számainak előállítása**.
- **Vezető felelős:** `lit-reviewer` (fájlok beolvasása, forrás-azonosítás, metaadat-egységesítés).
- ⛔ **Ágenshatár:** A deduplikáció tisztán determinisztikus kód alapján fut (`src/deduplicate_exports.py`); az LLM nem törölhet vagy válogathat tanulmányokat szubjektív alapon.

---

## 2. Műveleti Sorrend (Operational Steps)

1. **Nyers Export Fájlok Elhelyezése:**
   - A kutató vagy az irodalmi keresőmotor a letöltött fájlokat a projekt dedikált mappájába menti:
     `projects/<projekt_slug>/literature/exports/`
   - Támogatott formátumok:
     - PubMed: `.nbib` (vagy `.txt`)
     - Embase: `.ris`
     - Cochrane Library (CENTRAL): `.ris`
     - ClinicalTrials.gov / Scopus / Web of Science: `.ris` vagy `.csv`

2. **Deduplikációs Motor Futtatása:**
   - A többadatbázisos összefűzés és a Cochrane/Bramer kaszkád futtatása a master CLI-vel:
     ```bash
     python src/run_pipeline.py deduplicate <projekt_slug>
     ```
   - **A 4-Lépcsős Bramer/Cochrane Deduplikációs Kaszkád:**
     - **1. Szint:** Tiszta, normalizált DOI egyezés.
     - **2. Szint:** PubMed ID (PMID) numerikus egyezés.
     - **3. Szint:** Normalizált címszöveg (alfanumerikus szkeleton $\ge 20$ karakter) egyezés.
     - **4. Szint:** Első szerző vezetékneve + Publikációs év + Cím 30-karakteres előtag egyezés.

3. **PRISMA 2020 Eredmények Ellenőrzése:**
   - A motor automatikusan előállítja a következő deliverable-öket:
     - `projects/<slug>/literature/deduplicated_records.csv` — Tisztított, egységes táblázat a Phase 7 szűréshez.
     - `projects/<slug>/literature/deduplicated_records.ris` — Rayyan / Covidence / Zotero kompatibilis deduplikált fájl.
     - `projects/<slug>/literature/PRISMA_FLOW_DATA.json` — Strukturált számadatok az ábrákhoz.
     - `projects/<slug>/literature/PRISMA_2020_FLOW_REPORT.md` — Részletes CTM intézményi audit beszámoló.

4. **Kulcstanulmányok (Benchmark Studies) Ellenőrzése:**
   - Ha a Phase 1/2 során azonosítottunk ismert kötelező referencia-tanulmányokat (landmark studies), ellenőrizzük, hogy a deduplikáció után a szűrési alapállományban maradéktalanul megtalálhatóak-e.

---

## 3. Záró Kapu: Phase 6 Jóváhagyás

A Phase 6 sikeresen lezártnak minősül, ha:
1. Az összes bemeneti adatbázis rekordjai hiánytalanul beolvasásra kerültek.
2. A deduplikációs arány és a kizárási okok dokumentálva vannak a `PRISMA_2020_FLOW_REPORT.md`-ben.
3. Előállt a tisztított `deduplicated_records.csv`, amely készen áll a **Phase 7: Cím & Absztrakt Szűrésre** (`/phase-7-screening`).

