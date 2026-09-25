import json, sys, io, csv
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Manual review decisions for all 24 "needs_check" articles
# Based on full abstract review
manual_decisions = {
    # Title fragment : (decision, reason)
    "regional quality-improvement collaborative": 
        ("EXCLUDED", "Spontan/incidentalis hypothermia megelozese, nem teraipas hypothermia HIE-ben"),
    "association of neonatal hypothermia with neonatal hypoglycemia": 
        ("INCLUDED", "Neonatalis hypothermia + hypoglycaemia kapcsolat - relevans a mechanizmus szempontjabol"),
    "umbilical cord ph levels": 
        ("EXCLUDED", "Glukoz/TH nincs - csak pH es morbiditasi adatok"),
    "management and clinical outcomes of neonatal hypothermia": 
        ("EXCLUDED", "Spontan hypothermia, nem teraipas hypothermia (HIE TH)"),
    "rewarming rate of hypothermic neonates": 
        ("EXCLUDED", "Spontan/nem-teraipas hypothermia, felmelegites sebessege"),
    "serious infections are rare in well-appearing neonates": 
        ("EXCLUDED", "Incidentalis hypothermia, nem TH HIE-ben"),
    "active normothermia treatment for perioperative": 
        ("EXCLUDED", "Perioperativ normothermia, nem TH HIE-ben"),
    "referral challenges and outcomes of neonates": 
        ("EXCLUDED", "Szallitasi kimenetel Tanzaniaban - nem specifikusan glukoz/TH"),
    "persistent hyperglycemia in a neonate: is it a complication": 
        ("INCLUDED", "TH mint a perzisztens hyperglycaemia kauzalis tenyezoje - kozvetlenul relevans"),
    "golden 60 minutes of newborn": 
        ("EXCLUDED", "Altalanos neonatalis ellatasi guideline, nem specifikusan glukoz+TH+HIE"),
    "cardiac arrests associated with hyperkalemia": 
        ("EXCLUDED", "Hyperkalemia transfuzio alatt - nem relevans"),
    "group b streptococcal late-onset sepsis": 
        ("EXCLUDED", "GBS szepszis preterm ujszulottben - nem glukoz/TH/HIE"),
    "brain monitoring and protection during pediatric cardiac surgery": 
        ("EXCLUDED", "Gyermekkardiovascularis sebeszet - nem neonatalis HIE TH"),
    "estimation of rewarming time in transported extramural": 
        ("EXCLUDED", "Spontan hypothermia felmelegitese, nem TH"),
    "maternal and newborn outcomes related to maternal warming": 
        ("EXCLUDED", "Anya melegitese CS soran - nem neonatalis TH"),
    "hypothermia in iranian newborns": 
        ("EXCLUDED", "Spontan/environmentalis hypothermia, nem teraipas"),
    "essential mixed type ii cryoglobulinemia": 
        ("EXCLUDED", "Anyai kryoglobulinaemia - irrelevans"),
    "transportation of newborn infants": 
        ("EXCLUDED", "1990-es szallitasi adatok - hipoglikemia mint szallitasi szovt, nem TH-specifikus"),
    "effect of cooling on the glucoregulation of anaesthetized": 
        ("EXCLUDED", "Allatkiserleti tanulmany (kutya)"),
    "efficacy of a specialized transport service": 
        ("EXCLUDED", "Szallitasi hatekonysag, nem TH HIE-specifikus"),
    "effect of hypothermia on plasma metabolites in preterm": 
        ("EXCLUDED", "Spontan hypothermia prematur ujszulottekben, nem teraipas hypothermia"),
    "stabilization of blood glucose by cooling with ice": 
        ("EXCLUDED", "Laboratorios mintamegorzesi technika, nem klinikai"),
    "effect of environmental temperature on glucose-induced insulin": 
        ("EXCLUDED", "Allatkiserleti tanulmany (patkany)"),
    "influence of donor blood temperature on metabolic": 
        ("EXCLUDED", "Cserevertranszfuzio - nem TH HIE-ben"),
}

# Load data
with open('meta_hyperglycaemia/prisma_results_v3.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

needs_check = data['included_needs_check']
confirmed = data['included']

# Apply manual decisions
newly_included = []
manually_excluded = []

for art in needs_check:
    title_lower = art['title'].lower()
    decision = None
    reason = None
    for key, (dec, reas) in manual_decisions.items():
        if key in title_lower:
            decision = dec
            reason = reas
            break
    if decision is None:
        decision = "EXCLUDED"
        reason = "Manualis ellenorzessel kizarva (alapertelmezett)"
    
    art['screening_status'] = decision
    art['manual_review_reason'] = reason
    
    if decision == "INCLUDED":
        newly_included.append(art)
    else:
        manually_excluded.append(art)

# Final totals
all_included = confirmed + newly_included

print("=" * 70)
print("  MANUALIS ELLENORZES EREDMENYE")
print("=" * 70)
print(f"\n  24 kerdeses cikk attekintve")
print(f"  BEVALASZTVA:  {len(newly_included)}")
print(f"  KIZARVA:      {len(manually_excluded)}")
print(f"\n  === VEGLEGES PRISMA SZAMOK ===")
print(f"  Automatikusan bevalasztott:  {len(confirmed)}")
print(f"  Manualisan bevalasztott:     {len(newly_included)}")
print(f"  OSSZESEN FULL-TEXT-RE:       {len(all_included)}")

print(f"\n  === MANUALISAN BEVALASZTOTT ({len(newly_included)}) ===")
for a in newly_included:
    print(f"  + {a['title']}")
    print(f"    Indok: {a['manual_review_reason']}")

print(f"\n  === MANUALISAN KIZART CIKKEK ({len(manually_excluded)}) ===")
for a in manually_excluded:
    print(f"  - {a['title'][:80]}")
    print(f"    Indok: {a['manual_review_reason']}")

# Now check for RCTs among ALL included articles
print(f"\n  === RCT AZONOSITASA A BEVALASZTOTT CIKKEK KOZOTT ===")
rct_keywords = [
    'randomized controlled trial', 'randomised controlled trial',
    'randomized', 'randomised', 'rct', 'random allocation',
    'double-blind', 'single-blind', 'placebo-controlled',
    'pilot rct', 'feasibility trial', 'clinical trial'
]
rcts = []
for art in all_included:
    text = (art.get('title','') + ' ' + art.get('abstract','')).lower()
    pt = art.get('pub_types','').lower()
    if any(k in text for k in rct_keywords) or any(k in pt for k in ['randomized', 'controlled trial', 'clinical trial']):
        rcts.append(art)
        print(f"  [RCT] {art.get('year','')} - {art['title'][:80]}")
        # Show pub_types
        if art.get('pub_types'):
            print(f"        PubType: {art['pub_types'][:60]}")
        # Show relevant abstract snippet
        abs_text = art.get('abstract','')
        if abs_text:
            for kw in ['randomized', 'randomised', 'random', 'rct']:
                idx = abs_text.lower().find(kw)
                if idx > -1:
                    snippet = abs_text[max(0,idx-50):idx+120]
                    print(f"        Context: ...{snippet}...")
                    break

print(f"\n  OSSZES RCT AZONOSITOTT: {len(rcts)}")

# Save final results
final_output = {
    "prisma_summary": data['prisma_summary'],
    "final_included_count": len(all_included),
    "auto_included": confirmed,
    "manually_included": newly_included,
    "manually_excluded": manually_excluded,
    "rcts_identified": rcts,
    "exclusion_reasons": data['exclusion_reasons'],
}
final_output['prisma_summary']['final_after_manual'] = {
    'total_full_text': len(all_included),
    'rcts': len(rcts),
    'observational': len(all_included) - len(rcts),
}

with open('meta_hyperglycaemia/prisma_final.json', 'w', encoding='utf-8') as f:
    json.dump(final_output, f, ensure_ascii=False, indent=2)

# Save final included CSV
with open('meta_hyperglycaemia/final_included_all.csv', 'w', encoding='utf-8', newline='') as f:
    fields = ['database','pmid','doi','year','title','screening_status','screening_reason','manual_review_reason','pub_types','abstract']
    writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    for a in all_included:
        writer.writerow({k: a.get(k,'') for k in fields})

print(f"\n[OK] Vegleges PRISMA: meta_hyperglycaemia/prisma_final.json")
print(f"[OK] Osszes bevalasztott CSV: meta_hyperglycaemia/final_included_all.csv")
