"""
Hegyi Péter PubMed publikáció letöltő
=====================================
Ez a script leszedi az összes publikációt PubMed-ről,
és elmenti JSON + CSV formátumban elemzéshez.

Használat:
    pip install requests pandas
    python hegyi_pubmed_scraper.py

Nincs szükség API kulcsra az alaphasználathoz.
"""

import requests
import json
import csv
import time
import os
import sys
import io
from datetime import datetime
from xml.etree import ElementTree as ET

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# --- KONFIGURÁCIÓ ---
AUTHOR_NAME = "Hegyi Peter"
EMAIL = "shubailo@gmail.com"  # A rendszerben lévő felhasználói névből sejtve, de a user majd felülírhatja ha kell
OUTPUT_DIR = "hegyi_publications"
MAX_RESULTS = 1000  # Elég bőségesen

# NCBI E-utilities alap URL
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def search_pubmed(author: str, email: str, max_results: int = 1000) -> list[str]:
    """
    Lekéri az összes PubMed ID-t a szerző nevére.
    Visszatér: PMID-k listájával
    """
    print(f"🔍 Keresés: '{author}' az NCBI PubMed-en...")

    params = {
        "db": "pubmed",
        "term": f"{author}[Author]",
        "retmax": max_results,
        "retmode": "json",
        "email": email,
        "tool": "hegyi_agent_builder"
    }

    response = requests.get(BASE_URL + "esearch.fcgi", params=params)
    response.raise_for_status()
    data = response.json()

    pmids = data["esearchresult"]["idlist"]
    total = data["esearchresult"]["count"]

    print(f"✅ Találatok: {total} publikáció (letöltjük: {len(pmids)})")
    return pmids


def fetch_abstracts(pmids: list[str], email: str, batch_size: int = 100) -> list[dict]:
    """
    Lekéri az absztraktokat és metaadatokat batch-ekben.
    Visszatér: publikációk listájával (dict)
    """
    all_publications = []
    total_batches = (len(pmids) + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        start = batch_num * batch_size
        end = start + batch_size
        batch = pmids[start:end]

        print(f"📥 Batch {batch_num + 1}/{total_batches} letöltése ({len(batch)} cikk)...")

        params = {
            "db": "pubmed",
            "id": ",".join(batch),
            "retmode": "xml",
            "rettype": "abstract",
            "email": email,
            "tool": "hegyi_agent_builder"
        }

        response = requests.get(BASE_URL + "efetch.fcgi", params=params)
        response.raise_for_status()

        # XML parse
        publications = parse_pubmed_xml(response.text)
        all_publications.extend(publications)

        # NCBI rate limit: max 3 kérés/sec API kulcs nélkül
        time.sleep(0.4)

    print(f"\n✅ Összesen {len(all_publications)} publikáció letöltve!")
    return all_publications


def parse_pubmed_xml(xml_text: str) -> list[dict]:
    """
    Feldolgozza az NCBI XML választ.
    """
    publications = []

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"⚠️ XML parse hiba: {e}")
        return []

    for article in root.findall(".//PubmedArticle"):
        pub = {}

        # PMID
        pmid_el = article.find(".//PMID")
        pub["pmid"] = pmid_el.text if pmid_el is not None else ""

        # Cím
        title_el = article.find(".//ArticleTitle")
        # Handle cases where title might have nested tags like <i>
        pub["title"] = "".join(title_el.itertext()) if title_el is not None else ""

        # Absztrakt (lehet több szekció)
        abstract_texts = article.findall(".//AbstractText")
        if abstract_texts:
            abstract_parts = []
            for at in abstract_texts:
                label = at.get("Label", "")
                text = "".join(at.itertext()) if at.text is not None or len(at) > 0 else ""
                if label:
                    abstract_parts.append(f"{label}: {text}")
                else:
                    abstract_parts.append(text)
            pub["abstract"] = " ".join(abstract_parts)
        else:
            pub["abstract"] = ""

        # Folyóirat
        journal_el = article.find(".//Journal/Title")
        pub["journal"] = journal_el.text if journal_el is not None else ""

        # Év
        year_el = article.find(".//PubDate/Year")
        if year_el is None:
             # Try MedlineDate which sometimes contains the year
             date_el = article.find(".//PubDate/MedlineDate")
             if date_el is not None and date_el.text:
                 pub["year"] = date_el.text[:4]
             else:
                 pub["year"] = ""
        else:
            pub["year"] = year_el.text

        # Szerzők
        authors = []
        for author in article.findall(".//Author"):
            last = author.find("LastName")
            first = author.find("ForeName")
            if last is not None:
                name = last.text or ""
                if first is not None:
                    name += f" {first.text}"
                authors.append(name)
        pub["authors"] = "; ".join(authors)
        pub["author_count"] = len(authors)

        # Keywords / MeSH
        keywords = []
        for kw in article.findall(".//Keyword"):
            if kw.text:
                keywords.append(kw.text)
        for mesh in article.findall(".//MeshHeading/DescriptorName"):
            if mesh.text:
                keywords.append(mesh.text)
        pub["keywords"] = "; ".join(list(set(keywords)))

        # DOI
        for id_el in article.findall(".//ArticleId"):
            if id_el.get("IdType") == "doi":
                pub["doi"] = id_el.text or ""
                break
        else:
            pub["doi"] = ""

        # PubMed link
        pub["pubmed_url"] = f"https://pubmed.ncbi.nlm.nih.gov/{pub['pmid']}/"

        publications.append(pub)

    return publications


def save_outputs(publications: list[dict], output_dir: str):
    """
    Elmenti JSON és CSV formátumban.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # JSON mentés (teljes adatok)
    json_path = os.path.join(output_dir, f"hegyi_publications_{timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(publications, f, ensure_ascii=False, indent=2)
    print(f"💾 JSON mentve: {json_path}")

    # CSV mentés (könnyű megnyitni Excelben is)
    csv_path = os.path.join(output_dir, f"hegyi_publications_{timestamp}.csv")
    if publications:
        fieldnames = ["pmid", "year", "title", "journal", "abstract",
                      "authors", "author_count", "keywords", "doi", "pubmed_url"]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(publications)
    print(f"💾 CSV mentve: {csv_path}")

    # Szöveges corpus (RAG-hoz)
    corpus_path = os.path.join(output_dir, f"hegyi_corpus_{timestamp}.txt")
    with open(corpus_path, "w", encoding="utf-8") as f:
        for pub in publications:
            if pub.get("abstract"):
                f.write(f"=== PMID: {pub['pmid']} | {pub['year']} ===\n")
                f.write(f"Cím: {pub['title']}\n")
                f.write(f"Folyóirat: {pub['journal']}\n")
                f.write(f"Kulcsszavak: {pub['keywords']}\n")
                f.write(f"Absztrakt: {pub['abstract']}\n\n")
    print(f"💾 Szöveges corpus mentve (RAG-hoz): {corpus_path}")

    return json_path, csv_path, corpus_path


def print_summary(publications: list[dict]):
    """
    Rövid statisztika a letöltött publikációkról.
    """
    if not publications:
        print("Nincs megjeleníthető adat.")
        return

    years = [p["year"] for p in publications if p.get("year")]
    journals = [p["journal"] for p in publications if p.get("journal")]
    with_abstract = sum(1 for p in publications if p.get("abstract"))

    print("\n" + "="*50)
    print("📊 ÖSSZEFOGLALÓ")
    print("="*50)
    print(f"Összes publikáció:      {len(publications)}")
    print(f"Absztrakttal:           {with_abstract}")
    print(f"Legkorábbi év:          {min(years) if years else 'N/A'}")
    print(f"Legújabb év:            {max(years) if years else 'N/A'}")
    print(f"Különböző folyóiratok:  {len(set(journals))}")

    # Top 5 folyóirat
    from collections import Counter
    top_journals = Counter(journals).most_common(5)
    print("\n🏆 Top 5 folyóirat:")
    for journal, count in top_journals:
        print(f"   {count:3d}x  {journal}")
    print("="*50)


# ============================================================
# FŐPROGRAM
# ============================================================
if __name__ == "__main__":
    print("="*50)
    print("  Hegyi Péter PubMed Publikáció Letöltő")
    print("="*50 + "\n")

    # 1. Keresés
    pmids = search_pubmed(AUTHOR_NAME, EMAIL, MAX_RESULTS)

    if not pmids:
        print("❌ Nem találtunk publikációt. Ellenőrizd a nevet!")
        exit(1)

    # 2. Absztraktok letöltése
    publications = fetch_abstracts(pmids, EMAIL)

    # 3. Mentés
    json_path, csv_path, corpus_path = save_outputs(publications, OUTPUT_DIR)

    # 4. Összefoglaló
    print_summary(publications)

    print(f"""
✅ KÉSZ! A következő fájlok jöttek létre a '{OUTPUT_DIR}' mappában:

   📄 JSON  – teljes adatok (programokhoz)
   📄 CSV   – megnyitható Excelben is
   📄 TXT   – szöveges corpus (RAG rendszerhez)

Következő lépés:
   → Futtasd a hegyi_pattern_analyzer.py scriptet
     a gondolkodási mintázatok elemzéséhez!
""")
