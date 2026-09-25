"""
Full-text retrieval attempt for all 60 included articles.
Strategy:
  1. PubMed Central (PMC) open access check via E-utils
  2. If PMC available -> download full text XML
  3. If not -> flag as "needs manual download"
  4. Extract key data fields automatically where possible
"""
import json, sys, io, csv, time, requests, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EMAIL = "researcher@example.com"

def check_pmc(pmid):
    """Check if article has PMC full text available."""
    url = f"{BASE_EUTILS}/elink.fcgi"
    params = {
        "dbfrom": "pubmed",
        "db": "pmc",
        "id": pmid,
        "email": EMAIL,
        "retmode": "json"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        links = data.get("linksets", [{}])[0].get("linksetdbs", [])
        for l in links:
            if l.get("linkname") == "pubmed_pmc":
                ids = l.get("links", [])
                if ids:
                    return ids[0]  # PMC ID
        return None
    except:
        return None

def get_abstract_and_pubtypes(pmid):
    """Get abstract + publication types from PubMed."""
    url = f"{BASE_EUTILS}/efetch.fcgi"
    params = {"db": "pubmed", "id": pmid, "rettype": "xml", "retmode": "xml", "email": EMAIL}
    try:
        r = requests.get(url, params=params, timeout=15)
        text = r.text
        # Extract pub types
        pt_matches = re.findall(r'<PublicationType[^>]*>(.*?)</PublicationType>', text, re.DOTALL)
        pub_types = [p.strip() for p in pt_matches]
        # Extract abstract
        abs_match = re.search(r'<AbstractText[^>]*>(.*?)</AbstractText>', text, re.DOTALL)
        abstract = abs_match.group(1).strip() if abs_match else ""
        return pub_types, abstract
    except:
        return [], ""

# Load all included articles
with open('meta_hyperglycaemia/prisma_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_included = data['auto_included'] + data['manually_included']

# Add the 4 new CENTRAL articles
central_new = [
    {"title": "Neurological Outcome at 30 Months after Mild Hypothermia via Selective Head Cooling in Term Neonates with Perinatal Asphyxia Using Low-Cost CoolCap: a Single-Center Randomized Control Pilot Trial in India",
     "pmid": "28670226", "database": "Cochrane CENTRAL", "year": "2017"},
    {"title": "Experience of therapeutic hypothermia in neonates with perinatal asphyxia in a tertiary care center in North Karnataka",
     "pmid": "32055543", "database": "Cochrane CENTRAL", "year": "2020"},
    {"title": "Glycemic profile in infants with hypoxic ischemic encephalopathy predicts response to hypothermia",
     "pmid": "29684048", "database": "Cochrane CENTRAL", "year": "2018"},
    {"title": "Nutritional management in newborn babies receiving therapeutic hypothermia: two retrospective observational studies using propensity score matching",
     "pmid": "33824146", "database": "Cochrane CENTRAL", "year": "2021"},
]

all_articles = all_included + central_new
print(f"Total articles to check: {len(all_articles)}\n")

results = []
open_access = []
needs_manual = []

for i, art in enumerate(all_articles, 1):
    pmid = str(art.get('pmid', '')).strip()
    title = art.get('title', '')[:70]
    
    if not pmid or pmid == 'None':
        print(f"  [{i:2d}] NO PMID - {title}")
        results.append({**art, 'pmc_id': None, 'open_access': False, 'status': 'NO_PMID'})
        needs_manual.append(art)
        continue
    
    pmc_id = check_pmc(pmid)
    time.sleep(0.35)  # NCBI rate limit
    
    if pmc_id:
        print(f"  [{i:2d}] ✅ PMC{pmc_id} - PMID:{pmid} - {title}")
        results.append({**art, 'pmc_id': pmc_id, 'open_access': True, 'status': 'PMC_AVAILABLE'})
        open_access.append({**art, 'pmc_id': pmc_id})
    else:
        print(f"  [{i:2d}] 🔒 No PMC  - PMID:{pmid} - {title}")
        results.append({**art, 'pmc_id': None, 'open_access': False, 'status': 'NEEDS_MANUAL'})
        needs_manual.append(art)

print(f"\n{'='*60}")
print(f"  OPEN ACCESS (PMC): {len(open_access)}/{len(all_articles)}")
print(f"  NEEDS MANUAL:      {len(needs_manual)}/{len(all_articles)}")
print(f"{'='*60}")

# Save results
with open('meta_hyperglycaemia/fulltext_access_check.json', 'w', encoding='utf-8') as f:
    json.dump({'open_access': open_access, 'needs_manual': needs_manual, 'all': results}, f, ensure_ascii=False, indent=2)

# Save CSV
with open('meta_hyperglycaemia/fulltext_access_check.csv', 'w', newline='', encoding='utf-8') as f:
    fields = ['pmid', 'year', 'title', 'database', 'pmc_id', 'open_access', 'status']
    w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
    w.writeheader()
    for r in results:
        w.writerow({k: r.get(k,'') for k in fields})

print(f"\n[OK] Results: meta_hyperglycaemia/fulltext_access_check.csv")
print(f"\nOPEN ACCESS articles (downloadable):")
for a in open_access:
    print(f"  PMC{a['pmc_id']} - {a['title'][:70]}")
