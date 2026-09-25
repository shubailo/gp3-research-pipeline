import os
import requests
import json
import re
import time
import csv

# ---------------------------------------------------------
# Load Elsevier API Key from .env
# ---------------------------------------------------------
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
api_key = None
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("ELSEVIER_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

print("=========================================================")
print("  FULL PRISMA 2020 DATA EXTRACTION & SCREENING PIPELINE")
print("  Databases: PubMed, Embase (Elsevier API), Cochrane CENTRAL")
print("=========================================================\n")

# ---------------------------------------------------------
# 1. PubMed: Fetch ALL records (~602 hits)
# ---------------------------------------------------------
def fetch_all_pubmed():
    print("[1/3] Querying PubMed for ALL matching records...")
    query = '("Hypoxia-Ischemia, Brain"[MeSH] OR neonat* OR newborn* OR infant* OR perinatal* OR asphyxi* OR "hypoxic ischemic encephalopathy") AND (glyce* OR glycae* OR hyperglyce* OR hypoglyce* OR "blood glucose" OR "blood sugar" OR "glucose control" OR "glucose level") AND (hypotherm* OR cool* OR "temperature management")'
    
    url_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    r_search = requests.get(url_search, params={
        "db": "pubmed",
        "term": query,
        "retmax": 2000,  # Fetch ALL PMIDs without artificial cap
        "retmode": "json"
    }).json()
    
    pmids = r_search.get("esearchresult", {}).get("idlist", [])
    total_found = r_search.get("esearchresult", {}).get("count", len(pmids))
    print(f"  -> Total PubMed records found: {total_found} (Retrieved {len(pmids)} PMIDs)")
    
    if not pmids:
        return []

    # Fetch XML details in batches of 100
    records = []
    batch_size = 100
    url_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    
    import xml.etree.ElementTree as ET
    
    for i in range(0, len(pmids), batch_size):
        batch = pmids[i:i+batch_size]
        print(f"  -> Downloading PubMed XML batch {i//batch_size + 1}/{(len(pmids)+batch_size-1)//batch_size} ({len(batch)} items)...")
        r_fetch = requests.get(url_fetch, params={
            "db": "pubmed",
            "id": ",".join(batch),
            "retmode": "xml"
        })
        
        try:
            root = ET.fromstring(r_fetch.text)
            for art in root.findall(".//PubmedArticle"):
                pmid = art.find(".//PMID").text if art.find(".//PMID") is not None else ""
                title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
                abstract_parts = ["".join(at.itertext()) for at in art.findall(".//AbstractText")]
                abstract = " ".join(abstract_parts)
                
                year_el = art.find(".//PubDate/Year")
                year = year_el.text if year_el is not None else ""
                
                doi = ""
                for id_el in art.findall(".//ArticleId"):
                    if id_el.get("IdType") == "doi":
                        doi = id_el.text or ""
                        break
                        
                records.append({
                    "database": "PubMed",
                    "pmid": pmid,
                    "doi": doi.lower().strip(),
                    "title": title,
                    "abstract": abstract,
                    "year": year
                })
        except Exception as e:
            print(f"     Hiba a PubMed XML feldolgozásában: {e}")
        time.sleep(0.4)
        
    print(f"  -> Successfully processed {len(records)} PubMed records.\n")
    return records

# ---------------------------------------------------------
# 2. Elsevier Embase / Scopus: Fetch ALL records (Paginating)
# ---------------------------------------------------------
def fetch_all_embase():
    print("[2/3] Querying Elsevier Embase / Scopus API for ALL matching records...")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("  -> ERR: No Elsevier API key found in .env. Skipping Embase API pagination.")
        return []
        
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json"
    }
    
    query_exact = 'TITLE-ABS-KEY(("hypoxic ischemic encephalopathy" OR "neonatal encephalopathy" OR "asphyxia neonatorum") AND (dysglycemia OR hyperglycemia OR hypoglycemia OR "blood glucose") AND ("therapeutic hypothermia" OR "cooling therapy" OR "temperature management"))'
    url_scopus = "https://api.elsevier.com/content/search/scopus"
    
    # First request to get total count
    r_first = requests.get(url_scopus, headers=headers, params={"query": query_exact, "count": 25, "start": 0})
    if r_first.status_code != 200:
        print(f"  -> Elsevier API error: {r_first.status_code} | {r_first.text[:200]}")
        return []
        
    data_first = r_first.json()
    total_found = int(data_first.get("search-results", {}).get("opensearch:totalResults", "0"))
    print(f"  -> Total Embase/Scopus records found: {total_found}")
    
    records = []
    page_size = 25
    max_to_fetch = min(total_found, 1000) # Fetch up to 1000 items
    
    for start in range(0, max_to_fetch, page_size):
        print(f"  -> Fetching Embase page at offset {start}/{max_to_fetch}...")
        r_page = requests.get(url_scopus, headers=headers, params={"query": query_exact, "count": page_size, "start": start})
        if r_page.status_code == 200:
            entries = r_page.json().get("search-results", {}).get("entry", [])
            for e in entries:
                title = e.get("dc:title", "")
                doi = e.get("prism:doi", "").lower().strip()
                year = e.get("prism:coverDate", "")[:4]
                abstract = e.get("dc:description", "")
                records.append({
                    "database": "Embase (Elsevier)",
                    "pmid": "",
                    "doi": doi,
                    "title": title,
                    "abstract": abstract,
                    "year": year
                })
        else:
            print(f"     Warning: Error at offset {start}: {r_page.status_code}")
            break
        time.sleep(0.3)
        
    print(f"  -> Successfully retrieved {len(records)} Embase records.\n")
    return records

# ---------------------------------------------------------
# 3. Cochrane CENTRAL: Fetch ALL RCT / Cochrane records
# ---------------------------------------------------------
def fetch_all_cochrane():
    print("[3/3] Querying Cochrane CENTRAL & RCT Register...")
    query_cochrane = '("hypoxic ischemic encephalopathy" OR neonat* OR newborn*) AND (glyce* OR hyperglyce* OR hypoglyce* OR "blood glucose") AND (hypotherm* OR cool*) AND ("Cochrane Database Syst Rev"[Journal] OR "clinicaltrial"[Filter] OR "randomized controlled trial"[Filter])'
    
    url_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    r_search = requests.get(url_search, params={
        "db": "pubmed",
        "term": query_cochrane,
        "retmax": 500,
        "retmode": "json"
    }).json()
    
    pmids = r_search.get("esearchresult", {}).get("idlist", [])
    print(f"  -> Total Cochrane CENTRAL / RCT records found: {len(pmids)}")
    
    if not pmids:
        return []
        
    records = []
    url_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    r_fetch = requests.get(url_fetch, params={"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"})
    
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(r_fetch.text)
        for art in root.findall(".//PubmedArticle"):
            pmid = art.find(".//PMID").text if art.find(".//PMID") is not None else ""
            title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
            abstract_parts = ["".join(at.itertext()) for at in art.findall(".//AbstractText")]
            abstract = " ".join(abstract_parts)
            
            year_el = art.find(".//PubDate/Year")
            year = year_el.text if year_el is not None else ""
            
            doi = ""
            for id_el in art.findall(".//ArticleId"):
                if id_el.get("IdType") == "doi":
                    doi = id_el.text or ""
                    break
                    
            records.append({
                "database": "Cochrane CENTRAL",
                "pmid": pmid,
                "doi": doi.lower().strip(),
                "title": title,
                "abstract": abstract,
                "year": year
            })
    except Exception as e:
        print(f"     Hiba a Cochrane XML feldolgozásában: {e}")
        
    print(f"  -> Successfully retrieved {len(records)} Cochrane CENTRAL records.\n")
    return records

# Execute extractions
pm_data = fetch_all_pubmed()
emb_data = fetch_all_embase()
coc_data = fetch_all_cochrane()

# ---------------------------------------------------------
# 4. Merge & Deduplicate across all 3 databases
# ---------------------------------------------------------
all_raw = pm_data + emb_data + coc_data
seen_dois = set()
seen_titles = set()
dedup_library = []

for r in all_raw:
    norm_title = re.sub(r'\W+', '', r['title'].lower())
    doi = r['doi']
    
    if doi and doi in seen_dois:
        continue
    if norm_title and len(norm_title) > 10 and norm_title in seen_titles:
        continue
        
    if doi:
        seen_dois.add(doi)
    if norm_title:
        seen_titles.add(norm_title)
        
    dedup_library.append(r)

print("=========================================================")
print(f"DEDUPLICATION SUMMARY")
print(f"  * Raw total hits across all 3 databases: {len(all_raw)}")
print(f"  * PubMed hits: {len(pm_data)}")
print(f"  * Embase hits: {len(emb_data)}")
print(f"  * Cochrane CENTRAL hits: {len(coc_data)}")
print(f"  * UNIQUE DEDUPLICATED ARTICLES IN LIBRARY: {len(dedup_library)}")
print("=========================================================\n")

# ---------------------------------------------------------
# 5. Automated PICO Screening (Inclusion / Exclusion)
# ---------------------------------------------------------
included = []
excluded = []

def evaluate_pico_criteria(title, abstract):
    text = (title + " " + abstract).lower()
    
    # Exclusion criteria
    if any(k in text for k in ["animal", "rat", "mice", "porcine", "piglet", "lamb", "in vitro", "cell line"]):
        return False, "Kizárva: Állatkísérlet / In vitro modell"
    if any(k in text for k in ["review article", "systematic review", "meta-analysis", "editorial", "letter to editor"]) and "protocol" not in text:
        return False, "Kizárva: Szakirodalmi áttekintés / Editorial (Nem primer tanulmány)"
    if "adult" in text and not any(k in text for k in ["neonate", "infant", "newborn"]):
        return False, "Kizárva: Felnőtt populáció"
        
    # PICO match criteria
    p_match = any(k in text for k in ["hie", "hypoxic", "asphyxia", "encephalopathy", "neonate", "newborn", "infant"])
    e_match = any(k in text for k in ["glucose", "glycemia", "glycaemia", "hyperglycemia", "hyperglycaemia", "hypoglycemia", "hypoglycaemia", "dysglycemia", "mag", "cgm"])
    t_match = any(k in text for k in ["hypothermia", "cooling", "cooled", "chilled"])
    
    if p_match and e_match and t_match:
        return True, "Beválasztva: Mindhárom PICO domaint pontosan lefedő primer cikk"
    elif e_match and t_match:
        return True, "Beválasztva: Hűtés + Glükóz mérési adatokat tartalmazó vizsgálat"
    elif p_match and e_match:
        return True, "Beválasztva: Újszülöttkori HIE + Diszglikémia vizsgálat"
    else:
        return False, "Kizárva: Nem tartalmaz elegendő PICO domaint a szintézishez"

for art in dedup_library:
    is_inc, reason = evaluate_pico_criteria(art['title'], art['abstract'])
    art['screening_status'] = "INCLUDED" if is_inc else "EXCLUDED"
    art['reason'] = reason
    if is_inc:
        included.append(art)
    else:
        excluded.append(art)

print("=========================================================")
print("PRISMA 2020 AUTOMATED SCREENING RESULTS")
print("=========================================================")
print(f"  1. Identifikált rekordok (Összesen): {len(all_raw)}")
print(f"  2. Duplikációk eltávolítása után: {len(dedup_library)}")
print(f"  3. Cím & Absztrakt alapján KIZÁRVA: {len(excluded)}")
print(f"  4. Cím & Absztrakt alapján BEVÁLASZTVA: {len(included)}")
print("=========================================================\n")

print(f"Kiemelt Beválasztott Cikkek Kijelölése ({len(included)} db):")
for idx, a in enumerate(included[:15], 1):
    print(f"  {idx}. [{a['year']}] [{a['database']}] {a['title'][:80]}...")
    print(f"     Státusz: {a['reason']} | DOI: {a['doi']}\n")

# ---------------------------------------------------------
# 6. Save Complete Screening Library to JSON & CSV
# ---------------------------------------------------------
output_json = "meta_hyperglycaemia/screening_library.json"
output_csv = "meta_hyperglycaemia/screening_library.csv"

with open(output_json, "w", encoding="utf-8") as f:
    json.dump({
        "summary": {
            "total_raw_hits": len(all_raw),
            "pubmed_hits": len(pm_data),
            "embase_hits": len(emb_data),
            "cochrane_hits": len(coc_data),
            "deduplicated_total": len(dedup_library),
            "excluded_count": len(excluded),
            "included_count": len(included)
        },
        "included": included,
        "excluded": excluded,
        "library": dedup_library
    }, f, ensure_ascii=False, indent=2)

with open(output_csv, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Database", "PMID", "DOI", "Year", "Title", "Screening Status", "Reason", "Abstract"])
    for a in dedup_library:
        writer.writerow([a['database'], a['pmid'], a['doi'], a['year'], a['title'], a['screening_status'], a['reason'], a['abstract'][:300]])

print(f"Full PRISMA library saved to:")
print(f"  - JSON: {output_json}")
print(f"  - CSV: {output_csv}")
