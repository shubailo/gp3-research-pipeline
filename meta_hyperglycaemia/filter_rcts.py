import urllib.request
import urllib.parse
import json
import sys
import re
import time

sys.stdout.reconfigure(encoding='utf-8')

NCBI_BASE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

q_base = '(hypotherm* OR cool* OR "temperature management") AND (glyce* OR glycae* OR hyperglyce* OR hypoglyce* OR "blood glucose" OR "blood sugar" OR "glucose control" OR "glucose level") AND ("Hypoxia-Ischemia, Brain"[MeSH] OR neonat* OR newborn* OR infant* OR perinatal* OR asphyxi* OR "hypoxic ischemic encephalopathy")'
q_rct = f'({q_base}) AND "randomized controlled trial"[pt]'

def search_pubmed(query, max_results=100):
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
xml_text = fetch_abstracts(pmids)

articles = []
for article_xml in re.findall(r'<PubmedArticle>(.*?)</PubmedArticle>', xml_text, re.DOTALL):
    pmid_m = re.search(r'<PMID[^>]*>(\d+)</PMID>', article_xml)
    title_m = re.search(r'<ArticleTitle>(.*?)</ArticleTitle>', article_xml, re.DOTALL)
    year_m = re.search(r'<Year>(\d{4})</Year>', article_xml)
    
    abstract_parts = re.findall(r'<AbstractText[^>]*>(.*?)</AbstractText>', article_xml, re.DOTALL)
    abstract = ' '.join(p.strip() for p in abstract_parts)
    
    pmid = pmid_m.group(1) if pmid_m else "?"
    title = re.sub(r'<[^>]+>', '', title_m.group(1)) if title_m else "N/A"
    title = re.sub(r'&[#\w]+;', '', title)
    year = year_m.group(1) if year_m else "N/A"
    abstract = re.sub(r'<[^>]+>', '', abstract)
    abstract = re.sub(r'&[#\w]+;', '', abstract)
    
    articles.append({
        'pmid': pmid, 'year': year, 'title': title, 'abstract': abstract
    })

# Filter based on abstract content
# We want HIE/asphyxia + hypothermia + glucose/glycemia in the abstract or title as primary focus.
relevant = []
for a in articles:
    text = (a['title'] + " " + a['abstract']).lower()
    
    has_hie = any(x in text for x in ['hie', 'encephalopathy', 'asphyxia', 'hypoxic-ischemic'])
    has_cool = any(x in text for x in ['hypotherm', 'cool', 'temperature'])
    has_gluc = any(x in text for x in ['glucose', 'glycemi', 'glycaemi', 'sugar'])
    
    # We also exclude obvious pregnancy diabetes ones
    is_preg = any(x in text for x in ['pregnant', 'pregnancy', 'maternal', 'gestational diabetes'])
    
    if has_hie and has_cool and has_gluc and not is_preg:
        relevant.append(a)

print(f"Total RCTs: {len(articles)}")
print(f"Relevant based on heuristics (HIE + cooling + glucose, not pregnant): {len(relevant)}\n")

for a in relevant:
    print(f"PMID: {a['pmid']} ({a['year']})")
    print(f"Title: {a['title']}")
    print(f"Abstract: {a['abstract'][:400]}...")
    print("-" * 80)
