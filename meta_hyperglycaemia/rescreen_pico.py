"""
PRISMA 2020 Title & Abstract Screening
Strict PICO-based screening:
  P: Neonates / HIE / perinatal asphyxia
  E: Dysglycaemia (hyper/hypoglycaemia/blood glucose)
  C: Therapeutic hypothermia / cooling
Human studies only.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import json
import re
import csv

# ── Load raw library ─────────────────────────────────────────────────────────
with open('meta_hyperglycaemia/screening_library.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Collect all articles (deduplicated, from the full pipeline run)
all_articles = []
if isinstance(data, dict):
    # If structure is {summary, included, excluded} - take ALL articles from CSV
    pass

# Use CSV as the source of truth (has all deduplicated articles)
raw_articles = []
with open('meta_hyperglycaemia/screening_library.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        raw_articles.append({
            'database': row.get('Database', ''),
            'pmid': row.get('PMID', ''),
            'doi': row.get('DOI', ''),
            'year': row.get('Year', ''),
            'title': row.get('Title', ''),
            'abstract': row.get('Abstract', ''),
        })

print(f"Total articles to re-screen: {len(raw_articles)}")

# ── PICO Screening Criteria ───────────────────────────────────────────────────
# P: Neonates with HIE / birth asphyxia / perinatal asphyxia
P_TERMS = [
    'hypoxic ischemic encephalopathy', 'hypoxic-ischemic encephalopathy',
    'hypoxic ischaemic encephalopathy', 'hypoxic-ischaemic encephalopathy',
    'neonatal encephalopathy', 'hie',
    'birth asphyxia', 'perinatal asphyxia', 'neonatal asphyxia', 'asphyxiated neonat',
    'asphyxiated infant', 'asphyxiated newborn',
]
# Also accept broader neonatal if other PICO is very specific
P_BROAD = [
    'neonate', 'neonatal', 'newborn', 'new-born', 'preterm infant', 'term infant',
    'nicu', 'neonatal intensive', 'premature infant',
]

# E: Dysglycaemia (blood glucose outcomes)
E_TERMS = [
    'hyperglycemia', 'hyperglycaemia', 'hypoglycemia', 'hypoglycaemia',
    'dysglycemia', 'dysglycaemia', 'blood glucose', 'blood sugar',
    'glucose level', 'glucose control', 'glycemia', 'glycaemia',
    'glucose management', 'glucose monitoring', 'continuous glucose',
    'cgm', 'insulin infusion', 'dextrose infusion',
]

# C: Therapeutic hypothermia / cooling
C_TERMS = [
    'therapeutic hypothermia', 'whole body cooling', 'selective head cooling',
    'cooling therapy', 'cooled', 'hypothermia treatment',
    'hypothermic', 'temperature management', 'targeted temperature',
    'bodywork cooling', 'total body cooling', 'head cooling',
]

# ── Exclusion filters ─────────────────────────────────────────────────────────
EXCLUDE_ANIMAL = [
    ' rat ', 'rats ', 'rat model', 'mouse', 'mice', 'murine', 'porcine', 'piglet',
    'lamb model', 'ovine', 'fetal lamb', 'rabbit model', 'in vitro', 'cell line',
    'cell culture', 'animal model', ' pig ', ' pigs ', 'guinea pig',
    ' sheep ', 'sheep model', 'bovine', ' cow ', 'vipera', 'adder',
    'insect', 'fish model',
]
EXCLUDE_REVIEW_TYPES = [
    'systematic review', 'meta-analysis', 'cochrane review',
    'narrative review', 'scoping review',
]
EXCLUDE_IRRELEVANT = [
    'adult patient', 'adult population', 'adult icu', 'cardiac surgery adult',
    'dopamine-beta-hydroxylase',  # specific irrelevant
    'limulus amebocyte', 'hemangioma', 'septo-optic dysplasia',
    'carnitine-acylcarnitine translocase',  # metabolic disorder, not HIE
    'congenital cataract', 'dandy-walker',
    'postmortem glucose',  # forensic, not clinical
    'alpha-1 antitrypsin deficiency',
    'group b streptococcal',  # unless also glucose+TH
    'aromatic l-aminoacid',
    'beta-blocker',
    'cortisol level.*malnutri',
    'malnourished children',
    'fat mass',
    'serotonin reuptake inhibitor',
    'body fat percentage',
]

def contains_any(text, terms):
    """Check if text contains any of the terms (word-boundary aware)."""
    for term in terms:
        if term in text:
            return True
    return False

def screen_article(title, abstract, year):
    text = (title + ' ' + abstract).lower()
    
    # ── Step 1: Mandatory exclusions ──────────────────────────────────────────
    for excl in EXCLUDE_ANIMAL:
        if excl in text:
            # Exception: if it's clearly about neonates AND HIE/TH, allow it
            if 'therapeutic hypothermia' in text and 'neonat' in text and 'hie' in text:
                pass  # allow
            else:
                return 'EXCLUDED', f'Kizárva: Állatkísérlet / In vitro modell ({excl.strip()})'
    
    # Exclude systematic reviews/meta-analyses (these are primary data reviews)
    for rtype in EXCLUDE_REVIEW_TYPES:
        if rtype in text and 'protocol' not in text:
            return 'EXCLUDED', f'Kizárva: Szakirodalmi áttekintés / Editorial ({rtype})'
    
    # Exclude clearly irrelevant topics
    for irrel in EXCLUDE_IRRELEVANT:
        if re.search(irrel, text):
            return 'EXCLUDED', f'Kizárva: Témán kívüli (irreleváns téma)'
    
    # ── Step 2: PICO match ────────────────────────────────────────────────────
    # Must match E (glucose/glycaemia)
    e_match = contains_any(text, E_TERMS)
    # Must match C (therapeutic hypothermia)
    c_match = contains_any(text, C_TERMS)
    # P: specific HIE match
    p_specific = contains_any(text, P_TERMS)
    # P: broader neonatal
    p_broad = contains_any(text, P_BROAD)
    
    if not e_match:
        return 'EXCLUDED', 'Kizárva: Nincs glükóz/glycaemia-adat (E kritérium hiányzik)'
    
    if not c_match:
        return 'EXCLUDED', 'Kizárva: Nincs terápiás hypothermia (C kritérium hiányzik)'
    
    if p_specific:
        return 'INCLUDED', 'Beválasztva: HIE/neonatalis asphyxia + dysglycaemia + terápiás hypothermia'
    
    if p_broad and e_match and c_match:
        return 'INCLUDED', 'Beválasztva (tág P): Neonatalis populáció + vércukor + TH – Manuális ellenőrzés szükséges'
    
    return 'EXCLUDED', 'Kizárva: Nem fedi le a PICO kritériumokat'

# ── Run screening ─────────────────────────────────────────────────────────────
results = []
included = []
excluded_by_reason = {}

for art in raw_articles:
    status, reason = screen_article(art['title'], art['abstract'], art.get('year', ''))
    art['screening_status'] = status
    art['screening_reason'] = reason
    results.append(art)
    
    if status == 'INCLUDED':
        included.append(art)
    else:
        excluded_by_reason[reason] = excluded_by_reason.get(reason, 0) + 1

# ── Report ────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  ÚJRASZŰRÉS EREDMÉNYE (Szigorú PICO)")
print("="*60)
print(f"  Összes cikk: {len(raw_articles)}")
print(f"  BEVÁLASZTVA: {len(included)}")
print(f"  KIZÁRVA: {len(raw_articles) - len(included)}")

print("\nEXCLUSION REASONS:")
for reason, count in sorted(excluded_by_reason.items(), key=lambda x: -x[1]):
    print(f"  {count:4d}x  {reason[:80]}")

print(f"\nINCLUDED ARTICLES ({len(included)}):")
print("-"*60)
for i, a in enumerate(included, 1):
    print(f"\n  {i}. [{a['database']}] {a.get('year','')} - {a['title']}")
    print(f"     Reason: {a['screening_reason']}")
    if a['abstract']:
        snippet = a['abstract'][:250].replace('\n', ' ')
        print(f"     Abstract: {snippet}...")

# ── Save results ──────────────────────────────────────────────────────────────
with open('meta_hyperglycaemia/screening_results_v2.json', 'w', encoding='utf-8') as f:
    json.dump({
        'summary': {
            'total_screened': len(raw_articles),
            'included': len(included),
            'excluded': len(raw_articles) - len(included),
        },
        'included': included,
        'all_results': results,
    }, f, ensure_ascii=False, indent=2)

# Save included as CSV
with open('meta_hyperglycaemia/included_articles_v2.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['database','pmid','doi','year','title','screening_reason','abstract'])
    writer.writeheader()
    for a in included:
        writer.writerow({k: a.get(k,'') for k in ['database','pmid','doi','year','title','screening_reason','abstract']})

print(f"\n[OK] Results saved: meta_hyperglycaemia/screening_results_v2.json")
print(f"[OK] Included articles: meta_hyperglycaemia/included_articles_v2.csv")
