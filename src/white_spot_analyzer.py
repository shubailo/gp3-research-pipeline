from typing import List, Dict, Any
from collections import Counter
from datetime import datetime
import sys
import io

import os

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from src.utils.console import configure_utf8_console
configure_utf8_console()


class WhiteSpotAnalyzer:
    """
    Identifies research gaps ('white spots') from PubMed + Cochrane publication data.

    Quantitative analysis: publication volume, trend direction, recent activity.
    Qualitative analysis: performed by the AI (Claude) reading the output directly.
    """

    SPARSE_THRESHOLD_PER_YEAR = 2

    def deduplicate(self, publications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates by DOI (preferred) or normalised title. Merges source labels."""
        unique_pubs: Dict[str, Dict] = {}
        for pub in publications:
            key = (pub.get("doi") or "").strip() or pub.get("title", "").lower().strip()
            if not key:
                continue
            if key not in unique_pubs:
                unique_pubs[key] = pub
            else:
                existing_source = unique_pubs[key].get("source", "")
                new_source = pub.get("source", "")
                if new_source and new_source not in existing_source:
                    unique_pubs[key]["source"] = f"{existing_source}, {new_source}"
        return list(unique_pubs.values())

    def quantitative_analysis(
        self, publications: List[Dict[str, Any]], lookback_years: int = 5
    ) -> Dict[str, Any]:
        """
        Publication volume and trend analysis over configurable window.
        Compares recent period vs. equally long prior period to detect trend direction.
        """
        if not publications:
            return {
                "total_publications": 0,
                "recent_publications": 0,
                "prior_period_publications": 0,
                "lookback_years": lookback_years,
                "trend": "no_data",
                "is_quantitative_white_spot": True,
                "explanation": "Egyáltalán nincs publikáció erre a témára.",
                "year_distribution": {}
            }

        current_year = datetime.now().year
        year_counts = Counter(
            p.get("year") for p in publications if p.get("year")
        )

        recent_years = [str(y) for y in range(current_year - lookback_years + 1, current_year + 1)]
        prior_years  = [str(y) for y in range(current_year - lookback_years * 2 + 1, current_year - lookback_years + 1)]

        recent_count = sum(year_counts.get(y, 0) for y in recent_years)
        prior_count  = sum(year_counts.get(y, 0) for y in prior_years)

        if prior_count == 0 and recent_count == 0:
            trend = "flat"
        elif prior_count == 0:
            trend = "emerging"
        elif recent_count == 0:
            trend = "abandoned"
        else:
            ratio = recent_count / prior_count
            if ratio > 1.5:
                trend = "growing"
            elif ratio < 0.6:
                trend = "declining"
            else:
                trend = "stable"

        sparse = recent_count < (self.SPARSE_THRESHOLD_PER_YEAR * lookback_years)
        is_white_spot = sparse or trend in ("abandoned", "flat", "declining")

        trend_labels = {
            "growing":   "📈 Növekvő érdeklődés",
            "declining": "📉 Csökkenő érdeklődés – potenciális fehér folt",
            "stable":    "➡️  Stabil kutatási aktivitás",
            "flat":      "⬛ Nincs adat egyik periódusban sem",
            "emerging":  "🌱 Újonnan megjelenő téma",
            "abandoned": "⚠️  Korábban kutatott, jelenleg elhagyott terület",
            "no_data":   "❓ Nincs adat",
        }

        explanation_parts = [trend_labels.get(trend, trend)]
        if sparse:
            explanation_parts.append(
                f"Az elmúlt {lookback_years} évben csak {recent_count} publikáció "
                f"(min. elvárás: {self.SPARSE_THRESHOLD_PER_YEAR * lookback_years})."
            )

        return {
            "total_publications": len(publications),
            "recent_publications": recent_count,
            "prior_period_publications": prior_count,
            "lookback_years": lookback_years,
            "trend": trend,
            "is_quantitative_white_spot": is_white_spot,
            "explanation": " | ".join(explanation_parts),
            "year_distribution": dict(sorted(year_counts.items())),
        }

    def build_abstract_digest(
        self, publications: List[Dict[str, Any]], max_abstracts: int = 30
    ) -> str:
        """
        Build a compact, human-readable digest of the most informative abstracts.
        This text is designed to be read by Claude (or any AI) for qualitative gap analysis.
        """
        with_abstracts = sorted(
            [p for p in publications if p.get("abstract") and len(p["abstract"]) > 80],
            key=lambda p: len(p.get("abstract", "")),
            reverse=True
        )[:max_abstracts]

        if not with_abstracts:
            return "No abstracts available for qualitative analysis."

        lines = [
            f"=== ABSTRACT DIGEST ({len(with_abstracts)} publications) ===\n",
            "Use this to identify: missing populations/subgroups, absent interventions,",
            "author-stated limitations, geographic gaps, and unanswered clinical questions.\n",
        ]
        for i, pub in enumerate(with_abstracts, 1):
            lines.append(f"\n[{i}] {pub.get('title', 'No title')} ({pub.get('year', '?')}) — {pub.get('source', '?')}")
            if pub.get("doi"):
                lines.append(f"    DOI: {pub['doi']}")
            lines.append(f"    {pub['abstract']}")

        return "\n".join(lines)

    def analyze(
        self,
        publications: List[Dict[str, Any]],
        query: str,
        lookback_years: int = 5,
    ) -> Dict[str, Any]:
        """Full pipeline: dedup → quantitative analysis → abstract digest for AI review."""
        print(f"[Analyzer] Nyers találatok: {len(publications)}")

        deduped = self.deduplicate(publications)
        print(f"[Analyzer] Egyedi találatok (deduplikáció után): {len(deduped)}")

        quant = self.quantitative_analysis(deduped, lookback_years)
        print(f"[Analyzer] Trend: {quant['trend']} | Fehér folt: {quant['is_quantitative_white_spot']}")

        abstract_digest = self.build_abstract_digest(deduped)

        return {
            "query": query,
            "unique_results_count": len(deduped),
            "quantitative_analysis": quant,
            "abstract_digest": abstract_digest,
            "publications": deduped,
        }
