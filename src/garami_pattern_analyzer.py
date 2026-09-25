"""
Garami András Gondolkodási Mintázat Elemző
==========================================
Ez a script Claude AI segítségével elemzi Garami András publikációit
és kinyeri a hőszabályozási kutatói profilját.
"""

import json
import os
import sys
import io
import glob
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()
from anthropic import Anthropic

# --- KONFIGURÁCIÓ ---
OUTPUT_DIR = "garami_publications"
ANALYSIS_OUTPUT = "garami_agent_profile.json"
client = Anthropic()

def load_latest_publications(output_dir: str) -> list[dict]:
    json_files = glob.glob(os.path.join(output_dir, "garami_publications_*.json"))
    if not json_files:
        raise FileNotFoundError(f"Nem találtam publikációs fájlt a '{output_dir}' mappában.")
    latest = max(json_files)
    print(f"📂 Betöltés: {latest}")
    with open(latest, encoding="utf-8") as f:
        return json.load(f)

def analyze_garami_dna(publications: list[dict]) -> dict:
    print(f"🧠 {len(publications)} publikáció elemzése Claude-dal...")
    
    # Reprezentatív minta a kontextus limit miatt (50 cikk elég a stílushoz és fő témákhoz)
    sample = publications[:50]
    
    texts = []
    for p in sample:
        texts.append(f"Cím: {p['title']}\nKulcsszavak: hőszabályozás, TRP csatornák, láz\nAbsztrakt: {p['abstract']}")
    
    combined = "\n---\n".join(texts)
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": f"""Elemezd Dr. Garami András alábbi tudományos publikációit. Keress mintázatokat az alábbiakban:
1. Fő kutatási területek (hőszabályozás, láz mechanizmusok, TRP csatornák, energetika).
2. Kísérleti modellek (rágcsálól, humán kísérletek).
3. Hipotézis-alkotási stílus.
4. Tipikus érvelési struktúra (hogyan vezeti fel a hőszabályozási zavarokat?).

PUBLIKÁCIÓK:
{combined}

Hozz létre egy JSON-t az alábbi struktúrában, amely a Garami Agent "lelkéül" szolgál:
{{
  "expertise_areas": ["terület1", ...],
  "thermal_logic_framework": "leírás",
  "typical_experimental_patterns": ["módszer1", ...],
  "system_prompt": "Első személyű system prompt (400-600 szó), amely Dr. Garami András hőszabályozási szakértő hangvételét és tudását tükrözi. Legyen szakszerű, precíz, fókuszált a thermoreguláció élettani és kórélettani összefüggéseire."
}}
"""
        }]
    )
    
    text = response.content[0].text
    # JSON extract code from text here if needed, but for simplicity:
    # (Assuming Claude returns clean JSON or we'll wrap it)
    return text

if __name__ == "__main__":
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Error: Missing ANTHROPIC_API_KEY")
    else:
        pubs = load_latest_publications(OUTPUT_DIR)
        analysis = analyze_garami_dna(pubs)
        
        # Save raw analysis for now to check
        with open("garami_analysis_raw.txt", "w", encoding="utf-8") as f:
            f.write(analysis)
        print("✅ Elemzés elkészült.")
