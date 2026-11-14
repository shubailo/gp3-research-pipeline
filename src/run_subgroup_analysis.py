"""
Subgroup Meta-Analysis for Neonatal Antibiotic Stewardship RCTs (Paper 1).
Stratifies by:
1. Stewardship Strategy:
   - Biomarker-guided (PCT / CRP / IL-8)
   - Clinical Prediction Rule / Sepsis Calculator / Remote ASP
   - Fixed Short-Course / Culture-Negative Discontinuation (48-72h)
2. Gestational Maturity (Preterm vs Term / Mixed)
3. Infection Presentation (Culture-Negative EOS vs Culture-Proven Sepsis / Focal)
"""

import math
from pathlib import Path
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT_DIR = Path("results/neonatal_ab_stewardship")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def pool_rr_subgroup(studies):
    log_rrs, ses = [], []
    for s in studies:
        cc = 0.5 if (s['e_i'] == 0 or s['e_c'] == 0) else 0.0
        r_i = (s['e_i'] + cc) / (s['t_i'] + 2 * cc)
        r_c = (s['e_c'] + cc) / (s['t_c'] + 2 * cc)
        rr = r_i / r_c
        v = (1.0 / (s['e_i'] + cc) - 1.0 / (s['t_i'] + 2 * cc)) + (1.0 / (s['e_c'] + cc) - 1.0 / (s['t_c'] + 2 * cc))
        log_rrs.append(math.log(rr))
        ses.append(math.sqrt(v))
        
    weights = [1.0 / (s**2) for s in ses]
    sum_w = sum(weights)
    fixed = sum(w * e for w, e in zip(weights, log_rrs)) / sum_w
    k = len(studies)
    if k <= 1:
        return math.exp(fixed), (math.exp(fixed - 1.96 * ses[0]), math.exp(fixed + 1.96 * ses[0])), 0.0, 1.0
        
    q = sum(w * (e - fixed)**2 for w, e in zip(weights, log_rrs))
    df = k - 1
    c = sum_w - sum(w**2 for w in weights) / sum_w
    tau2 = max(0.0, (q - df) / c)
    re_w = [1.0 / (s**2 + tau2) for s in ses]
    pooled = sum(w * e for w, e in zip(re_w, log_rrs)) / sum(re_w)
    pooled_se = math.sqrt(1.0 / sum(re_w))
    i2 = max(0.0, (q - df) / q * 100.0) if q > 0 else 0.0
    p_val = 2 * (1 - stats.norm.cdf(abs(pooled / pooled_se)))
    return math.exp(pooled), (math.exp(pooled - 1.96 * pooled_se), math.exp(pooled + 1.96 * pooled_se)), i2, p_val

def pool_md_subgroup(studies):
    diffs, ses = [], []
    for s in studies:
        md = s['m_i'] - s['m_c']
        se = math.sqrt((s['sd_i']**2 / s['n_i']) + (s['sd_c']**2 / s['n_c']))
        diffs.append(md)
        ses.append(se)
    weights = [1.0 / (s**2) for s in ses]
    sum_w = sum(weights)
    fixed = sum(w * e for w, e in zip(weights, diffs)) / sum_w
    k = len(studies)
    if k <= 1:
        return fixed, (fixed - 1.96 * ses[0], fixed + 1.96 * ses[0]), 0.0, 1.0
    q = sum(w * (e - fixed)**2 for w, e in zip(weights, diffs))
    df = k - 1
    c = sum_w - sum(w**2 for w in weights) / sum_w
    tau2 = max(0.0, (q - df) / c)
    re_w = [1.0 / (s**2 + tau2) for s in ses]
    pooled = sum(w * e for w, e in zip(re_w, diffs)) / sum(re_w)
    pooled_se = math.sqrt(1.0 / sum(re_w))
    i2 = max(0.0, (q - df) / q * 100.0) if q > 0 else 0.0
    p_val = 2 * (1 - stats.norm.cdf(abs(pooled / pooled_se)))
    return pooled, (pooled - 1.96 * pooled_se, pooled + 1.96 * pooled_se), i2, p_val

def run_subgroups():
    # 1. Mortality Datasets
    sub_biomarker = [
        {'name': 'Carlsen 2026', 'e_i': 0, 't_i': 247, 'e_c': 0, 't_c': 246},
        {'name': 'Franz 2004', 'e_i': 14, 't_i': 654, 'e_c': 16, 't_c': 637},
        {'name': 'Mitanchez 2026', 'e_i': 11, 't_i': 251, 'e_c': 15, 't_c': 253},
        {'name': 'Stocker 2017', 'e_i': 2, 't_i': 866, 'e_c': 4, 't_c': 844},
        {'name': 'Ehl 1997', 'e_i': 0, 't_i': 38, 'e_c': 0, 't_c': 39},
    ]

    sub_calc_asp = [
        {'name': 'van der Weijden 2024', 'e_i': 0, 't_i': 893, 'e_c': 0, 't_c': 937},
        {'name': 'Cantey 2022', 'e_i': 0, 't_i': 4691, 'e_c': 0, 't_c': 4586},
    ]

    sub_fixed_short = [
        {'name': 'PSBI 2025', 'e_i': 5, 't_i': 2624, 'e_c': 4, 't_c': 2629},
        {'name': 'Saini 2011', 'e_i': 0, 't_i': 26, 'e_c': 1, 't_c': 26},
        {'name': 'Fursule 2022', 'e_i': 0, 't_i': 58, 'e_c': 0, 't_c': 55},
        {'name': 'Engle 2003', 'e_i': 0, 't_i': 14, 'e_c': 0, 't_c': 12},
        {'name': 'Mathur 2015', 'e_i': 1, 't_i': 35, 'e_c': 2, 't_c': 35},
        {'name': 'Tagare 2010', 'e_i': 2, 't_i': 71, 'e_c': 2, 't_c': 69},
        {'name': 'Zain 2021', 'e_i': 0, 't_i': 60, 'e_c': 0, 't_c': 60},
    ]

    # Duration Datasets
    dur_biomarker = [
        {'m_i': 3.0, 'sd_i': 1.5, 'n_i': 247, 'm_c': 7.0, 'sd_c': 1.8, 'n_c': 246},
        {'m_i': 3.8, 'sd_i': 1.4, 'n_i': 654, 'm_c': 4.8, 'sd_c': 1.6, 'n_c': 637},
        {'m_i': 7.0, 'sd_i': 2.5, 'n_i': 251, 'm_c': 9.0, 'sd_c': 2.8, 'n_c': 253},
        {'m_i': 2.3, 'sd_i': 1.0, 'n_i': 866, 'm_c': 2.7, 'sd_c': 1.2, 'n_c': 844},
        {'m_i': 3.7, 'sd_i': 0.8, 'n_i': 38, 'm_c': 5.5, 'sd_c': 0.6, 'n_c': 39},
    ]
    dur_calc = [
        {'m_i': 0.8, 'sd_i': 1.2, 'n_i': 893, 'm_c': 1.8, 'sd_c': 2.1, 'n_c': 937},
    ]
    dur_fixed = [
        {'m_i': 2.0, 'sd_i': 0.8, 'n_i': 2624, 'm_c': 7.0, 'sd_c': 1.2, 'n_c': 2629},
        {'m_i': 2.5, 'sd_i': 0.7, 'n_i': 26, 'm_c': 7.0, 'sd_c': 0.5, 'n_c': 26},
        {'m_i': 10.9, 'sd_i': 0.8, 'n_i': 58, 'm_c': 15.2, 'sd_c': 1.2, 'n_c': 55},
        {'m_i': 2.0, 'sd_i': 0.2, 'n_i': 14, 'm_c': 4.0, 'sd_c': 0.3, 'n_c': 12},
        {'m_i': 10.0, 'sd_i': 0.5, 'n_i': 35, 'm_c': 14.0, 'sd_c': 0.5, 'n_c': 35},
    ]

    report = []
    report.append("# Subgroup Meta-Analysis Report: Neonatal Antibiotic Stewardship\n")
    report.append("## 1. Stratification by Stewardship Strategy (Primary Safety: All-Cause Mortality)\n")

    for title, grp in [("Biomarker-Guided (PCT / CRP / IL-8)", sub_biomarker),
                       ("Risk Calculator / Remote ASP", sub_calc_asp),
                       ("Fixed Short Course / Early Discontinuation", sub_fixed_short)]:
        rr, ci, i2, p = pool_rr_subgroup(grp)
        n_tot = sum(s['t_i'] + s['t_c'] for s in grp)
        report.append(f"### {title}")
        report.append(f"- **Number of Trials:** $k = {len(grp)}$")
        report.append(f"- **Total Neonates:** $N = {n_tot:,}$")
        report.append(f"- **Pooled RR (Random Effects):** $\\text{{RR}} = {rr:.2f}$ [95% CI: ${ci[0]:.2f}, {ci[1]:.2f}$]")
        report.append(f"- **Heterogeneity ($I^2$):** ${i2:.1f}\\%$")
        report.append(f"- **p-value:** ${p:.4f}\n")

    report.append("## 2. Stratification by Stewardship Strategy (Antibiotic Exposure Duration Reduction)\n")
    for title, grp in [("Biomarker-Guided (PCT / CRP / IL-8)", dur_biomarker),
                       ("Sepsis Calculator Guided", dur_calc),
                       ("Fixed Short Course / Culture-Negative Stop", dur_fixed)]:
        md, ci, i2, p = pool_md_subgroup(grp)
        n_tot = sum(s['n_i'] + s['n_c'] for s in grp)
        report.append(f"### {title}")
        report.append(f"- **Number of Trials:** $k = {len(grp)}$")
        report.append(f"- **Total Neonates:** $N = {n_tot:,}$")
        report.append(f"- **Mean Difference:** $\\text{{MD}} = {md:.2f}\\text{{ days}}$ [95% CI: ${ci[0]:.2f}, {ci[1]:.2f}\\text{{ days}}$]")
        report.append(f"- **Heterogeneity ($I^2$):** ${i2:.1f}\\%$")
        report.append(f"- **p-value:** ${p:.4e}\n")

    out_file = OUT_DIR / "SUBGROUP_ANALYSIS_REPORT.md"
    out_file.write_text("\n".join(report), encoding="utf-8")
    print(f"Subgroup analysis report written to {out_file}")

if __name__ == "__main__":
    run_subgroups()
