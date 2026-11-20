#!/usr/bin/env python3
"""
========================================================================================
GP3 Universal Meta-Analysis Pipeline (UMAP) — Master Orchestration CLI
========================================================================================
Standard: Centre for Translational Medicine (CTM) · Cochrane Handbook v6.5 · PRISMA 2020
Purpose: Universal, reproducible CLI for researchers conducting systematic reviews and meta-analyses.

Commands:
  umap new <slug>                  Scaffold a new standardized meta-analysis workspace
  umap status [slug]               Inspect stage progress, phase gates, and mentor scores
  umap validate-protocol <file>    Run the 7-Gate CTM Protocol Compliance Linter
  umap check-gate <phase>          Verify phase gate readiness (Phases 1 to 5)
  umap search "<query>"            Execute 3-domain systematic literature search
  umap screen --from-file <json>   Run PRISMA 2020 literature screening and Kappa audit
  umap audit-data                  Execute TRIPOD+AI data and modeling integrity audit
  umap verify-citations <file>     Verify PMIDs and citations against live PubMed
"""

import sys
import os
import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime

# Root workspace directory
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
PROJECTS_DIR = ROOT_DIR / "projects"
TEMPLATES_DIR = ROOT_DIR / "data" / "wiki" / "templates"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.utils.console import configure_utf8_console
configure_utf8_console()


def command_new(args):
    """Scaffold a new standardized meta-analysis workspace."""
    slug = args.slug.strip().lower().replace(" ", "_")
    target_dir = PROJECTS_DIR / slug

    if target_dir.exists():
        print(f"[-] Error: Project '{slug}' already exists at {target_dir}")
        return 1

    print(f"[*] Initializing Universal Meta-Analysis Workspace for: '{slug}'")

    # Create canonical directory structure
    subdirs = [
        target_dir / "protocol",
        target_dir / "literature",
        target_dir / "data" / "study_dossiers",
        target_dir / "synthesis" / "forest_plots",
        target_dir / "manuscript" / "figures_and_tables",
        target_dir / "scripts",
    ]
    for d in subdirs:
        d.mkdir(parents=True, exist_ok=True)

    # Copy project template
    template_project = ROOT_DIR / "PROJECT.template.md"
    project_md = target_dir / "PROJECT.md"
    if template_project.exists():
        content = template_project.read_text(encoding="utf-8")
        content = content.replace("{{PROJECT_SLUG}}", slug)
        content = content.replace("{{DATE}}", datetime.now().strftime("%Y-%m-%d"))
        project_md.write_text(content, encoding="utf-8")
    else:
        project_md.write_text(f"# Project: {slug}\nCreated: {datetime.now().strftime('%Y-%m-%d')}\n", encoding="utf-8")

    # Copy PROSPERO registration template
    template_prospero = TEMPLATES_DIR / "PROSPERO_REGISTRATION_TEMPLATE.md"
    prospero_md = target_dir / "protocol" / "PROSPERO_DRAFT.md"
    if template_prospero.exists():
        p_content = template_prospero.read_text(encoding="utf-8")
        p_content = p_content.replace("[INSERT PROJECT TITLE / SLUG]", slug)
        prospero_md.write_text(p_content, encoding="utf-8")

    # Copy CTM Excel template if available
    template_xlsx = TEMPLATES_DIR / "Data_extraction_template_v9_BLANK.xlsx"
    if not template_xlsx.exists():
        template_xlsx = TEMPLATES_DIR / "Data_extraction_template_v9.xlsx"
    if template_xlsx.exists():
        shutil.copy(template_xlsx, target_dir / "data" / f"Extraction_{slug}_Template_v9.xlsx")

    print(f"[+] Successfully scaffolded project at: {target_dir}")
    print(f"    - Protocol drafting: {prospero_md}")
    print(f"    - Project Manifest:  {project_md}")
    print(f"    - Data Extraction:   {target_dir / 'data'}")
    return 0


def command_status(args):
    """Report status and active projects."""
    print("=" * 72)
    print("   GP3 UNIVERSAL META-ANALYSIS PIPELINE — WORKSPACE STATUS   ")
    print("=" * 72)

    if not PROJECTS_DIR.exists():
        print("[-] No projects directory found.")
        return 0

    projects = [p for p in PROJECTS_DIR.iterdir() if p.is_dir()]
    if not projects:
        print("No active projects found in projects/.")
        return 0

    print(f"Found {len(projects)} registered project workspaces:\n")
    for p in sorted(projects):
        p_md = p / "PROJECT.md"
        prospero_f = p / "protocol" / "PROSPERO_DRAFT.md"
        data_f = p / "data"
        has_data = any(data_f.iterdir()) if data_f.exists() else False

        status_str = "ACTIVE"
        if p_md.exists():
            for line in p_md.read_text(encoding="utf-8", errors="ignore").splitlines()[:15]:
                if "Phase" in line or "Status" in line:
                    status_str = line.strip().strip("-*# ")
                    break

        print(f" • {p.name:<25} | Status: {status_str}")
        print(f"   Directory: {p}")
        print(f"   Has Protocol: {'Yes' if prospero_f.exists() else 'No'} | Has Extraction Data: {'Yes' if has_data else 'No'}\n")

    return 0


def forward_to_script(script_name, script_args):
    """Execute another script in src/ passing through arguments."""
    script_path = SRC_DIR / script_name
    if not script_path.exists():
        print(f"[-] Error: Script not found: {script_path}")
        return 1

    cmd = [sys.executable, str(script_path)] + script_args
    import subprocess
    res = subprocess.run(cmd)
    return res.returncode


def main():
    parser = argparse.ArgumentParser(
        description="GP3 Universal Meta-Analysis Pipeline (UMAP) Master CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: new
    parser_new = subparsers.add_parser("new", help="Scaffold a new meta-analysis project")
    parser_new.add_argument("slug", help="Project slug (e.g., neonatal_cooling_biomarkers)")

    # Command: status
    parser_status = subparsers.add_parser("status", help="Inspect workspace project statuses")
    parser_status.add_argument("slug", nargs="?", help="Optional specific project slug")

    # Command: validate-protocol
    parser_val = subparsers.add_parser("validate-protocol", help="Run 7-Gate CTM Protocol Compliance Linter")
    parser_val.add_argument("protocol_file", help="Path to PROTOCOL.md or PROSPERO draft")

    # Command: check-gate
    parser_gate = subparsers.add_parser("check-gate", help="Check deterministic phase gate readiness")
    parser_gate.add_argument("--target-phase", type=int, required=True, help="Target phase number (1 to 5)")

    # Command: search
    parser_search = subparsers.add_parser("search", help="Execute 3-domain systematic literature search")
    parser_search.add_argument("query", help="PubMed Boolean search query")
    parser_search.add_argument("--analyze", action="store_true", help="Analyze results and identify white spots")
    parser_search.add_argument("--max-results", type=int, default=100, help="Max results to fetch")

    # Command: screen
    parser_screen = subparsers.add_parser("screen", help="Screen literature results against inclusion criteria")
    parser_screen.add_argument("--from-file", required=True, help="JSON search results file")
    parser_screen.add_argument("--p-terms", default="", help="Population search terms")
    parser_screen.add_argument("--i-terms", default="", help="Intervention/exposure search terms")

    # Command: audit-data
    subparsers.add_parser("audit-data", help="Execute TRIPOD+AI data and modeling integrity audit")

    # Command: verify-citations
    parser_cite = subparsers.add_parser("verify-citations", help="Verify PMIDs in protocol file")
    parser_cite.add_argument("file", help="Path to markdown protocol file")

    # Command: compile-prospero
    parser_comp_prospero = subparsers.add_parser("compile-prospero", help="Compile CTM PROSPERO draft (Guide v6.0/v6.1)")
    parser_comp_prospero.add_argument("slug", help="Project slug in projects/<slug>")
    parser_comp_prospero.add_argument("--output", "-o", help="Custom output path")

    # Command: validate-prospero
    parser_val_prospero = subparsers.add_parser("validate-prospero", help="Audit PROSPERO draft against CTM Guide v6.0/v6.1")
    parser_val_prospero.add_argument("target", nargs="?", help="Path to PROSPERO draft markdown or project slug")

    # Command: deduplicate / dedup
    parser_dedup = subparsers.add_parser("deduplicate", aliases=["dedup"], help="Phase 6: Multi-database search deduplication and PRISMA 2020 calculation")
    parser_dedup.add_argument("slug", help="Project slug in projects/<slug>")
    parser_dedup.add_argument("--input-dir", "-i", help="Custom input directory with .ris/.nbib files")
    parser_dedup.add_argument("--output-dir", "-o", help="Custom output directory")

    # Command: screen-nlp
    parser_screennlp = subparsers.add_parser("screen-nlp", help="Phase 7: AI/NLP TF-IDF & BM25 Relevance Screener")
    parser_screennlp.add_argument("slug", help="Project slug in projects/<slug>")
    parser_screennlp.add_argument("--threshold", "-t", type=float, default=0.15, help="Similarity threshold for inclusion")

    args, unknown = parser.parse_known_args()

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "new":
        return command_new(args)
    elif args.command == "status":
        return command_status(args)
    elif args.command == "validate-protocol":
        return forward_to_script("validate_protocol.py", [args.protocol_file] + unknown)
    elif args.command == "check-gate":
        return forward_to_script("check_phase_gate.py", ["--target-phase", str(args.target_phase)] + unknown)
    elif args.command == "compile-prospero":
        p_args = ["--project", args.slug]
        if args.output:
            p_args.extend(["--output", args.output])
        return forward_to_script("prospero_compiler.py", p_args + unknown)
    elif args.command == "validate-prospero":
        v_args = []
        if args.target:
            if (PROJECTS_DIR / args.target).is_dir():
                v_args.extend(["--project", args.target])
            else:
                v_args.extend(["--file", args.target])
        return forward_to_script("validate_prospero_draft.py", v_args + unknown)
    elif args.command in ("deduplicate", "dedup"):
        d_args = ["--project", args.slug]
        if args.input_dir:
            d_args.extend(["--input-dir", args.input_dir])
        if args.output_dir:
            d_args.extend(["--output-dir", args.output_dir])
        return forward_to_script("deduplicate_exports.py", d_args + unknown)
    elif args.command == "screen-nlp":
        return forward_to_script("ai_screener.py", ["--project", args.slug, "--threshold", str(args.threshold)] + unknown)
    elif args.command == "search":
        s_args = [args.query, "--max-results", str(args.max_results)]
        if args.analyze:
            s_args.append("--analyze")
        return forward_to_script("literature_search.py", s_args + unknown)
    elif args.command == "screen":
        s_args = ["--from-file", args.from_file]
        if args.p_terms:
            s_args.extend(["--p-terms", args.p_terms])
        if args.i_terms:
            s_args.extend(["--i-terms", args.i_terms])
        return forward_to_script("screen_literature.py", s_args + unknown)
    elif args.command == "audit-data":
        return forward_to_script("audit_data_integrity.py", unknown)
    elif args.command == "verify-citations":
        return forward_to_script("citation_verifier.py", [args.file] + unknown)

    return 0


if __name__ == "__main__":
    sys.exit(main())

