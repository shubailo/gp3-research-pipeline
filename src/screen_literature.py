#!/usr/bin/env python3
"""
Reusable PRISMA Literature Screening Engine
===========================================
General-purpose tool for systematic reviews and meta-analyses to deduplicate,
filter, and screen titles and abstracts against configurable PICO criteria.

Usage:
    # 1. Screen an existing search results JSON file:
    python src/screen_literature.py --from-file results/search_20260912_135015.json --p-terms "hie,neonate" --e-terms "cooling,hypothermia"

    # 2. Run a direct PubMed query and screen:
    python src/screen_literature.py --query "mild HIE cooling" --max-results 100

    # 3. Basic science screening (retaining animal models):
    python src/screen_literature.py --from-file results/search.json --keep-animals
"""

import os
import sys
import json
import re
import csv
import argparse
from datetime import datetime
import io

# Safe Windows UTF-8 reconfigure without stream closure
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from api_clients.pubmed_client import PubMedClient
except ImportError:
    PubMedClient = None

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def parse_abstract_digest(digest_text: str) -> list[dict]:
    """Parse human-readable abstract_digest string back into structured article records."""
    entries = re.split(r'\n(?=\[\d+\])', digest_text)
    records = []
    for entry in entries:
        entry = entry.strip()
        if not entry or not entry.startswith('['):
            continue
        
        lines = entry.split('\n')
        header_line = lines[0].strip()
        
        m = re.match(r'^\[\d+\]\s+(.*?)(?:\s+\((\d{4}|\?)\))?(?:\s+[—\-]\s+(.*))?$', header_line)
        if m:
            title = m.group(1).strip()
            year = m.group(2) if m.group(2) and m.group(2) != '?' else ""
            source = m.group(3).strip() if m.group(3) else "Digest"
        else:
            title = header_line
            year = ""
            source = "Digest"
            
        doi = ""
        pmid = ""
        abstract_lines = []
        
        for line in lines[1:]:
            line_str = line.strip()
            if line_str.startswith("DOI:"):
                doi = line_str.replace("DOI:", "").strip()
            elif line_str.startswith("PMID:"):
                pmid = line_str.replace("PMID:", "").strip()
            else:
                abstract_lines.append(line_str)
                
        abstract = " ".join([l for l in abstract_lines if l]).strip()
        
        records.append({
            "source": source,
            "title": title,
            "year": year,
            "doi": doi,
            "pmid": pmid,
            "abstract": abstract
        })
    return records

def load_from_file(json_path: str) -> list[dict]:
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"File not found: {json_path}")
    with open(json_path, "r", encoding="utf-8", errors="ignore") as f:
        data = json.load(f)
    
    # 1. Handle raw list of articles
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # 2. Check standard list keys
        for k in ["articles", "library", "results", "publications"]:
            if k in data and isinstance(data[k], list):
                return data[k]
        # 3. Check included / excluded library formats
        if "included" in data or "excluded" in data:
            records = []
            if isinstance(data.get("included"), list):
                records.extend(data["included"])
            if isinstance(data.get("excluded"), list):
                records.extend(data["excluded"])
            if records:
                return records
        # 4. Check abstract_digest fallback
        if "abstract_digest" in data and isinstance(data["abstract_digest"], str):
            parsed = parse_abstract_digest(data["abstract_digest"])
            if parsed:
                return parsed
    return []

def fetch_direct_pubmed(query: str, max_results: int = 100, email: str = "researcher@example.com") -> list[dict]:
    import requests
    import xml.etree.ElementTree as ET
    
    print(f"🔍 Querying PubMed: '{query}' (Max results: {max_results})...")
    url_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    r_search = requests.get(url_search, params={
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "email": email
    }).json()
    
    pmids = r_search.get("esearchresult", {}).get("idlist", [])
    if not pmids:
        print("⚠️ No PMIDs found.")
        return []
        
    print(f"📥 Fetching metadata for {len(pmids)} PMIDs...")
    url_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    r_fetch = requests.get(url_fetch, params={
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "email": email
    })
    
    root = ET.fromstring(r_fetch.text)
    records = []
    for art in root.findall(".//PubmedArticle"):
        pmid = art.find(".//PMID").text if art.find(".//PMID") is not None else ""
        title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
        abstract_parts = ["".join(at.itertext()) for at in art.findall(".//AbstractText")]
        abstract = " ".join(abstract_parts)
        
        year_el = art.find(".//PubDate/Year")
        if year_el is None:
            year_el = art.find(".//PubDate/MedlineDate")
        year = year_el.text[:4] if year_el is not None and year_el.text else ""
        
        doi = ""
        for id_el in art.findall(".//ArticleId"):
            if id_el.get("IdType") == "doi":
                doi = id_el.text or ""
                break
                
        journal = art.find(".//Journal/Title")
        journal_title = journal.text if journal is not None else ""
        
        records.append({
            "source": "PubMed",
            "pmid": pmid,
            "doi": doi.lower().strip(),
            "title": title.strip(),
            "abstract": abstract.strip(),
            "journal": journal_title,
            "year": year
        })
    return records

def deduplicate_records(records: list[dict]) -> tuple[list[dict], int]:
    seen_dois = set()
    seen_titles = set()
    deduped = []
    duplicates_removed = 0
    
    for r in records:
        doi = r.get("doi", "").lower().strip()
        raw_title = r.get("title", "").lower()
        norm_title = re.sub(r"\W+", "", raw_title)
        
        is_dup = False
        if doi and doi in seen_dois:
            is_dup = True
        elif norm_title and norm_title in seen_titles:
            is_dup = True
            
        if is_dup:
            duplicates_removed += 1
            continue
            
        if doi:
            seen_dois.add(doi)
        if norm_title:
            seen_titles.add(norm_title)
            
        deduped.append(r)
        
    return deduped, duplicates_removed

def evaluate_article(
    article: dict, 
    p_terms: list[str], 
    e_terms: list[str], 
    o_terms: list[str],
    exclude_animals: bool = True,
    exclude_reviews: bool = True,
    exclude_adults: bool = True
) -> tuple[str, str, bool, bool, bool]:
    title = article.get("title", "")
    abstract = article.get("abstract", "")
    text = f"{title} {abstract}".lower()
    
    # --- Exclusion Checks ---
    if exclude_animals:
        animal_keywords = ["animal model", "in mice", "in rats", "rat model", "murine model", 
                           "porcine model", "piglet model", "in piglets", "lamb model", "in vitro", "cell culture", "cell line"]
        if any(k in text for k in animal_keywords):
            return "EXCLUDED", "Excluded: Animal / In Vitro model", False, False, False

    if exclude_reviews:
        review_keywords = ["systematic review", "meta-analysis", "review article", "scoping review", "editorial", "letter to editor", "narrative review"]
        if any(k in text for k in review_keywords) and "protocol" not in text:
            return "EXCLUDED", "Excluded: Review / Editorial (Non-primary study)", False, False, False

    if exclude_adults:
        adult_keywords = ["adult patient", "elderly", "adult intensive care", "geriatric"]
        pediatric_keywords = ["neonate", "newborn", "infant", "pediatric", "paediatric", "child"]
        if any(k in text for k in adult_keywords) and not any(k in text for k in pediatric_keywords):
            return "EXCLUDED", "Excluded: Adult population", False, False, False

    # --- PICO Inclusion Matching ---
    p_match = any(t.lower() in text for t in p_terms) if p_terms else True
    e_match = any(t.lower() in text for t in e_terms) if e_terms else True
    o_match = any(t.lower() in text for t in o_terms) if o_terms else True
    
    if p_match and e_match and o_match:
        return "INCLUDED", "Included: Full PICO criteria met", p_match, e_match, o_match
    elif p_match and e_match:
        return "INCLUDED", "Included: Population + Exposure match (Outcome unconfirmed in abstract)", p_match, e_match, o_match
    elif e_match and o_match:
        return "UNSURE", "Unsure: Secondary review needed (Exposure + Outcome match, unclear population)", p_match, e_match, o_match
    elif p_match:
        return "EXCLUDED", "Excluded: Population match only (Missing exposure/intervention)", p_match, e_match, o_match
    elif e_match:
        return "EXCLUDED", "Excluded: Exposure match only (Missing target population)", p_match, e_match, o_match
    else:
        return "EXCLUDED", "Excluded: Neither Population nor Exposure found", p_match, e_match, o_match

def run_screening(
    records: list[dict],
    p_terms: list[str],
    e_terms: list[str],
    o_terms: list[str],
    exclude_animals: bool = True,
    exclude_reviews: bool = True,
    exclude_adults: bool = True,
    output_dir: str = "results"
) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    total_raw = len(records)
    deduped, dups_removed = deduplicate_records(records)
    
    included = []
    unsure = []
    excluded = []
    exclusion_reasons = {}
    
    for art in deduped:
        status, reason, p_m, e_m, o_m = evaluate_article(
            art, p_terms, e_terms, o_terms, 
            exclude_animals=exclude_animals, 
            exclude_reviews=exclude_reviews, 
            exclude_adults=exclude_adults
        )
        art["screening_status"] = status
        art["screening_reason"] = reason
        art["p_match"] = p_m
        art["e_match"] = e_m
        art["o_match"] = o_m
        
        if status == "INCLUDED":
            included.append(art)
        elif status == "UNSURE":
            unsure.append(art)
        else:
            excluded.append(art)
            exclusion_reasons[reason] = exclusion_reasons.get(reason, 0) + 1

    # --- Print PRISMA 2020 Flow Table ---
    print(f"\n{Colors.BOLD}{Colors.BLUE}========================================================================{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}               PRISMA 2020 AUTOMATED SCREENING REPORT                   {Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}========================================================================{Colors.RESET}")
    print(f"Total raw records identified:         {total_raw:>6}")
    print(f"Duplicates removed:                   {dups_removed:>6}")
    print(f"Unique records screened (Title/Abs):  {len(deduped):>6}")
    print(f"-" * 72)
    print(f"{Colors.RED}Records EXCLUDED:{Colors.RESET}                     {len(excluded):>6}")
    for reason, count in sorted(exclusion_reasons.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {reason:<48} : {count:>4}")
    print(f"-" * 72)
    print(f"{Colors.YELLOW}Records flagged for UNSURE / 2nd Review:{Colors.RESET} {len(unsure):>6}")
    print(f"{Colors.GREEN}{Colors.BOLD}Records INCLUDED for Full-Text Retrieval:{Colors.RESET} {len(included):>5}")
    print(f"{Colors.BOLD}========================================================================{Colors.RESET}\n")

    # Print Top Included Studies
    if included:
        print(f"{Colors.BOLD}Top Included Studies Preview (showing up to 10 of {len(included)}):{Colors.RESET}")
        for idx, a in enumerate(included[:10], 1):
            pmid_str = f"PMID: {a['pmid']}" if a.get('pmid') else ""
            doi_str = f"DOI: {a['doi']}" if a.get('doi') else ""
            id_info = " | ".join(filter(None, [pmid_str, doi_str]))
            print(f"  {Colors.BOLD}{idx}. [{a.get('year', 'N/A')}] {a['title'][:95]}...{Colors.RESET}")
            print(f"     Status: {Colors.GREEN}{a['screening_reason']}{Colors.RESET} | {id_info}")

    # Export to JSON
    json_out_path = os.path.join(output_dir, f"screening_results_{timestamp}.json")
    with open(json_out_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "prisma_flow": {
                "identified": total_raw,
                "duplicates_removed": dups_removed,
                "screened": len(deduped),
                "excluded": len(excluded),
                "unsure": len(unsure),
                "included": len(included),
                "exclusion_breakdown": exclusion_reasons
            },
            "pico_filters": {"p": p_terms, "e": e_terms, "o": o_terms},
            "included": included,
            "unsure": unsure,
            "excluded": excluded
        }, f, ensure_ascii=False, indent=2)

    # Export to CSV
    csv_out_path = os.path.join(output_dir, f"screening_results_{timestamp}.csv")
    with open(csv_out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["PMID", "DOI", "Year", "Journal", "Status", "Reason", "Title", "Abstract"])
        for a in included + unsure + excluded:
            writer.writerow([
                a.get("pmid", ""),
                a.get("doi", ""),
                a.get("year", ""),
                a.get("journal", ""),
                a.get("screening_status", ""),
                a.get("screening_reason", ""),
                a.get("title", ""),
                a.get("abstract", "")
            ])

    print(f"\n{Colors.BOLD}Artifacts Exported:{Colors.RESET}")
    print(f"  - JSON Report: {json_out_path}")
    print(f"  - CSV Library: {csv_out_path}")
    
    return {
        "included_count": len(included),
        "unsure_count": len(unsure),
        "excluded_count": len(excluded),
        "json_path": json_out_path,
        "csv_path": csv_out_path
    }

def main():
    parser = argparse.ArgumentParser(description="PRISMA 2020 Automated Literature Screening Engine.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--from-file", help="Path to search results JSON file")
    group.add_argument("--query", help="Direct PubMed search query")
    
    parser.add_argument("--max-results", type=int, default=100, help="Max results for direct PubMed query")
    parser.add_argument("--p-terms", default="", help="Comma-separated Population keywords (e.g. 'hie,neonate,infant')")
    parser.add_argument("--e-terms", default="", help="Comma-separated Exposure/Intervention keywords (e.g. 'cooling,hypothermia')")
    parser.add_argument("--o-terms", default="", help="Comma-separated Outcome keywords (e.g. 'mortality,bayley,death')")
    parser.add_argument("--keep-animals", action="store_true", help="Do not exclude animal and in vitro models")
    parser.add_argument("--keep-reviews", action="store_true", help="Do not exclude review articles and editorials")
    parser.add_argument("--keep-adults", action="store_true", help="Do not exclude adult populations")
    parser.add_argument("--dual-adjudicate", action="store_true", help="Automatically trigger PRISMA 2020 full-text adjudication on included/unsure candidates")
    parser.add_argument("--project", default="neonatal_antibiotics", help="Project slug for adjudication (default: neonatal_antibiotics)")
    parser.add_argument("--output", default="results", help="Output directory for reports (default: results)")
    
    args = parser.parse_args()
    
    # Parse terms
    p_terms = [t.strip() for t in args.p_terms.split(",") if t.strip()]
    e_terms = [t.strip() for t in args.e_terms.split(",") if t.strip()]
    o_terms = [t.strip() for t in args.o_terms.split(",") if t.strip()]
    
    if args.from_file:
        records = load_from_file(args.from_file)
    else:
        records = fetch_direct_pubmed(args.query, max_results=args.max_results)
        
    if not records:
        print("❌ No records to screen. Exiting.")
        sys.exit(1)
        
    res = run_screening(
        records=records,
        p_terms=p_terms,
        e_terms=e_terms,
        o_terms=o_terms,
        exclude_animals=not args.keep_animals,
        exclude_reviews=not args.keep_reviews,
        exclude_adults=not args.keep_adults,
        output_dir=args.output
    )

    if args.dual_adjudicate:
        print("\n" + "=" * 72)
        print("  TRIGGERING PHASE 2/3 FULL-TEXT ADJUDICATION PIPELINE...")
        print("=" * 72)
        from src.full_text_adjudicator import run_adjudication
        with open(res["json_path"], "r", encoding="utf-8") as f:
            scr_data = json.load(f)
        candidates = scr_data.get("included", []) + scr_data.get("unsure", [])
        if candidates:
            run_adjudication(
                records=candidates,
                project=args.project,
                output_dir=os.path.join(args.output, args.project) if args.output == "results" else args.output
            )
        else:
            print("⚠️ No candidates eligible for full-text adjudication.")

if __name__ == "__main__":
    main()
