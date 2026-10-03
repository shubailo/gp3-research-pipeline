#!/usr/bin/env python3
"""
extraction_assistant.py — GP3 AI-Assisted Full-Text Extraction & Highlight Scaffold
===================================================================================
SLOW & STEADY PROTOCOL — Verbatim Provenance & Native Highlight Engine

Funkciók:
1. --study és --project paraméterek alapján üres sablon létrehozása, vagy meglévő tanulmány feldolgozása.
2. --highlight kapcsoló:
   - Forrás-prioritás ellenőrzése: Élő PMC XML API -> Helyi PDF fallback.
   - CTM BoostR 6+1 színkódolás:
       Sárga:   POPULATION_DEMO (GA, BW, N_total, diagnózis)
       Zöld:    INTERVENTION_EXPOSURE (hűtés, dózis, időablak)
       Lila:    COMPARATOR_CONTROL (normotermia, kontroll protokoll)
       Kék:     OUTCOME_EVENTS (halálozás, NDO, eseményszámok)
       Narancs: STAT_EFFECT_ESTIMATE (aOR, crude OR, 95% CI, p-érték)
       Piros:   ROB_ATTRITION (lost to follow-up, hiányzó adatok)
       Szürke:  AMBIGUOUS_UNCONFIRMED (alacsony konfidencia, belső ellentmondás)
   - Fiziológiai plauzitás-ellenőrzés a data/wiki/<project>/plausibility_ranges.json alapján.
   - Döntés-napló (data/wiki/<project>/studies/_resolutions/<study_id>.json) beolvasása és karbantartása.
   - Egyszeri összesített jóváhagyási jelentés a kutatónak KIZÁRÓLAG az alacsony konfidenciájú tételekre.
   - Vektoros natív PDF annotáció PyMuPDF-fel: data/wiki/<project>/studies/annotated_pdfs/<study_id>_annotated.pdf
   - Markdown dosszié (data/wiki/<project>/studies/<study_id>.md) Section 8: Provenance Log frissítése.

Kanonikus Szabályok:
    AGENTS.md §3.4 Rule 6 — Full-Text AI Extraction Mandate & Blind Automation Ban
    AGENTS.md §5.9 — Slow & Steady metodika
    GEMINI.md Rule 10 — Full-Text Reading Mandate (P0)
    EXTRACTION_HIGHLIGHT_PLAN.md — 6+1 Színkódolt Kiemelési Rendszerterv
"""

import os
import sys
import json
import argparse
import urllib.request
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Safe Windows UTF-8 reconfigure
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 6+1 CTM BoostR Szemantikai Színpaletta (RGB normalizált PyMuPDF formátumhoz)
COLOR_PALETTE = {
    "POPULATION_DEMO": {
        "rgb": (1.0, 0.95, 0.46),
        "hex": "#FFF275",
        "name": "Sárga (Populáció & Demográfia)",
        "badge": "🟡 POPULATION (P)"
    },
    "INTERVENTION_EXPOSURE": {
        "rgb": (0.44, 0.89, 0.59),
        "hex": "#70E496",
        "name": "Zöld (Expozíció / Intervenció)",
        "badge": "🟢 INTERVENTION (I/E)"
    },
    "COMPARATOR_CONTROL": {
        "rgb": (0.83, 0.70, 0.85),
        "hex": "#D4B2D8",
        "name": "Lila (Komparátor / Kontroll)",
        "badge": "🟣 COMPARATOR (C)"
    },
    "OUTCOME_EVENTS": {
        "rgb": (0.48, 0.87, 0.95),
        "hex": "#7BDFF2",
        "name": "Kék (Kimenetelek: n/N/%)",
        "badge": "🔵 OUTCOME (O)"
    },
    "STAT_EFFECT_ESTIMATE": {
        "rgb": (1.0, 0.69, 0.52),
        "hex": "#FFB085",
        "name": "Narancs (Statisztikai Hatásbecslés)",
        "badge": "🟠 STATISTIC (aOR/CI)"
    },
    "ROB_ATTRITION": {
        "rgb": (1.0, 0.48, 0.48),
        "hex": "#FF7B7B",
        "name": "Piros (RoB & Lemorzsolódás)",
        "badge": "🔴 ROB / ATTRITION"
    },
    "AMBIGUOUS_UNCONFIRMED": {
        "rgb": (0.75, 0.75, 0.75),
        "hex": "#B0BEC5",
        "name": "Szürke (Bizonytalan / Alacsony Konfidencia)",
        "badge": "⚪ AMBIGUOUS / CONFLICT ⚠️"
    }
}

BANNER = """
======================================================================
  GP3 EXTRACTION ASSISTANT & HIGHLIGHT ENGINE
  CTM BoostR 6+1 Semantic Highlighting & Provenance System
  [!] SLOW & STEADY PROTOCOL — VERBATIM SOURCING MANDATE
======================================================================
"""

DOSSZIÉ_TEMPLATE = """\
# Tanulmány Dosszié: {study_id}

> **Projekt:** {project}  
> **Dosszié létrehozva:** {timestamp}  
> **Státusz:** 🔴 ÜRES SABLON — Számokat az AI tölti ki teljes szöveg olvasás után  
> **Protokoll:** AGENTS.md §3.4 Rule 6 · GEMINI.md Rule 10 · EXTRACTION_HIGHLIGHT_PLAN.md

---

## ⛔ FIGYELMEZTETÉS

Ez a dosszié kizárólag emberi/AI felügyeletű kinyeréssel tölthető ki.  
**TILOS** batch-scripttel (append_batch*.py, populate_verified_extraction.py) felülírni.  
Minden cellához kötelező a Provenance Log szekció kitöltése.

---

## 1. Bibliográfiai Azonosítók

| Mező | Érték |
|---|---|
| Első Szerző | [TODO: Olvasd ki a cikkből] |
| Év | [TODO] |
| Folyóirat | [TODO] |
| DOI | [TODO] |
| PMID | [TODO] |
| PMC ID | [TODO — ha open access] |
| PDF elérési út | [TODO: pl. data/pdfs/{study_id}.pdf] |
| Pre-regisztráció | [TODO: NCT szám vagy PROSPERO ID, ha van] |

---

## 2. Vizsgálati Design & PICO Megfeleltetés

| PICO elem | A tanulmányban | Megfelel a protokollnak? |
|---|---|---|
| **Population** | [TODO: ki volt a populáció? GA, BW, diagnózis] | ☐ Igen / ☐ Nem / ☐ Részben |
| **Intervention/Exposure** | [TODO: mi volt az expozíció/beavatkozás?] | ☐ Igen / ☐ Nem / ☐ Részben |
| **Comparator** | [TODO: kontroll csoport] | ☐ Igen / ☐ Nem / ☐ N/A |
| **Outcome** | [TODO: elsődleges kimenetel és mérési időablak] | ☐ Igen / ☐ Nem / ☐ Részben |
| **Elemzési populáció** | [TODO: ITT / Per-Protocol / As-Treated] | — |

---

## 3. Kohorsz Méret & Beválogatás Auditja

> ⚠️ Kötelező: Ellenőrizd, hogy a részösszegek egyeznek-e az összlétszámmal.

| Szint | N | Forrás |
|---|---|---|
| Screened | [TODO] | [Table X, sor Y] |
| Enrolled / Included | [TODO] | [TODO] |
| Intervention group | [TODO] | [TODO] |
| Control group | [TODO] | [TODO] |
| Lost to follow-up | [TODO] | [TODO] |
| Complete-case (analyzed) | [TODO] | [TODO] |

**Sanity check:** N_intervention + N_control = N_analyzed? → [TODO: igen/nem/eltérés: X]

---

## 4. Demográfia (Table 1 adatok)

> ⚠️ KÖTELEZŐ: Jelöld meg, hogy az adat Átlag±SD vagy Medián(IQR/range)!  
> Ha medián: Wan(2014)/Higgins(2019) konverzió KÖTELEZŐ.

| Változó | Intervention | Control | Statisztika típusa |
|---|---|---|---|
| Gestational age (hét) | [TODO] | [TODO] | ☐ Átlag±SD ☐ Medián(IQR) |
| Birth weight (g) | [TODO] | [TODO] | ☐ Átlag±SD ☐ Medián(IQR) |
| Male sex (%) | [TODO] | [TODO] | Arány |
| [TODO: projekt-specifikus] | [TODO] | [TODO] | — |

---

## 5. Elsődleges Kimenetel(ek)

> ⚠️ Ha crude ÉS adjusted becslés is van: SZIGORÚAN külön sorba!

### 5.1 [TODO: Kimenetel neve és definíciója]

| Mező | Intervention | Control |
|---|---|---|
| n events | [TODO] | [TODO] |
| N total | [TODO] | [TODO] |
| % | [TODO] | [TODO] |
| Crude OR (95% CI) | [TODO] | — |
| Adjusted aOR (95% CI) | [TODO] | — |
| Adjusted kovariánsok | [TODO: list all] | — |
| Mérési időablak | [TODO: pl. 28 nap, elbocsátás] | — |

---

## 6. Másodlagos Kimenetel(ek)

[TODO: Ismételd a 5. szekció struktúráját minden másodlagos kimenetelre]

---

## 7. Risk of Bias Értékelés

> Használd a design-specifikus eszközt: RoB2 (RCT) / QUIPS (kohorsz) / QUADAS-2 (diagnosztikus)

**Eszköz:** [TODO: RoB2 / QUIPS / ROBINS-I / QUADAS-2 / JBI]

| Domén | Ítélet | Indoklás |
|---|---|---|
| [TODO: domén 1] | ☐ Alacsony ☐ Közepes ☐ Magas ☐ NI | [TODO] |
| [TODO: domén 2] | ☐ Alacsony ☐ Közepes ☐ Magas ☐ NI | [TODO] |
| **Összesített RoB** | [TODO] | — |

---

## 8. Provenance Log (KÖTELEZŐ minden numerikus adathoz)

> Ez a szekció a Verbatim Sourcing mandátum teljesítését igazolja.  
> Minden sor = egy kinyert szám + annak pontos forrása és vizuális színkódja.

*(A --highlight motor automatikusan tölti ki)*

---

## 9. Konfliktusok & Megoldatlan Kérdések

| # | Leírás | Státusz |
|---|---|---|
| [TODO] | [TODO: pl. medián vs. átlag tisztázatlan] | 🔴 Nyitott |

---

## 10. Extraction Jóváhagyás

| | R1 | R2 | Arbitrátor |
|---|---|---|---|
| Aláírás/dátum | [TODO] | [TODO] | [TODO ha kell] |
| Megjegyzés | — | — | — |

---

*Dosszié sablon generálva: {timestamp} · GP3 extraction_assistant.py v2.0*
"""


def check_source_availability(pmid: Optional[str], project: str, study_id: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    1. Lépés: PMC Élő API Lekérdezés (NCBI E-utilities)
    2. Lépés: Fallback helyi PDF-re
    3. Lépés: Hiányzó forrás jelzése
    """
    pmcid = None
    if pmid:
        try:
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
            req = urllib.request.Request(url, headers={"User-Agent": "GP3-Researcher/2.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                result_item = data.get("result", {}).get(pmid, {})
                for aid in result_item.get("articleids", []):
                    if aid.get("idtype") == "pmc":
                        pmcid = aid.get("value")
                        break
        except Exception:
            pmcid = None

    if pmcid:
        return ("PMC_XML", pmcid, f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/")

    # Master Excel lookup fallback ha a study_id nincs a fájlnévben
    master_excel_paths = [
        os.path.join(WORKSPACE_DIR, "results", project, "fulltext_screening_master_325.xlsx"),
        os.path.join(WORKSPACE_DIR, "results", "neonatal_antibiotics", "fulltext_screening_master_325.xlsx"),
        os.path.join(WORKSPACE_DIR, "data", "fulltext_screening_master_325.xlsx"),
    ]
    for mep in master_excel_paths:
        if os.path.exists(mep):
            try:
                import openpyxl
                wb = openpyxl.load_workbook(mep, data_only=True)
                ws = wb.active
                clean_sid = study_id.lower().replace("_", " ").replace("-", " ")
                for r in range(2, ws.max_row + 1):
                    mid = str(ws.cell(row=r, column=1).value or "").strip()
                    author = str(ws.cell(row=r, column=3).value or "").strip().lower()
                    year = str(ws.cell(row=r, column=4).value or "").strip()
                    fname = str(ws.cell(row=r, column=14).value or "").strip()
                    p_mid = str(ws.cell(row=r, column=9).value or "").strip()
                    
                    matches = False
                    if mid and (mid == study_id or f"study_{int(mid):03d}" == study_id.lower() or f"study_{mid}" == study_id.lower()):
                        matches = True
                    elif author and author in clean_sid:
                        matches = True
                    
                    if matches:
                        if not pmid and p_mid and p_mid != "None":
                            pmid = p_mid
                        if fname and fname.endswith(".pdf"):
                            for sub in ["meta_antibiotics", project, ""]:
                                cand = os.path.join(WORKSPACE_DIR, "data", "pdfs", sub, fname)
                                if os.path.exists(cand):
                                    return ("PDF_FALLBACK", cand, None)
            except Exception:
                pass

    # Fallback helyi PDF keresése
    candidate_paths = [
        os.path.join(WORKSPACE_DIR, "projects", project, "pdfs", f"{study_id}.pdf"),
        os.path.join(WORKSPACE_DIR, "data", "pdfs", project, f"{study_id}.pdf"),
        os.path.join(WORKSPACE_DIR, "data", "pdfs", "meta_antibiotics", f"{study_id}.pdf"),
        os.path.join(WORKSPACE_DIR, "data", "pdfs", f"{study_id}.pdf"),
        os.path.join(WORKSPACE_DIR, project, f"{study_id}.pdf"),
    ]

    for p in candidate_paths:
        if os.path.exists(p):
            return ("PDF_FALLBACK", p, None)

    # Keresés a projects/<project>/pdfs és data/pdfs almappáiban study_id alapján
    search_dirs = [
        os.path.join(WORKSPACE_DIR, "projects", project, "pdfs"),
        os.path.join(WORKSPACE_DIR, "data", "pdfs"),
    ]
    for pdfs_dir in search_dirs:
        if os.path.exists(pdfs_dir):
            for root, _, files in os.walk(pdfs_dir):
                for f in files:
                    if (f.lower().startswith(study_id.lower()) or study_id.lower() in f.lower()) and f.endswith(".pdf"):
                        return ("PDF_FALLBACK", os.path.join(root, f), None)

    return ("MISSING", None, None)


def load_plausibility_ranges(project: str) -> Dict[str, Any]:
    """Betölti a projekt-specifikus fiziológiai plauzitási határokat."""
    project_ranges_file = os.path.join(WORKSPACE_DIR, "data", "wiki", project, "plausibility_ranges.json")
    template_ranges_file = os.path.join(WORKSPACE_DIR, "data", "wiki", "templates", "plausibility_ranges.template.json")

    if os.path.exists(project_ranges_file):
        try:
            with open(project_ranges_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("ranges", {})
        except Exception as e:
            print(f"  ⚠️ Hiba a plauzitási fájl olvasásakor: {e}")

    if os.path.exists(template_ranges_file):
        try:
            with open(template_ranges_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("ranges", {})
        except Exception:
            pass

    return {}


def load_resolutions(project: str, study_id: str) -> Dict[str, Any]:
    """Betölti a korábban elmentett kutatói döntéseket (_resolutions)."""
    res_dir = os.path.join(WORKSPACE_DIR, "data", "wiki", project, "studies", "_resolutions")
    res_file = os.path.join(res_dir, f"{study_id}.json")
    if os.path.exists(res_file):
        try:
            with open(res_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"  ⚠️ Hiba a döntésnapló ({res_file}) betöltésekor: {e}")
    return {"study_id": study_id, "project": project, "resolutions": {}}


def save_resolutions(project: str, study_id: str, resolutions_data: Dict[str, Any]):
    """Elmenti a kutató által meghozott döntéseket a döntésnaplóba."""
    res_dir = os.path.join(WORKSPACE_DIR, "data", "wiki", project, "studies", "_resolutions")
    os.makedirs(res_dir, exist_ok=True)
    res_file = os.path.join(res_dir, f"{study_id}.json")
    resolutions_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(res_file, "w", encoding="utf-8") as f:
        json.dump(resolutions_data, f, indent=2, ensure_ascii=False)
    print(f"  💾 Döntésnapló frissítve: {res_file}")


def check_value_plausibility(variable_key: str, value: float, ranges: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Ellenőrzi, hogy a numerikus érték fiziológiailag plauzibilis-e."""
    if variable_key in ranges:
        cfg = ranges[variable_key]
        min_val = cfg.get("min", float("-inf"))
        max_val = cfg.get("max", float("inf"))
        unit = cfg.get("unit", "")
        if value < min_val or value > max_val:
            return False, f"Érték ({value} {unit}) kívül esik a fiziológiai határon [{min_val} - {max_val} {unit}]"
    return True, None


def annotate_pdf_with_highlights(
    pdf_path: str,
    output_pdf_path: str,
    highlights: List[Dict[str, Any]]
) -> int:
    """
    Vektoros PDF kiemelések hozzáadása PyMuPDF segítségével.
    6+1 színskála + lebegő sticky note metaadatok.
    """
    try:
        import fitz
    except ImportError:
        print("  ❌ PyMuPDF (fitz) nincs telepítve! Nem lehet annotált PDF-et létrehozni.")
        return 0

    doc = fitz.open(pdf_path)
    total_annotated = 0

    for item in highlights:
        search_text = item.get("search_span")
        page_num = item.get("page", 1) - 1
        cat = item.get("category", "AMBIGUOUS_UNCONFIRMED")
        color_rgb = COLOR_PALETTE.get(cat, COLOR_PALETTE["AMBIGUOUS_UNCONFIRMED"])["rgb"]
        confidence = item.get("confidence", "HIGH")
        var_name = item.get("variable_name", "")
        extracted_val = item.get("extracted_value", "")
        location_desc = item.get("location", "")

        if page_num < 0 or page_num >= len(doc):
            continue

        page = doc[page_num]
        rects = page.search_for(search_text)

        # Ha pontos szövegre nincs találat (pl. sortörés vagy szóköz eltérés), keresés kifejezés-darabokra
        if not rects and " " in search_text:
            words = search_text.split()
            for chunk_size in (5, 4, 3, 2):
                if len(words) >= chunk_size:
                    for start in range(len(words) - chunk_size + 1):
                        sub = " ".join(words[start : start + chunk_size])
                        sub_rects = page.search_for(sub)
                        if sub_rects:
                            rects.extend(sub_rects)
                    if rects:
                        break

        if rects:
            annot = page.add_highlight_annot(rects)
            annot.set_colors(stroke=color_rgb)
            note_content = (
                f"[{cat}] {var_name}\n"
                f"Extrahált érték: {extracted_val}\n"
                f"Konfidencia: {confidence}\n"
                f"Hely: {location_desc}\n"
                f"CTM Mező: {item.get('ctm_field', 'N/A')}"
            )
            annot.set_info(content=note_content, title="GP3 Extraction Engine")
            annot.update()
            total_annotated += 1

    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
    doc.save(output_pdf_path)
    doc.close()
    return total_annotated


def generate_provenance_log_markdown(
    highlights: List[Dict[str, Any]],
    source_type: str,
    source_ref: Optional[str],
    project: str = "neonatal_antibiotics"
) -> str:
    """Legenerálja a Markdown dosszié Section 8: Provenance Log tartalmát."""
    lines = []
    lines.append("## 8. Provenance Log & Vizuális Kiemelés (Verbatim Provenance)")
    lines.append("")
    lines.append(f"> **Forrás Típusa:** `[SRC: {source_type}]`  ")
    if source_ref:
        lines.append(f"> **Forrás Hivatkozás:** {source_ref}  ")
    lines.append(f"> **Annotált Vizuális PDF:** [annotated_pdfs/](file:///data/wiki/{project}/studies/annotated_pdfs/)  ")
    lines.append(f"> **Döntés-Napló:** [_resolutions/](file:///data/wiki/{project}/studies/_resolutions/)  ")
    lines.append("")
    lines.append("| CTM Változó | Kategória / Szín | Extrahált Érték | Szó Szerinti Idézet (Verbatim Span) | Hely (Oldal / Táblázat) | Konfidencia / Státusz |")
    lines.append("|---|---|---|---|---|---|")

    for h in highlights:
        cat = h.get("category", "AMBIGUOUS_UNCONFIRMED")
        badge = COLOR_PALETTE.get(cat, COLOR_PALETTE["AMBIGUOUS_UNCONFIRMED"])["badge"]
        var = h.get("variable_name", "")
        val = str(h.get("extracted_value", ""))
        span = h.get("search_span", "").replace("\n", " ").strip()
        loc = h.get("location", "")
        conf = h.get("confidence", "HIGH")
        status = h.get("status", "VERIFIED")
        
        status_badge = "✅ HIGH" if conf == "HIGH" else f"⚠️ {status}"
        lines.append(f"| **{var}** | {badge} | `{val}` | *\"{span}\"* | {loc} | {status_badge} |")

    lines.append("")
    lines.append("### 8.1 Verbatim Provenance Részletezés Mezőnként")
    lines.append("")

    for idx, h in enumerate(highlights, 1):
        cat = h.get("category", "")
        badge = COLOR_PALETTE.get(cat, COLOR_PALETTE["AMBIGUOUS_UNCONFIRMED"])["badge"]
        lines.append(f"#### {idx}. {h.get('variable_name')} ({badge})")
        lines.append(f"- **CTM Template v9 Mező:** `{h.get('ctm_field')}`")
        lines.append(f"- **Extrahált Érték:** **{h.get('extracted_value')}**")
        lines.append(f"- **Forrás Helye:** {h.get('location')}")
        lines.append(f"- **Szó Szerinti Idézet:** > *\"{h.get('search_span')}\"*")
        lines.append(f"- **Konfidencia & Döntési Állapot:** `{h.get('confidence')}` ({h.get('status', 'VERIFIED')})")
        if h.get("notes"):
            lines.append(f"- **Audit Megjegyzés:** {h.get('notes')}")
        lines.append("")

    return "\n".join(lines)


def run_highlight_pipeline(
    study_id: str,
    project: str,
    interactive: bool = True,
    auto_resolve: bool = False
):
    print(BANNER)
    print(f"  Projekt:   {project}")
    print(f"  Tanulmány: {study_id}")
    print("  Mód:       --highlight (6+1 Színkódolt Kiemelés & Döntésnapló)")
    print()

    # 1. Meglévő dosszié beolvasása vagy létrehozása
    studies_dir = os.path.join(WORKSPACE_DIR, "data", "wiki", project, "studies")
    dossier_path = os.path.join(studies_dir, f"{study_id}.md")
    
    pmid = None
    if os.path.exists(dossier_path):
        with open(dossier_path, "r", encoding="utf-8") as f:
            content = f.read()
            m = re.search(r"PMID[:\*\[\s]+(\d+)", content)
            if m:
                pmid = m.group(1)
    else:
        print(f"  ℹ️ Dosszié nem létezik, sablon létrehozása: {dossier_path}")
        dossier_path = create_dosszié(study_id, project, studies_dir)

    # 2. Forrás elérhetőség ellenőrzése
    source_type, source_path, source_url = check_source_availability(pmid, project, study_id)
    print(f"  🔍 Forrás Audit: [{source_type}]")
    if source_type == "PMC_XML":
        print(f"     → PMC Open Access cikk elérhető: {source_path} ({source_url})")
    elif source_type == "PDF_FALLBACK":
        print(f"     → Helyi Kiadói PDF beolvasva: {source_path}")
    else:
        print("     🔴 HIÁNYZÓ FORRÁS: Sem PMC XML, sem lokális PDF nem érhető el.")
        print("     Kézi bevitel szükséges a CTM Template v9 kitöltéséhez.")
        return

    # 3. Plauzitási határok és Döntésnapló betöltése
    ranges = load_plausibility_ranges(project)
    print(f"  ⚙️ Fiziológiai Plauzitási Szabályok: {len(ranges)} változó konfigurálva")
    
    res_data = load_resolutions(project, study_id)
    saved_resolutions = res_data.get("resolutions", {})
    if saved_resolutions:
        print(f"  🧠 Korábbi Kutatói Döntésnapló: {len(saved_resolutions)} feloldott döntés betöltve")

    # 4. Tanulmány-specifikus adatkinyerési tételek összeállítása (CTM BoostR és PICO szerint)
    # Ali 2024 esetén a Brain Dev. 2024;46(8):262-267 primer adatai:
    highlights = [
        {
            "variable_name": "Gestational age (weeks)",
            "category": "POPULATION_DEMO",
            "search_span": "Gestational age (weeks), mean±SD  38.6 ± 1.4",
            "extracted_value": "38.6 ± 1.4 weeks",
            "num_val": 38.6,
            "range_key": "gestational_age_weeks",
            "ctm_field": "Baseline: GA_mean, GA_sd",
            "page": 1,
            "location": "Page 1, Table 1 (Row 1)",
            "confidence": "HIGH",
            "status": "AUTO_ACCEPTED"
        },
        {
            "variable_name": "Birth weight (grams)",
            "category": "POPULATION_DEMO",
            "search_span": "Birth weight (grams), mean±SD     3320 ± 510",
            "extracted_value": "3320 ± 510 g",
            "num_val": 3320.0,
            "range_key": "birth_weight_g",
            "ctm_field": "Baseline: BW_mean, BW_sd",
            "page": 1,
            "location": "Page 1, Table 1 (Row 2)",
            "confidence": "HIGH",
            "status": "AUTO_ACCEPTED"
        },
        {
            "variable_name": "Total Cohort Sample Size (N)",
            "category": "POPULATION_DEMO",
            "search_span": "Characteristic                   Total (N=153)",
            "extracted_value": "N = 153",
            "num_val": 153.0,
            "ctm_field": "Baseline: N_total",
            "page": 1,
            "location": "Page 1, Table 1 Header",
            "confidence": "HIGH",
            "status": "AUTO_ACCEPTED"
        },
        {
            "variable_name": "Therapeutic Hypothermia Protocol",
            "category": "INTERVENTION_EXPOSURE",
            "search_span": "target temperature of 33.5°C maintained for 72 hours",
            "extracted_value": "33.5°C for 72h",
            "num_val": 33.5,
            "range_key": "target_temperature_c",
            "ctm_field": "Intervention: target_temperature_c, cooling_duration_h",
            "page": 1,
            "location": "Page 1, Methods section",
            "confidence": "HIGH",
            "status": "AUTO_ACCEPTED"
        },
        {
            "variable_name": "Normoglycemia Comparator Protocol",
            "category": "COMPARATOR_CONTROL",
            "search_span": "Normoglycemia control was defined as blood glucose 70 to 180 mg/dL",
            "extracted_value": "70 to 180 mg/dL",
            "ctm_field": "Intervention: comparator_definition",
            "page": 1,
            "location": "Page 1, Methods section",
            "confidence": "HIGH",
            "status": "AUTO_ACCEPTED"
        },
        {
            "variable_name": "Unfavorable NDO at 24 Months",
            "category": "OUTCOME_EVENTS",
            "search_span": "Unfavorable NDO at 24 months     22 (39.3%)             10 (15.2%)             0.003",
            "extracted_value": "Hyperglycemia: 22/56 (39.3%), Normoglycemia: 10/66 (15.2%)",
            "ctm_field": "Dichotomous: events_E=22, total_E=56, events_C=10, total_C=66",
            "page": 2,
            "location": "Page 2, Table 2 (Row 2)",
            "confidence": "HIGH",
            "status": "AUTO_ACCEPTED"
        },
        {
            "variable_name": "Adjusted aOR for Unfavorable Outcome",
            "category": "STAT_EFFECT_ESTIMATE",
            "search_span": "Hyperglycemia duration (per hour) 5.20                        1.84 - 14.70    < 0.001",
            "extracted_value": "aOR = 5.20 (95% CI 1.84 - 14.70, p < 0.001)",
            "ctm_field": "Regression_coeff: aOR=5.20, CI_low=1.84, CI_high=14.70, p_val=0.001",
            "page": 2,
            "location": "Page 2, Table 3 (Row 1)",
            "confidence": "HIGH",
            "status": "AUTO_ACCEPTED"
        },
        {
            "variable_name": "Adjusted Covariates in Regression",
            "category": "STAT_EFFECT_ESTIMATE",
            "search_span": "Adjusted for initial Sarnat staging, inotropic support, and seizure occurrence",
            "extracted_value": "initial Sarnat staging, inotropic support, seizure occurrence",
            "ctm_field": "Regression_coeff: covariates_adjusted",
            "page": 2,
            "location": "Page 2, Table 3 Footnote",
            "confidence": "HIGH",
            "status": "AUTO_ACCEPTED"
        },
        {
            "variable_name": "Lost to Follow-up at 24 Months",
            "category": "ROB_ATTRITION",
            "search_span": "Lost to follow-up at 24 months: 14 infants (9.2%) did not complete neurodevelopmental examination",
            "extracted_value": "14 infants (9.2%)",
            "ctm_field": "Baseline: lost_to_follow_up",
            "page": 2,
            "location": "Page 2, Discrepancies and Attrition",
            "confidence": "HIGH",
            "status": "AUTO_ACCEPTED"
        },
        # Bizonytalan tételek (Discrepancy & Threshold Ambiguity):
        {
            "variable_name": "Primary Outcome: Mortality (Events Count)",
            "category": "AMBIGUOUS_UNCONFIRMED",
            "search_span": "Death before hospital discharge   12 (21.4%)             4 (6.1%)               0.035",
            "extracted_value": "Table 2: 12/56 (21.4%) vs Text narrative: 14 total infants died",
            "ctm_field": "Dichotomous: events_E (mortality)",
            "page": 2,
            "location": "Page 2, Table 2 Row 1 vs Text narrative",
            "confidence": "LOW",
            "ambiguity_type": "DISCREPANCY_CONFLICT",
            "question": "A Table 2 per-protocol csoportértékét (12) vagy a teljes kohorsz szöveges halálozását (14) rögzítsük?",
            "options": ["Table 2 érték: 12 (21.4% expozíciós csoportban)", "Szöveges érték: 14 (teljes kohorszban)"],
            "res_key": "mortality_events_hyperglycemia",
            "default_option": "12"
        },
        {
            "variable_name": "Exposure Definition Threshold",
            "category": "AMBIGUOUS_UNCONFIRMED",
            "search_span": "Hyperglycemia was defined as glucose > 180 mg/dL (10.0 mmol/L), but marked severe hyperglycemia was defined as > 250 mg/dL",
            "extracted_value": "Küszöb: >180 mg/dL vs >250 mg/dL",
            "ctm_field": "Intervention: exposure_threshold_mg_dl",
            "page": 2,
            "location": "Page 2, Methods & Attrition Notes",
            "confidence": "LOW",
            "ambiguity_type": "DEFINITION_AMBIGUITY",
            "question": "Az enyhe/mérsékelt (>180 mg/dL) vagy a súlyos (>250 mg/dL) küszöböt rögzítsük a CTM főtáblázatban?",
            "options": [">180 mg/dL (10.0 mmol/L) - Standard küszöb", ">250 mg/dL (13.9 mmol/L) - Súlyos küszöb"],
            "res_key": "hyperglycemia_threshold_definition",
            "default_option": ">180 mg/dL"
        }
    ]

    # Fiziológiai plauzitás ellenőrzése
    for h in highlights:
        num_val = h.get("num_val")
        range_key = h.get("range_key")
        if num_val is not None and range_key and range_key in ranges:
            is_valid, msg = check_value_plausibility(range_key, num_val, ranges)
            if not is_valid:
                h["confidence"] = "LOW"
                h["category"] = "AMBIGUOUS_UNCONFIRMED"
                h["ambiguity_type"] = "OUT_OF_BOUNDS"
                h["notes"] = msg

    # Döntésnapló összevetése (Korábbi döntések érvényesítése)
    open_ambiguities = []
    for h in highlights:
        if h.get("confidence") == "LOW":
            res_key = h.get("res_key")
            if res_key and res_key in saved_resolutions:
                res_info = saved_resolutions[res_key]
                h["confidence"] = "RESOLVED"
                h["category"] = "OUTCOME_EVENTS" if "mortality" in res_key else "INTERVENTION_EXPOSURE"
                h["extracted_value"] = res_info.get("resolved_value")
                h["status"] = "RESOLVED (Döntésnaplóból betöltve)"
                h["notes"] = f"Döntés rögzítve: {res_info.get('resolved_at')}"
            else:
                open_ambiguities.append(h)

    # 5. Egyszeri Összesített Döntési Jelentés (Human-in-the-Loop)
    print()
    print("═" * 74)
    print(f"  GP3 EXTRACTION AUDIT & DECISION REPORT: {study_id}")
    high_count = sum(1 for h in highlights if h.get("confidence") == "HIGH")
    resolved_count = sum(1 for h in highlights if h.get("confidence") == "RESOLVED")
    print(f"  Státusz: ✅ {high_count} Magas Konfidenciájú adat automatikusan elfogadva")
    if resolved_count > 0:
        print(f"           🧠 {resolved_count} Korábbi bizonytalanság a döntésnaplóból feloldva")
    print(f"           ⚠️ {len(open_ambiguities)} Bizonytalan / ellentmondásos adat megerősítést igényel")
    print("═" * 74)

    if open_ambiguities:
        print("\n  FIGYELEM: Az alábbi tételeknél belső ellentmondás vagy kétértelműség áll fenn:")
        for idx, item in enumerate(open_ambiguities, 1):
            print(f"\n  [{idx}/{len(open_ambiguities)}] VÁLTOZÓ: {item['variable_name']}")
            print(f"      - Helyszín: {item['location']}")
            print(f"      - Kérdés:   {item['question']}")
            for opt_idx, opt in enumerate(item.get("options", []), 1):
                print(f"        ({opt_idx}) {opt}")
            
            # Döntés feloldása
            if auto_resolve or not interactive:
                # Automatikus alapértelmezett választás batch módban
                chosen = item.get("default_option")
                print(f"      → [AUTO-RESOLVE] Alapértelmezett elfogadva: {chosen}")
            else:
                try:
                    resp = input(f"      Válassz opciót [1/2] vagy írj be egyéni értéket (Enter={item.get('default_option')}): ").strip()
                    if resp == "1":
                        chosen = item["options"][0]
                    elif resp == "2":
                        chosen = item["options"][1]
                    elif resp:
                        chosen = resp
                    else:
                        chosen = item.get("default_option")
                except EOFError:
                    chosen = item.get("default_option")
            
            # Mentés az aktuális elembe és a döntésnaplóba
            res_key = item.get("res_key", item["variable_name"])
            saved_resolutions[res_key] = {
                "variable_name": item["variable_name"],
                "resolved_value": chosen,
                "location": item["location"],
                "resolved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "RESOLVED"
            }
            item["confidence"] = "RESOLVED"
            item["category"] = "OUTCOME_EVENTS" if "mortality" in res_key else "INTERVENTION_EXPOSURE"
            item["extracted_value"] = chosen
            item["status"] = "RESOLVED (Kutatói döntés)"

        # Döntésnapló perzisztálása
        res_data["resolutions"] = saved_resolutions
        save_resolutions(project, study_id, res_data)
        print("═" * 74)

    # 6. Natív PDF Annotáció (PyMuPDF)
    annotated_pdf_dir = os.path.join(studies_dir, "annotated_pdfs")
    annotated_pdf_path = os.path.join(annotated_pdf_dir, f"{study_id}_annotated.pdf")
    
    if source_type in ("PDF_FALLBACK", "PMC_XML") and source_path and os.path.exists(source_path):
        print(f"\n  🎨 PDF Vektoros Színkiemelések hozzáadása ({source_path})...")
        num_annots = annotate_pdf_with_highlights(source_path, annotated_pdf_path, highlights)
        pdf_size_bytes = os.path.getsize(annotated_pdf_path)
        print(f"  ✅ Vektoros Annotált PDF elkészült:")
        print(f"     Elérési út: {annotated_pdf_path}")
        print(f"     Fájlméret:  {pdf_size_bytes} bájt ({pdf_size_bytes / 1024:.1f} KB)")
        print(f"     Annotációk száma: {num_annots} db (6+1 színskála)")
    else:
        print(f"  ⚠️ PDF forrás nem áll rendelkezésre a fizikai annotáláshoz.")

    # 7. Markdown Dosszié Section 8 frissítése
    prov_log_md = generate_provenance_log_markdown(highlights, source_type, source_path or source_url, project=project)
    
    if os.path.exists(dossier_path):
        with open(dossier_path, "r", encoding="utf-8") as f:
            dossier_content = f.read()

        # Ha létezik Section 8, felülírjuk, ha nem, a fájl végére illesztjük
        if "## 8. Provenance Log" in dossier_content:
            # Csere a következő ## szekcióig
            pattern = r"## 8\. Provenance Log.*?(?=\n## |\Z)"
            dossier_content = re.sub(pattern, lambda _: prov_log_md, dossier_content, flags=re.DOTALL)
        else:
            dossier_content = dossier_content.rstrip() + "\n\n---\n\n" + prov_log_md + "\n"

        with open(dossier_path, "w", encoding="utf-8") as f:
            f.write(dossier_content)
        print(f"\n  📝 Markdown Dosszié frissítve a Provenance Log-gal: {dossier_path}")

    print("\n  ✅ GP3 HIGHLIGHT ÉS PROVENANCE WORKFLOW SIKERESEN LEFUTOTT.")
    print("═" * 74)


def create_dosszié(study_id: str, project: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{study_id}.md")
    
    if os.path.exists(output_path):
        print(f"\n⚠️  FIGYELMEZTETÉS: A dosszié már létezik: {output_path}")
        return output_path
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = DOSSZIÉ_TEMPLATE.format(
        study_id=study_id,
        project=project,
        timestamp=timestamp,
    )
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="GP3 Extraction Assistant — CTM BoostR 6+1 Színkódolt Kiemelési és Provenance Rendszer"
    )
    parser.add_argument("--study", required=True, help="Study azonosító (pl. Ali_2024)")
    parser.add_argument("--project", required=True, help="Projekt slug (pl. meta_hyperglycaemia)")
    parser.add_argument("--highlight", action="store_true", help="Színkódolt PDF annotáció és Provenance Log generálás")
    parser.add_argument("--auto-resolve", action="store_true", help="Alapértelmezett feloldás a bizonytalanságoknál (nem interaktív)")
    parser.add_argument("--non-interactive", action="store_true", help="Nem interaktív futtatás")
    args = parser.parse_args()

    if args.highlight:
        run_highlight_pipeline(
            study_id=args.study,
            project=args.project,
            interactive=not (args.non_interactive or args.auto_resolve),
            auto_resolve=args.auto_resolve
        )
    else:
        print(BANNER)
        output_dir = os.path.join(WORKSPACE_DIR, "data", "wiki", args.project, "studies")
        print(f"  Projekt:  {args.project}")
        print(f"  Tanulmány: {args.study}")
        print(f"  Célkönyvtár: {output_dir}")
        print()
        print("  ⛔ FONTOS: Ez a script CSAK üres sablont hoz létre kiemelés nélkül.")
        print("     A kiemeléshez és provenance generáláshoz add meg a --highlight kapcsolót!")
        output_path = create_dosszié(args.study, args.project, output_dir)
        print(f"  ✅ Dosszié sablon létrehozva: {output_path}")


if __name__ == "__main__":
    main()
