import sys
import subprocess

query_complex = """(
  ("hypothermia, induced"[MeSH] OR "therapeutic hypothermia"[tiab] OR "cooling therapy"[tiab] 
   OR "therapeutic cooling"[tiab] OR "whole body cooling"[tiab] OR "selective head cooling"[tiab])
  AND
  ("hyperglycemia"[MeSH] OR "hyperglycaemia"[tiab] OR "hyperglycemia"[tiab] 
   OR "hypoglycemia"[MeSH] OR "hypoglycaemia"[tiab] OR "hypoglycemia"[tiab]
   OR "blood glucose"[MeSH] OR "blood glucose"[tiab] OR "glycemia"[tiab] 
   OR "glycaemia"[tiab] OR "glucose level"[tiab] OR "glucose control"[tiab]
   OR "dysglycemia"[tiab] OR "dysglycaemia"[tiab])
  AND
  ("infant, newborn"[MeSH] OR "neonatal"[tiab] OR "neonate"[tiab] 
   OR "newborn"[tiab] OR "perinatal"[tiab]
   OR "infant, premature"[MeSH] OR "preterm"[tiab] OR "premature infant"[tiab]
   OR "hypoxia-ischemia, brain"[MeSH] OR "hypoxic ischemic encephalopathy"[tiab] 
   OR "HIE"[tiab] OR "neonatal encephalopathy"[tiab] OR "asphyxia"[tiab]
   OR "birth asphyxia"[tiab] OR "perinatal asphyxia"[tiab])
)""".replace("\n", " ")

query_simple = '("hypoxic ischemic encephalopathy" OR HIE) AND ("therapeutic hypothermia" OR cooling) AND (glucose OR glycemia OR hypoglycemia OR hyperglycemia)'

import os

script_path = os.path.join(os.path.dirname(__file__), "literature_search.py")
print("Running complex...")
subprocess.run([sys.executable, script_path, query_complex, "--max-results", "1000", "--output", "results_complex"])

print("\nRunning simple...")
subprocess.run([sys.executable, script_path, query_simple, "--max-results", "1000", "--output", "results_simple"])
