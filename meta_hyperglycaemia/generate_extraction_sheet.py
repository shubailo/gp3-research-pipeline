import csv, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load included articles
with open('meta_hyperglycaemia/prisma_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_included = data['auto_included'] + data['manually_included']

# Add CENTRAL articles
central_new = [
    {"title": "Neurological Outcome at 30 Months after Mild Hypothermia via Selective Head Cooling in Term Neonates (Das 2017 RCT)",
     "pmid": "28670226", "database": "Cochrane CENTRAL", "year": "2017"},
    {"title": "Experience of therapeutic hypothermia in neonates with perinatal asphyxia - North Karnataka (Charki 2020)",
     "pmid": "32055543", "database": "Cochrane CENTRAL", "year": "2020"},
    {"title": "Glycemic profile in infants with HIE predicts response to hypothermia (Basu 2018)",
     "pmid": "29684048", "database": "Cochrane CENTRAL", "year": "2018"},
    {"title": "Nutritional management in newborn babies receiving TH - propensity matched (Gale 2021)",
     "pmid": "33824146", "database": "Cochrane CENTRAL", "year": "2021"},
]
all_articles = all_included + central_new

# Define all extraction fields
fields = [
    # Identification
    'reviewer', 'extraction_date', 'pmid', 'doi', 'year', 'first_author', 'journal', 'country',
    'funding', 'coi',
    # Study design
    'study_design', 'multicenter', 'n_centers', 'study_period',
    'randomization_method', 'allocation_concealment', 'blinding',
    'glucose_endpoint_apriori', 'preregistered',
    # Population
    'n_total', 'n_th_treated', 'gestational_age_weeks', 'ga_inclusion_criterion',
    'birth_weight_g', 'hie_severity', 'age_at_enrollment_hours',
    'key_exclusion_criteria',
    # TH Protocol
    'th_type', 'target_temp_rectal', 'th_duration_hours', 'th_start_hours',
    'rewarming_rate', 'cooling_index_coin', 'adjunct_neuroprotection', 'glucose_protocol_used', 'insulin_used',
    # Glucose / Dysglycaemia
    'glucose_measurement_method', 'cgm_device', 'measurement_frequency',
    'measurement_timeframe',
    'hypoglycaemia_threshold_mmolL', 'hyperglycaemia_threshold_mmolL',
    'normoglycaemia_range',
    'dysglycaemia_types_studied',
    'glucose_variability_measure',
    'hypoglycaemia_prevalence_n', 'hypoglycaemia_prevalence_pct',
    'hyperglycaemia_prevalence_n', 'hyperglycaemia_prevalence_pct',
    'mean_glucose_mmolL', 'sd_glucose', 'glucose_min', 'glucose_max',
    # Primary Outcomes
    'mortality_n', 'mortality_pct', 'mortality_timepoint',
    'ndi_definition', 'ndi_n', 'ndi_pct', 'ndi_timepoint',
    'composite_death_or_ndi_n', 'composite_death_or_ndi_pct',
    'mri_abnormality_n', 'mri_abnormality_pct', 'mri_classification_system', 'mri_timepoint',
    # Secondary Outcomes
    'seizure_n', 'seizure_pct',
    'bayley_cognitive_mean', 'bayley_cognitive_sd',
    'bayley_motor_mean', 'bayley_motor_sd',
    'bayley_language_mean', 'bayley_language_sd',
    'cerebral_palsy_n', 'cerebral_palsy_pct',
    'aeeg_pattern',
    'nicu_stay_days',
    # Glucose-Outcome Association
    'statistical_method',
    'hypo_outcome_estimate', 'hypo_outcome_95ci', 'hypo_outcome_p',
    'hyper_outcome_estimate', 'hyper_outcome_95ci', 'hyper_outcome_p',
    'variability_outcome_estimate', 'variability_outcome_p',
    'confounders_adjusted',
    'statistically_significant',
    'effect_direction',
    # Risk of Bias
    'rob_tool', # RoB2 or ROBINS-I
    'rob_domain1', 'rob_domain2', 'rob_domain3', 'rob_domain4', 'rob_domain5',
    'rob_domain6', 'rob_domain7', 'rob_overall',
    # Full-text decision
    'fulltext_available', 'final_decision', 'exclusion_reason', 'notes',
    # Pre-filled
    'title',
]

# Write the empty extraction CSV
outfile = 'meta_hyperglycaemia/data_extraction_sheet.csv'
with open(outfile, 'w', newline='', encoding='utf-8-sig') as f:  # utf-8-sig for Excel
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for art in all_articles:
        row = {f: '' for f in fields}
        row['pmid'] = art.get('pmid', '')
        row['doi'] = art.get('doi', '')
        row['year'] = art.get('year', '')
        row['title'] = art.get('title', '')
        row['reviewer'] = ''  # to be filled
        row['final_decision'] = 'PENDING'
        writer.writerow(row)

print(f"[OK] Data extraction sheet created: {outfile}")
print(f"     Rows: {len(all_articles)} articles")
print(f"     Columns: {len(fields)} data fields")
print(f"     Format: UTF-8 with BOM (Excel-compatible)")
print(f"\n  Excel-ben megnyitva a PMID es Title oszlopok mar ki lesznek toltve.")
print(f"  A tobbi mezo ures - reviewer toltse ki full-text alapjan.")
