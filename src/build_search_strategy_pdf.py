"""
build_search_strategy_pdf.py
Generates the publication-quality, standalone Search Strategy PDF for PROSPERO upload (Section 6f).
Project: meta_hyperglycaemia
Standard: Centre for Translational Medicine (CTM) - PROSPERO Guide v6.0/v6.1
"""

import os
import sys
import argparse
from typing import Optional
import fitz  # PyMuPDF

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from src.utils.console import configure_utf8_console
configure_utf8_console()

DEFAULT_OUTPUT_PDF = os.path.join(WORKSPACE_ROOT, "docs", "meta_hyperglycaemia_search_strategy.pdf")


def generate_pdf(output_path: Optional[str] = None) -> str:
    pdf_path = output_path or DEFAULT_OUTPUT_PDF
    os.makedirs(os.path.dirname(os.path.abspath(pdf_path)), exist_ok=True)
    
    doc = fitz.open()
    
    # Page 1: Header, Metadata, PubMed & Embase search queries
    page1 = doc.new_page(width=595, height=842)  # A4 size
    
    # Margin and bounds
    margin_x = 45
    page_w = 595
    content_w = page_w - (2 * margin_x)
    
    y = 45
    
    # Header Banner
    header_rect = fitz.Rect(margin_x, y, margin_x + content_w, y + 55)
    page1.draw_rect(header_rect, color=(0.1, 0.25, 0.5), fill=(0.95, 0.97, 1.0), width=1.2)
    page1.insert_text(fitz.Point(margin_x + 12, y + 20), "CENTRE FOR TRANSLATIONAL MEDICINE — SEMMELWEIS UNIVERSITY", fontsize=10, fontname="helv", color=(0.1, 0.25, 0.5))
    page1.insert_text(fitz.Point(margin_x + 12, y + 36), "PROSPERO Supplementary Search Strategy (Field 6f)", fontsize=13, fontname="helv", color=(0.0, 0.0, 0.0))
    page1.insert_text(fitz.Point(margin_x + 12, y + 48), "Project: meta_hyperglycaemia | Status: Executable Search Queries", fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))
    
    y += 70
    
    # Review Title Block
    title_rect = fitz.Rect(margin_x, y, margin_x + content_w, y + 42)
    page1.draw_rect(title_rect, color=(0.8, 0.8, 0.8), fill=(0.98, 0.98, 0.98), width=0.8)
    page1.insert_text(fitz.Point(margin_x + 8, y + 14), "REVIEW TITLE:", fontsize=8, fontname="helv", color=(0.2, 0.2, 0.2))
    page1.insert_textbox(
        fitz.Rect(margin_x + 8, y + 16, margin_x + content_w - 8, y + 40),
        "Dysglycemia and Clinical Outcomes in Neonates with Hypoxic-Ischemic Encephalopathy Undergoing Therapeutic Cooling: A Systematic Review and Meta-analysis",
        fontsize=9, fontname="helv", color=(0.0, 0.15, 0.4)
    )
    
    y += 52
    
    # Review Authors & Team Block
    authors_text = "Review Team: Teodóra Eklics (Guarantor), Fekete Kata, Dr. András Garami, Prof. Dr. Péter Hegyi\nAffiliation: Centre for Translational Medicine, Semmelweis University, Budapest, Hungary"
    page1.insert_textbox(fitz.Rect(margin_x, y, margin_x + content_w, y + 26), authors_text, fontsize=8.5, fontname="helv", color=(0.3, 0.3, 0.3))
    
    y += 35
    
    # 1. PubMed Section
    page1.insert_text(fitz.Point(margin_x, y), "1. MEDLINE (via PubMed) — Executable Search Strategy", fontsize=11, fontname="helv", color=(0.1, 0.25, 0.5))
    y += 8
    page1.insert_text(fitz.Point(margin_x, y + 6), "Hit Count: 998 records | Settings: All Fields, no filters (1. Condition AND 2. Neonate AND 3. Glycemia)", fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
    y += 12
    
    pubmed_query = (
        '("Asphyxia" OR "encephalopathy" OR "HIE" OR "hypoxia-ischemia" OR "hypoxic-ischemic" OR "hypoxic ischaemic") '
        'AND (neonat* OR newborn* OR infant*) AND (hyperglyce* OR hypoglyce* OR dysglyce* OR glycaemi* OR glycemi* '
        'OR "blood glucose" OR "blood sugar" OR "glucose level*")'
    )
    
    box1_rect = fitz.Rect(margin_x, y, margin_x + content_w, y + 65)
    page1.draw_rect(box1_rect, color=(0.2, 0.4, 0.7), fill=(0.97, 0.98, 1.0), width=0.8)
    page1.insert_textbox(fitz.Rect(margin_x + 6, y + 4, margin_x + content_w - 6, y + 61), pubmed_query, fontsize=8.2, fontname="courier", color=(0.0, 0.0, 0.0))
    
    y += 80
    
    # 2. Embase Section
    page1.insert_text(fitz.Point(margin_x, y), "2. Embase (Embase.com) — Executable Search Strategy", fontsize=11, fontname="helv", color=(0.1, 0.25, 0.5))
    y += 8
    page1.insert_text(fitz.Point(margin_x, y + 6), "Hit Count: 2,731 records | Settings: Default search across all fields, Embase mapping enabled", fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
    y += 12
    
    embase_native = (
        "('asphyxia' OR 'encephalopathy' OR 'HIE' OR 'hypoxia-ischemia' OR 'hypoxic-ischemic' OR 'hypoxic ischaemic') "
        "AND (neonat* OR newborn* OR infant*) AND (hyperglyce* OR hypoglyce* OR dysglyce* OR glycaemi* OR glycemi* "
        "OR 'blood glucose' OR 'blood sugar' OR 'glucose level*')"
    )
    box2a_rect = fitz.Rect(margin_x, y, margin_x + content_w, y + 65)
    page1.draw_rect(box2a_rect, color=(0.2, 0.4, 0.7), fill=(0.97, 0.98, 1.0), width=0.8)
    page1.insert_textbox(fitz.Rect(margin_x + 6, y + 4, margin_x + content_w - 6, y + 61), embase_native, fontsize=8.2, fontname="courier", color=(0.0, 0.0, 0.0))
    
    y += 80

    # Page 2: Cochrane CENTRAL & CitationChaser Protocol
    page2 = doc.new_page(width=595, height=842)
    y = 45
    
    # 3. Cochrane CENTRAL Section
    page2.insert_text(fitz.Point(margin_x, y), "3. Cochrane Central Register of Controlled Trials (CENTRAL)", fontsize=11, fontname="helv", color=(0.1, 0.25, 0.5))
    y += 8
    page2.insert_text(fitz.Point(margin_x, y + 6), "Platform: Cochrane Library | Fields: Title, Abstract, Keyword", fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
    y += 14
    
    page2.insert_text(fitz.Point(margin_x, y + 6), "Cochrane Executable Query:", fontsize=8.5, fontname="helv", color=(0.2, 0.2, 0.2))
    y += 10
    central_single = (
        "('asphyxia' OR 'encephalopathy' OR 'HIE' OR 'hypoxia-ischemia' OR 'hypoxic-ischemic' OR 'hypoxic ischaemic') "
        "AND (neonat* OR newborn* OR infant*) AND (hyperglyce* OR hypoglyce* OR dysglyce* OR glycaemi* OR glycemi* "
        "OR 'blood glucose' OR 'blood sugar' OR 'glucose NEXT level*')"
    )
    box3b_rect = fitz.Rect(margin_x, y, margin_x + content_w, y + 60)
    page2.draw_rect(box3b_rect, color=(0.2, 0.4, 0.7), fill=(0.97, 0.98, 1.0), width=0.8)
    page2.insert_textbox(fitz.Rect(margin_x + 6, y + 4, margin_x + content_w - 6, y + 56), central_single, fontsize=8.0, fontname="courier", color=(0.0, 0.0, 0.0))
    
    y += 80
    
    # 4. Secondary Search & Screening Standards
    page2.insert_text(fitz.Point(margin_x, y), "4. Secondary Identification & Citation Chasing Protocol", fontsize=11, fontname="helv", color=(0.1, 0.25, 0.5))
    y += 8
    
    secondary_text = (
        "• CitationChaser: Forward and backward citation chasing will be systematically conducted for all included "
        "primary studies and key previous systematic reviews to ensure complete bibliographic capture.\n"
        "• Trial Registries: Ongoing and completed unpublished trials will be searched via ClinicalTrials.gov and the "
        "WHO International Clinical Trials Registry Platform (ICTRP).\n"
        "• Boolean 'NOT' Prohibition: In strict adherence to CTM / Cochrane standards, the boolean 'NOT' operator was "
        "strictly excluded from all search algorithms to prevent inadvertent exclusion of relevant clinical cohorts.\n"
        "• Deduplication & Screening: Multi-database exports (PubMed NBIB, Embase RIS, CENTRAL RIS) "
        "will be deduplicated in EndNote / Rayyan and screened independently in duplicate by two reviewers."
    )
    box4_rect = fitz.Rect(margin_x, y, margin_x + content_w, y + 95)
    page2.draw_rect(box4_rect, color=(0.8, 0.8, 0.8), fill=(0.98, 0.98, 0.98), width=0.8)
    page2.insert_textbox(fitz.Rect(margin_x + 8, y + 6, margin_x + content_w - 8, y + 90), secondary_text, fontsize=8.5, fontname="helv", color=(0.2, 0.2, 0.2))
    
    y += 115
    page2.insert_text(fitz.Point(margin_x, y), "Centre for Translational Medicine (CTM) · Semmelweis University · PRISMA 2020 · PROSPERO", fontsize=8, fontname="helv", color=(0.5, 0.5, 0.5))

    doc.save(pdf_path)
    doc.close()
    print(f"Generated PDF search strategy successfully: {pdf_path}")
    return pdf_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate PROSPERO Search Strategy PDF.")
    parser.add_argument('--output', type=str, default=DEFAULT_OUTPUT_PDF, help="Output PDF file path")
    args = parser.parse_args()
    generate_pdf(output_path=args.output)


if __name__ == "__main__":
    main()
