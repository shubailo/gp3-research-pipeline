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
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def main():
    parser = argparse.ArgumentParser(
        description="Irodalomkutató, Fehér Folt (White Spot) és Keresőkulcs Provenance Elemző – PubMed + Cochrane.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Példák:
  # Keresés és mentés (az AI ezután elemezheti a találatokat):
  python literature_search.py "neonatal hypothermia AND outcome"

  # Keresés + absztraktok és kulcsszavak kinyomtatása stdout-ra:
  python literature_search.py "TRPA1 AND inflammation" --analyze

  # Precedens metaanalízisek vizsgálata adott PMID-k alapján:
  python literature_search.py --pmids 23440789,37316160,39501186 --enrich-provenance

  # Meglévő eredmény fájl betöltése és kinyomtatása elemzéshez:
  python literature_search.py --from-file results/search_20260912_135015.json
        """
    )
    parser.add_argument(
        "query", type=str, nargs="?",
        help="Keresési kifejezés (PubMed szintaxis: pl. 'neonatal hypothermia AND outcome')"
    )
    parser.add_argument(
        "--pmids", type=str, default="",
        help="Vesszővel elválasztott PMID lista közvetlen lekéréshez és precedens-analízishez"
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
        help="Kinyomtatja az absztraktokat és metaadatokat stdout-ra – így az AI azonnal elemezheti"
    )
    parser.add_argument(
        "--enrich-provenance", action="store_true",
        help="Futtatja a 3 szintű (Gold/Silver/Bronze) keresőkulcs-provenance besorolást és PMC ellenőrzést"
    )
    parser.add_argument(
        "--from-file", type=str, metavar="JSON_PATH",
        help="Meglévő keresési eredmény JSON betöltése új keresés nélkül"
    )

    args = parser.parse_args()
    analyzer = WhiteSpotAnalyzer()
    pubmed   = PubMedClient(email=args.email)

    # ── Mode: direct PMID list analysis ──────────────────────────────────────
    if args.pmids:
        pmid_list = [p.strip() for p in args.pmids.split(",") if p.strip()]
        print("="*68)
        print(" 🔍 PRECEDENS METAANALÍZIS PROVENANCE ÉS ADATGAZDAGÍTÁS")
        print("="*68)
        print(f"Lekérdezett PMID-k ({len(pmid_list)} db): {', '.join(pmid_list)}\n")

        raw_pubs = pubmed.get_by_pmids(pmid_list)
        if not raw_pubs:
            print("[Hiba] Egyik megadott PMID sem tölthető le az NCBI-ről.")
            sys.exit(1)

        print(f">>> {len(raw_pubs)} db publikáció sikeresen letöltve a PubMedről.")
        print(">>> Provenance hierarchia értékelése (Cochrane -> PMC OA -> MeSH -> Text)...")
        enriched_pubs = pubmed.enrich_with_provenance(raw_pubs, check_pmc_oa=True)

        print("\n" + "="*68)
        print(" 📋 KANONIKUS PRECEDENS TÁBLÁZAT (CTM SEARCH KEY GUIDE)")
        print("="*68)
        table_md = pubmed.format_precedent_table(enriched_pubs)
        print(table_md)
        print("\n" + "="*68)
        print(" 🔬 RÉSZLETES PRECEDENS DOKUMENTÁCIÓ")
        print("="*68)
        for pub in enriched_pubs:
            prov = pub.get("provenance", {})
            print(f"\n[PMID: {pub.get('id')}] {pub.get('title')}")
            print(f"  • Folyóirat  : {pub.get('journal', 'Ismeretlen')}")
            print(f"  • PMCID      : {pub.get('pmcid') or 'Nincs (Paywall / Non-PMC)'}")
            print(f"  • Provenance : {prov.get('provenance_label')} ({prov.get('tier')} Tier)")
            print(f"  • Forrás leírás: {prov.get('description')}")
            
            # Print MeSH terms
            mesh = pub.get("mesh_headings", [])
            major_mesh = [m["descriptor"] for m in mesh if m.get("is_major")]
            all_mesh = [m["descriptor"] for m in mesh]
            print(f"  • MeSH száma : {len(mesh)} (Kiemelt Major: {len(major_mesh)})")
            if major_mesh:
                print(f"  • Kiemelt MeSH: {', '.join(major_mesh)}")
            elif all_mesh:
                print(f"  • MeSH list  : {', '.join(all_mesh[:6])}")
                
            # Print Keywords
            kws = [k["keyword"] for k in pub.get("author_keywords", [])]
            if kws:
                print(f"  • Szerzői KW : {', '.join(kws)}")
                
            if prov.get("search_strategy_snippet"):
                print(f"  • Kinyert keresési stratégia részlet:\n    \"{prov.get('search_strategy_snippet')}\"")

        # Save results
        os.makedirs(args.output, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = os.path.join(args.output, f"precedents_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(enriched_pubs, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Mentve: {json_path}")
        return

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
        parser.error("Adj meg keresési kifejezést (--pmids, keresési string, vagy --from-file).")

    print("="*62)
    print(" 🔎 Irodalomkutató és Fehér Folt (White Spot) Elemző")
    print("="*62)
    print(f"Keresési kifejezés : {args.query}")
    print(f"Visszatekintési ablak: {args.years} év\n")

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

    # If provenance enrichment requested
    if args.enrich_provenance:
        print(">>> Provenance és MeSH gazdagítás futtatása...")
        result["publications"] = pubmed.enrich_with_provenance(result["publications"], check_pmc_oa=True)

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

        if args.enrich_provenance:
            f.write("## 3. Precedens & Provenance Elemzés\n\n")
            f.write(pubmed.format_precedent_table(result["publications"][:15]))
            f.write("\n\n")

        f.write("## 4. Kvalitatív Elemzés (AI)\n\n")
        f.write("*A kvalitatív elemzést az AI (Claude) végzi az absztraktok alapján.*\n")
        f.write("*Futtasd: `python literature_search.py --from-file <json_path>` és add át az AI-nak.*\n\n")

    print(f"\n💾 Elmentve → '{args.output}' mappa:")
    print(f"   📄 {json_path}  (nyers JSON – AI elemzéshez)")
    print(f"   📝 {md_path}  (kvantitatív összefoglaló)")

    if args.analyze:
        print("\n" + "─"*62)
        print("  📋 ABSZTRAKT DIGEST (AI ELEMZÉSHEZ)")
        print("─"*62 + "\n")
        print(result["abstract_digest"])


if __name__ == "__main__":
    main()
