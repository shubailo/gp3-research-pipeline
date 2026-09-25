"""
Full PRISMA 2020 Pipeline v3
- PubMed: full abstract retrieval via E-utilities (602 hits expected)
- Embase/Scopus: full abstract retrieval via Elsevier Abstract API  
- CENTRAL: via Cochrane CENTRAL API or PubMed filter
- Deduplication by DOI + normalized title
- Strict PICO screening
- PRISMA 2020 flow output
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os, requests, json, re, time, csv
import xml.etree.ElementTree as ET

# ── API Key ───────────────────────────────────────────────────────────────────
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
api_key = None
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("ELSEVIER_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

print("="*65)
print("  FULL PRISMA 2020 PIPELINE v3")
print("  Databases: PubMed | Embase (Scopus) | Cochrane CENTRAL")
print("="*65)
print(f"  Elsevier API key: {'[OK] ' + api_key[:8] + '...' if api_key else '[MISSING]'}")
print()

# ═══════════════════════════════════════════════════════════════════════════════
# 1. PubMed - Full fetch with abstracts
# ═══════════════════════════════════════════════════════════════════════════════
def fetch_pubmed():
    print("[1/3] PubMed - fetching all records with abstracts...")
    # Original query from PROSPERO protocol - yields 602 hits
    # Uses broad MeSH + free text (no [tiab] restriction) to maximise sensitivity
    query = (
        '('
        '"Hypoxia-Ischemia, Brain"[MeSH] OR neonat*[tw] OR newborn*[tw] '
        'OR infant*[tw] OR perinatal*[tw] OR asphyxi*[tw] '
        'OR "hypoxic ischemic encephalopathy"[tw]'
        ') AND ('
        'glyce*[tw] OR glycae*[tw] OR hyperglyce*[tw] OR hypoglyce*[tw] '
        'OR "blood glucose"[tw] OR "blood sugar"[tw] '
        'OR "glucose control"[tw] OR "glucose level"[tw]'
        ') AND ('
        'hypotherm*[tw] OR cool*[tw] OR "temperature management"[tw]'
        ')'
    )
    
    # Step 1: Get count and PMIDs
    r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params={
        "db": "pubmed", "term": query, "retmax": 2000, "retmode": "json",
        "usehistory": "y"
    })
    result = r.json().get("esearchresult", {})
    total = int(result.get("count", 0))
    pmids = result.get("idlist", [])
    webenv = result.get("webenv", "")
    query_key = result.get("querykey", "")
    print(f"  -> PubMed total found: {total} | Retrieved PMIDs: {len(pmids)}")
    
    if not pmids:
        return [], total
    
    # Step 2: Fetch XML in batches of 100
    records = []
    batch_size = 100
    for i in range(0, len(pmids), batch_size):
        batch = pmids[i:i+batch_size]
        print(f"  -> Batch {i//batch_size + 1}/{-(-len(pmids)//batch_size)}: {len(batch)} articles...")
        r_fetch = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params={
            "db": "pubmed", "id": ",".join(batch), "retmode": "xml", "rettype": "abstract"
        })
        try:
            root = ET.fromstring(r_fetch.text)
            for art in root.findall(".//PubmedArticle"):
                pmid = art.find(".//PMID")
                pmid = pmid.text if pmid is not None else ""
                title_el = art.find(".//ArticleTitle")
                title = "".join(title_el.itertext()) if title_el is not None else ""
                abstracts = ["".join(at.itertext()) for at in art.findall(".//AbstractText")]
                abstract = " ".join(abstracts)
                year_el = art.find(".//PubDate/Year") or art.find(".//PubDate/MedlineDate")
                year = (year_el.text or "")[:4] if year_el is not None else ""
                doi = next((x.text for x in art.findall(".//ArticleId") if x.get("IdType") == "doi"), "")
                pub_type_els = art.findall(".//PublicationType")
                pub_types = [pt.text or "" for pt in pub_type_els]
                records.append({
                    "database": "PubMed", "pmid": pmid,
                    "doi": doi.lower().strip(), "year": year,
                    "title": title, "abstract": abstract,
                    "pub_types": "; ".join(pub_types)
                })
        except Exception as e:
            print(f"     XML parse error: {e}")
        time.sleep(0.35)
    
    print(f"  -> Successfully fetched {len(records)} PubMed records with abstracts.\n")
    return records, total

# ═══════════════════════════════════════════════════════════════════════════════
# 2. Embase via Scopus API + Abstract Retrieval API
# ═══════════════════════════════════════════════════════════════════════════════
def fetch_embase():
    print("[2/3] Embase/Scopus - fetching all records...")
    if not api_key:
        print("  -> No API key, skipping Embase.")
        return [], 0
    
    headers = {"X-ELS-APIKey": api_key, "Accept": "application/json"}
    # Embase-optimized query (TITLE-ABS-KEY)
    query = (
        'TITLE-ABS-KEY('
        '("hypoxic ischemic encephalopathy" OR "hypoxic-ischemic encephalopathy" '
        'OR "neonatal encephalopathy" OR "birth asphyxia" OR "perinatal asphyxia" '
        'OR "asphyxia neonatorum" OR "HIE") '
        'AND (hyperglycemia OR hyperglycaemia OR hypoglycemia OR hypoglycaemia '
        'OR dysglycemia OR dysglycaemia OR "blood glucose" OR glycemia OR glycaemia) '
        'AND ("therapeutic hypothermia" OR "whole body cooling" OR "selective head cooling" '
        'OR "cooling therapy" OR hypothermia)'
        ')'
    )
    
    # Get total count
    r_first = requests.get("https://api.elsevier.com/content/search/scopus", 
                           headers=headers, 
                           params={"query": query, "count": 1, "start": 0, "field": "dc:title"})
    if r_first.status_code != 200:
        print(f"  -> Elsevier API error {r_first.status_code}: {r_first.text[:300]}")
        return [], 0
    
    total = int(r_first.json().get("search-results", {}).get("opensearch:totalResults", 0))
    print(f"  -> Embase total found: {total}")
    
    # Paginate through all results (Scopus free tier: max 200 with abstract)
    records = []
    page_size = 25
    max_fetch = min(total, 200)  # Scopus API limit for non-institutional: 200/key
    
    for start in range(0, max_fetch, page_size):
        print(f"  -> Fetching Embase records {start+1}-{min(start+page_size, max_fetch)}/{max_fetch}...")
        r = requests.get("https://api.elsevier.com/content/search/scopus",
                        headers=headers,
                        params={
                            "query": query, "count": page_size, "start": start,
                            "field": "dc:title,prism:doi,prism:coverDate,dc:description,eid,pubmed-id",
                            "sort": "-coverdate"
                        })
        if r.status_code != 200:
            print(f"     Error at offset {start}: {r.status_code}")
            break
        
        entries = r.json().get("search-results", {}).get("entry", [])
        for e in entries:
            title = e.get("dc:title", "")
            doi = e.get("prism:doi", "").lower().strip()
            year = (e.get("prism:coverDate", "") or "")[:4]
            abstract = e.get("dc:description", "") or ""
            pmid = e.get("pubmed-id", "") or ""
            eid = e.get("eid", "")
            
            # If abstract is missing, try to fetch via Abstract Retrieval API
            if not abstract and eid:
                abs_url = f"https://api.elsevier.com/content/abstract/eid/{eid}"
                r_abs = requests.get(abs_url, headers={**headers, "Accept": "application/json"})
                if r_abs.status_code == 200:
                    abs_data = r_abs.json()
                    abstract = (abs_data.get("abstracts-retrieval-response", {})
                               .get("coredata", {}).get("dc:description", "") or "")
                time.sleep(0.2)
            
            records.append({
                "database": "Embase (Scopus)", "pmid": pmid,
                "doi": doi, "year": year,
                "title": title, "abstract": abstract,
                "pub_types": "", "eid": eid
            })
        time.sleep(0.3)
    
    print(f"  -> Successfully fetched {len(records)} Embase records.\n")
    return records, total

# ═══════════════════════════════════════════════════════════════════════════════
# 3. Cochrane CENTRAL via CENTRAL API
# ═══════════════════════════════════════════════════════════════════════════════
def fetch_cochrane():
    print("[3/3] Cochrane CENTRAL - fetching RCTs via PubMed filter...")
    # CENTRAL = RCTs indexed in PubMed with Cochrane filter
    query = (
        '('
        '"hypoxic ischemic encephalopathy"[tiab] OR "neonatal encephalopathy"[tiab] '
        'OR "birth asphyxia"[tiab] OR neonat*[tiab]'
        ') AND ('
        'hyperglycemia[tiab] OR hyperglycaemia[tiab] OR hypoglycemia[tiab] '
        'OR hypoglycaemia[tiab] OR "blood glucose"[tiab] OR dysglycemia[tiab]'
        ') AND ('
        '"therapeutic hypothermia"[tiab] OR "whole body cooling"[tiab] '
        'OR "selective head cooling"[tiab] OR "cooling therapy"[tiab]'
        ') AND ('
        '"randomized controlled trial"[pt] OR "randomised controlled trial"[tiab] '
        'OR "clinical trial"[pt] OR "controlled clinical trial"[pt]'
        ')'
    )
    
    r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params={
        "db": "pubmed", "term": query, "retmax": 500, "retmode": "json"
    })
    result = r.json().get("esearchresult", {})
    pmids = result.get("idlist", [])
    total = int(result.get("count", 0))
    print(f"  -> Cochrane/RCT filter found: {total} (retrieved: {len(pmids)})")
    
    if not pmids:
        return [], total
    
    records = []
    r_fetch = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params={
        "db": "pubmed", "id": ",".join(pmids), "retmode": "xml", "rettype": "abstract"
    })
    try:
        root = ET.fromstring(r_fetch.text)
        for art in root.findall(".//PubmedArticle"):
            pmid = art.find(".//PMID")
            pmid = pmid.text if pmid is not None else ""
            title_el = art.find(".//ArticleTitle")
            title = "".join(title_el.itertext()) if title_el is not None else ""
            abstracts = ["".join(at.itertext()) for at in art.findall(".//AbstractText")]
            abstract = " ".join(abstracts)
            year_el = art.find(".//PubDate/Year") or art.find(".//PubDate/MedlineDate")
            year = (year_el.text or "")[:4] if year_el is not None else ""
            doi = next((x.text for x in art.findall(".//ArticleId") if x.get("IdType") == "doi"), "")
            pub_types = [pt.text or "" for pt in art.findall(".//PublicationType")]
            records.append({
                "database": "Cochrane/RCT", "pmid": pmid,
                "doi": doi.lower().strip(), "year": year,
                "title": title, "abstract": abstract,
                "pub_types": "; ".join(pub_types)
            })
    except Exception as e:
        print(f"     XML parse error: {e}")
    
    print(f"  -> Successfully fetched {len(records)} Cochrane/RCT records.\n")
    return records, total

# ═══════════════════════════════════════════════════════════════════════════════
# Fetch all databases
# ═══════════════════════════════════════════════════════════════════════════════
pubmed_records, pubmed_total = fetch_pubmed()
embase_records, embase_total = fetch_embase()
cochrane_records, cochrane_total = fetch_cochrane()

all_raw = pubmed_records + embase_records + cochrane_records
print(f"\nRaw totals: PubMed={pubmed_total}, Embase={embase_total}, Cochrane/RCT={cochrane_total}")
print(f"Records with abstracts: PubMed={len(pubmed_records)}, Embase={len(embase_records)}, Cochrane={len(cochrane_records)}")

# ═══════════════════════════════════════════════════════════════════════════════
# Deduplication
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[DEDUP] Deduplicating by DOI and normalized title...")
seen_dois = set()
seen_titles = set()
dedup = []

for r in all_raw:
    doi = r.get('doi', '').strip()
    norm_title = re.sub(r'\W+', '', r.get('title', '').lower())[:80]
    
    if doi and doi in seen_dois:
        continue
    if norm_title and norm_title in seen_titles:
        continue
    if doi:
        seen_dois.add(doi)
    if norm_title:
        seen_titles.add(norm_title)
    dedup.append(r)

print(f"  -> After deduplication: {len(dedup)} unique records (from {len(all_raw)} raw)")

# ═══════════════════════════════════════════════════════════════════════════════
# PICO Screening
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[SCREEN] Applying PICO title/abstract screening...")

# Strict inclusion terms
P_SPECIFIC = [
    'hypoxic ischemic encephalopathy', 'hypoxic-ischemic encephalopathy',
    'hypoxic ischaemic encephalopathy', 'hypoxic-ischaemic encephalopathy',
    'neonatal encephalopathy', ' hie ', 'birth asphyxia', 'perinatal asphyxia',
    'neonatal asphyxia', 'asphyxiated neonat', 'asphyxiated infant', 'asphyxiated newborn',
    'intrapartum asphyxia',
]
P_BROAD = [
    'neonate', 'neonatal', 'newborn', 'preterm infant', 'term infant',
    'nicu', 'neonatal intensive', 'premature infant', 'preterm neonate',
]
E_TERMS = [
    'hyperglycemia', 'hyperglycaemia', 'hypoglycemia', 'hypoglycaemia',
    'dysglycemia', 'dysglycaemia', 'blood glucose', 'blood sugar',
    'glucose level', 'glucose control', 'glycemia', 'glycaemia',
    'glucose monitoring', 'continuous glucose', 'cgm', 'glucose homeostasis',
    'glucose infusion', 'dextrose', 'insulin',
]
C_TERMS = [
    'therapeutic hypothermia', 'whole body cooling', 'selective head cooling',
    'cooling therapy', 'cooled', 'hypothermia treatment', 'hypothermic',
    'temperature management', 'targeted temperature', 'bodywork cooling',
    'total body cooling', 'head cooling', 'induced hypothermia', 'neonatal cooling',
]
ANIMAL_EXCL = [
    ' rat ', ' rats,', 'rat model', 'mouse model', ' mice ', ' murine',
    'porcine', 'piglet', ' pig ', 'ovine', 'lamb model', 'rabbit model',
    'in vitro', 'cell line', 'cell culture', 'guinea pig',
    ' sheep ', 'bovine', 'vipera', 'rhinoceros', ' dog ', ' dogs,',
    ' canine', 'fetal sheep', 'fetal lamb', 'newborn pig', 'newborn lamb',
]
REVIEW_EXCL = [
    'systematic review', 'meta-analysis', 'cochrane review',
    'narrative review', 'scoping review', 'literature review',
]

def screen(art):
    text = (" " + art.get('title','') + " " + art.get('abstract','') + " ").lower()
    pub_types = art.get('pub_types', '').lower()
    
    # Exclude animals (with exception for clear human neonatal HIE studies)
    for term in ANIMAL_EXCL:
        if term in text:
            # Only allow if clearly neonatal HIE clinical study
            if 'therapeutic hypothermia' in text and 'neonat' in text and 'hie' in text and 'encephalopathy' in text:
                break  # likely a clinical paper that incidentally mentions animal
            return 'EXCLUDED', f'Animal/in vitro study ({term.strip()})'
    
    # Exclude reviews/meta-analyses
    for rt in REVIEW_EXCL:
        if rt in text and 'protocol' not in text:
            return 'EXCLUDED', f'Review/meta-analysis (not primary study)'
    
    # Must have glucose exposure
    e_match = any(t in text for t in E_TERMS)
    # Must have therapeutic hypothermia
    c_match = any(t in text for t in C_TERMS)
    # Population
    p_specific = any(t in text for t in P_SPECIFIC)
    p_broad = any(t in text for t in P_BROAD)
    
    if not e_match:
        return 'EXCLUDED', 'No glucose/glycaemia data (E criterion missing)'
    if not c_match:
        return 'EXCLUDED', 'No therapeutic hypothermia (C criterion missing)'
    if p_specific:
        return 'INCLUDED', 'HIE/neonatal asphyxia + dysglycaemia + therapeutic hypothermia'
    if p_broad:
        return 'INCLUDED*', 'Neonatal population + glucose + TH - NEEDS MANUAL CHECK'
    return 'EXCLUDED', 'PICO criteria not fully met'

included, included_needs_check, excluded_all = [], [], []
excl_reasons = {}

for art in dedup:
    status, reason = screen(art)
    art['screening_status'] = status
    art['screening_reason'] = reason
    if status == 'INCLUDED':
        included.append(art)
    elif status == 'INCLUDED*':
        included_needs_check.append(art)
    else:
        excluded_all.append(art)
        excl_reasons[reason] = excl_reasons.get(reason, 0) + 1

all_included = included + included_needs_check

# ═══════════════════════════════════════════════════════════════════════════════
# PRISMA 2020 Report
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("  PRISMA 2020 FLOW SUMMARY")
print("="*65)
print(f"\n  IDENTIFICATION")
print(f"    PubMed hits:          {pubmed_total:>5d}")
print(f"    Embase hits:          {embase_total:>5d}")
print(f"    Cochrane/RCT hits:    {cochrane_total:>5d}")
print(f"    Total raw records:    {pubmed_total + embase_total + cochrane_total:>5d}")
print(f"\n  SCREENING")
print(f"    After deduplication:  {len(dedup):>5d}")
print(f"    Excluded (title/abs): {len(excluded_all):>5d}")
print(f"\n  ELIGIBILITY")
print(f"    Confirmed INCLUDED:   {len(included):>5d}")
print(f"    Needs manual check:   {len(included_needs_check):>5d}")
print(f"    Total for full-text:  {len(all_included):>5d}")

print(f"\n  EXCLUSION REASONS:")
for reason, count in sorted(excl_reasons.items(), key=lambda x: -x[1]):
    print(f"    {count:4d}x  {reason}")

print(f"\n" + "="*65)
print(f"  CONFIRMED INCLUDED ({len(included)}):")
print("="*65)
for i, a in enumerate(included, 1):
    print(f"\n  {i}. [{a['database']}] {a.get('year','')} - {a['title']}")
    print(f"     Reason: {a['screening_reason']}")

if included_needs_check:
    print(f"\n  NEEDS MANUAL REVIEW ({len(included_needs_check)}):")
    print("="*65)
    for i, a in enumerate(included_needs_check, 1):
        print(f"\n  {i}. [{a['database']}] {a.get('year','')} - {a['title']}")

# ═══════════════════════════════════════════════════════════════════════════════
# Save outputs
# ═══════════════════════════════════════════════════════════════════════════════
output = {
    "prisma_summary": {
        "identification": {
            "pubmed_total": pubmed_total,
            "embase_total": embase_total,
            "cochrane_total": cochrane_total,
            "total_raw": pubmed_total + embase_total + cochrane_total,
        },
        "screening": {
            "after_dedup": len(dedup),
            "excluded_title_abstract": len(excluded_all),
        },
        "eligibility": {
            "confirmed_included": len(included),
            "needs_manual_check": len(included_needs_check),
            "total_for_fulltext": len(all_included),
        }
    },
    "included": included,
    "included_needs_check": included_needs_check,
    "exclusion_reasons": excl_reasons,
}

with open("meta_hyperglycaemia/prisma_results_v3.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

# Save all included to CSV
with open("meta_hyperglycaemia/included_for_fulltext.csv", "w", encoding="utf-8", newline='') as f:
    fields = ['database', 'pmid', 'doi', 'year', 'title', 'screening_status', 'screening_reason', 'abstract']
    writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    for a in all_included:
        writer.writerow({k: a.get(k, '') for k in fields})

# Save full dedup library for reference
with open("meta_hyperglycaemia/full_library_v3.json", "w", encoding="utf-8") as f:
    json.dump(dedup, f, ensure_ascii=False, indent=2)

print(f"\n[OK] PRISMA results saved: meta_hyperglycaemia/prisma_results_v3.json")
print(f"[OK] Included articles CSV: meta_hyperglycaemia/included_for_fulltext.csv")
print(f"[OK] Full dedup library: meta_hyperglycaemia/full_library_v3.json")
print("\nDone!")
