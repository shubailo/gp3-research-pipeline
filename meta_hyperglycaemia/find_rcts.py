import urllib.request
import urllib.parse
import json
import time
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

NCBI_BASE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

# The current search query
q_base = '(hypotherm* OR cool* OR "temperature management") AND (glyce* OR glycae* OR hyperglyce* OR hypoglyce* OR "blood glucose" OR "blood sugar" OR "glucose control" OR "glucose level") AND ("Hypoxia-Ischemia, Brain"[MeSH] OR neonat* OR newborn* OR infant* OR perinatal* OR asphyxi* OR "hypoxic ischemic encephalopathy")'

# Add RCT filter
q_rct = f'({q_base}) AND "randomized controlled trial"[pt]'

def search_pubmed(query, max_results=50):
    url = NCBI_BASE + 'esearch.fcgi?' + urllib.parse.urlencode({
        'db': 'pubmed', 'term': query, 'retmode': 'json', 'retmax': max_results
    })
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read().decode())
        return data['esearchresult']['count'], data['esearchresult']['idlist']

def fetch_abstracts(pmids):
    if not pmids:
        return ""
    url = NCBI_BASE + "efetch.fcgi?" + urllib.parse.urlencode({
        "db": "pubmed", "id": ",".join(pmids), "retmode": "xml", "rettype": "abstract"
    })
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as r:
        return r.read().decode()

count, pmids = search_pubmed(q_rct)
print(f"Number of RCTs found: {count}\n")

if pmids:
    xml_text = fetch_abstracts(pmids)
    for article_xml in re.findall(r'<PubmedArticle>(.*?)</PubmedArticle>', xml_text, re.DOTALL):
        pmid_m = re.search(r'<PMID[^>]*>(\d+)</PMID>', article_xml)
        title_m = re.search(r'<ArticleTitle>(.*?)</ArticleTitle>', article_xml, re.DOTALL)
        year_m = re.search(r'<Year>(\d{4})</Year>', article_xml)
        
        pmid = pmid_m.group(1) if pmid_m else "?"
        title = re.sub(r'<[^>]+>', '', title_m.group(1)) if title_m else "N/A"
        title = re.sub(r'&[#\w]+;', '', title)
        year = year_m.group(1) if year_m else "N/A"
        
        print(f"PMID: {pmid} ({year})")
        print(f"Title: {title}")
        print("-" * 60)
