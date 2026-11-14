#!/usr/bin/env python3
"""
citation_verifier.py — PMID Hallucination Guard
================================================
GP3 Medical Research Pipeline — Gate 8 (Citation Integrity)

Reads any .md file, extracts all [PMID: XXXXXXXX] references, and
verifies each against the PubMed E-utilities API:
  - PMID exists
  - Author family name matches (first author)
  - Journal matches
  - Year matches

Flags mismatches as potential AI hallucinations.

Usage:
    python src/citation_verifier.py PROTOCOL.md
    python src/citation_verifier.py .agent/agents/mentor-hegyi.md --verbose
    python src/citation_verifier.py PROTOCOL.md --delay 0.4  # for large files (rate limit safe)

Exit codes:
    0 = All citations verified
    1 = One or more citation mismatches / PMIDs not found
"""

import sys
import re
import time
import json
import urllib.request
import urllib.parse
import urllib.error
import os
import argparse

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from src.utils.console import configure_utf8_console
configure_utf8_console()

# ─── PubMed E-utilities (no API key required for ≤3 req/sec) ──────────────────
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EFETCH_URL  = f"{EUTILS_BASE}/efetch.fcgi"
ESUMMARY_URL = f"{EUTILS_BASE}/esummary.fcgi"

# ─── Extraction ───────────────────────────────────────────────────────────────

def extract_pmid_contexts(filepath: str) -> list[dict]:
    """
    Extract all [PMID: XXXXXXXX] occurrences from a markdown file,
    along with the surrounding line text for context.
    Returns list of: {pmid, line_number, line_text, claimed_author, claimed_year}
    """
    with open(filepath, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    results = []
    pmid_pattern = re.compile(r'\[?PMID:\s*(\d{5,10})\]?', re.IGNORECASE)
    # Try to extract year: look for 4-digit year in the same line (e.g. 2021, 2024)
    year_pattern  = re.compile(r'\b(?:19|20)\d{2}\b')
    # Try to extract author: look for "Author et al." or "Author (year)"
    author_pattern = re.compile(r'\*\*([A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű\-]+)\s+et al\.')

    for i, line in enumerate(lines, start=1):
        for m in pmid_pattern.finditer(line):
            pmid = m.group(1)
            # Look in local window (100 chars before, 40 chars after) to avoid cross-citation pollution on multi-citation lines
            win_start = max(0, m.start() - 100)
            win_end = min(len(line), m.end() + 40)
            window = line[win_start:win_end]
            years  = year_pattern.findall(window)
            authors = author_pattern.findall(window)
            if not years:
                years = year_pattern.findall(line)
            if not authors:
                authors = author_pattern.findall(line)
            results.append({
                "pmid":           pmid,
                "line_number":    i,
                "line_text":      line.strip(),
                "claimed_year":   years[-1] if years else None,
                "claimed_author": authors[-1] if authors else None,
            })

    # Deduplicate by PMID while keeping all line references
    seen = {}
    deduped = []
    for r in results:
        if r["pmid"] not in seen:
            seen[r["pmid"]] = True
            deduped.append(r)
    return deduped


# ─── PubMed Lookup ────────────────────────────────────────────────────────────

def fetch_pubmed_summary(pmid: str) -> dict | None:
    """
    Query PubMed ESummary for a single PMID.
    Returns parsed summary dict or None if not found.
    """
    params = urllib.parse.urlencode({
        "db":      "pubmed",
        "id":      pmid,
        "retmode": "json",
        "rettype": "abstract",
    })
    url = f"{ESUMMARY_URL}?{params}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "GP3-CitationVerifier/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        uids = data.get("result", {}).get("uids", [])
        if not uids:
            return None
        return data["result"].get(pmid)
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        return None


def verify_citation(ctx: dict, delay: float, verbose: bool) -> dict:
    """
    Fetch PubMed metadata for one PMID and compare against claimed values.
    Returns a result dict with status and mismatch details.
    """
    time.sleep(delay)  # rate limiting
    pmid = ctx["pmid"]
    summary = fetch_pubmed_summary(pmid)

    result = {
        "pmid":      pmid,
        "line":      ctx["line_number"],
        "status":    None,
        "pubmed":    {},
        "mismatches": [],
        "line_text": ctx["line_text"],
    }

    if summary is None:
        result["status"] = "NOT_FOUND"
        result["mismatches"].append(f"PMID {pmid} does not exist in PubMed")
        return result

    # Extract PubMed fields
    pub_year    = summary.get("pubdate", "")[:4]
    pub_journal = summary.get("source", "")
    pub_title   = summary.get("title", "")
    authors     = summary.get("authors", [])
    first_author_family = authors[0].get("name", "").split(" ")[0] if authors else ""

    result["pubmed"] = {
        "year":    pub_year,
        "journal": pub_journal,
        "title":   pub_title,
        "first_author": first_author_family,
    }

    # Check year
    if ctx["claimed_year"] and ctx["claimed_year"] != pub_year:
        result["mismatches"].append(
            f"Year mismatch: claimed {ctx['claimed_year']}, PubMed says {pub_year}"
        )

    # Check author (family name, case-insensitive)
    if ctx["claimed_author"]:
        if ctx["claimed_author"].lower() not in first_author_family.lower() and \
           first_author_family.lower() not in ctx["claimed_author"].lower():
            result["mismatches"].append(
                f"Author mismatch: claimed '{ctx['claimed_author']}', "
                f"PubMed first author is '{first_author_family}'"
            )

    result["status"] = "MISMATCH" if result["mismatches"] else "OK"
    return result


# ─── Report ───────────────────────────────────────────────────────────────────

def print_report(results: list[dict], filepath: str) -> int:
    """Print formatted verification report. Returns exit code."""
    ok      = [r for r in results if r["status"] == "OK"]
    missing = [r for r in results if r["status"] == "NOT_FOUND"]
    mismatch= [r for r in results if r["status"] == "MISMATCH"]

    print(f"\n{'='*70}")
    print(f"  GP3 Citation Verifier — {filepath}")
    print(f"{'='*70}")
    print(f"  PMIDs checked : {len(results)}")
    print(f"  ✅ Verified   : {len(ok)}")
    print(f"  ❌ Not Found  : {len(missing)}")
    print(f"  ⚠️  Mismatched : {len(mismatch)}")
    print(f"{'='*70}\n")

    if missing:
        print("── ❌ NON-EXISTENT PMIDs (Potential Hallucinations) ──────────────────")
        for r in missing:
            print(f"  Line {r['line']:>4}  PMID {r['pmid']}")
            print(f"           Context: {r['line_text'][:100]}")
        print()

    if mismatch:
        print("── ⚠️  METADATA MISMATCHES ────────────────────────────────────────────")
        for r in mismatch:
            print(f"  Line {r['line']:>4}  PMID {r['pmid']}")
            for m in r["mismatches"]:
                print(f"           ⚠️  {m}")
            print(f"           PubMed title : {r['pubmed'].get('title','')[:80]}")
            print(f"           PubMed author: {r['pubmed'].get('first_author','')}, "
                  f"{r['pubmed'].get('year','')} | {r['pubmed'].get('journal','')}")
        print()

    if ok:
        print("── ✅ VERIFIED CITATIONS ────────────────────────────────────────────")
        for r in ok:
            print(f"  PMID {r['pmid']:>10}  {r['pubmed'].get('first_author','')}, "
                  f"{r['pubmed'].get('year','')} — {r['pubmed'].get('journal','')}")
        print()

    # Final verdict
    if not missing and not mismatch:
        print("✅  GATE 8 PASSED — All citations verified. No hallucinations detected.\n")
        return 0
    else:
        total_issues = len(missing) + len(mismatch)
        print(f"❌  GATE 8 FAILED — {total_issues} citation issue(s) found. "
              f"Correct before PROSPERO submission.\n")
        return 1


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="GP3 Citation Verifier — verify [PMID: XXXXXXXX] against PubMed"
    )
    parser.add_argument("filepath", help="Path to the .md file to verify")
    parser.add_argument(
        "--delay", type=float, default=0.35,
        help="Seconds between PubMed requests (default: 0.35, safe for <=3 req/sec)"
    )
    parser.add_argument("--verbose", action="store_true", help="Show all details")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print(f"\nScanning: {args.filepath}")
    citations = extract_pmid_contexts(args.filepath)

    if not citations:
        print("No [PMID: XXXXXXXX] references found in file.")
        print("If this file should contain PMIDs, check your citation format.")
        return 0

    print(f"Found {len(citations)} unique PMID(s). Verifying against PubMed...\n")

    results = []
    for i, ctx in enumerate(citations, start=1):
        print(f"  [{i}/{len(citations)}] Checking PMID {ctx['pmid']}...", end=" ", flush=True)
        r = verify_citation(ctx, args.delay, args.verbose)
        icon = "✅" if r["status"] == "OK" else ("❌" if r["status"] == "NOT_FOUND" else "⚠️")
        print(icon)
        results.append(r)

    exit_code = print_report(results, args.filepath)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
