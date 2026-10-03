---
description: "Kötelező AI teljes szövegű olvasási és adatkinyerési protokoll. Használd minden primer tanulmány feldolgozásakor — a batch scriptek (append_batch*.py, populate_verified_extraction.py) TILOSAK ennél a lépésnél."
---

# /extraction-ai-read — AI Teljes Szövegű Adatkinyerés (Slow & Steady)

> **Státusz:** ⛔ KÖTELEZŐ PROTOKOLL — Nem opcionális  
> **Felelős Ágens:** `meta-analyzer`  
> **Kanonikus Szabály:** `AGENTS.md §3.4 Rule 6` · `GEMINI.md Rule 10`  
> **Eszköz:** `python src/extraction_assistant.py --study <study_id> --project <project_slug>`

---

## ⛔ TILALOM — Mielőtt bármit csinálsz

A következő scriptek **TILOSAK** adatkinyerésre való használatra:

| ❌ Script | Miért tilos |
|---|---|
| `append_batch2_extraction.py` – `append_batch5_extraction.py` | Hardcoded számokat írnak be ellenőrzés nélkül |
| `populate_verified_extraction.py` | Pandas/regex alapú automatikus feltöltés, kontextus nélkül |
| `generate_study_wiki.py` | Excel-ből generál dossziét, nem a cikkből olvas |
| `extract_batch_demographics.py` | Demográfiát regex-szel nyeri ki, mediánt SD-ként kezelheti |

**Egyetlen megengedett workflow:** az alábbi 5 lépéses AI olvasási protokoll.

---

## 1. Előkészítés: Dosszié-sablon generálása

```bash
python src/extraction_assistant.py --study <study_id> --project <project_slug>
```

Ez létrehozza a `data/wiki/<project_slug>/studies/<study_id>.md` fájlt üres provenance-helyőrzőkkel.  
⚠️ A script **CSAK a sablont** hozza létre. Számokat NEM ír be.

---

## 2. Methods szekció szisztematikus átolvasása (AI olvassa a cikket)

Az AI közvetlen teljes szöveget olvas (PDF → `read_pdf_text.py`, vagy PMC HTML/XML).

**Kötelező ellenőrzőlista:**
- [ ] Hogyan definiálták az intervenciót/expozíciót?
- [ ] Milyen időablakban mérték a kimenetelt? (24 h, elbocsátás, 18 hónapos követés)
- [ ] Mi az elemzési populáció? (ITT vs. Per-Protocol / As-Treated)
- [ ] Milyen szoftverrel végezték az analízist? (SPSS, R, SAS)
- [ ] Van-e pre-regisztráció hivatkozás? (ClinicalTrials.gov NCT szám)

---

## 3. Táblázatok közvetlen vizsgálata

### Table 1 — Demográfia
- [ ] Az adat átlag ± SD, vagy medián (IQR/range)?  
  → Ha medián: **Wan (2014) / Higgins (2019) konverzió kötelező**, tilos SD-ként kezelni
- [ ] A csoportok összlétszáma megegyezik a beválogatott N-nel?
- [ ] Van-e lábjegyzet ami módosítja az értelmezést?

### Table 2–3 — Kimenetelek
- [ ] A szám esemény (n), arány (%), vagy százalék?
- [ ] Szerepel-e crude ÉS adjusted becslés? → **Szigorúan külön oszlopba**
- [ ] Az adjusted modell kovariánsai fel vannak sorolva?

---

## 4. Szó Szerinti Provenance rögzítése a dossziéba

Minden kinyert adat mellé **kötelező** a verbatim idézet:

```markdown
## Provenance Log

### Mortality (Primary Outcome)
- **Forrás:** Table 2, sor 1, oszlop "Intervention group (n=45)"
- **Verbatim:** "Death before discharge: 12 (26.7%)"
- **Kinyert:** n_events = 12, N_intervention = 45
- **Típus:** Dichotóm (nyers 2x2) → ORs-RRs sheet, crude oszlop

### Adjusted OR (aOR)
- **Forrás:** Table 3, lábjegyzet dagger
- **Verbatim:** "Adjusted for gestational age, birth weight, and Sarnat stage: aOR 2.14 (95% CI 1.08-4.23)"
- **Kinyert:** aOR = 2.14, CI_low = 1.08, CI_high = 4.23
```

---

## 5. Kettős Ésszerűségi Ellenőrzés (Sanity Check)

```
N_intervention + N_control = N_total ?
Crude OR kézzel reprodukálható-e? → OR = (n1/(N1-n1)) / (n2/(N2-n2))
Adjusted OR CI szélessége biológiailag plauzibilis-e?
```

Ha eltérés → jelöld [CONFLICT — needs arbitration]-nal, ne írd be az adatot.

---

## Hivatkozások

- AGENTS.md §3.4 Rule 6 — Full-Text AI Extraction Mandate
- AGENTS.md §5.9 — Slow & Steady módszertan
- GEMINI.md Rule 10 — Full-Text Reading Mandate (P0)
- data/wiki/methodology/07_data_extraction_and_boostr.md
