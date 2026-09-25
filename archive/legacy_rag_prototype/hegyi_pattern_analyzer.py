"""
Hegyi Péter Gondolkodási Mintázat Elemző
=========================================
Ez a script Claude AI segítségével elemzi a publikációkat
és kinyeri a kutatói gondolkodásmód mintázatait.

A kimenet lesz az agent "lelke" – a system prompt alapja.

Előfeltétel: futtasd előbb a hegyi_pubmed_scraper.py-t!

Használat:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python hegyi_pattern_analyzer.py
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
OUTPUT_DIR = "hegyi_publications"
ANALYSIS_OUTPUT = "hegyi_agent_profile.json"
client = Anthropic()


def load_latest_publications(output_dir: str) -> list[dict]:
    """Betölti a legfrissebb JSON fájlt."""
    json_files = glob.glob(os.path.join(output_dir, "hegyi_publications_*.json"))
    if not json_files:
        raise FileNotFoundError(
            f"Nem találtam publikációs fájlt a '{output_dir}' mappában.\n"
            "Futtasd először a hegyi_pubmed_scraper.py scriptet!"
        )
    latest = max(json_files)
    print(f"📂 Betöltés: {latest}")
    with open(latest, encoding="utf-8") as f:
        return json.load(f)


def select_representative_sample(publications: list[dict], n: int = 50) -> list[dict]:
    """
    Kiválaszt n reprezentatív cikket elemzésre:
    - Csak absztrakttal rendelkezők
    - Különböző évekből
    - Különböző témákból
    """
    with_abstract = [p for p in publications if p.get("abstract") and len(p["abstract"]) > 100]

    # Évek szerinti elosztás
    from collections import defaultdict
    by_year = defaultdict(list)
    for p in with_abstract:
        by_year[p.get("year", "unknown")].append(p)

    selected = []
    years = sorted(by_year.keys(), reverse=True)
    per_year = max(1, n // len(years))

    for year in years:
        selected.extend(by_year[year][:per_year])
        if len(selected) >= n:
            break

    return selected[:n]


def analyze_batch_with_claude(publications: list[dict], batch_num: int, total_batches: int) -> str:
    """
    Elemez egy batch-nyi publikációt Claude-dal.
    """
    # Összeállítjuk a szöveget
    texts = []
    for p in publications:
        text = f"""
Cím: {p['title']}
Év: {p['year']}
Folyóirat: {p['journal']}
Kulcsszavak: {p.get('keywords', '')}
Absztrakt: {p['abstract']}
"""
        texts.append(text)

    combined = "\n---\n".join(texts)

    print(f"🧠 Claude elemzés: batch {batch_num}/{total_batches}...")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f\
                "\"\"Elemezd az alábbi tudományos publikációkat, amelyek mind Hegyi Péter transzlációs medicina kutatótól származnak.

Azonosítsd:
1. Visszatérő kutatási témák és fókuszterületek
2. Tipikus érvelési struktúrák (hogyan vezeti fel a klinikai relevanciát?)
3. Milyen kérdéseket tesz fel egy kutatási probléma kapcsán?
4. Hogyan köti össze az alapkutatást a klinikai alkalmazással?
5. Milyen módszertani megközelítések jellemzők?
6. Milyen betegségterületek, szervrendszerek dominálnak?

PUBLIKÁCIÓK:
{combined}

Válaszolj strukturáltan, pontokba szedve. Legyél konkrét és idézz példákat!\"\"\"
        }]
    )

    return response.content[0].text


def synthesize_agent_profile(batch_analyses: list[str], all_publications: list[dict]) -> dict:
    """
    Szintetizálja az összes batch-elemzést egy egységes agent profillá.
    """
    print("\n🔮 Agent profil szintézis...")

    combined_analyses = "\n\n===BATCH HATÁR===\n\n".join(batch_analyses)

    # Statisztikák
    years = [p["year"] for p in all_publications if p.get("year")]
    journals = [p["journal"] for p in all_publications if p.get("journal")]
    from collections import Counter
    top_journals = Counter(journals).most_common(10)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": f\"\"\"Az alábbi részleges elemzések alapján szintetizálj egy teljes 
\"digitális mentor\" profilt Hegyi Péter transzlációs medicina kutató személyiségéről.

STATISZTIKÁK:
- Összes publikáció: {len(all_publications)}
- Aktív évek: {min(years) if years else 'N/A'} - {max(years) if years else 'N/A'}
- Top folyóiratok: {', '.join([j for j,_ in top_journals[:5]])}

RÉSZLEGES ELEMZÉSEK:
{combined_analyses}

Hozz létre egy JSON objektumot az alábbi struktúrában:
{{
  "research_themes": ["téma1", "téma2", ...],
  "clinical_relevance_framework": "Hogyan gondolkodik a klinikai relevanciáról?",
  "typical_question_patterns": ["Milyen kérdést tesz fel?", ...],
  "translational_approach": "A T1→T4 transzlációs pipeline leírása nála",
  "methodology_preferences": ["módszer1", ...],
  "disease_focus_areas": ["terület1", ...],
  "mentoring_style_prompt": "System prompt egy PhD mentor agenthez (2-3 bekezdés)",
  "evaluation_criteria": ["Milyen szempontok alapján értékel egy PhD témát?", ...]
}}

CSAK JSON-t adj vissza, semmi mást!\"\"\"
        }]
    )

    text = response.content[0].text
    # JSON tisztítás
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print("⚠️ JSON parse hiba, nyers szöveget mentjük...")
        return {"raw_analysis": text}


def generate_system_prompt(profile: dict) -> str:
    """
    Generálja a végső system promptot az agent számára.
    """
    print("\n✍️ System prompt generálása...")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[{
            "role": "user",
            "content": f\"\"\"Az alábbi kutatói profil alapján írj egy részletes system promptot 
egy AI agenthez, amely Hegyi Péter stílusában segít PhD hallgatóknak 
klinikai szempontból releváns kutatási témákat megfogalmazni.

PROFIL:
{json.dumps(profile, ensure_ascii=False, indent=2)}

A system prompt:
- Legyen első személyben (\"Te egy tapasztalt transzlációs medicina kutató vagy...\")
- Tartalmazzon konkrét kérdéseket, amiket az agent mindig feltesz
- Definiálja, hogyan értékeli a klinikai relevanciát
- Magyar és angol témákat egyaránt tudjon kezelni
- Legyen 400-600 szó hosszú
- Tartalmazza Hegyi Péter kutatási területeit és szemléletmódját\"\"\"
        }]
    )

    return response.content[0].text


def main():
    print("="*55)
    print("  Hegyi Péter Gondolkodási Mintázat Elemző")
    print("="*55 + "\n")

    # 1. Betöltés
    publications = load_latest_publications(OUTPUT_DIR)
    print(f"📚 {len(publications)} publikáció betöltve\n")

    # 2. Mintavétel
    sample = select_representative_sample(publications, n=60)
    print(f"🎯 {len(sample)} reprezentatív cikk kiválasztva elemzésre\n")

    # 3. Batch elemzés (20-as batch-ek)
    batch_size = 20
    batches = [sample[i:i+batch_size] for i in range(0, len(sample), batch_size)]
    batch_analyses = []

    for i, batch in enumerate(batches):
        analysis = analyze_batch_with_claude(batch, i+1, len(batches))
        batch_analyses.append(analysis)

    # 4. Szintézis
    profile = synthesize_agent_profile(batch_analyses, publications)

    # 5. System prompt generálás
    system_prompt = generate_system_prompt(profile)
    profile["system_prompt"] = system_prompt

    # 6. Mentés
    with open(ANALYSIS_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Agent profil mentve: {ANALYSIS_OUTPUT}")

    # Előnézet
    print("\n" + "="*55)
    print("🤖 GENERÁLT SYSTEM PROMPT ELŐNÉZET:")
    print("="*55)
    print(system_prompt[:500] + "...")
    print("\n✅ Következő lépés: futtasd a hegyi_agent_app.py-t!")


if __name__ == "__main__":
    main()
