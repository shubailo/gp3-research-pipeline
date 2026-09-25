import argparse
import json
import os
import sys
from datetime import datetime

# Ensure project root is in sys.path so api_clients can be imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from api_clients.pubmed_client import PubMedClient
from api_clients.cochrane_client import CochraneClient
from white_spot_analyzer import WhiteSpotAnalyzer

import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(
        description="Irodalomkutató és Fehér Folt (White Spot) Elemző – PubMed + Cochrane.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Példák:
  # Keresés és mentés (az AI ezután elemzi a találatokat):
  python literature_search.py "neonatal hypothermia AND outcome"

  # Keresés + az absztraktok kinyomtatása (AI közvetlen elemzéshez):
  python literature_search.py "TRPA1 AND inflammation" --analyze

  # Meglévő eredmény fájl betöltése és kinyomtatása elemzéshez:
  python literature_search.py --from-file results/search_20260912_135015.json

  # Visszatekintési ablak és max találat beállítása:
  python literature_search.py "propofol AND newborn" --years 10 --max-results 50
        """
    )
    parser.add_argument(
        "query", type=str, nargs="?",
        help="Keresési kifejezés (PubMed szintaxis: pl. 'neonatal hypothermia AND outcome')"
    )
    parser.add_argument(
        "--max-results", type=int, default=100,
        help="Maximum találat forrásonként (alapértelmezett: 100)"
    )
    parser.add_argument(
        "--years", type=int, default=5,
        help="Visszatekintési ablak években fehér folt értékeléshez (alapértelmezett: 5)"
    )
    parser.add_argument(
        "--email", type=str, default="researcher@example.com",
        help="Email cím az NCBI E-utilities-hez (ajánlott megadni)"
    )
    parser.add_argument(
        "--output", type=str, default="results",
        help="Kimeneti mappa neve (alapértelmezett: results/)"
    )
    parser.add_argument(
        "--analyze", action="store_true",
        help="Kinyomtatja az absztraktokat stdout-ra – így az AI azonnal elemezheti"
    )
    parser.add_argument(
        "--from-file", type=str, metavar="JSON_PATH",
        help="Meglévő keresési eredmény JSON betöltése új keresés nélkül"
    )

    args = parser.parse_args()
    analyzer = WhiteSpotAnalyzer()

    # ── Mode: load from existing JSON ────────────────────────────────────────
    if args.from_file:
        with open(args.from_file, encoding="utf-8") as f:
            saved = json.load(f)
        digest = saved.get("analysis", {}).get("abstract_digest") or \
                 analyzer.build_abstract_digest(saved.get("publications", []))
        print(digest)
        return

    # ── Mode: new search ─────────────────────────────────────────────────────
    if not args.query:
        parser.error("Adj meg keresési kifejezést, vagy használd a --from-file opciót.")

    print("="*62)
    print(" 🔎 Irodalomkutató és Fehér Folt (White Spot) Elemző")
    print("="*62)
    print(f"Keresési kifejezés : {args.query}")
    print(f"Visszatekintési ablak: {args.years} év\n")

    pubmed   = PubMedClient(email=args.email)
    cochrane = CochraneClient(email=args.email)
    all_publications = []

    print(">>> PubMed lekérdezése...")
    pubmed_results = pubmed.search(args.query, args.max_results)
    print(f"    Találat: {len(pubmed_results)}")
    all_publications.extend(pubmed_results)

    print(">>> Cochrane lekérdezése...")
    cochrane_results = cochrane.search(args.query, args.max_results)
    print(f"    Találat: {len(cochrane_results)}")
    all_publications.extend(cochrane_results)

    print("\n>>> Elemzés és deduplikáció...")
    result = analyzer.analyze(all_publications, args.query, lookback_years=args.years)

    # ── Display summary ───────────────────────────────────────────────────────
    quant = result["quantitative_analysis"]
    print("\n" + "="*62)
    print(" 📊 KVANTITATÍV ÖSSZEFOGLALÓ")
    print("="*62)
    print(f"Összes egyedi publikáció  : {result['unique_results_count']}")
    print(f"Elmúlt {quant['lookback_years']} év              : {quant['recent_publications']} cikk")
    print(f"Előző {quant['lookback_years']} év              : {quant['prior_period_publications']} cikk")
    print(f"Trend                     : {quant['trend']}")
    print(f"Kvantitatív fehér folt    : {'✅ IGEN' if quant['is_quantitative_white_spot'] else '❌ NEM'}")
    print(f"Magyarázat                : {quant['explanation']}")
    print("="*62)

    # ── Save outputs ──────────────────────────────────────────────────────────
    os.makedirs(args.output, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = os.path.join(args.output, f"search_{timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    md_path = os.path.join(args.output, f"analysis_{timestamp}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Irodalomkutatás: Fehér Folt Elemzés\n\n")
        f.write(f"**Keresési kifejezés:** `{args.query}`  \n")
        f.write(f"**Dátum:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Visszatekintési ablak:** {args.years} év\n\n---\n\n")

        f.write("## 1. Találatok összesítő\n\n")
        f.write(f"| Forrás | Találat |\n|--------|--------|\n")
        f.write(f"| PubMed | {len(pubmed_results)} |\n")
        f.write(f"| Cochrane | {len(cochrane_results)} |\n")
        f.write(f"| **Összes egyedi** | **{result['unique_results_count']}** |\n\n")

        f.write("## 2. Kvantitatív Fehér Folt Elemzés\n\n")
        f.write(f"| Mutató | Érték |\n|--------|------|\n")
        f.write(f"| Elmúlt {quant['lookback_years']} év | {quant['recent_publications']} cikk |\n")
        f.write(f"| Előző {quant['lookback_years']} év | {quant['prior_period_publications']} cikk |\n")
        f.write(f"| Trend | `{quant['trend']}` |\n")
        f.write(f"| Fehér folt | {'**IGEN** ⚠️' if quant['is_quantitative_white_spot'] else 'NEM ✅'} |\n\n")
        f.write(f"**Magyarázat:** {quant['explanation']}\n\n")
        f.write("### Évenkénti eloszlás\n\n```json\n")
        f.write(json.dumps(quant.get("year_distribution", {}), indent=2, sort_keys=True))
        f.write("\n```\n\n")

        f.write("## 3. Kvalitatív Elemzés (AI)\n\n")
        f.write("*A kvalitatív elemzést az AI (Claude) végzi az absztraktok alapján.*\n")
        f.write("*Futtasd: `python literature_search.py --from-file <json_path>` és add át az AI-nak.*\n\n")

    print(f"\n💾 Elmentve → '{args.output}' mappa:")
    print(f"   📄 {json_path}  (nyers JSON – AI elemzéshez)")
    print(f"   📝 {md_path}  (kvantitatív összefoglaló)")

    # ── If --analyze: print digest for immediate AI reading ───────────────────
    if args.analyze:
        print("\n" + "─"*62)
        print("  📋 ABSZTRAKT DIGEST (AI ELEMZÉSHEZ)")
        print("─"*62 + "\n")
        print(result["abstract_digest"])


if __name__ == "__main__":
    main()
