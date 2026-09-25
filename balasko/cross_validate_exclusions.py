# -*- coding: utf-8 -*-
"""
cross_validate_exclusions.py
----------------------------
Logika:
  1. Beolvassa az Animal_metadata lap összes jelölt állatát (kommenttel rendelkezők)
  2. Minden jelölt állathoz megkeresi a tényleges adatait a csoport-lapon
  3. Kiszámítja az állat átlagát a POST-injekciós időszakra (t >= 0)
  4. Összehasonlítja a saját csoportjának átlagával és SD-jével (z-score)
  5. CSAK akkor javasolja a kizárást, ha |z| > 2.0 VAGY ha az adat hiányzik/csonka

Eredmény: táblázat három oszloppal:
  - ZÁRJUK KI (komment + kiugró adat)
  - TARTSUK BENT (komment van, de az adat normális)
  - NEM ÉRTÉKELHETŐ (nincs adat az adott lapban)
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Azok a kommentek, amik technikai problémát jeleznek (kizárásra GYANÚS)
PROBLEM_KEYWORDS = [
    "szétcsúszott", "szétrágta", "lyukas", "nehezen megy be",
    "nem kap pg", "nem kap pg-t", "pg nincs", "oxy nincs",
    "pg-", "gennyes", "véres", "visszafordulva", "visszacsúszott",
    "fürdetés", "ül", "magas tc", "beszaladt a pg"
]

# Paraméterek, amiket vizsgálunk (az Excel lapokban lévő sorok Parameter oszlopa alapján)
PARAMS_OF_INTEREST = ['VO2', 'VCO2', 'RQ', 'EE', 'dVO2', 'dVCO2', 'Tc', 'Ts', 'Ta', 'HLI', 'dTc', 'dTs']

Z_THRESHOLD = 2.0  # Ha |z| > ez, akkor kiugrónak számít


def has_problem_keyword(text):
    if not text:
        return False, None
    t = str(text).lower().strip()
    for kw in PROBLEM_KEYWORDS:
        if kw.lower() in t:
            return True, kw
    return False, None


def load_metadata(filepath):
    """Animal_metadata lap betöltése."""
    df = pd.read_excel(filepath, sheet_name='Animal_metadata', header=0)
    return df


def get_animal_data_from_sheet(xls, sheet_name, animal_id, post_injection_only=True):
    """
    Kiolvassa egy állat adatait egy adott lapból.
    Visszaadja: {param: mean_value} dict, post-injekció (t>=0) átlagait.
    """
    try:
        df = pd.read_excel(xls, sheet_name=sheet_name, header=0)
    except Exception:
        return None, None

    # Megkeressük az időoszlopot
    time_col = None
    time_idx = None
    for i, col in enumerate(df.columns):
        if 'Time' in str(col) or 'time' in str(col):
            time_col = col
            time_idx = i
            break

    if time_col is None:
        return None, None

    # Paraméter oszlop
    param_col = None
    for col in df.columns[:time_idx]:
        if 'Parameter' in str(col) or 'Param' in str(col):
            param_col = col
            break

    # Állatoszlopok
    animal_cols = list(df.columns[time_idx + 1:])

    # Az állat ID-ja lehet int vagy string is a fejlécben
    animal_id_str = str(animal_id).strip()
    # Próbáljuk megtalálni az állatot
    matched_col = None
    for col in animal_cols:
        col_str = str(col).strip()
        # Eltávolítjuk a .0 végűt ha float
        col_clean = col_str.rstrip('0').rstrip('.') if '.' in col_str else col_str
        id_clean = animal_id_str.rstrip('0').rstrip('.') if '.' in animal_id_str else animal_id_str
        if col_clean == id_clean or col_str == animal_id_str:
            matched_col = col
            break

    if matched_col is None:
        return None, None  # Az állat nem szerepel ezen a lapon

    # Szűrés post-injekciós időre
    if post_injection_only:
        df_post = df[pd.to_numeric(df[time_col], errors='coerce') >= 0].copy()
    else:
        df_post = df.copy()

    # Param → mean dict az állathoz
    animal_means = {}
    if param_col:
        for param, sub in df_post.groupby(param_col):
            vals = pd.to_numeric(sub[matched_col], errors='coerce').dropna()
            if len(vals) > 0:
                animal_means[str(param).strip()] = vals.mean()
    else:
        # Nincs paraméter oszlop, az egész lapot kezeljük egységként
        vals = pd.to_numeric(df_post[matched_col], errors='coerce').dropna()
        if len(vals) > 0:
            animal_means['overall'] = vals.mean()

    return animal_means, matched_col


def get_group_stats(xls, sheet_name, post_injection_only=True):
    """
    Kiszámítja az összes állat átlagát és SD-jét minden paraméterhez.
    Visszaad: {param: (mean, std, n)} dict
    """
    try:
        df = pd.read_excel(xls, sheet_name=sheet_name, header=0)
    except Exception:
        return {}

    time_col = None
    time_idx = None
    for i, col in enumerate(df.columns):
        if 'Time' in str(col) or 'time' in str(col):
            time_col = col
            time_idx = i
            break

    if time_col is None:
        return {}

    param_col = None
    for col in df.columns[:time_idx]:
        if 'Parameter' in str(col) or 'Param' in str(col):
            param_col = col
            break

    # Szűrt adatok
    if post_injection_only:
        df_post = df[pd.to_numeric(df[time_col], errors='coerce') >= 0].copy()
    else:
        df_post = df.copy()

    # Meghatározzuk az állatoszlopokat (numerikus fejlécű)
    animal_cols = []
    for col in df.columns[time_idx + 1:]:
        col_str = str(col).strip()
        # Csak numerikus ID-k (állatok)
        try:
            float(col_str)
            animal_cols.append(col)
        except ValueError:
            # Esetleg van '.1', '.2' stb. suffix
            base = col_str.split('.')[0]
            try:
                float(base)
                animal_cols.append(col)
            except ValueError:
                pass

    if not animal_cols:
        return {}

    group_stats = {}
    if param_col:
        for param, sub in df_post.groupby(param_col):
            animal_means = []
            for ac in animal_cols:
                vals = pd.to_numeric(sub[ac], errors='coerce').dropna()
                if len(vals) > 0:
                    animal_means.append(vals.mean())
            if len(animal_means) >= 2:
                arr = np.array(animal_means)
                group_stats[str(param).strip()] = (arr.mean(), arr.std(), len(arr))
    else:
        all_means = []
        for ac in animal_cols:
            vals = pd.to_numeric(df_post[ac], errors='coerce').dropna()
            if len(vals) > 0:
                all_means.append(vals.mean())
        if len(all_means) >= 2:
            arr = np.array(all_means)
            group_stats['overall'] = (arr.mean(), arr.std(), len(arr))

    return group_stats


def find_animal_sheet(xls, animal_id, group_code):
    """
    Megkeresi, melyik lapon szerepel az állat.
    group_code: pl. 'NF12', 'TR12', 'CR12'
    """
    candidate_sheets = [s for s in xls.sheet_names
                        if group_code in s and s not in ['Summary', 'Animal_metadata']]
    for sheet in candidate_sheets:
        animal_means, matched_col = get_animal_data_from_sheet(xls, sheet, animal_id)
        if matched_col is not None:
            return sheet, animal_means
    return None, None


def main():
    results = []

    for filename in ['animaldata_metabolism.xlsx', 'animaldata_temperature.xlsx']:
        filepath = BASE_DIR / filename
        if not filepath.exists():
            print(f"Nem található: {filename}")
            continue

        print(f"\n{'='*60}")
        print(f"Feldolgozás: {filename}")
        print(f"{'='*60}")

        xls = pd.ExcelFile(filepath)
        meta_df = load_metadata(filepath)

        # Megkeressük a metadata oszlopokat
        # Tipikus struktúra: No, ID, Group, Treatment, Comment_1, Comment_2...
        cols = list(meta_df.columns)
        print(f"  Metadata oszlopok: {cols}")

        # ID és megjegyzés oszlopok azonosítása
        id_col = None
        group_col = None
        comment_cols = []

        for col in cols:
            col_l = str(col).lower().strip()
            if col_l in ['id', 'animal id', 'animal_id', 'rat id', 'rat_id', 'azonosító']:
                id_col = col
            elif col_l in ['group', 'diet', 'csoport', 'diéta']:
                group_col = col
            elif col_l in ['comment', 'megjegyzés', 'note', 'notes', 'megj', 'remarks']:
                comment_cols.append(col)

        # Ha nem találtuk automatikusan, próbáljuk index alapján
        if id_col is None and len(cols) >= 2:
            id_col = cols[1]  # Általában 2. oszlop
        if group_col is None and len(cols) >= 3:
            group_col = cols[2]
        if not comment_cols and len(cols) >= 6:
            comment_cols = cols[5:]  # Utolsó oszlopok

        print(f"  ID oszlop: {id_col}, Csoport oszlop: {group_col}, Megjegyzés: {comment_cols}")

        # Előre kiszámítjuk a csoportstatisztikákat
        sheet_stats_cache = {}
        for sheet in xls.sheet_names:
            if sheet in ['Summary', 'Animal_metadata']:
                continue
            stats = get_group_stats(xls, sheet)
            if stats:
                sheet_stats_cache[sheet] = stats

        # Végigmegyünk az állatokon
        for _, row in meta_df.iterrows():
            animal_id = row.get(id_col)
            if pd.isna(animal_id) or not animal_id:
                continue

            animal_id_str = str(animal_id).strip()

            # Kommentek összegyűjtése
            all_comments = []
            for cc in comment_cols:
                val = row.get(cc)
                if pd.notna(val) and str(val).strip():
                    all_comments.append(str(val).strip())

            # Van-e kizárásra utaló komment?
            problem_found = False
            problem_reasons = []
            for comment in all_comments:
                found, kw = has_problem_keyword(comment)
                if found:
                    problem_found = True
                    problem_reasons.append(f"{kw}: '{comment}'")

            if not problem_found:
                continue  # Nincs probléma megjegyezve, kihagyjuk

            # Megkeressük az állat csoportját a lapok nevéből
            group_code = str(row.get(group_col, '')).strip() if group_col else ''

            # Próbáljuk megtalálni az állatot valamely lapon
            found_sheet = None
            animal_means = None

            for sheet in xls.sheet_names:
                if sheet in ['Summary', 'Animal_metadata']:
                    continue
                am, matched = get_animal_data_from_sheet(xls, sheet, animal_id)
                if matched is not None:
                    found_sheet = sheet
                    animal_means = am
                    break

            # Adatok kiértékelése
            if found_sheet is None or not animal_means:
                verdict = "NEM ÉRTÉKELHETŐ"
                z_info = "Nincs adat az állat lapján"
                max_z = None
            else:
                group_stats = sheet_stats_cache.get(found_sheet, {})
                z_scores = []
                z_details = []

                for param, animal_mean in animal_means.items():
                    if param in group_stats:
                        gmean, gstd, gn = group_stats[param]
                        if gstd > 0:
                            z = (animal_mean - gmean) / gstd
                            z_scores.append(abs(z))
                            if abs(z) > Z_THRESHOLD:
                                z_details.append(f"{param}: z={z:.2f} (állat={animal_mean:.3f}, csoport={gmean:.3f}±{gstd:.3f})")

                max_z = max(z_scores) if z_scores else None

                if max_z is not None and max_z > Z_THRESHOLD:
                    verdict = "KIZÁRANDÓ"
                    z_info = " | ".join(z_details) if z_details else f"max|z|={max_z:.2f}"
                else:
                    verdict = "MEGTARTHATÓ"
                    z_info = f"max|z|={max_z:.2f}" if max_z is not None else "Nincs kiugró érték"

            results.append({
                'Fájl': filename,
                'ID': animal_id_str,
                'Csoport/Lap': found_sheet or group_code or 'ismeretlen',
                'Komment': ' | '.join(problem_reasons[:2]),
                'max_z': round(max_z, 2) if max_z else None,
                'Kiugró paraméterek': z_info[:120] if verdict == "KIZÁRANDÓ" else '-',
                'Döntés': verdict,
            })

        xls.close()

    # Eredmény kiírás
    df_result = pd.DataFrame(results)

    print(f"\n{'='*70}")
    print("DÖNTÉSEK ÖSSZESÍTŐJE")
    print(f"{'='*70}\n")

    for verdict, group in df_result.groupby('Döntés'):
        emoji = "🔴" if verdict == "KIZÁRANDÓ" else ("🟢" if verdict == "MEGTARTHATÓ" else "⚫")
        print(f"{emoji}  {verdict}: {len(group)} állat")
        for _, r in group.iterrows():
            print(f"      ID={r['ID']:>8} | Lap={r['Csoport/Lap']:>20} | z={str(r['max_z']):>6} | Komment: {r['Komment'][:50]}")
        print()

    # CSV mentés
    out_csv = BASE_DIR / "cross_validated_exclusions.csv"
    df_result.to_csv(out_csv, index=False, encoding='utf-8-sig')
    print(f"✅  Mentve: {out_csv}")

    # Markdown összefoglaló
    out_md = BASE_DIR / "cross_validated_exclusions.md"
    with open(out_md, 'w', encoding='utf-8') as f:
        f.write("# Keresztvalidált kizárási lista\n\n")
        f.write("> Csak azok az állatok kerülnek kizárásra, amelyeknél **a komment ÉS az adat is problémás** (|z| > 2.0).\n\n")
        f.write(f"Z-score küszöb: **{Z_THRESHOLD}** | Post-injekciós adatok alapján (t ≥ 0 min)\n\n")

        for verdict in ["KIZÁRANDÓ", "MEGTARTHATÓ", "NEM ÉRTÉKELHETŐ"]:
            sub = df_result[df_result['Döntés'] == verdict]
            if sub.empty:
                continue
            icon = "🔴" if verdict == "KIZÁRANDÓ" else ("🟢" if verdict == "MEGTARTHATÓ" else "⚫")
            f.write(f"## {icon} {verdict} ({len(sub)} állat)\n\n")
            f.write("| ID | Csoport/Lap | max |z| | Kiugró paraméterek | Komment |\n")
            f.write("|----|------------|--------|---------------------|--------|\n")
            for _, r in sub.iterrows():
                f.write(f"| {r['ID']} | {r['Csoport/Lap']} | {r['max_z']} | {r['Kiugró paraméterek'][:60]} | {r['Komment'][:60]} |\n")
            f.write("\n")

    print(f"✅  Markdown: {out_md}")


if __name__ == '__main__':
    main()
