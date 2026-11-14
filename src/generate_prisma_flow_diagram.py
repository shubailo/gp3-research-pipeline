#!/usr/bin/env python3
"""
generate_prisma_flow_diagram.py
Generates a PRISMA 2020 compliant flow diagram for Neonatal Antibiotic Stewardship Meta-Analysis.
Standard Cochrane / CTM workflow:
- 13,352 raw records from databases
- 3,722 duplicates removed
- 9,630 screened by title and abstract
- 9,236 excluded by title/abstract
- 394 sought for retrieval & full-text assessment
- 271 excluded at full-text with explicit PRISMA reasons
- 17 Level-1 RCTs included in Paper 1 (Primary Synthesis, N = 21,222)
- 106 Comparative Cohorts included in Paper 2 (Secondary RWE)
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_prisma_flow_diagram(output_path):
    fig, ax = plt.subplots(figsize=(14, 16), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Styles
    stage_header_style = dict(boxstyle="square,pad=0.4", fc="#2F5597", ec="#2F5597")
    stage_font = {'fontsize': 12, 'fontweight': 'bold', 'color': 'white', 'rotation': 90, 'ha': 'center', 'va': 'center'}
    
    box_style = dict(boxstyle="round,pad=0.5", fc="#F2F4F8", ec="#2F5597", lw=1.5)
    excl_box_style = dict(boxstyle="round,pad=0.5", fc="#FFF2F2", ec="#C00000", lw=1.5)
    incl_box_style = dict(boxstyle="round,pad=0.5", fc="#E2EFDA", ec="#385723", lw=1.8)
    cohort_box_style = dict(boxstyle="round,pad=0.5", fc="#FFF2CC", ec="#D6B656", lw=1.8)
    
    body_font = {'fontsize': 9.5, 'color': '#111111', 'ha': 'center', 'va': 'center', 'linespacing': 1.4}
    excl_font = {'fontsize': 9, 'color': '#111111', 'ha': 'left', 'va': 'center', 'linespacing': 1.4}

    # Main Title
    ax.text(50, 97.5, "PRISMA 2020 Flow Diagram: Neonatal Antibiotic Stewardship Meta-Analysis",
            fontsize=15, fontweight='bold', color='#1F4E79', ha='center', va='center')
    ax.text(50, 95.2, "Universal Multi-Database Systematic Review (Cochrane CENTRAL, Embase, PubMed / MEDLINE)",
            fontsize=10.5, fontstyle='italic', color='#555555', ha='center', va='center')

    # Stage Indicators on Left Bar
    ax.add_patch(patches.FancyBboxPatch((2, 75), 5, 17, **stage_header_style))
    ax.text(4.5, 83.5, "IDENTIFICATION", **stage_font)

    ax.add_patch(patches.FancyBboxPatch((2, 49), 5, 23, **stage_header_style))
    ax.text(4.5, 60.5, "SCREENING", **stage_font)

    ax.add_patch(patches.FancyBboxPatch((2, 23), 5, 23, **stage_header_style))
    ax.text(4.5, 34.5, "ELIGIBILITY", **stage_font)

    ax.add_patch(patches.FancyBboxPatch((2, 3), 5, 17, **stage_header_style))
    ax.text(4.5, 11.5, "INCLUDED", **stage_font)

    # 1. Identification Box
    id_text = (
        "Records identified from databases (n = 13,352):\n"
        "• Embase (Elsevier, Part 1 & 2): n = 8,491\n"
        "• PubMed / MEDLINE: n = 4,001\n"
        "• Cochrane Library (CENTRAL): n = 860"
    )
    ax.text(32, 85, id_text, **body_font, bbox=box_style)

    # Duplicate Removal Box
    dup_text = (
        "Duplicate records removed\n"
        "before screening (n = 3,722)\n"
        "• Deduplicated by DOI: n = 3,084\n"
        "• Deduplicated by Title: n = 638\n"
        "(Bramer / Cochrane method)"
    )
    ax.text(78, 85, dup_text, **body_font, bbox=excl_box_style)

    # Arrow Id -> Dup
    ax.annotate('', xy=(64, 85), xytext=(50, 85),
                arrowprops=dict(facecolor='#C00000', edgecolor='#C00000', width=1.5, headwidth=7))

    # 2. Screening Box
    screen_text = (
        "Unique records screened\n"
        "by title and abstract\n"
        "(n = 9,630)"
    )
    ax.text(32, 68, screen_text, **body_font, bbox=box_style)

    # Arrow Id -> Screen
    ax.annotate('', xy=(32, 73.5), xytext=(32, 79),
                arrowprops=dict(facecolor='#2F5597', edgecolor='#2F5597', width=1.5, headwidth=7))

    # Excluded Title/Abstract
    screen_excl_text = (
        "Records excluded by title/abstract (n = 9,236):\n"
        "• Non-neonatal / adult / pediatric conditions: n = 4,120\n"
        "• Not antibacterial stewardship / no duration comparison: n = 3,772\n"
        "• Animal models / in vitro laboratory studies: n = 712\n"
        "• Non-primary publications (Reviews, Editorials): n = 632"
    )
    ax.text(78, 68, screen_excl_text, **excl_font, bbox=excl_box_style)

    # Arrow Screen -> Excl Screen
    ax.annotate('', xy=(59, 68), xytext=(45, 68),
                arrowprops=dict(facecolor='#C00000', edgecolor='#C00000', width=1.5, headwidth=7))

    # 3. Reports Sought for Retrieval
    sought_text = (
        "Reports sought for retrieval\n"
        "and full-text assessment\n"
        "(n = 394 candidate articles)"
    )
    ax.text(32, 53, sought_text, **body_font, bbox=box_style)

    # Arrow Screen -> Sought
    ax.annotate('', xy=(32, 58.5), xytext=(32, 62.5),
                arrowprops=dict(facecolor='#2F5597', edgecolor='#2F5597', width=1.5, headwidth=7))

    # Full-Text Assessment Box
    eval_text = (
        "Reports assessed for full-text eligibility\n"
        "and data extraction audit\n"
        "(n = 394 full-text articles retrieved)"
    )
    ax.text(32, 38, eval_text, **body_font, bbox=box_style)

    # Arrow Sought -> Eval
    ax.annotate('', xy=(32, 42.5), xytext=(32, 47.5),
                arrowprops=dict(facecolor='#2F5597', edgecolor='#2F5597', width=1.5, headwidth=7))

    # Exclusion Criteria at Full-Text
    excl_ft_text = (
        "Full-text articles excluded with reasons (n = 271):\n"
        "• Lack of comparator group (single-arm audits): n = 188\n"
        "• Maternal antenatal prophylaxis without duration data: n = 38\n"
        "• Non-stewardship interventions (topical, colostrum, lipids): n = 28\n"
        "• Adult / older pediatric intensive care: n = 15\n"
        "• Overlapping cohort / duplicate registry report: n = 2"
    )
    ax.text(78, 38, excl_ft_text, **excl_font, bbox=excl_box_style)

    # Arrow Eval -> Excl FT
    ax.annotate('', xy=(59, 38), xytext=(49, 38),
                arrowprops=dict(facecolor='#C00000', edgecolor='#C00000', width=1.5, headwidth=7))

    # Benchmark Recovery Note
    benchmark_note = (
        "Full-Text Benchmark Verification:\n"
        "• 17/17 Level-1 RCTs Verified & Extracted (100.0% Recall)\n"
        "• 106 Observational Cohorts Verified & Audited"
    )
    ax.text(78, 21, benchmark_note,
            fontsize=9.5, fontweight='bold', color='#1F4E79', ha='left', va='center',
            bbox=dict(boxstyle="round,pad=0.5", fc="#EBF1F5", ec="#1F4E79", lw=1.2))

    # 4. Included Studies: Primary Level-1 RCTs
    incl_rct_text = (
        "Paper 1: Primary Level-1 Synthesis\n"
        "17 Randomized Controlled Trials (RCTs)\n"
        "Total Sample Size: N = 21,222 neonates\n"
        "• All-Cause Mortality: 17 RCTs (N = 21,222)\n"
        "• Treatment Failure / Relapse: 17 RCTs (N = 21,222)\n"
        "• Antibiotic Exposure Duration: 14 RCTs (N = 19,402)"
    )
    ax.text(23, 13, incl_rct_text, **body_font, bbox=incl_box_style)

    # 4. Included Studies: Secondary RWE Cohorts
    incl_cohort_text = (
        "Paper 2: Secondary RWE Repository\n"
        "106 Comparative Observational Cohorts\n"
        "Real-World Evidence (RWE)\n"
        "• Before-After & Interrupted Time Series\n"
        "• Multilevel Meta-Regression (RVE)\n"
        "• Hospital-acquired sepsis & broad-spectrum use"
    )
    ax.text(52, 13, incl_cohort_text, **body_font, bbox=cohort_box_style)

    # Arrows to Included
    ax.annotate('', xy=(23, 21), xytext=(28, 33),
                arrowprops=dict(facecolor='#385723', edgecolor='#385723', width=1.8, headwidth=7))
    ax.annotate('', xy=(52, 21), xytext=(36, 33),
                arrowprops=dict(facecolor='#D6B656', edgecolor='#D6B656', width=1.8, headwidth=7))

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"PRISMA Flow Diagram successfully generated at: {output_path}")

if __name__ == '__main__':
    out_file = r'01_Stewardship_Vegleges_Anyagok\PRISMA_2020_Flow_Diagram.png'
    create_prisma_flow_diagram(out_file)
