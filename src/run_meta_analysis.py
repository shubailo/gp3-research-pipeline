import openpyxl
import math
import numpy as np
import matplotlib.pyplot as plt
import os

# Set style
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9

wb_path = 'projects/neonatal_antibiotics/data/Data_extraction_neonatal_antibiotics_v9.xlsx'
wb = openpyxl.load_workbook(wb_path, data_only=True)
ws_or = wb['ORs - RRs']

def extract_outcome(target_outcome):
    records = []
    for r in range(4, ws_or.max_row + 1):
        o = str(ws_or.cell(r, 1).value or '').strip()
        if o == target_outcome:
            sid = str(ws_or.cell(r, 3).value or '').strip()
            a = ws_or.cell(r, 13).value
            tot_i = ws_or.cell(r, 14).value
            c = ws_or.cell(r, 15).value
            tot_c = ws_or.cell(r, 16).value
            est_type = str(ws_or.cell(r, 24).value or '').strip()
            pe = ws_or.cell(r, 25).value
            ci_min = ws_or.cell(r, 27).value
            ci_max = ws_or.cell(r, 28).value
            conf = str(ws_or.cell(r, 32).value or '').strip()
            
            if est_type == 'aOR' and pe and ci_min and ci_max and ci_min > 0:
                log_or = math.log(pe)
                se = (math.log(ci_max) - math.log(ci_min)) / (2 * 1.95996)
                records.append({
                    'study': sid, 'type': 'aOR', 'or': pe, 'ci_min': ci_min, 'ci_max': ci_max,
                    'log_or': log_or, 'se': se, 'var': se**2, 'conf': conf,
                    'a': a, 'tot_i': tot_i, 'c': c, 'tot_c': tot_c
                })
            elif a is not None and tot_i is not None and c is not None and tot_c is not None:
                b = tot_i - a
                d = tot_c - c
                if a == 0 or b == 0 or c == 0 or d == 0:
                    a_c, b_c, c_c, d_c = a + 0.5, b + 0.5, c + 0.5, d + 0.5
                else:
                    a_c, b_c, c_c, d_c = a, b, c, d
                log_or = math.log((a_c * d_c) / (b_c * c_c))
                se = math.sqrt(1/a_c + 1/b_c + 1/c_c + 1/d_c)
                or_val = math.exp(log_or)
                ci_l = math.exp(log_or - 1.95996 * se)
                ci_u = math.exp(log_or + 1.95996 * se)
                records.append({
                    'study': sid, 'type': 'crude', 'or': or_val, 'ci_min': ci_l, 'ci_max': ci_u,
                    'log_or': log_or, 'se': se, 'var': se**2, 'conf': conf,
                    'a': a, 'tot_i': tot_i, 'c': c, 'tot_c': tot_c
                })
    return records

def pool_random_effects(recs):
    if not recs:
        return None
    y = np.array([r['log_or'] for r in recs])
    v = np.array([r['var'] for r in recs])
    k = len(y)
    
    w_fe = 1.0 / v
    w_fe_sum = np.sum(w_fe)
    theta_fe = np.sum(w_fe * y) / w_fe_sum
    
    Q = np.sum(w_fe * (y - theta_fe)**2)
    df = k - 1
    
    c = w_fe_sum - np.sum(w_fe**2) / w_fe_sum
    tau2 = max(0.0, (Q - df) / c) if c > 0 else 0.0
    
    w_re = 1.0 / (v + tau2)
    w_re_sum = np.sum(w_re)
    theta_re = np.sum(w_re * y) / w_re_sum
    se_re = math.sqrt(1.0 / w_re_sum)
    
    pooled_or = math.exp(theta_re)
    ci_min = math.exp(theta_re - 1.95996 * se_re)
    ci_max = math.exp(theta_re + 1.95996 * se_re)
    z_val = theta_re / se_re
    p_val = 2 * (1 - 0.5 * (1 + math.erf(abs(z_val) / math.sqrt(2))))
    
    I2 = max(0.0, (Q - df) / Q) * 100 if Q > 0 else 0.0
    
    # Study weights
    weights = (w_re / w_re_sum) * 100
    for i, r in enumerate(recs):
        r['weight'] = weights[i]
        
    return {
        'k': k, 'or': pooled_or, 'ci_min': ci_min, 'ci_max': ci_max,
        'z': z_val, 'p': p_val, 'Q': Q, 'df': df, 'I2': I2, 'tau2': tau2,
        'theta_re': theta_re, 'se_re': se_re
    }

def create_forest_plot(recs, pool_res, title, filename, xlim=(0.1, 20.0)):
    # Sort by publication year / study name
    recs_sorted = sorted(recs, key=lambda x: x['study'])
    k = len(recs_sorted)
    
    fig_height = max(8, k * 0.28 + 2.5)
    fig, ax = plt.subplots(figsize=(10, fig_height))
    
    y_pos = np.arange(k, 0, -1)
    
    for i, r in enumerate(recs_sorted):
        y = y_pos[i]
        # Box size proportional to weight
        sz = max(4, min(14, math.sqrt(r['weight']) * 3.5))
        color = '#1f77b4' if r['type'] == 'aOR' else '#2ca02c'
        ax.plot([r['ci_min'], r['ci_max']], [y, y], color='black', lw=1.2)
        ax.plot(r['or'], y, 's', color=color, markersize=sz)
        
        # Text label on the left
        label = f"{r['study']} ({r['type']})"
        ax.text(xlim[0] * 0.95, y, label, ha='right', va='center', fontsize=8)
        
        # Effect text on the right
        eff_txt = f"{r['or']:.2f} [{r['ci_min']:.2f}, {r['ci_max']:.2f}] ({r['weight']:.1f}%)"
        ax.text(xlim[1] * 1.05, y, eff_txt, ha='left', va='center', fontsize=8)
        
    # Pooled Diamond
    diamond_y = -0.5
    d_x = [pool_res['ci_min'], pool_res['or'], pool_res['ci_max'], pool_res['or'], pool_res['ci_min']]
    d_y = [diamond_y, diamond_y + 0.4, diamond_y, diamond_y - 0.4, diamond_y]
    ax.fill(d_x, d_y, color='#d62728', alpha=0.85)
    
    ax.text(xlim[0] * 0.95, diamond_y, "RE Model (DerSimonian-Laird)", ha='right', va='center', fontsize=9, fontweight='bold')
    d_txt = f"{pool_res['or']:.2f} [{pool_res['ci_min']:.2f}, {pool_res['ci_max']:.2f}] (100.0%)"
    ax.text(xlim[1] * 1.05, diamond_y, d_txt, ha='left', va='center', fontsize=9, fontweight='bold')
    
    # Vertical line of no effect
    ax.axvline(1.0, color='grey', linestyle='--', lw=1.0)
    
    ax.set_xscale('log')
    ax.set_xlim(xlim[0], xlim[1])
    ax.set_ylim(-1.5, k + 1)
    ax.set_yticks([])
    
    ax.set_xlabel("Odds Ratio (log scale)\n<--- Favors Short/Stop (Protective) | Favors Prolonged (Harmful) --->", fontsize=9, fontweight='bold')
    
    # Subtitle with heterogeneity
    sub_title = f"{title}\nRandom-Effects: OR = {pool_res['or']:.2f} (95% CI: {pool_res['ci_min']:.2f} - {pool_res['ci_max']:.2f}), Z = {pool_res['z']:.2f}, P = {pool_res['p']:.2e}\nHeterogeneity: Q = {pool_res['Q']:.1f} (P < 0.001), I² = {pool_res['I2']:.1f}%, τ² = {pool_res['tau2']:.4f}"
    ax.set_title(sub_title, fontsize=10, fontweight='bold', pad=15)
    
    # Legend
    from matplotlib.lines import Line2D
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

# Generate Plots
out_dir = 'projects/neonatal_antibiotics/results'
os.makedirs(out_dir, exist_ok=True)

# 1. NEC
nec_recs = extract_outcome('Necrotizing Enterocolitis (Bell >= 2)')
nec_pool = pool_random_effects(nec_recs)
create_forest_plot(nec_recs, nec_pool, "Necrotizing Enterocolitis (Bell stage ≥2)", f"{out_dir}/forest_plot_nec.png", xlim=(0.1, 30.0))

# 2. Mortality
mort_recs = extract_outcome('All-cause In-Hospital Mortality')
mort_pool = pool_random_effects(mort_recs)
create_forest_plot(mort_recs, mort_pool, "All-cause In-Hospital Mortality", f"{out_dir}/forest_plot_mortality.png", xlim=(0.05, 50.0))

# 3. Late-Onset Sepsis
los_recs = extract_outcome('Late-Onset Sepsis')
los_pool = pool_random_effects(los_recs)
create_forest_plot(los_recs, los_pool, "Late-Onset Sepsis (Culture-proven bacteremia)", f"{out_dir}/forest_plot_los.png", xlim=(0.1, 20.0))

# 4. Subgroup Comparison Plot
def create_subgroup_plot(filename):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # NEC Subgroups
    nec_adj = [r for r in nec_recs if r['type'] == 'aOR']
    nec_crd = [r for r in nec_recs if r['type'] == 'crude']
    p_nec_adj = pool_random_effects(nec_adj)
    p_nec_crd = pool_random_effects(nec_crd)
    
    # Mortality Subgroups
    mort_adj = [r for r in mort_recs if r['type'] == 'aOR']
    mort_crd = [r for r in mort_recs if r['type'] == 'crude']
    p_mort_adj = pool_random_effects(mort_adj)
    p_mort_crd = pool_random_effects(mort_crd)
    
    def plot_sub(ax, overall, adj, crd, title):
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
            ax.plot(ors[i], y_pts[i], 'D' if i==0 else 's', color=colors[i], markersize=9)
            
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

create_subgroup_plot(f"{out_dir}/forest_plot_subgroups.png")
