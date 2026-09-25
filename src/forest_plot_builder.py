#!/usr/bin/env python3
"""
forest_plot_builder.py — Statistical Execution Layer
=====================================================
GP3 Medical Research Pipeline — Evidence Synthesis Engine

Performs meta-analysis calculations and produces a text-based forest plot
from a CSV data extraction file. Uses only Python standard library + scipy
(optional for exact confidence intervals) and optionally matplotlib.

INPUT CSV FORMAT:
    author,year,n_treatment,events_treatment,n_control,events_control[,weight_override]
    Shankaran,2014,65,12,70,20
    Gluckman,2005,102,19,106,31
    ...

    OR for continuous outcomes:
    author,year,n_treatment,mean_treatment,sd_treatment,n_control,mean_control,sd_control

USAGE:
    # Dichotomous (OR/RR):
    python src/forest_plot_builder.py data/extraction.csv --outcome odds-ratio
    python src/forest_plot_builder.py data/extraction.csv --outcome risk-ratio

    # Continuous (MD):
    python src/forest_plot_builder.py data/extraction.csv --outcome mean-diff

    # Save plot image (requires matplotlib):
    python src/forest_plot_builder.py data/extraction.csv --plot forest_plot.png

    # Generate GRADE heterogeneity assessment:
    python src/forest_plot_builder.py data/extraction.csv --grade
"""

import sys
import csv
import math
import os
import argparse
from typing import Optional

# ─── Constants ────────────────────────────────────────────────────────────────
Z_95  = 1.95996   # z for 95% CI
Z_975 = 1.95996
PLOT_WIDTH = 60   # characters wide for text forest plot

# ─── Dichotomous Calculations ─────────────────────────────────────────────────

def log_odds_ratio(a: float, b: float, c: float, d: float):
    """
    Compute log(OR) and its variance.
    a = events_treatment, b = n_treatment-events_treatment
    c = events_control,   d = n_control-events_control
    Adds 0.5 continuity correction to zero cells.
    """
    a, b, c, d = [x + 0.5 if x == 0 else x for x in [a, b, c, d]]
    lor = math.log((a * d) / (b * c))
    var = 1/a + 1/b + 1/c + 1/d
    return lor, var


def log_risk_ratio(a: float, n1: float, c: float, n2: float):
    """Log(RR) and variance."""
    if a == 0: a = 0.5
    if c == 0: c = 0.5
    lrr = math.log((a / n1) / (c / n2))
    var = 1/a - 1/n1 + 1/c - 1/n2
    return lrr, var


# ─── Continuous Calculations ──────────────────────────────────────────────────

def mean_difference(m1, sd1, n1, m2, sd2, n2):
    """Mean difference and variance."""
    md  = m1 - m2
    var = (sd1**2 / n1) + (sd2**2 / n2)
    return md, var


# ─── Pooling (Random-Effects DerSimonian-Laird) ───────────────────────────────

def random_effects_pool(effects: list[float], variances: list[float]):
    """
    DerSimonian-Laird random-effects pooling.
    Returns: pooled_effect, pooled_variance, tau2, I2, Q, df, weights
    """
    k = len(effects)
    # Fixed-effects weights
    w_fe = [1/v for v in variances]
    W    = sum(w_fe)
    WW   = sum(w**2 for w in w_fe)

    # Weighted mean (FE)
    theta_fe = sum(w*e for w, e in zip(w_fe, effects)) / W

    # Q statistic
    Q  = sum(w * (e - theta_fe)**2 for w, e in zip(w_fe, effects))
    df = k - 1

    # I² (%)
    I2 = max(0.0, (Q - df) / Q * 100) if Q > 0 else 0.0

    # τ² (DerSimonian-Laird estimator)
    tau2 = max(0.0, (Q - df) / (W - WW / W))

    # Random-effects weights
    w_re = [1 / (v + tau2) for v in variances]
    W_re = sum(w_re)

    # Pooled estimate
    pooled = sum(w * e for w, e in zip(w_re, effects)) / W_re
    pooled_var = 1 / W_re

    return pooled, pooled_var, tau2, I2, Q, df, w_re


# ─── Data Loading ─────────────────────────────────────────────────────────────

def load_csv(filepath: str, outcome_type: str) -> list[dict]:
    """Load extraction CSV and parse into study records."""
    studies = []
    with open(filepath, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        headers = [h.strip().lower() for h in reader.fieldnames]

        for row in reader:
            row = {k.strip().lower(): v.strip() for k, v in row.items()}
            try:
                s = {
                    "label": f"{row.get('author','?')} {row.get('year','')}".strip(),
                }
                if outcome_type in ("odds-ratio", "risk-ratio"):
                    s["n1"]  = float(row["n_treatment"])
                    s["a"]   = float(row["events_treatment"])
                    s["n2"]  = float(row["n_control"])
                    s["c"]   = float(row["events_control"])
                elif outcome_type == "mean-diff":
                    s["m1"]  = float(row["mean_treatment"])
                    s["sd1"] = float(row["sd_treatment"])
                    s["n1"]  = float(row["n_treatment"])
                    s["m2"]  = float(row["mean_control"])
                    s["sd2"] = float(row["sd_control"])
                    s["n2"]  = float(row["n_control"])
                studies.append(s)
            except (KeyError, ValueError) as e:
                print(f"  ⚠️  Skipping row (missing field): {dict(row)} — {e}")

    return studies


def compute_effects(studies: list[dict], outcome_type: str):
    """Compute per-study effects and variances."""
    for s in studies:
        if outcome_type == "odds-ratio":
            b = s["n1"] - s["a"]
            d = s["n2"] - s["c"]
            log_e, var = log_odds_ratio(s["a"], b, s["c"], d)
        elif outcome_type == "risk-ratio":
            log_e, var = log_risk_ratio(s["a"], s["n1"], s["c"], s["n2"])
        elif outcome_type == "mean-diff":
            log_e, var = mean_difference(s["m1"], s["sd1"], s["n1"],
                                          s["m2"], s["sd2"], s["n2"])
        else:
            raise ValueError(f"Unknown outcome type: {outcome_type}")

        s["effect"] = log_e
        s["variance"] = var
        s["se"]     = math.sqrt(var)
        s["ci_lo"]  = log_e - Z_95 * math.sqrt(var)
        s["ci_hi"]  = log_e + Z_95 * math.sqrt(var)
    return studies


# ─── Text Forest Plot ─────────────────────────────────────────────────────────

def render_text_forest(studies, pooled_e, pooled_var, I2, Q, df, tau2,
                        outcome_type, label_width=22, is_log=True):
    """Render a unicode text forest plot to stdout."""

    def to_display(x):
        return math.exp(x) if is_log else x

    all_vals = [s["ci_lo"] for s in studies] + [s["ci_hi"] for s in studies]
    x_min = min(all_vals + [pooled_e - Z_95 * math.sqrt(pooled_var)])
    x_max = max(all_vals + [pooled_e + Z_95 * math.sqrt(pooled_var)])
    x_range = x_max - x_min
    null_line = 0.0  # log scale null = log(1) = 0; MD null = 0

    def to_col(x):
        return int((x - x_min) / x_range * PLOT_WIDTH)

    null_col = to_col(null_line)
    pool_col = to_col(pooled_e)
    pool_lo  = to_col(pooled_e - Z_95 * math.sqrt(pooled_var))
    pool_hi  = to_col(pooled_e + Z_95 * math.sqrt(pooled_var))

    unit = "OR" if outcome_type == "odds-ratio" else ("RR" if outcome_type == "risk-ratio" else "MD")

    header = f"\n{'Study':<{label_width}}  {'Effect':>8}  {'95% CI':>20}  Plot"
    sep    = "─" * (label_width + 2 + 8 + 2 + 20 + 2 + PLOT_WIDTH + 4)
    print(header)
    print(sep)

    total_w = 0.0
    for s in studies:
        e_disp  = to_display(s["effect"])
        lo_disp = to_display(s["ci_lo"])
        hi_disp = to_display(s["ci_hi"])
        col_lo  = to_col(s["ci_lo"])
        col_hi  = to_col(s["ci_hi"])
        col_e   = to_col(s["effect"])

        # Build plot line
        row = [" "] * (PLOT_WIDTH + 2)
        for c in range(min(col_lo, col_hi), min(max(col_lo, col_hi) + 1, PLOT_WIDTH + 2)):
            row[c] = "─"
        if 0 <= col_lo < len(row):   row[col_lo] = "├"
        if 0 <= col_hi < len(row):   row[col_hi] = "┤"
        if 0 <= col_e  < len(row):   row[col_e]  = "◆"
        if 0 <= null_col < len(row): row[null_col] = ("|" if row[null_col] == " " else row[null_col])

        label = s["label"][:label_width]
        effect_str = f"{e_disp:8.3f}"
        ci_str     = f"[{lo_disp:.3f}, {hi_disp:.3f}]"
        plot_str   = "".join(row)

        print(f"{label:<{label_width}}  {effect_str}  {ci_str:>20}  {plot_str}")

    # Pooled row
    print(sep)
    p_disp  = to_display(pooled_e)
    p_lo    = to_display(pooled_e - Z_95 * math.sqrt(pooled_var))
    p_hi    = to_display(pooled_e + Z_95 * math.sqrt(pooled_var))

    pool_row = [" "] * (PLOT_WIDTH + 2)
    for c in range(pool_lo, min(pool_hi + 1, PLOT_WIDTH + 2)):
        pool_row[c] = "═"
    if 0 <= pool_lo < len(pool_row):  pool_row[pool_lo] = "╠"
    if 0 <= pool_hi < len(pool_row):  pool_row[pool_hi] = "╣"
    if 0 <= pool_col < len(pool_row): pool_row[pool_col] = "◆"
    if 0 <= null_col < len(pool_row): pool_row[null_col] = ("|" if pool_row[null_col] == " " else pool_row[null_col])

    pool_label = f"Pooled {unit} (RE)"
    print(f"{pool_label:<{label_width}}  {p_disp:8.3f}  [{p_lo:.3f}, {p_hi:.3f}]  {''.join(pool_row)}")
    print(sep)

    # Heterogeneity stats
    p_val_q = _chi2_p(Q, df)
    print(f"\n  Heterogeneity:  Q = {Q:.2f} (df={df}, p={p_val_q:.4f}) | I² = {I2:.1f}% | τ² = {tau2:.4f}")
    print(f"  Pooled {unit}:    {p_disp:.3f}  95% CI [{p_lo:.3f}, {p_hi:.3f}]")

    # GRADE heterogeneity interpretation
    if I2 < 25:
        grade_h = "Low heterogeneity — consistent findings (I² < 25%)"
    elif I2 < 50:
        grade_h = "Moderate heterogeneity — explore subgroups (I² 25-50%)"
    elif I2 < 75:
        grade_h = "Substantial heterogeneity — consider narrative synthesis (I² 50-75%)"
    else:
        grade_h = "⚠️  CONSIDERABLE HETEROGENEITY — pooling may be inappropriate (I² ≥ 75%)"

    print(f"  GRADE:          {grade_h}")


def _chi2_p(q: float, df: int) -> float:
    """Approximate chi² p-value using Wilson-Hilferty approximation."""
    if df <= 0: return 1.0
    try:
        import math
        # Normal approximation for chi² p-value
        z = ((q / df) ** (1/3) - (1 - 2/(9*df))) / math.sqrt(2/(9*df))
        # Standard normal survival function (approximation)
        return _norm_sf(z)
    except Exception:
        return float("nan")


def _norm_sf(z: float) -> float:
    """Standard normal survival function P(Z > z) — Horner's method."""
    import math
    return 0.5 * math.erfc(z / math.sqrt(2))


# ─── GRADE Assessment ─────────────────────────────────────────────────────────

def print_grade_table(I2, n_studies, pooled_e, pooled_var, outcome_type):
    """Print a GRADE Summary of Findings table shell."""
    is_log = outcome_type in ("odds-ratio", "risk-ratio")
    p_disp = math.exp(pooled_e) if is_log else pooled_e
    p_lo   = math.exp(pooled_e - Z_95 * math.sqrt(pooled_var)) if is_log else pooled_e - Z_95 * math.sqrt(pooled_var)
    p_hi   = math.exp(pooled_e + Z_95 * math.sqrt(pooled_var)) if is_log else pooled_e + Z_95 * math.sqrt(pooled_var)
    unit   = "OR" if outcome_type == "odds-ratio" else ("RR" if outcome_type == "risk-ratio" else "MD")

    # Auto-score GRADE domains
    rob     = "Unknown — complete RoB assessment"
    indir   = "Direct" if n_studies >= 5 else "Possibly indirect (few studies)"
    imperc  = "Precise" if (p_lo > 1.0 or p_hi < 1.0) else "Imprecise — 95% CI crosses null"
    incons  = "Consistent (I² < 25%)" if I2 < 25 else (
              "Inconsistent — downgrade (I² ≥ 50%)" if I2 >= 50 else
              "Possibly inconsistent — explore (I² 25-50%)")
    pub_b   = "Not assessed — run Egger's test"
    overall = "Moderate" if I2 < 50 else "Low"

    print(f"\n{'─'*70}")
    print("  GRADE Summary of Findings (Auto-Generated Shell)")
    print(f"{'─'*70}")
    print(f"  Outcome:          Primary [{unit}]")
    print(f"  Studies (k):      {n_studies}")
    print(f"  Pooled {unit}:       {p_disp:.3f} [{p_lo:.3f}, {p_hi:.3f}]")
    print(f"  Study limitations:{rob}")
    print(f"  Inconsistency:    {incons}")
    print(f"  Indirectness:     {indir}")
    print(f"  Imprecision:      {imperc}")
    print(f"  Publication bias: {pub_b}")
    print(f"  ──────────────────────────────────────────────────")
    print(f"  Overall certainty: {overall} ⊕⊕{'⊕⊕' if overall == 'High' else ('⊕⊕' if overall == 'Moderate' else '○○')}")
    print(f"{'─'*70}")
    print(f"  ⚠️  This is an auto-generated shell. Complete manually before publication.\n")


# ─── Main CLI ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="GP3 Forest Plot Builder — meta-analysis calculations + text forest plot"
    )
    parser.add_argument("filepath", help="CSV data extraction file")
    parser.add_argument(
        "--outcome", choices=["odds-ratio", "risk-ratio", "mean-diff"],
        default="odds-ratio", help="Effect measure (default: odds-ratio)"
    )
    parser.add_argument("--grade", action="store_true", help="Show GRADE assessment shell")
    parser.add_argument(
        "--plot", default=None, metavar="FILE.png",
        help="Save matplotlib forest plot to image file (requires matplotlib)"
    )
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if not os.path.isfile(args.filepath):
        print(f"ERROR: File not found: {args.filepath}", file=sys.stderr)
        sys.exit(1)

    print(f"\nGP3 Forest Plot Builder")
    print(f"  Input:   {args.filepath}")
    print(f"  Outcome: {args.outcome}")

    # Load & compute
    studies = load_csv(args.filepath, args.outcome)
    if len(studies) < 2:
        print(f"\n❌ POOLABILITY GATE: Only {len(studies)} study loaded. Need ≥2 for pooling.")
        print("   GP3 Rule: Need ≥3 studies with identical outcome for meta-analysis.")
        sys.exit(1)

    if len(studies) < 3:
        print(f"\n⚠️  POOLABILITY WARNING: Only {len(studies)} studies — GP3 requires ≥3.")

    studies = compute_effects(studies, args.outcome)

    is_log = args.outcome in ("odds-ratio", "risk-ratio")
    effects   = [s["effect"]   for s in studies]
    variances = [s["variance"] for s in studies]

    pooled_e, pooled_var, tau2, I2, Q, df, weights = random_effects_pool(effects, variances)

    # Assign relative weights (for display)
    w_sum = sum(weights)
    for s, w in zip(studies, weights):
        s["weight_pct"] = w / w_sum * 100

    # Render
    render_text_forest(studies, pooled_e, pooled_var, I2, Q, df, tau2, args.outcome, is_log=is_log)

    if args.grade:
        print_grade_table(I2, len(studies), pooled_e, pooled_var, args.outcome)

    # Optional matplotlib plot
    if args.plot:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches

            fig, ax = plt.subplots(figsize=(10, 1.5 + len(studies) * 0.6))
            ax.set_title(f"Forest Plot — {args.outcome.replace('-',' ').title()}", fontsize=13, fontweight="bold")

            y_positions = list(range(len(studies), 0, -1))
            null_x = 1.0 if is_log else 0.0

            for i, (s, y) in enumerate(zip(studies, y_positions)):
                e_d  = math.exp(s["effect"])  if is_log else s["effect"]
                lo_d = math.exp(s["ci_lo"])   if is_log else s["ci_lo"]
                hi_d = math.exp(s["ci_hi"])   if is_log else s["ci_hi"]
                size = max(5, s["weight_pct"] * 2)
                ax.plot([lo_d, hi_d], [y, y], color="#2c7bb6", linewidth=1.5)
                ax.scatter([e_d], [y], s=size, color="#2c7bb6", zorder=5)
                ax.text(-0.02, y, s["label"], ha="right", va="center", fontsize=9, transform=ax.get_yaxis_transform())

            # Pooled diamond
            p_d  = math.exp(pooled_e) if is_log else pooled_e
            p_lo = math.exp(pooled_e - Z_95 * math.sqrt(pooled_var)) if is_log else pooled_e - Z_95 * math.sqrt(pooled_var)
            p_hi = math.exp(pooled_e + Z_95 * math.sqrt(pooled_var)) if is_log else pooled_e + Z_95 * math.sqrt(pooled_var)
            diamond_y = 0
            diamond = mpatches.FancyArrow(
                p_lo, diamond_y, p_hi - p_lo, 0,
                width=0.35, head_width=0.0, head_length=0.0,
                color="#d73027", alpha=0.8
            )
            ax.add_patch(diamond)
            ax.axvline(null_x, color="black", linewidth=0.8, linestyle="--")
            ax.set_xlabel("OR (95% CI)" if is_log else "MD (95% CI)")
            ax.set_yticks([])
            ax.text(0, -0.05, f"I² = {I2:.1f}%  |  Pooled = {p_d:.3f} [{p_lo:.3f}, {p_hi:.3f}]",
                    ha="center", fontsize=9, transform=ax.transAxes)
            plt.tight_layout()
            plt.savefig(args.plot, dpi=150, bbox_inches="tight")
            print(f"\n✅ Forest plot saved: {args.plot}")
        except ImportError:
            print("\n⚠️  matplotlib not available. Install with: pip install matplotlib")
        except Exception as e:
            print(f"\n⚠️  Plot generation failed: {e}")

    print()


if __name__ == "__main__":
    main()
