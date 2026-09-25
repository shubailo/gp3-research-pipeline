import urllib.request
import urllib.parse
import json
import sys
import re
import time

sys.stdout.reconfigure(encoding='utf-8')

NCBI_BASE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

# Exact query matching PROSPERO
q_base = '(hypotherm* OR cool* OR "temperature management") AND (glyce* OR glycae* OR hyperglyce* OR hypoglyce* OR "blood glucose" OR "blood sugar" OR "glucose control" OR "glucose level") AND ("Hypoxia-Ischemia, Brain"[MeSH] OR neonat* OR newborn* OR infant* OR perinatal* OR asphyxi* OR "hypoxic ischemic encephalopathy") AND "humans"[MeSH Terms] NOT (Review[pt] OR Editorial[pt])'

def get_pubmed_ids(query):
    print(f"Searching: {query}")
    url = NCBI_BASE + 'esearch.fcgi?' + urllib.parse.urlencode({
        'db': 'pubmed', 'term': query, 'retmode': 'json', 'retmax': 1000
    })
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read().decode())
        count = data['esearchresult']['count']
        pmids = data['esearchresult']['idlist']
        print(f"Found {count} hits, retrieving {len(pmids)} PMIDs.")
        return pmids

def fetch_abstracts_in_batches(pmids, batch_size=100):
    articles = []
    for i in range(0, len(pmids), batch_size):
        batch = pmids[i:i+batch_size]
        url = NCBI_BASE + "efetch.fcgi?" + urllib.parse.urlencode({
            "db": "pubmed", "id": ",".join(batch), "retmode": "xml", "rettype": "abstract"
        })
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req) as r:
                xml_text = r.read().decode()
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
            print(f"Fetched batch {i//batch_size + 1}")
            time.sleep(0.5)
        except Exception as e:
            print(f"Error fetching batch: {e}")
    return articles

pmids = get_pubmed_ids(q_base)
all_articles = fetch_abstracts_in_batches(pmids)

# Heuristic Filtering
relevant = []
maybe = []
irrelevant = []

# Exclude words
exclude_words = ['pregnant', 'pregnancy', 'maternal', 'gestational diabetes', 'adult', 'cardiac arrest', 'piglet', 'rat', 'mice', 'mouse']

for a in all_articles:
    text = (a['title'] + " " + a['abstract']).lower()
    
    # Check exclude words
    if any(x in text for x in exclude_words):
        # Allow if it mentions neonate frequently, but for this quick screen, let's just categorize it
        pass
    
    has_hie = any(x in text for x in ['hie', 'encephalopathy', 'asphyxia', 'hypoxic-ischemic', 'hypoxic ischemic'])
    has_cool = any(x in text for x in ['hypotherm', 'cool', 'temperature'])
    has_gluc = any(x in text for x in ['glucose', 'glycemi', 'glycaemi', 'sugar'])
    
    is_preg = any(x in text for x in exclude_words)
    
    if has_hie and has_cool and has_gluc and not is_preg:
        relevant.append(a)
    elif (has_hie and has_cool) or (has_hie and has_gluc) or (has_cool and has_gluc):
        if not is_preg:
            maybe.append(a)
        else:
            irrelevant.append(a)
    else:
        irrelevant.append(a)

print(f"\n--- FEASIBILITY SUMMARY ---")
print(f"Total processed: {len(all_articles)}")
print(f"Highly Relevant (contains HIE + Cooling + Glucose): {len(relevant)}")
print(f"Potentially Relevant (contains 2 out of 3): {len(maybe)}")
print(f"Irrelevant (Missing terms or contains exclude words like pregnant/adult): {len(irrelevant)}")

print("\n--- TOP 10 HIGHLY RELEVANT ARTICLES ---")
for a in relevant[:10]:
    print(f"[{a['year']}] {a['title']}")

print("\n--- Saving full list of relevant PMIDs to file ---")
with open('highly_relevant_pmids.txt', 'w') as f:
    for a in relevant:
        f.write(f"{a['pmid']}\n")
