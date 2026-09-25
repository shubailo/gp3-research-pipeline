import urllib.request
import urllib.parse
import json
import sys
import time

NCBI_BASE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

def get_pmids(query):
    url = NCBI_BASE + 'esearch.fcgi?' + urllib.parse.urlencode({'db': 'pubmed', 'term': query, 'retmode': 'json', 'retmax': 1000})
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as r:
        return set(json.loads(r.read().decode())['esearchresult']['idlist'])

q_base = '(hypotherm* OR cool* OR "temperature management") AND (glyce* OR glycae* OR hyperglyce* OR hypoglyce* OR "blood glucose" OR "blood sugar" OR "glucose control" OR "glucose level") AND ("Hypoxia-Ischemia, Brain"[MeSH] OR neonat* OR newborn* OR infant* OR perinatal* OR asphyxia OR "hypoxic ischemic encephalopathy")'

base_pmids = get_pmids(q_base)
print(f"Base PMIDs: {len(base_pmids)}")

parts = {
    'temp': ['hypotherm*', 'cool*', '"temperature management"'],
    'glyc': ['glyce*', 'glycae*', 'hyperglyce*', 'hypoglyce*', '"blood glucose"', '"blood sugar"', '"glucose control"', '"glucose level"'],
    'pop': ['"Hypoxia-Ischemia, Brain"[MeSH]', 'neonat*', 'newborn*', 'infant*', 'perinatal*', 'asphyxia', '"hypoxic ischemic encephalopathy"']
}

minimal_parts = {'temp': [], 'glyc': [], 'pop': []}

# We will try dropping each term. If dropping it doesn't reduce coverage of base_pmids, it's redundant.
# Wait, this is a greedy approach. Let's just find which terms actually contribute to the base_pmids.

for group, terms in parts.items():
    necessary = []
    for term in terms:
        # build query with ONLY this term for this group, and full for other groups
        other_groups = []
        for g, t in parts.items():
            if g == group:
                other_groups.append(term)
            else:
                other_groups.append("(" + " OR ".join(t) + ")")
        
        q_test = " AND ".join(other_groups)
        test_pmids = get_pmids(q_test)
        
        # how many base pmids does this term alone capture?
        captured = len(base_pmids.intersection(test_pmids))
        print(f"Term '{term}' captures {captured} base PMIDs.")
        if captured > 0:
            necessary.append(term)
    
    minimal_parts[group] = necessary
    time.sleep(1)

# Now, with the necessary terms, let's see if we get all base PMIDs
q_min = " AND ".join(["(" + " OR ".join(minimal_parts[g]) + ")" for g in parts.keys()])
min_pmids = get_pmids(q_min)
missing = base_pmids - min_pmids
print(f"\nMinimal query: {q_min}")
print(f"Minimal PMIDs: {len(min_pmids)}")
print(f"Missing base PMIDs: {len(missing)}")

# To be safe, let's find the absolute minimal set of terms needed to cover all base_pmids.
# For each group, we want a subset of `terms` that covers all base_pmids that the full `terms` covers.

for group, terms in parts.items():
    print(f"\nOptimizing group {group}...")
    
    # Get the set of base_pmids covered by the FULL group (which should be all of them, since they are from base_pmids)
    # Actually, we can just test combinations
    
    current_kept = []
    covered_so_far = set()
    
    # Order terms by how many they capture (descending)
    term_captures = []
    for term in terms:
        other_groups = ["(" + " OR ".join(parts[g]) + ")" for g in parts.keys() if g != group]
        q_test = term + " AND " + " AND ".join(other_groups)
        test_pmids = get_pmids(q_test)
        captured = base_pmids.intersection(test_pmids)
        term_captures.append((term, captured))
        time.sleep(0.5)
        
    term_captures.sort(key=lambda x: len(x[1]), reverse=True)
    
    for term, captured in term_captures:
        new_coverage = captured - covered_so_far
        if new_coverage:
            current_kept.append(term)
            covered_so_far.update(captured)
            print(f"Keeping '{term}' because it uniquely adds {len(new_coverage)} PMIDs.")
            
    minimal_parts[group] = current_kept

q_opt = " AND ".join(["(" + " OR ".join(minimal_parts[g]) + ")" for g in parts.keys()])
opt_pmids = get_pmids(q_opt)
print(f"\nOptimized query: {q_opt}")
print(f"Optimized PMIDs: {len(opt_pmids)} (should be >= base PMIDs)")
print(f"Coverage of base: {len(base_pmids.intersection(opt_pmids))} / {len(base_pmids)}")
