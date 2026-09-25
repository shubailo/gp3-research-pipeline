import os
import requests
import json
import re

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
api_key = None
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("ELSEVIER_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

print("=== STARTING AUTOMATED PRISMA SCREENING PIPELINE ===")

# 1. Fetch records from PubMed
def fetch_pubmed_records():
    query = '("Hypoxia-Ischemia, Brain"[MeSH] OR neonat* OR newborn* OR infant* OR perinatal* OR asphyxi* OR "hypoxic ischemic encephalopathy") AND (glyce* OR glycae* OR hyperglyce* OR hypoglyce* OR "blood glucose" OR "blood sugar" OR "glucose control" OR "glucose level") AND (hypotherm* OR cool* OR "temperature management")'
    url_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    r_search = requests.get(url_search, params={"db": "pubmed", "term": query, "retmax": 100, "retmode": "json"}).json()
    pmids = r_search.get("esearchresult", {}).get("idlist", [])
    print(f"[PubMed] Found {len(pmids)} PMIDs for screening.")
    
    if not pmids:
        return []
        
    url_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    r_fetch = requests.get(url_fetch, params={"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"})
    
    import xml.etree.ElementTree as ET
    root = ET.fromstring(r_fetch.text)
    
    records = []
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
            "source": "PubMed",
            "pmid": pmid,
            "doi": doi.lower().strip(),
            "title": title,
            "abstract": abstract,
            "year": year
        })
    return records

# 2. Fetch records from Elsevier / Embase API
def fetch_elsevier_records():
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("[Elsevier API] No key found, skipping API fetch.")
        return []
        
    headers = {"X-ELS-APIKey": api_key, "Accept": "application/json"}
    query_exact = 'TITLE-ABS-KEY(("hypoxic ischemic encephalopathy" OR "neonatal encephalopathy" OR "asphyxia neonatorum") AND (dysglycemia OR hyperglycemia OR hypoglycemia OR "blood glucose") AND ("therapeutic hypothermia" OR "cooling therapy" OR "temperature management"))'
    url_scopus = "https://api.elsevier.com/content/search/scopus"
    
    r = requests.get(url_scopus, headers=headers, params={"query": query_exact, "count": 100, "sort": "-coverDate"})
    records = []
    if r.status_code == 200:
        data = r.json()
        entries = data.get("search-results", {}).get("entry", [])
        print(f"[Elsevier API] Found {len(entries)} entries for screening.")
        for e in entries:
            title = e.get("dc:title", "")
            doi = e.get("prism:doi", "").lower().strip()
            year = e.get("prism:coverDate", "")[:4]
            abstract = e.get("dc:description", "")
            records.append({
                "source": "Embase/Elsevier",
                "pmid": "",
                "doi": doi,
                "title": title,
                "abstract": abstract,
                "year": year
            })
    return records

pm_records = fetch_pubmed_records()
els_records = fetch_elsevier_records()

# 3. Merge & Deduplicate
all_raw = pm_records + els_records
seen_dois = set()
seen_titles = set()
dedup_library = []

for r in all_raw:
    norm_title = re.sub(r'\W+', '', r['title'].lower())
    doi = r['doi']
    
    if doi and doi in seen_dois:
        continue
    if norm_title and norm_title in seen_titles:
        continue
        
    if doi:
        seen_dois.add(doi)
    if norm_title:
        seen_titles.add(norm_title)
        
    dedup_library.append(r)

print(f"\n[Deduplication Complete] Total unique articles in library: {len(dedup_library)} (from {len(all_raw)} raw hits)")

# 4. Automated Inclusion/Exclusion Criteria Evaluator
included = []
excluded = []

def evaluate_criteria(title, abstract):
    text = (title + " " + abstract).lower()
    
    # Exclusion checks
    if any(k in text for k in ["animal", "rat", "mice", "porcine", "piglet", "lamb", "in vitro", "cell line"]):
        return False, "Kizárva: Állatkísérletes / In vitro vizsgálat"
    if any(k in text for k in ["review article", "systematic review", "meta-analysis", "editorial", "letter to editor"]) and "protocol" not in text:
        return False, "Kizárva: Szakirodalmi áttekintés / Editorial (Nem primer tanulmány)"
    if "adult" in text and not any(k in text for k in ["neonate", "infant", "newborn"]):
        return False, "Kizárva: Felnőtt populáció"
        
    # Inclusion checks (PICO match)
    p_match = any(k in text for k in ["hie", "hypoxic", "asphyxia", "encephalopathy", "neonate", "newborn", "infant"])
    e_match = any(k in text for k in ["glucose", "glycemia", "glycaemia", "hyperglycemia", "hyperglycaemia", "hypoglycemia", "hypoglycaemia", "dysglycemia", "mag", "cgm"])
    t_match = any(k in text for k in ["hypothermia", "cooling", "cooled", "chilled"])
    
    if p_match and e_match and t_match:
        return True, "Beválasztva: Tervezett PICO kritériumoknak megfelel"
    elif e_match and t_match:
        return True, "Beválasztva (Másodlagos felülvizsgálat): TH + Vércukor adatok"
    else:
        return False, "Kizárva: Nem fedi le mindhárom PICO domaint"

for art in dedup_library:
    is_inc, reason = evaluate_criteria(art['title'], art['abstract'])
    art['screening_status'] = "INCLUDED" if is_inc else "EXCLUDED"
    art['reason'] = reason
    if is_inc:
        included.append(art)
    else:
        excluded.append(art)

print(f"\n==========================================")
print(f"AUTOMATED PRISMA SCREENING RESULTS")
print(f"==========================================")
print(f"1. Identifikált rekordok (PubMed + Embase): {len(all_raw)}")
print(f"2. Duplikációk eltávolítása után: {len(dedup_library)}")
print(f"3. Cím & Absztrakt szűrés alapján KIZÁRVA: {len(excluded)}")
print(f"4. Cím & Absztrakt szűrés alapján BEVÁLASZTVA: {len(included)}")

print(f"\nTop Beválasztott Cikkek Kiemelése ({len(included)} db):")
for idx, a in enumerate(included[:10], 1):
    print(f"  {idx}. [{a['year']}] [{a['source']}] {a['title']}")
    print(f"     Status: {a['reason']} | DOI: {a['doi']}\n")

with open("meta_hyperglycaemia/screening_library.json", "w", encoding="utf-8") as f:
    json.dump({"library": dedup_library, "included": included, "excluded": excluded}, f, ensure_ascii=False, indent=2)

print("Screening library and results saved to meta_hyperglycaemia/screening_library.json")
