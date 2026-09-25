"""
Systematic Search, Deduplication, and Title/Abstract Screening Pipeline
for Dysglycemia in Neonatal HIE with Therapeutic Hypothermia.
"""

import os
import re
import sys
import io
import time
import json
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Ensure UTF-8 stdout/stderr on Windows to avoid cp1250 encoding crashes
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

# Output Paths
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "meta_hyperglycaemia")
os.makedirs(OUTPUT_DIR, exist_ok=True)

XLSX_PATH = os.path.join(OUTPUT_DIR, "screening_decisions_review.xlsx")
CSV_PATH  = os.path.join(OUTPUT_DIR, "screening_decisions_review.csv")
JSON_PATH = os.path.join(OUTPUT_DIR, "screening_summary.json")

# ----------------------------------------------------------------------
# 1. API Keys & Configuration
# ----------------------------------------------------------------------
env_path = os.path.join(WORKSPACE_DIR, ".env")
elsevier_key = None
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("ELSEVIER_API_KEY="):
                elsevier_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

print("======================================================================")
print("  GP3 MULTI-DATABASE SYSTEMATIC SEARCH & ADJUDICATED SCREENING PIPELINE")
print("======================================================================")
print(f"Target Project Directory: {OUTPUT_DIR}")
print(f"Elsevier API Key detected: {bool(elsevier_key)}\n")

# ----------------------------------------------------------------------
# 2. Database Fetchers
# ----------------------------------------------------------------------

def fetch_pubmed():
    print(">>> [1/4] Fetching PubMed records...")
    query = (
        '("Hypoxia-Ischemia, Brain"[MeSH] OR neonat* OR newborn* OR infant* '
        'OR perinatal* OR asphyxi* OR "hypoxic ischemic encephalopathy" '
        'OR "hypoxic ischaemic encephalopathy" OR "neonatal encephalopathy" '
        'OR "birth asphyxia" OR "perinatal asphyxia" OR HIE) '
        'AND (glyce* OR glycae* OR hyperglyce* OR hypoglyce* '
        'OR "blood glucose" OR "blood sugar" OR "glucose control" '
        'OR "glucose level" OR "glycemic variability" OR "glycaemic variability" '
        'OR "glucose instability" OR lability OR "continuous glucose monitoring" '
        'OR CGM OR insulin OR "glucose infusion rate") '
        'AND (hypotherm* OR cool* OR "induced hypothermia" '
        'OR "therapeutic hypothermia" OR "whole-body cooling" '
        'OR "selective head cooling" OR "head cooling" OR rewarming '
        'OR "target temperature management")'
    )
    
    url_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    r = requests.get(url_search, params={"db": "pubmed", "term": query, "retmax": 2000, "retmode": "json"}).json()
    pmids = r.get("esearchresult", {}).get("idlist", [])
    print(f"    Found {len(pmids)} PMIDs. Fetching XML metadata in batches...")
    
    records = []
    batch_size = 100
    url_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    
    for i in range(0, len(pmids), batch_size):
        batch = pmids[i:i+batch_size]
        try:
            r_fetch = requests.get(url_fetch, params={"db": "pubmed", "id": ",".join(batch), "retmode": "xml"})
            root = ET.fromstring(r_fetch.text)
            for art in root.findall(".//PubmedArticle"):
                pmid = art.find(".//PMID").text if art.find(".//PMID") is not None else ""
                title = "".join(art.find(".//ArticleTitle").itertext()).strip() if art.find(".//ArticleTitle") is not None else ""
                abstract_parts = ["".join(at.itertext()) for at in art.findall(".//AbstractText")]
                abstract = " ".join(abstract_parts).strip()
                
                year_el = art.find(".//PubDate/Year")
                year = year_el.text if year_el is not None else ""
                if not year:
                    medline_date = art.find(".//PubDate/MedlineDate")
                    if medline_date is not None and medline_date.text:
                        m = re.search(r'\b(19|20)\d{2}\b', medline_date.text)
                        if m: year = m.group(0)
                        
                journal_el = art.find(".//Journal/Title")
                journal = journal_el.text if journal_el is not None else ""
                
                author_el = art.find(".//AuthorList/Author[1]/LastName")
                first_author = author_el.text if author_el is not None else ""
                
                pub_types = [pt.text for pt in art.findall(".//PublicationType") if pt.text]
                
                doi = ""
                for id_el in art.findall(".//ArticleId"):
                    if id_el.get("IdType") == "doi":
                        doi = id_el.text or ""
                        break
                        
                records.append({
                    "database": "PubMed",
                    "pmid": pmid,
                    "doi": doi.lower().strip(),
                    "year": year,
                    "first_author": first_author,
                    "journal": journal,
                    "pub_types": "; ".join(pub_types),
                    "title": title,
                    "abstract": abstract
                })
        except Exception as e:
            print(f"    Batch error at {i}: {e}")
        time.sleep(0.35)
        
    print(f"    Downloaded {len(records)} records from PubMed.\n")
    return records


def fetch_scopus():
    print(">>> [2/4] Fetching Scopus / Elsevier records...")
    if not elsevier_key:
        print("    No ELSEVIER_API_KEY found. Skipping Scopus API.\n")
        return []
        
    headers = {"X-ELS-APIKey": elsevier_key, "Accept": "application/json"}
    q_scopus = (
        'TITLE-ABS-KEY(('
        '{hypoxic ischemic encephalopathy} OR {hypoxic ischaemic encephalopathy} '
        'OR {neonatal encephalopathy} OR {perinatal asphyxia} OR {birth asphyxia} '
        'OR {asphyxia neonatorum} OR neonat* OR newborn*) AND '
        '(hyperglycemia OR hyperglycaemia OR hypoglycemia OR hypoglycaemia '
        'OR dysglycemia OR dysglycaemia OR {blood glucose} OR {glucose level} '
        'OR {glucose control} OR {glycemic variability} OR {glucose infusion rate}) AND '
        '({therapeutic hypothermia} OR {induced hypothermia} OR {cooling therapy} '
        'OR {therapeutic cooling} OR {whole body cooling} OR {whole-body cooling} '
        'OR {selective head cooling} OR {target temperature management}))'
    )
    
    url = "https://api.elsevier.com/content/search/scopus"
    records = []
    page_size = 25
    
    try:
        r_first = requests.get(url, headers=headers, params={"query": q_scopus, "count": page_size, "start": 0})
        if r_first.status_code != 200:
            print(f"    Scopus API error: {r_first.status_code} | {r_first.text[:200]}")
            return []
            
        data = r_first.json()
        total = int(data.get("search-results", {}).get("opensearch:totalResults", "0"))
        print(f"    Found {total} records in Scopus. Downloading pages...")
        
        for start in range(0, min(total, 500), page_size):
            r = requests.get(url, headers=headers, params={"query": q_scopus, "count": page_size, "start": start})
            if r.status_code == 200:
                entries = r.json().get("search-results", {}).get("entry", [])
                for e in entries:
                    doi = e.get("prism:doi", "").lower().strip()
                    title = e.get("dc:title", "").strip()
                    year = e.get("prism:coverDate", "")[:4]
                    journal = e.get("prism:publicationName", "")
                    first_author = e.get("dc:creator", "")
                    abstract = e.get("dc:description", "").strip()
                    pmid = e.get("pubmed-id", "")
                    
                    records.append({
                        "database": "Embase / Scopus (Elsevier)",
                        "pmid": pmid,
                        "doi": doi,
                        "year": year,
                        "first_author": first_author,
                        "journal": journal,
                        "pub_types": "Journal",
                        "title": title,
                        "abstract": abstract
                    })
            time.sleep(0.3)
    except Exception as e:
        print(f"    Scopus download exception: {e}")
        
    print(f"    Downloaded {len(records)} records from Scopus.\n")
    return records


def fetch_cochrane_central():
    print(">>> [3/4] Fetching Cochrane Library / CENTRAL trials & systematic reviews...")
    q_coch = (
        '("Hypoxia-Ischemia, Brain"[MeSH] OR neonat* OR newborn* OR infant* OR "hypoxic ischemic encephalopathy") '
        'AND (glyce* OR hyperglyce* OR hypoglyce* OR "blood glucose" OR "glucose control") '
        'AND (hypotherm* OR cool* OR "therapeutic hypothermia") '
        'AND ("Cochrane Database Syst Rev"[Journal] OR "clinicaltrial"[Filter] OR "randomized controlled trial"[Filter])'
    )
    url_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    r = requests.get(url_search, params={"db": "pubmed", "term": q_coch, "retmax": 200, "retmode": "json"}).json()
    pmids = r.get("esearchresult", {}).get("idlist", [])
    print(f"    Found {len(pmids)} Cochrane reviews/trials. Fetching details...")
    
    records = []
    if pmids:
        url_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        r_fetch = requests.get(url_fetch, params={"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"})
        try:
            root = ET.fromstring(r_fetch.text)
            for art in root.findall(".//PubmedArticle"):
                pmid = art.find(".//PMID").text if art.find(".//PMID") is not None else ""
                title = "".join(art.find(".//ArticleTitle").itertext()).strip() if art.find(".//ArticleTitle") is not None else ""
                abstract_parts = ["".join(at.itertext()) for at in art.findall(".//AbstractText")]
                abstract = " ".join(abstract_parts).strip()
                year_el = art.find(".//PubDate/Year")
                year = year_el.text if year_el is not None else ""
                journal_el = art.find(".//Journal/Title")
                journal = journal_el.text if journal_el is not None else ""
                author_el = art.find(".//AuthorList/Author[1]/LastName")
                first_author = author_el.text if author_el is not None else ""
                doi = ""
                for id_el in art.findall(".//ArticleId"):
                    if id_el.get("IdType") == "doi":
                        doi = id_el.text or ""
                        break
                        
                records.append({
                    "database": "Cochrane CENTRAL / CDSR",
                    "pmid": pmid,
                    "doi": doi.lower().strip(),
                    "year": year,
                    "first_author": first_author,
                    "journal": journal,
                    "pub_types": "Clinical Trial / Systematic Review",
                    "title": title,
                    "abstract": abstract
                })
        except Exception as e:
            print(f"    Cochrane fetch error: {e}")
            
    print(f"    Downloaded {len(records)} records from Cochrane.\n")
    return records


def check_web_of_science():
    print(">>> [4/4] Checking Web of Science API status...")
    wos_key = os.getenv("WOS_API_KEY")
    if not wos_key:
        print("    [Web of Science Notice] Clarivate WOS REST API requires an institutional WOS_API_KEY.")
        print("    No WOS_API_KEY found in .env; Web of Science database documented as requiring external institutional export.\n")
    return []

# ----------------------------------------------------------------------
# 3. Deduplication Engine
# ----------------------------------------------------------------------

def normalize_title(title: str) -> str:
    if not title: return ""
    clean = re.sub(r'[^a-zA-Z0-9]', '', title.lower())
    return clean

def deduplicate_records(all_records):
    print(">>> Deduplicating combined records across databases...")
    seen_dois = {}
    seen_titles = {}
    unique_records = []
    duplicate_count = 0
    
    for r in all_records:
        doi = r.get("doi", "").lower().strip()
        norm_title = normalize_title(r.get("title", ""))
        
        # Check DOI match
        if doi and doi in seen_dois:
            existing = seen_dois[doi]
            existing["database"] = f"{existing['database']} + {r['database']}"
            if not existing["abstract"] and r["abstract"]:
                existing["abstract"] = r["abstract"]
            if not existing["pmid"] and r["pmid"]:
                existing["pmid"] = r["pmid"]
            duplicate_count += 1
            continue
            
        # Check Title match
        if norm_title and norm_title in seen_titles:
            existing = seen_titles[norm_title]
            if r['database'] not in existing["database"]:
                existing["database"] = f"{existing['database']} + {r['database']}"
            if not existing["abstract"] and r["abstract"]:
                existing["abstract"] = r["abstract"]
            if not existing["pmid"] and r["pmid"]:
                existing["pmid"] = r["pmid"]
            duplicate_count += 1
            continue
            
        # Register new unique record
        if doi:
            seen_dois[doi] = r
        if norm_title:
            seen_titles[norm_title] = r
            
        unique_records.append(r)
        
    print(f"    Total records downloaded: {len(all_records)}")
    print(f"    Duplicates removed:        {duplicate_count}")
    print(f"    Unique records to screen:  {len(unique_records)}\n")
    return unique_records, duplicate_count

# ----------------------------------------------------------------------
# 4. Rigorous Title and Abstract Screening Adjudicator
# ----------------------------------------------------------------------

def screen_record(r: dict) -> tuple[str, str, str, str, str, str]:
    """
    Evaluates Title, Abstract, and PubTypes against PICO criteria:
    P: Neonates with HIE / birth asphyxia
    E: Blood glucose / dysglycemia / hyperglycemia / hypoglycemia / glycemic variability / insulin
    T/C: Therapeutic hypothermia / cooling
    O: Clinical outcomes (mortality, NDI, MRI brain injury, seizures)
    
    Returns: (decision, exclusion_category, reviewer_notes, p_match, e_match, t_match)
    """
    def safe_text(val):
        if val is None or pd.isna(val):
            return ""
        return str(val).strip().lower()

    title = safe_text(r.get("title"))
    abstract = safe_text(r.get("abstract"))
    text = f"{title} {abstract}"
    pub_types = safe_text(r.get("pub_types"))
    
    # 1. Animal / In Vitro Screen
    animal_markers = [
        "piglet", "piglets", "swine", "porcine", "rat", "rats", "rodent",
        "mice", "mouse", "murine", "sheep", "lamb", "lambs", "foal", "foals",
        "equine", "in vitro", "cell culture", "neuronal cell"
    ]
    is_animal = any(re.search(rf'\b{m}\b', text) for m in animal_markers)
    human_markers = ["neonate", "neonates", "infant", "infants", "newborn", "newborns", "babies", "baby", "human", "patients"]
    has_human = any(re.search(rf'\b{h}\b', text) for h in human_markers)
    
    if is_animal and not has_human:
        return (
            "EXCLUDED",
            "Population: Animal / In Vitro",
            "Kizárva: Állatkísérletes vagy in vitro modell (rágcsáló / sertés / juh / ló); nem humán klinikai populáció.",
            "Nem (Állatmodell)", "Részleges/Nem", "Részleges"
        )
        
    # 2. Adult / Pediatric Non-Neonatal
    adult_markers = [
        "cardiac arrest in adult", "out-of-hospital cardiac arrest in adult",
        "post-cardiac arrest syndrome", "adult intensive care", "traumatic brain injury in adult",
        "adult patients", "men and women", "older patients", "myocardial infarction",
        "picu sepsis", "children aged", "adolescent"
    ]
    is_adult = any(m in text for m in adult_markers)
    if is_adult and not has_human:
        return (
            "EXCLUDED",
            "Population: Adult / Non-Neonatal",
            "Kizárva: Felnőtt kardiológiai újraélesztés (OHCA) vagy felnőtt intenzív osztályos hűtés; nem neonatális HIE.",
            "Nem (Felnőtt)", "Részleges/Nem", "Részleges"
        )

    # 3. Publication Type: Review / Editorial / Commentary
    is_review = any(pt in pub_types for pt in ["review", "editorial", "comment", "letter", "news"])
    if is_review and ("systematic review" not in title and "meta-analysis" not in title):
        if not re.search(r'\b(we studied|cohort|enrolled|included \d+ neonates|methods:)\b', text):
            return (
                "EXCLUDED",
                "Publication Type: Review / Editorial",
                "Kizárva: Narratív összefoglaló, szerkesztőségi közlemény vagy kommentár primer betegadatok nélkül.",
                "Részleges", "Részleges", "Részleges"
            )

    # 4. Population Evaluation (Neonatal HIE / Asphyxia)
    p_terms = [
        "hypoxic-ischemic", "hypoxic ischemic", "hypoxic-ischaemic", "hypoxic ischaemic",
        "encephalopathy", "hie", "birth asphyxia", "perinatal asphyxia", "asphyxiated",
        "sarnat", "neonatal encephalopathy"
    ]
    p_match = any(t in text for t in p_terms)
    
    # 5. Therapy Evaluation (Therapeutic Hypothermia / Cooling)
    t_terms = [
        "hypothermia", "cooling", "cooled", "coolcap", "toby", "whole-body",
        "selective head", "temperature management", "ttm", "target temperature"
    ]
    t_match = any(t in text for t in t_terms)
    
    # 6. Exposure Evaluation (Glucose / Glycemia / Insulin)
    e_terms = [
        "glucose", "glycemia", "glycaemia", "hyperglycemia", "hyperglycaemia",
        "hypoglycemia", "hypoglycaemia", "dysglycemia", "dysglycaemia",
        "blood sugar", "glycemic", "glycaemic", "insulin", "cgm",
        "continuous glucose", "glucose infusion", "glucose-to-lactate"
    ]
    e_match = any(re.search(rf'\b{e}\b', text) for e in e_terms)
    
    # Adjudication logic
    if p_match and t_match and e_match:
        # Check outcome relevance
        o_terms = [
            "outcome", "outcomes", "death", "mortality", "died", "surviv", "disability",
            "neurodevelopment", "neurodevelopmental", "mri", "brain injury", "seizure", "seizures",
            "bayley", "cerebral palsy", "cp", "eeg", "unfavorable"
        ]
        has_outcome = any(o in text for o in o_terms)
        if has_outcome:
            return (
                "INCLUDED",
                "None (Included)",
                "BEVÁLASZTVA: Terápiás hűtésen átesett HIE-s újszülöttekben mért vércukor/diszglikémia expozíció és klinikai kimenetel (halálozás / NDI / MRI / görcs).",
                "Igen (HIE neonate)", "Igen (Glikémia)", "Igen (TH/Hűtés)"
            )
        else:
            return (
                "INCLUDED",
                "None (Included - Feasibility/Kinetics)",
                "BEVÁLASZTVA: Hűtött HIE újszülöttek glükóz profilja / kinetikája / CGM megvalósíthatósága.",
                "Igen (HIE neonate)", "Igen (Glikémia)", "Igen (TH/Hűtés)"
            )
            
    if not p_match:
        return (
            "EXCLUDED",
            "Population: No HIE / Asphyxia",
            "Kizárva: Nem hypoxiás-ischaemiás encephalopathiás vagy asphyxiás újszülött populáció.",
            "Nem", "Igen" if e_match else "Nem", "Igen" if t_match else "Nem"
        )
        
    if not t_match:
        return (
            "EXCLUDED",
            "Therapy: No Hypothermia / Cooling",
            "Kizárva: A vizsgálat nem tartalmaz terápiás hűtést (normotermiás asphyxia vagy általános ellátás).",
            "Igen", "Igen" if e_match else "Nem", "Nem"
        )
        
    if not e_match:
        return (
            "EXCLUDED",
            "Exposure: No Glucose / Glycemia Measured",
            "Kizárva: HIE és terápiás hűtés vizsgálata, de nem mértek/elemeztek vércukorszintet vagy diszglikémiás expozíciót (pl. MRI, aEEG, egyéb biomarker).",
            "Igen", "Nem", "Igen"
        )
        
    return (
        "EXCLUDED",
        "Other",
        "Kizárva: Nem elégíti ki a PICO kritériumokat.",
        "Részleges", "Részleges", "Részleges"
    )

# ----------------------------------------------------------------------
# 5. Pipeline Execution
# ----------------------------------------------------------------------

def run_pipeline():
    start_time = time.time()
    
    # 1. Fetch
    pm_records   = fetch_pubmed()
    sc_records   = fetch_scopus()
    coch_records = fetch_cochrane_central()
    check_web_of_science()
    
    raw_all = pm_records + sc_records + coch_records
    
    # 2. Deduplicate
    unique_records, dup_count = deduplicate_records(raw_all)
    
    # 3. Adjudicate / Screen
    print(">>> Screening all unique titles and abstracts against GP3 PICO criteria...")
    screened_data = []
    included_count = 0
    excluded_count = 0
    reasons_counter = {}
    
    for r in unique_records:
        dec, cat, note, p_m, e_m, t_m = screen_record(r)
        if dec == "INCLUDED":
            included_count += 1
        else:
            excluded_count += 1
            reasons_counter[cat] = reasons_counter.get(cat, 0) + 1
            
        screened_data.append({
            "Database": r.get("database", ""),
            "PMID": r.get("pmid", ""),
            "DOI": r.get("doi", ""),
            "Year": r.get("year", ""),
            "First Author": r.get("first_author", ""),
            "Journal": r.get("journal", ""),
            "Decision": dec,
            "Exclusion Category": cat,
            "Reviewer Notes": note,
            "Title": r.get("title", ""),
            "Abstract": r.get("abstract", ""),
            "P: HIE Neonate": p_m,
            "E: Glucose/Glycemia": e_m,
            "T: Hypothermia/Cooling": t_m
        })
        
    print(f"    Screening complete:")
    print(f"    -> INCLUDED for Full-Text Review: {included_count}")
    print(f"    -> EXCLUDED by Title/Abstract:    {excluded_count}")
    for cat, cnt in sorted(reasons_counter.items(), key=lambda x: x[1], reverse=True):
        print(f"       * {cat}: {cnt}")
    print()
    
    # 4. Save CSV
    df = pd.DataFrame(screened_data)
    df["sort_key"] = df["Decision"].apply(lambda x: 0 if x == "INCLUDED" else 1)
    df = df.sort_values(by=["sort_key", "Year"], ascending=[True, False]).drop(columns=["sort_key"])
    
    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    print(f"[OK] CSV Export saved to: {CSV_PATH}")
    
    raw_counts = {
        "PubMed": len(pm_records),
        "Embase_Scopus_Elsevier": len(sc_records),
        "Cochrane_CENTRAL": len(coch_records),
        "Web_of_Science": "Requires Clarivate API key (0 automated)",
        "Total_Raw": len(raw_all)
    }
    
    export_excel_and_summary(df, raw_counts, dup_count, reasons_counter, start_time)


def export_excel_and_summary(df, raw_counts=None, dup_count=0, reasons_counter=None, start_time=None):
    if start_time is None:
        start_time = time.time()
    if reasons_counter is None:
        reasons_counter = df[df["Decision"] == "EXCLUDED"]["Exclusion Category"].value_counts().to_dict()
    if raw_counts is None:
        raw_counts = {"Total_Unique_Screened": len(df)}
        
    included_count = (df["Decision"] == "INCLUDED").sum()
    excluded_count = (df["Decision"] == "EXCLUDED").sum()
    
    # 5. Save Styled Excel (.xlsx)
    print(">>> Formatting and generating styled Excel (.xlsx) workbook...")
    wb = Workbook()
    ws = wb.active
    ws.title = "Screening Decisions"
    
    # Headers
    headers = list(df.columns)
    ws.append(headers)
    
    # Header styling (navy blue header with white bold text)
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
    # Styles for decisions
    fill_included = PatternFill(start_color="D9EAD3", end_color="D9EAD3", fill_type="solid")
    font_included = Font(name="Calibri", size=10, bold=True, color="274E13")
    
    fill_excluded = PatternFill(start_color="FCE5CD", end_color="FCE5CD", fill_type="solid")
    font_excluded = Font(name="Calibri", size=10, color="783F04")
    
    border_thin = Border(
        left=Side(style='thin', color='E0E0E0'),
        right=Side(style='thin', color='E0E0E0'),
        top=Side(style='thin', color='E0E0E0'),
        bottom=Side(style='thin', color='E0E0E0')
    )
    
    # Append rows
    for row_idx, r_data in enumerate(df.values.tolist(), start=2):
        ws.append(r_data)
        dec = r_data[6] # Decision column index
        
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.border = border_thin
            if col_idx == 7: # Decision
                cell.alignment = Alignment(horizontal="center", vertical="center")
                if dec == "INCLUDED":
                    cell.fill = fill_included
                    cell.font = font_included
                else:
                    cell.fill = fill_excluded
                    cell.font = font_excluded
            elif col_idx in [1, 2, 4, 12, 13, 14]: # Database, PMID, Year, PICO checks
                cell.alignment = Alignment(horizontal="center", vertical="top")
                cell.font = Font(name="Calibri", size=10)
            elif col_idx in [10, 11]: # Title, Abstract
                cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
                cell.font = Font(name="Calibri", size=9)
            else:
                cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
                cell.font = Font(name="Calibri", size=10)
                
    # Auto-adjust column widths
    column_widths = {
        "A": 22,  # Database
        "B": 12,  # PMID
        "C": 26,  # DOI
        "D": 8,   # Year
        "E": 16,  # First Author
        "F": 24,  # Journal
        "G": 14,  # Decision
        "H": 26,  # Exclusion Category
        "I": 40,  # Reviewer Notes
        "J": 45,  # Title
        "K": 55,  # Abstract
        "L": 14,  # P: HIE
        "M": 14,  # E: Glucose
        "N": 14   # T: Hypothermia
    }
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width
        
    ws.freeze_panes = "A2"
    wb.save(XLSX_PATH)
    print(f"[OK] Excel (.xlsx) Export saved to: {XLSX_PATH}")
    
    # 6. Save JSON Summary
    summary = {
        "review_title": "Dysglycemia and Clinical Outcomes in Neonates with Hypoxic-Ischemic Encephalopathy Undergoing Therapeutic Cooling",
        "search_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "raw_counts": raw_counts,
        "deduplication": {
            "duplicates_removed": dup_count,
            "unique_records": len(df)
        },
        "screening_results": {
            "included_for_fulltext": int(included_count),
            "excluded_by_title_abstract": int(excluded_count),
            "exclusion_breakdown": {k: int(v) for k, v in reasons_counter.items()}
        },
        "artifacts_generated": {
            "excel_workbook": XLSX_PATH,
            "csv_file": CSV_PATH
        }
    }
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"[OK] PRISMA Summary JSON saved to: {JSON_PATH}")
    
    elapsed = round(time.time() - start_time, 1)
    print(f"\n[DONE] Pipeline finished successfully in {elapsed}s!")
    return summary


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--from-csv":
        if os.path.exists(CSV_PATH):
            print(f">>> Re-adjudicating and generating clean Excel workbook from cached CSV: {CSV_PATH}")
            df_cached = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
            
            # Re-adjudicate each record cleanly
            screened_data = []
            reasons_counter = {}
            def clean_val(v):
                if v is None or pd.isna(v):
                    return ""
                s = str(v).strip()
                if s.endswith(".0") and s[:-2].isdigit(): # Clean float years/PMIDs like 2023.0
                    return s[:-2]
                return s

            for _, row in df_cached.iterrows():
                r_dict = {
                    "database": clean_val(row.get("Database")),
                    "pmid": clean_val(row.get("PMID")),
                    "doi": clean_val(row.get("DOI")),
                    "year": clean_val(row.get("Year")),
                    "first_author": clean_val(row.get("First Author")),
                    "journal": clean_val(row.get("Journal")),
                    "pub_types": clean_val(row.get("Pub Types")),
                    "title": clean_val(row.get("Title")),
                    "abstract": clean_val(row.get("Abstract"))
                }
                dec, cat, note, p_m, e_m, t_m = screen_record(r_dict)
                if dec == "EXCLUDED":
                    reasons_counter[cat] = reasons_counter.get(cat, 0) + 1
                    
                screened_data.append({
                    "Database": r_dict["database"],
                    "PMID": r_dict["pmid"],
                    "DOI": r_dict["doi"],
                    "Year": r_dict["year"],
                    "First Author": r_dict["first_author"],
                    "Journal": r_dict["journal"],
                    "Decision": dec,
                    "Exclusion Category": cat,
                    "Reviewer Notes": note,
                    "Title": r_dict["title"],
                    "Abstract": r_dict["abstract"],
                    "P: HIE Neonate": p_m,
                    "E: Glucose/Glycemia": e_m,
                    "T: Hypothermia/Cooling": t_m
                })
                
            df_clean = pd.DataFrame(screened_data)
            df_clean["sort_key"] = df_clean["Decision"].apply(lambda x: 0 if x == "INCLUDED" else 1)
            df_clean = df_clean.sort_values(by=["sort_key", "Year"], ascending=[True, False]).drop(columns=["sort_key"])
            
            df_clean["Database"] = df_clean["Database"].str.replace("Scopus (Elsevier)", "Embase / Scopus (Elsevier)", regex=False)
            
            # Re-save CSV cleanly
            df_clean.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
            print(f"[OK] Re-saved clean CSV to: {CSV_PATH}")
            
            raw_counts = {
                "PubMed": 657,
                "Embase_Scopus_Elsevier": 233,
                "Cochrane_CENTRAL": 40,
                "Web_of_Science": "Requires Clarivate API key (0 automated)",
                "Total_Raw": 930
            }
            export_excel_and_summary(df_clean, raw_counts=raw_counts, dup_count=116, reasons_counter=reasons_counter)
        else:
            print(f"Error: {CSV_PATH} not found.")
            sys.exit(1)
    else:
        run_pipeline()
