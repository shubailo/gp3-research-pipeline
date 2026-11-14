"""Statistical and epidemiological mathematical utilities."""
from typing import Dict, Any, List, Optional
import math

def interpret_cohens_kappa(kappa: float) -> str:
    """Returns canonical Landis & Koch (1977) interpretation for Cohen's Kappa."""
    if kappa >= 0.81:
        return "Almost Perfect Agreement (PRISMA Gold Standard)"
    elif kappa >= 0.61:
        return "Substantial Agreement (Standard Methodological Rigor)"
    elif kappa >= 0.41:
        return "Moderate Agreement (Reviewer Calibration Recommended)"
    elif kappa >= 0.21:
        return "Fair Agreement (Significant Inter-Reviewer Divergence)"
    elif kappa >= 0.00:
        return "Slight Agreement (High Discrepancy)"
    else:
        return "Poor Agreement / Disagreement"


def calculate_cohens_kappa(
    both_include: int,
    both_exclude: int,
    r1_only: int,
    r2_only: int
) -> Dict[str, Any]:
    """
    Calculates Cohen's Kappa for 2 reviewers from a 2x2 contingency table.
    
    Matrix:
                 Reviewer 2 Include    Reviewer 2 Exclude
    R1 Include   both_include (A)      r1_only (B)
    R1 Exclude   r2_only (C)           both_exclude (D)
    """
    total = both_include + both_exclude + r1_only + r2_only
    if total == 0:
        return {
            "kappa": 0.0,
            "po": 0.0,
            "pe": 0.0,
            "interpretation": "Insufficient data (total=0)",
            "total": 0,
            "action": "Need more data"
        }

    po = (both_include + both_exclude) / total

    r1_yes = (both_include + r1_only) / total
    r1_no = (r2_only + both_exclude) / total
    r2_yes = (both_include + r2_only) / total
    r2_no = (r1_only + both_exclude) / total

    pe = (r1_yes * r2_yes) + (r1_no * r2_no)

    if pe >= 1.0:
        kappa = 1.0
    else:
        kappa = (po - pe) / (1.0 - pe)

    # CTM Guidebook categorization (Page 17)
    if kappa < 0.01:
        category = "Poor / No agreement (< 0.01)"
    elif kappa <= 0.20:
        category = "Slight agreement (0.01 - 0.20)"
    elif kappa <= 0.40:
        category = "Fair agreement (0.21 - 0.40)"
    elif kappa <= 0.60:
        category = "Moderate agreement (0.41 - 0.60)"
    elif kappa <= 0.80:
        category = "Substantial agreement (0.61 - 0.80)"
    else:
        category = "Almost perfect or perfect agreement (0.81 - 1.00)"

    interp = interpret_cohens_kappa(kappa)

    action = "Folytatható a teljes szöveges fázis."
    if kappa < 0.60:
        action = "Konszenzusos megbeszélés és a szelekciós kritériumok újrakalibrálása szükséges!"

    return {
        "both_include": both_include,
        "both_exclude": both_exclude,
        "r1_only": r1_only,
        "r2_only": r2_only,
        "total": total,
        "po": round(po, 4),
        "pe": round(pe, 4),
        "kappa": round(kappa, 4),
        "observed_agreement": round(po, 4),
        "percent_agreement": f"{po * 100:.1f}%",
        "category": category,
        "interpretation": interp,
        "action": action
    }


def calculate_cohens_kappa_from_lists(
    r1_decisions: List[str],
    r2_decisions: List[str]
) -> Dict[str, Any]:
    """
    Computes Cohen's kappa (κ) between two lists of decisions.
    Binary categorization: POSITIVE (INCLUDE) vs NEGATIVE (EXCLUDE / UNSURE).
    """
    if len(r1_decisions) != len(r2_decisions) or len(r1_decisions) == 0:
        return {
            "kappa": 0.0,
            "cohens_kappa": 0.0,
            "observed_agreement": 0.0,
            "observed_agreement_pct": 0.0,
            "chance_agreement_pct": 0.0,
            "percent_agreement": "0.0%",
            "total_screened": 0,
            "interpretation": "Insufficient data"
        }

    bin_r1 = [1 if str(d).upper().startswith("INC") else 0 for d in r1_decisions]
    bin_r2 = [1 if str(d).upper().startswith("INC") else 0 for d in r2_decisions]

    both_inc = sum(1 for i in range(len(bin_r1)) if bin_r1[i] == 1 and bin_r2[i] == 1)
    r1_only = sum(1 for i in range(len(bin_r1)) if bin_r1[i] == 1 and bin_r2[i] == 0)
    r2_only = sum(1 for i in range(len(bin_r1)) if bin_r1[i] == 0 and bin_r2[i] == 1)
    both_exc = sum(1 for i in range(len(bin_r1)) if bin_r1[i] == 0 and bin_r2[i] == 0)

    res = calculate_cohens_kappa(both_inc, both_exc, r1_only, r2_only)
    res["r1_includes"] = sum(bin_r1)
    res["r2_includes"] = sum(bin_r2)
    res["total_screened"] = res["total"]
    res["r1_only_include"] = r1_only
    res["r2_only_include"] = r2_only
    res["observed_agreement_pct"] = round(res["po"] * 100, 2)
    res["chance_agreement_pct"] = round(res["pe"] * 100, 2)
    res["cohens_kappa"] = round(res["kappa"], 3)
    return res


def calculate_odds_ratio(
    a: float,
    total_intervention: float,
    c: float,
    total_control: float,
    continuity_correction: float = 0.5,
    z_critical: float = 1.95996
) -> Dict[str, Any]:
    """
    Computes odds ratio, standard error, and 95% confidence interval
    from 2x2 contingency table with standard Woolf continuity correction if zero cell exists.
    
    a: events in intervention
    total_intervention: total in intervention
    c: events in control
    total_control: total in control
    """
    b = total_intervention - a
    d = total_control - c

    if a == 0 or b == 0 or c == 0 or d == 0:
        a_adj = a + continuity_correction
        b_adj = b + continuity_correction
        c_adj = c + continuity_correction
        d_adj = d + continuity_correction
    else:
        a_adj, b_adj, c_adj, d_adj = a, b, c, d

    log_or = math.log((a_adj * d_adj) / (b_adj * c_adj))
    se = math.sqrt(1 / a_adj + 1 / b_adj + 1 / c_adj + 1 / d_adj)
    odds_ratio = math.exp(log_or)
    ci_min = math.exp(log_or - z_critical * se)
    ci_max = math.exp(log_or + z_critical * se)

    return {
        "or": odds_ratio,
        "log_or": log_or,
        "se": se,
        "var": se ** 2,
        "ci_min": ci_min,
        "ci_max": ci_max,
        "a": a,
        "total_intervention": total_intervention,
        "c": c,
        "total_control": total_control
    }


def calculate_or_from_ci(
    pe: float,
    ci_min: float,
    ci_max: float,
    z_critical: float = 1.95996
) -> Dict[str, Any]:
    """
    Recovers log_or, se, and variance from point estimate and 95% CI (e.g. reported aOR).
    """
    if pe <= 0 or ci_min <= 0 or ci_max <= 0:
        raise ValueError("Point estimate and confidence bounds must be strictly positive.")

    log_or = math.log(pe)
    se = (math.log(ci_max) - math.log(ci_min)) / (2 * z_critical)

    return {
        "or": pe,
        "log_or": log_or,
        "se": se,
        "var": se ** 2,
        "ci_min": ci_min,
        "ci_max": ci_max
    }


def pool_random_effects(recs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    DerSimonian-Laird random-effects meta-analysis pooling.
    Expects each record in recs to contain 'log_or' and 'var' (variance of log_or).
    Modifies records in-place or sets 'weight' field with percentage weights.
    """
    if not recs:
        return None

    import numpy as np

    y = np.array([r["log_or"] for r in recs], dtype=float)
    v = np.array([r["var"] for r in recs], dtype=float)
    k = len(y)
    if k == 0:
        return None

    # Fixed-effects inverse-variance weights
    w_fe = 1.0 / v
    w_fe_sum = float(np.sum(w_fe))
    theta_fe = float(np.sum(w_fe * y) / w_fe_sum)

    # Cochran's Q
    q_stat = float(np.sum(w_fe * (y - theta_fe) ** 2))
    df = k - 1

    # DerSimonian-Laird between-study variance (tau^2)
    c_val = w_fe_sum - float(np.sum(w_fe ** 2)) / w_fe_sum
    tau2 = max(0.0, (q_stat - df) / c_val) if c_val > 0 else 0.0

    # Random-effects weights
    w_re = 1.0 / (v + tau2)
    w_re_sum = float(np.sum(w_re))
    theta_re = float(np.sum(w_re * y) / w_re_sum)
    se_re = math.sqrt(1.0 / w_re_sum)

    pooled_or = math.exp(theta_re)
    ci_min = math.exp(theta_re - 1.95996 * se_re)
    ci_max = math.exp(theta_re + 1.95996 * se_re)
    z_val = theta_re / se_re if se_re > 0 else 0.0
    p_val = 2 * (1 - 0.5 * (1 + math.erf(abs(z_val) / math.sqrt(2))))

    i2 = max(0.0, (q_stat - df) / q_stat) * 100 if q_stat > 0 else 0.0

    # Study weights (percentage)
    weights = (w_re / w_re_sum) * 100
    for i, r in enumerate(recs):
        r["weight"] = float(weights[i])

    return {
        "k": k,
        "or": pooled_or,
        "ci_min": ci_min,
        "ci_max": ci_max,
        "z": z_val,
        "p": p_val,
        "Q": q_stat,
        "df": df,
        "I2": i2,
        "tau2": tau2,
        "theta_re": theta_re,
        "se_re": se_re
    }
