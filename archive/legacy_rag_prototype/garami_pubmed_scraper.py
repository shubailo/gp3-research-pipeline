"""
Garami András PubMed publikáció letöltő
=======================================
Ez a script leszedi az összes publikációt PubMed-ről Dr. Garami András számára.
Módosított verzió a specifikus hőszabályozási kutatások fókuszálására.
"""

import requests
import json
import csv
import time
import os
import sys
import io
from datetime import datetime

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# --- KONFIGURÁCIÓ ---
AUTHOR_NAME = "Garami Andras"
EMAIL = "shubailo@med-buddy.ai" 
OUTPUT_DIR = "garami_publications"
MAX_RESULTS = 1000

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def search_pubmed(author: str, email: str, max_results: int = 1000) -> list[str]:
    print(f"🔍 Keresés: '{author}' az NCBI PubMed-en...")
    params = {
        "db": "pubmed",
        "term": f"{author}[Author]",
        "retmode": "json",
        "retmax": max_results,
        "email": email,
        "tool": "MedBuddyScraper"
    }
    response = requests.get(f"{BASE_URL}esearch.fcgi", params=params)
    response.raise_for_status()
    ids = response.json().get("esearchresult", {}).get("idlist", [])
    print(f"✅ Talált PMID-k száma: {len(ids)}")
    return ids

def fetch_details(pmids: list[str], email: str) -> list[dict]:
    print(f"📥 Részletek lekérése {len(pmids)} publikációhoz...")
    results = []
    batch_size = 50
    for i in range(0, len(pmids), batch_size):
        batch = pmids[i:i + batch_size]
        params = {
            "db": "pubmed",
            "id": ",".join(batch),
            "retmode": "json",
            "email": email,
            "tool": "MedBuddyScraper"
        }
        response = requests.get(f"{BASE_URL}esummary.fcgi", params=params)
        response.raise_for_status()
        summaries = response.json().get("result", {})
        
        abstract_params = {
            "db": "pubmed",
            "id": ",".join(batch),
            "retmode": "xml",
            "email": email
        }
        abs_response = requests.get(f"{BASE_URL}efetch.fcgi", params=abstract_params)
        
        import xml.etree.ElementTree as ET
        root = ET.fromstring(abs_response.content)
        
        abstracts = {}
        for article in root.findall(".//PubmedArticle"):
            pmid = article.find(".//PMID").text
            abst_text = article.find(".//AbstractText")
            if abst_text is not None:
                 abstracts[pmid] = "".join(abst_text.itertext())

        for pmid in batch:
            if pmid in summaries:
                s = summaries[pmid]
                results.append({
                    "pmid": pmid,
                    "title": s.get("title", ""),
                    "abstract": abstracts.get(pmid, ""),
                    "journal": s.get("source", ""),
                    "year": s.get("pubdate", "")[:4],
                    "authors": "; ".join([a["name"] for a in s.get("authors", [])]),
                    "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
        print(f"   Feldolgozva: {min(i + batch_size, len(pmids))}/{len(pmids)}")
        time.sleep(0.5)
    return results

def save_data(data: list[dict]):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(OUTPUT_DIR, f"garami_publications_{timestamp}.json")
    csv_path = os.path.join(OUTPUT_DIR, f"garami_publications_{timestamp}.csv")
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    if data:
        keys = data[0].keys()
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
    
    print(f"\n💾 Mentve:\n - {json_path}\n - {csv_path}")

if __name__ == "__main__":
    pmids = search_pubmed(AUTHOR_NAME, EMAIL, MAX_RESULTS)
    if pmids:
        publications = fetch_details(pmids, EMAIL)
        save_data(publications)
    else:
        print("❌ Nem találtam publikációt.")
