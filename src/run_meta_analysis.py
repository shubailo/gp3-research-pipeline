"""Meta-analysis random-effects calculation and forest plot generation."""
import math
import os
import sys
import argparse
from typing import List, Dict, Any, Optional

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

import openpyxl
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from src.utils.console import configure_utf8_console
from src.utils.math_stats import calculate_odds_ratio, calculate_or_from_ci, pool_random_effects

# Set plotting typography
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9

DEFAULT_WORKBOOK = 'data/Data_extraction_neonatal_antibiotics_v9.xlsx'
DEFAULT_OUT_DIR = 'results/neonatal_antibiotics'


def extract_outcome(ws_or: Any, target_outcome: str) -> List[Dict[str, Any]]:
    """Extracts study effect estimates (adjusted aOR or 2x2 crude counts) for target outcome."""
    records = []
    for r in range(4, ws_or.max_row + 1):
        outcome_name = str(ws_or.cell(r, 1).value or '').strip()
        if outcome_name != target_outcome:
            continue

        study_id = str(ws_or.cell(r, 3).value or '').strip()
        a_events = ws_or.cell(r, 13).value
        tot_intervention = ws_or.cell(r, 14).value
        c_events = ws_or.cell(r, 15).value
        tot_control = ws_or.cell(r, 16).value
        est_type = str(ws_or.cell(r, 24).value or '').strip()
        pe = ws_or.cell(r, 25).value
        ci_min = ws_or.cell(r, 27).value
        ci_max = ws_or.cell(r, 28).value
        conf = str(ws_or.cell(r, 32).value or '').strip()

        if est_type == 'aOR' and pe and ci_min and ci_max and ci_min > 0:
            eff = calculate_or_from_ci(pe=pe, ci_min=ci_min, ci_max=ci_max)
            records.append({
                'study': study_id,
                'type': 'aOR',
                'or': eff['or'],
                'ci_min': eff['ci_min'],
                'ci_max': eff['ci_max'],
                'log_or': eff['log_or'],
                'se': eff['se'],
                'var': eff['var'],
                'conf': conf,
                'a': a_events,
                'tot_i': tot_intervention,
                'c': c_events,
                'tot_c': tot_control
            })
        elif a_events is not None and tot_intervention is not None and c_events is not None and tot_control is not None:
            eff = calculate_odds_ratio(
                a=float(a_events),
                total_intervention=float(tot_intervention),
                c=float(c_events),
                total_control=float(tot_control)
            )
            records.append({
                'study': study_id,
                'type': 'crude',
                'or': eff['or'],
                'ci_min': eff['ci_min'],
                'ci_max': eff['ci_max'],
                'log_or': eff['log_or'],
                'se': eff['se'],
                'var': eff['var'],
                'conf': conf,
                'a': a_events,
                'tot_i': tot_intervention,
                'c': c_events,
                'tot_c': tot_control
            })
    return records


def create_forest_plot(
    recs: List[Dict[str, Any]],
    pool_res: Dict[str, Any],
    title: str,
    filename: str,
    xlim: tuple = (0.1, 20.0)
) -> None:
    """Renders high-resolution forest plot for primary outcomes."""
    recs_sorted = sorted(recs, key=lambda x: x['study'])
    k = len(recs_sorted)

    fig_height = max(8, k * 0.28 + 2.5)
    fig, ax = plt.subplots(figsize=(10, fig_height))
    y_pos = np.arange(k, 0, -1)

    for i, r in enumerate(recs_sorted):
        y = y_pos[i]
        sz = max(4, min(14, math.sqrt(r['weight']) * 3.5))
        color = '#1f77b4' if r['type'] == 'aOR' else '#2ca02c'
        ax.plot([r['ci_min'], r['ci_max']], [y, y], color='black', lw=1.2)
        ax.plot(r['or'], y, 's', color=color, markersize=sz)

        label = f"{r['study']} ({r['type']})"
        ax.text(xlim[0] * 0.95, y, label, ha='right', va='center', fontsize=8)

        eff_txt = f"{r['or']:.2f} [{r['ci_min']:.2f}, {r['ci_max']:.2f}] ({r['weight']:.1f}%)"
        ax.text(xlim[1] * 1.05, y, eff_txt, ha='left', va='center', fontsize=8)

    diamond_y = -0.5
    d_x = [pool_res['ci_min'], pool_res['or'], pool_res['ci_max'], pool_res['or'], pool_res['ci_min']]
    d_y = [diamond_y, diamond_y + 0.4, diamond_y, diamond_y - 0.4, diamond_y]
    ax.fill(d_x, d_y, color='#d62728', alpha=0.85)

    ax.text(xlim[0] * 0.95, diamond_y, "RE Model (DerSimonian-Laird)", ha='right', va='center', fontsize=9, fontweight='bold')
    d_txt = f"{pool_res['or']:.2f} [{pool_res['ci_min']:.2f}, {pool_res['ci_max']:.2f}] (100.0%)"
    ax.text(xlim[1] * 1.05, diamond_y, d_txt, ha='left', va='center', fontsize=9, fontweight='bold')

    ax.axvline(1.0, color='grey', linestyle='--', lw=1.0)
    ax.set_xscale('log')
    ax.set_xlim(xlim[0], xlim[1])
    ax.set_ylim(-1.5, k + 1)
    ax.set_yticks([])
    ax.set_xlabel("Odds Ratio (log scale)\n<--- Favors Short/Stop (Protective) | Favors Prolonged (Harmful) --->", fontsize=9, fontweight='bold')

    sub_title = (
        f"{title}\n"
        f"Random-Effects: OR = {pool_res['or']:.2f} (95% CI: {pool_res['ci_min']:.2f} - {pool_res['ci_max']:.2f}), "
        f"Z = {pool_res['z']:.2f}, P = {pool_res['p']:.2e}\n"
        f"Heterogeneity: Q = {pool_res['Q']:.1f} (P < 0.001), I² = {pool_res['I2']:.1f}%, τ² = {pool_res['tau2']:.4f}"
    )
    ax.set_title(sub_title, fontsize=10, fontweight='bold', pad=15)

    legend_elements = [
        Line2D([0], [0], marker='s', color='w', label='Multivariable Adjusted (aOR)', markerfacecolor='#1f77b4', markersize=8),
        Line2D([0], [0], marker='s', color='w', label='Crude Unadjusted (OR)', markerfacecolor='#2ca02c', markersize=8),
        Line2D([0], [0], marker='D', color='w', label='Pooled Summary Estimate', markerfacecolor='#d62728', markersize=8)
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.0, 1.04), frameon=True, fontsize=8)

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")


def create_subgroup_plot(
    nec_recs: List[Dict[str, Any]],
    mort_recs: List[Dict[str, Any]],
    filename: str
) -> None:
    """Renders subgroup forest plots comparing Adjusted vs Crude."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    nec_pool = pool_random_effects(nec_recs)
    mort_pool = pool_random_effects(mort_recs)

    nec_adj = [r for r in nec_recs if r['type'] == 'aOR']
    nec_crd = [r for r in nec_recs if r['type'] == 'crude']
    p_nec_adj = pool_random_effects(nec_adj)
    p_nec_crd = pool_random_effects(nec_crd)

    mort_adj = [r for r in mort_recs if r['type'] == 'aOR']
    mort_crd = [r for r in mort_recs if r['type'] == 'crude']
    p_mort_adj = pool_random_effects(mort_adj)
    p_mort_crd = pool_random_effects(mort_crd)

    def plot_sub(ax, overall, adj, crd, title):
        if not overall or not adj or not crd:
            return
        y_pts = [2, 1, 0]
        labels = [
            f"Overall ({overall['k']} studies)\nOR={overall['or']:.2f} [{overall['ci_min']:.2f}, {overall['ci_max']:.2f}]",
            f"Adjusted aOR ({adj['k']} studies)\naOR={adj['or']:.2f} [{adj['ci_min']:.2f}, {adj['ci_max']:.2f}]",
            f"Crude OR ({crd['k']} studies)\nOR={crd['or']:.2f} [{crd['ci_min']:.2f}, {crd['ci_max']:.2f}]"
        ]
        ors = [overall['or'], adj['or'], crd['or']]
        ci_ls = [overall['ci_min'], adj['ci_min'], crd['ci_min']]
        ci_us = [overall['ci_max'], adj['ci_max'], crd['ci_max']]
        colors = ['#d62728', '#1f77b4', '#2ca02c']

        for i in range(3):
            ax.plot([ci_ls[i], ci_us[i]], [y_pts[i], y_pts[i]], color='black', lw=2)
            ax.plot(ors[i], y_pts[i], 'D' if i == 0 else 's', color=colors[i], markersize=9)

        ax.axvline(1.0, color='grey', linestyle='--', lw=1)
        ax.set_xscale('log')
        ax.set_xlim(0.5, 4.0)
        ax.set_ylim(-0.8, 2.8)
        ax.set_yticks(y_pts)
        ax.set_yticklabels(labels, fontsize=9, fontweight='bold')
        ax.set_xlabel("Odds Ratio (log scale)", fontsize=9, fontweight='bold')
        ax.set_title(title, fontsize=10, fontweight='bold', pad=10)
        ax.grid(axis='x', linestyle=':', alpha=0.6)

    plot_sub(ax1, nec_pool, p_nec_adj, p_nec_crd, "Necrotizing Enterocolitis (Bell ≥2)\nSubgroup: Adjusted vs Crude")
    plot_sub(ax2, mort_pool, p_mort_adj, p_mort_crd, "All-cause In-Hospital Mortality\nSubgroup: Adjusted vs Crude")

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")


def main(wb_path: Optional[str] = None, out_dir: Optional[str] = None) -> None:
    configure_utf8_console()
    wb_file = wb_path or DEFAULT_WORKBOOK
    output_directory = out_dir or DEFAULT_OUT_DIR
    os.makedirs(output_directory, exist_ok=True)

    if not os.path.exists(wb_file):
        print(f"Error: Workbook not found at {wb_file}")
        return

    wb = openpyxl.load_workbook(wb_file, data_only=True)
    sheet_name = 'ORs - RRs' if 'ORs - RRs' in wb.sheetnames else 'ORs and RRs'
    ws_or = wb[sheet_name]

    # 1. NEC
    nec_recs = extract_outcome(ws_or, 'Necrotizing Enterocolitis (Bell >= 2)')
    if nec_recs:
        nec_pool = pool_random_effects(nec_recs)
        create_forest_plot(nec_recs, nec_pool, "Necrotizing Enterocolitis (Bell stage ≥2)", f"{output_directory}/forest_plot_nec.png", xlim=(0.1, 30.0))

    # 2. Mortality
    mort_recs = extract_outcome(ws_or, 'All-cause In-Hospital Mortality')
    if mort_recs:
        mort_pool = pool_random_effects(mort_recs)
        create_forest_plot(mort_recs, mort_pool, "All-cause In-Hospital Mortality", f"{output_directory}/forest_plot_mortality.png", xlim=(0.05, 50.0))

    # 3. Late-Onset Sepsis
    los_recs = extract_outcome(ws_or, 'Late-Onset Sepsis')
    if los_recs:
        los_pool = pool_random_effects(los_recs)
        create_forest_plot(los_recs, los_pool, "Late-Onset Sepsis (Culture-proven bacteremia)", f"{output_directory}/forest_plot_los.png", xlim=(0.1, 20.0))

    # 4. Subgroup plot
    if nec_recs and mort_recs:
        create_subgroup_plot(nec_recs, mort_recs, f"{output_directory}/forest_plot_subgroups.png")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run meta-analysis and generate forest plots.")
    parser.add_argument('--workbook', type=str, default=DEFAULT_WORKBOOK, help="Path to extraction workbook")
    parser.add_argument('--outdir', type=str, default=DEFAULT_OUT_DIR, help="Output directory for plots")
    args = parser.parse_args()
    main(wb_path=args.workbook, out_dir=args.outdir)
