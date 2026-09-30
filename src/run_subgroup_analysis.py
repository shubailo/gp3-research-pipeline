"""
Subgroup meta-analysis for neonatal empirical antibiotics project.
Stratification variables:
  - Region (North America / Europe / Asia / Middle East-Africa / Oceania / Other)
  - Study Design (RCT / Prospective Cohort / Retrospective Cohort / Before-After)
  - Publication Period (Pre-2010 / 2010-2019 / 2020+)
  - Population (VLBW-focused vs Mixed)

Uses the same DerSimonian-Laird random-effects engine as run_meta_analysis.py
"""
import openpyxl
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9

# ── 1. MODERATOR LOOKUP TABLE (manually coded from Basic layout + dossiers) ──
# Format: 'Author Year (variant)' -> {region, design_cat, period, pop_cat}
# Design categories: 'RCT', 'Prospective', 'Retrospective', 'Before-After/QE'

MODERATORS = {
    'Ting 2019':            {'region': 'North America', 'design': 'Retrospective',   'period': '2010-2019', 'pop': 'VLBW'},
    'Zhu 2023':             {'region': 'Asia',           'design': 'Retrospective',   'period': '2020+',     'pop': 'Mixed'},
    'Abdel-Ghany 2012':     {'region': 'Middle East/Africa', 'design': 'Retrospective','period': '2010-2019','pop': 'Mixed'},
    'Kuppala 2011':         {'region': 'North America', 'design': 'Retrospective',   'period': '2010-2019', 'pop': 'VLBW'},
    'Alexander 2011':       {'region': 'North America', 'design': 'Retrospective',   'period': '2010-2019', 'pop': 'VLBW'},
    'Cantey 2017':          {'region': 'North America', 'design': 'Retrospective',   'period': '2010-2019', 'pop': 'Mixed'},
    'Vatne 2023':           {'region': 'Europe',         'design': 'Prospective',     'period': '2020+',     'pop': 'Mixed'},
    'Letouzey 2022':        {'region': 'Europe',         'design': 'Prospective',     'period': '2020+',     'pop': 'VLBW'},
    'Greenberg 2019':       {'region': 'North America', 'design': 'Retrospective',   'period': '2010-2019', 'pop': 'VLBW'},
    'Shi 2024':             {'region': 'Asia',           'design': 'Retrospective',   'period': '2020+',     'pop': 'Mixed'},
    'Stoll 2020':           {'region': 'North America', 'design': 'Retrospective',   'period': '2020+',     'pop': 'VLBW'},
    'Dierikx 2022':         {'region': 'Europe',         'design': 'Prospective',     'period': '2020+',     'pop': 'Mixed'},
    'Raba 2019':            {'region': 'Europe',         'design': 'Retrospective',   'period': '2010-2019', 'pop': 'Mixed'},
    'Al-Mouqdad 2018':      {'region': 'Middle East/Africa', 'design': 'Retrospective','period': '2010-2019','pop': 'VLBW'},
    'Flannery 2018':        {'region': 'North America', 'design': 'Retrospective',   'period': '2010-2019', 'pop': 'VLBW'},
    'Tolia 2016':           {'region': 'North America', 'design': 'Before-After/QE', 'period': '2010-2019', 'pop': 'Mixed'},
    'Mitanchez 2026':       {'region': 'Europe',         'design': 'RCT',             'period': '2020+',     'pop': 'Mixed'},
    'Hou 2022':             {'region': 'Asia',           'design': 'Prospective',     'period': '2020+',     'pop': 'Mixed'},
    'Rallis 2025':          {'region': 'Oceania',        'design': 'Retrospective',   'period': '2020+',     'pop': 'VLBW'},
    'Garg 2025':            {'region': 'North America', 'design': 'Retrospective',   'period': '2020+',     'pop': 'VLBW'},
    'Garg 2025 (Medical NEC)': {'region': 'North America', 'design': 'Retrospective','period': '2020+',    'pop': 'VLBW'},
    'Garg 2025 (Surgical NEC)': {'region': 'North America', 'design': 'Retrospective','period': '2020+',   'pop': 'VLBW'},
    'Garg 2025 (Mortality)':{'region': 'North America', 'design': 'Retrospective',   'period': '2020+',     'pop': 'VLBW'},
    'Fajardo 2018':         {'region': 'North America', 'design': 'Retrospective',   'period': '2010-2019', 'pop': 'VLBW'},
    'Martinez 2017':        {'region': 'Other',          'design': 'Retrospective',   'period': '2010-2019', 'pop': 'Mixed'},
    'Afjeh 2016':           {'region': 'Middle East/Africa', 'design': 'Retrospective','period': '2010-2019','pop': 'Mixed'},
    'Charron 2019':         {'region': 'North America', 'design': 'Retrospective',   'period': '2010-2019', 'pop': 'Mixed'},
    'Thampi 2019':          {'region': 'North America', 'design': 'Prospective',     'period': '2010-2019', 'pop': 'Mixed'},
    'Pace 2023':            {'region': 'North America', 'design': 'Before-After/QE', 'period': '2020+',     'pop': 'Mixed'},
    'Grant 2017':           {'region': 'Europe',         'design': 'Before-After/QE', 'period': '2010-2019', 'pop': 'Mixed'},
    'Al-Turk 2017':         {'region': 'North America', 'design': 'Retrospective',   'period': '2010-2019', 'pop': 'Mixed'},
    'Reed 2018':            {'region': 'North America', 'design': 'Prospective',     'period': '2010-2019', 'pop': 'VLBW'},
    'Torres 2018':          {'region': 'Other',          'design': 'Retrospective',   'period': '2010-2019', 'pop': 'Mixed'},
    'Songer 2021':          {'region': 'North America', 'design': 'Retrospective',   'period': '2020+',     'pop': 'Mixed'},
    'Zhu 2022':             {'region': 'Asia',           'design': 'Retrospective',   'period': '2020+',     'pop': 'Mixed'},
    'Filip 2025':           {'region': 'Europe',         'design': 'Retrospective',   'period': '2020+',     'pop': 'Mixed'},
    'Karakatsani 2025':     {'region': 'Europe',         'design': 'Before-After/QE', 'period': '2020+',     'pop': 'Mixed'},
    'Cantey 2016':          {'region': 'North America', 'design': 'Prospective',     'period': '2010-2019', 'pop': 'Mixed'},
    'Shah 2013':            {'region': 'Oceania',        'design': 'Retrospective',   'period': '2010-2019', 'pop': 'VLBW'},
    'Song 2026':            {'region': 'Asia',           'design': 'Retrospective',   'period': '2020+',     'pop': 'Mixed'},
    'Dimopoulou 2025':      {'region': 'Europe',         'design': 'Retrospective',   'period': '2020+',     'pop': 'Mixed'},
    'Wu 2025':              {'region': 'Asia',           'design': 'Retrospective',   'period': '2020+',     'pop': 'Mixed'},
    'Alturk 2021':          {'region': 'Middle East/Africa', 'design': 'Retrospective','period': '2020+',   'pop': 'Mixed'},
    'Li 2026':              {'region': 'Asia',           'design': 'Prospective',     'period': '2020+',     'pop': 'Mixed'},
    'Zini 2024':            {'region': 'Europe',         'design': 'Before-After/QE', 'period': '2020+',     'pop': 'Mixed'},
    'Yao 2025':             {'region': 'Asia',           'design': 'Before-After/QE', 'period': '2020+',     'pop': 'Mixed'},
    'Sanchez 2023':         {'region': 'North America', 'design': 'Retrospective',   'period': '2020+',     'pop': 'Mixed'},
    'Chu 2023':             {'region': 'Asia',           'design': 'Before-After/QE', 'period': '2020+',     'pop': 'Mixed'},
    'Cotten 2009':          {'region': 'North America', 'design': 'Prospective',     'period': 'Pre-2010',  'pop': 'VLBW'},
    'Stocker 2017':         {'region': 'Europe',         'design': 'RCT',             'period': '2010-2019', 'pop': 'Mixed'},
    'Coggins 2013':         {'region': 'North America', 'design': 'Retrospective',   'period': '2010-2019', 'pop': 'VLBW'},
    'Cordero 2003':         {'region': 'North America', 'design': 'Retrospective',   'period': 'Pre-2010',  'pop': 'VLBW'},
    'Kopsidas 2021':        {'region': 'Europe',         'design': 'Before-After/QE', 'period': '2020+',     'pop': 'Mixed'},
    'Gyllensvard 2020':     {'region': 'Europe',         'design': 'Before-After/QE', 'period': '2020+',     'pop': 'Mixed'},
    'Mesilhy 2025':         {'region': 'Middle East/Africa', 'design': 'Retrospective','period': '2020+',   'pop': 'Mixed'},
    'Villanueva 2021':      {'region': 'Oceania',        'design': 'Before-After/QE', 'period': '2020+',     'pop': 'Mixed'},
    # Vatne sub-arms
    'Vatne 2023 (4-7d vs 1-3d)': {'region': 'Europe', 'design': 'Prospective',      'period': '2020+',     'pop': 'Mixed'},
    'Vatne 2023 (>=5d vs 0-4d)': {'region': 'Europe', 'design': 'Prospective',      'period': '2020+',     'pop': 'Mixed'},
    # Wu sub-arms
    'Wu 2025 (aOR)':        {'region': 'Asia',           'design': 'Retrospective',   'period': '2020+',     'pop': 'Mixed'},
}

def lookup_mod(study_id, field):
    """Fuzzy match study_id to MODERATORS dict."""
    # Exact match
    if study_id in MODERATORS:
        return MODERATORS[study_id].get(field, 'NR')
    # Partial match (for variant arms)
    for k, v in MODERATORS.items():
        if k.lower() in study_id.lower() or study_id.lower() in k.lower():
            return v.get(field, 'NR')
    # Try author+year
    parts = study_id.split()
    if len(parts) >= 2:
        for k in MODERATORS:
            kp = k.split()
            if len(kp) >= 2 and kp[0].lower() == parts[0].lower() and kp[1] == parts[1]:
                return MODERATORS[k].get(field, 'NR')
    return 'NR'

# ── 2. DATA LOADING ──
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

            rec = {'study': sid, 'type': est_type,
                   'region': lookup_mod(sid, 'region'),
                   'design': lookup_mod(sid, 'design'),
                   'period': lookup_mod(sid, 'period'),
                   'pop':    lookup_mod(sid, 'pop')}

            if est_type == 'aOR' and pe and ci_min and ci_max and ci_min > 0:
                log_or = math.log(pe)
                se = (math.log(ci_max) - math.log(ci_min)) / (2 * 1.95996)
                rec.update({'or': pe, 'ci_min': ci_min, 'ci_max': ci_max,
                             'log_or': log_or, 'se': se, 'var': se**2})
                records.append(rec)
            elif a is not None and tot_i is not None and c is not None and tot_c is not None:
                b = tot_i - a; d = tot_c - c
                if a == 0 or b == 0 or c == 0 or d == 0:
                    a, b, c, d = a+0.5, b+0.5, c+0.5, d+0.5
                log_or = math.log((a * d) / (b * c))
                se = math.sqrt(1/a + 1/b + 1/c + 1/d)
                or_val = math.exp(log_or)
                rec.update({'or': or_val, 'ci_min': math.exp(log_or - 1.95996*se),
                             'ci_max': math.exp(log_or + 1.95996*se),
                             'log_or': log_or, 'se': se, 'var': se**2})
                records.append(rec)
    return records

def pool_re(recs):
    if len(recs) < 2:
        return None
    y = np.array([r['log_or'] for r in recs])
    v = np.array([r['var'] for r in recs])
    k = len(y)
    w_fe = 1.0/v; wsum = w_fe.sum()
    theta_fe = (w_fe*y).sum()/wsum
    Q = (w_fe*(y-theta_fe)**2).sum()
    df = k-1
    c = wsum - (w_fe**2).sum()/wsum
    tau2 = max(0.0, (Q-df)/c) if c>0 else 0.0
    w_re = 1.0/(v+tau2); wrsum = w_re.sum()
    theta_re = (w_re*y).sum()/wrsum
    se_re = math.sqrt(1.0/wrsum)
    or_p = math.exp(theta_re)
    ci_l = math.exp(theta_re - 1.95996*se_re)
    ci_u = math.exp(theta_re + 1.95996*se_re)
    z = theta_re/se_re
    p = 2*(1 - 0.5*(1+math.erf(abs(z)/math.sqrt(2))))
    I2 = max(0.0, (Q-df)/Q)*100 if Q>0 else 0.0
    return {'k':k,'or':or_p,'ci_min':ci_l,'ci_max':ci_u,'z':z,'p':p,'Q':Q,'df':df,'I2':I2,'tau2':tau2}

# ── 3. LOAD OUTCOMES ──
nec_recs   = extract_outcome('Necrotizing Enterocolitis (Bell >= 2)')
mort_recs  = extract_outcome('All-cause In-Hospital Mortality')
los_recs   = extract_outcome('Late-Onset Sepsis')

out_dir = 'projects/neonatal_antibiotics/results'
os.makedirs(out_dir, exist_ok=True)

# ── 4. SUBGROUP COMPARISON PLOT ──
def subgroup_forest(outcome_name, recs, mod_field, subgroups, xlim=(0.3, 5.0), filename=None):
    """
    Creates a publication-quality subgroup forest plot.
    Each subgroup gets its own pooled estimate + CI.
    """
    subgroup_results = {}
    for sg in subgroups:
        sg_recs = [r for r in recs if r[mod_field] == sg]
        pool = pool_re(sg_recs)
        if pool:
            subgroup_results[sg] = pool

    if not subgroup_results:
        print(f"No subgroups found for {outcome_name} / {mod_field}")
        return

    overall = pool_re(recs)
    n_sg = len(subgroup_results)

    fig_height = max(4, n_sg * 0.9 + 2.5)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    y_positions = {}
    y = n_sg + 1
    # Overall first
    ax.axhline(y=n_sg + 0.3, color='lightgray', lw=0.5)
    ax.plot([overall['ci_min'], overall['ci_max']], [n_sg+1, n_sg+1], color='#d62728', lw=2.5)
    d_x = [overall['ci_min'], overall['or'], overall['ci_max'], overall['or'], overall['ci_min']]
    d_y = [n_sg+1, n_sg+1.3, n_sg+1, n_sg+0.7, n_sg+1]
    ax.fill(d_x, d_y, color='#d62728', alpha=0.9)
    ax.text(-0.02, n_sg+1, f"Overall (k={overall['k']})", ha='right', va='center', fontsize=9,
            fontweight='bold', transform=ax.get_yaxis_transform())
    txt = f"OR={overall['or']:.2f} [{overall['ci_min']:.2f}, {overall['ci_max']:.2f}], I²={overall['I2']:.0f}%"
    ax.text(1.01, n_sg+1, txt, ha='left', va='center', fontsize=8, fontweight='bold',
            transform=ax.get_yaxis_transform())

    colors = ['#1f77b4','#2ca02c','#ff7f0e','#9467bd','#8c564b','#e377c2','#17becf','#bcbd22']
    for i, (sg, pool) in enumerate(subgroup_results.items()):
        y_pos = n_sg - i
        c = colors[i % len(colors)]
        ax.plot([pool['ci_min'], pool['ci_max']], [y_pos, y_pos], color='black', lw=1.5)
        ax.plot(pool['or'], y_pos, 's', color=c, markersize=10)
        ax.text(-0.02, y_pos, f"{sg} (k={pool['k']})", ha='right', va='center', fontsize=9,
                transform=ax.get_yaxis_transform())
        txt2 = f"OR={pool['or']:.2f} [{pool['ci_min']:.2f}, {pool['ci_max']:.2f}], I²={pool['I2']:.0f}%"
        ax.text(1.01, y_pos, txt2, ha='left', va='center', fontsize=8,
                transform=ax.get_yaxis_transform())

    ax.axvline(1.0, color='grey', linestyle='--', lw=1)
    ax.set_xscale('log')
    ax.set_xlim(xlim[0], xlim[1])
    ax.set_ylim(0.3, n_sg + 2)
    ax.set_yticks([])
    ax.set_xlabel("Odds Ratio (log scale)\n<--- Protective | Harmful --->", fontsize=9, fontweight='bold')
    title_str = f"{outcome_name}\nSubgroup: {mod_field.capitalize()} | Random-Effects (DerSimonian-Laird)"
    ax.set_title(title_str, fontsize=10, fontweight='bold', pad=12)
    ax.grid(axis='x', linestyle=':', alpha=0.5)
    plt.tight_layout()
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Saved: {filename}")
    plt.close()
    return subgroup_results

# ── 5. RUN ALL SUBGROUP ANALYSES ──
print("=" * 65)
print("SUBGROUP META-ANALYSIS RESULTS")
print("=" * 65)

analyses = [
    ('Necrotizing Enterocolitis (Bell >= 2)', nec_recs, 'NEC'),
    ('All-cause In-Hospital Mortality', mort_recs, 'Mortality'),
    ('Late-Onset Sepsis', los_recs, 'LOS'),
]

for outcome_label, recs, short in analyses:
    print(f"\n" + "-"*60)
    print(f"OUTCOME: {outcome_label}  (k={len(recs)} total records)")
    print("-"*60)

    for mod_field, subgroups, label in [
        ('region',  ['North America','Europe','Asia','Middle East/Africa','Oceania','Other'], 'Region'),
        ('design',  ['RCT','Prospective','Retrospective','Before-After/QE'], 'Study Design'),
        ('period',  ['Pre-2010','2010-2019','2020+'], 'Publication Period'),
        ('pop',     ['VLBW','Mixed'], 'Population Category'),
    ]:
        fname = f"{out_dir}/subgroup_{short.lower()}_{mod_field}.png"
        sg_res = subgroup_forest(outcome_label, recs, mod_field, subgroups, xlim=(0.1, 15.0), filename=fname)
        if sg_res:
            print(f"\n  [{label}]")
            for sg, p in sg_res.items():
                star = " *" if p['p'] < 0.05 else ""
                print(f"    {sg:25s}: k={p['k']:2d}, OR={p['or']:.2f} [{p['ci_min']:.2f}, {p['ci_max']:.2f}], I²={p['I2']:.0f}%, p={p['p']:.3f}{star}")

print("\n\nAll subgroup plots saved to:", out_dir)
