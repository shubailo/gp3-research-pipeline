"""
Kizárásra jelölt állatok azonosítása az Excel táblázatokban.
Keres minden olyan megjegyzést (comment/note), ami kizárásra utaló szót tartalmaz.
"""

import openpyxl
import pandas as pd
from pathlib import Path
import re

BASE_DIR = Path(__file__).parent

# Kizárásra utaló kulcsszavak (magyar/latin/rövidítések)
EXCLUSION_KEYWORDS = [
    # technikai problémák
    "szétcsúszott", "szétrágta", "lyukas", "lyuk", "nehezen megy be",
    "kanül", "kanál",
    # injekció problémák
    "pg-", "pg +", "pg+", "pg nincs", "nem kap pg", "nem kap pg-t",
    "beszaladt", "visszacsúszott", "visszafordulva",
    # fiziológiai problémák
    "magas tc", "alacsony tc", "véres", "gennyes",
    # egyéb
    "ül", "fürdetés", "oxy nincs", "oxigén nincs",
]

def cell_has_exclusion_keyword(cell_value):
    if not cell_value:
        return False, None
    val = str(cell_value).lower().strip()
    for kw in EXCLUSION_KEYWORDS:
        if kw.lower() in val:
            return True, kw
    return False, None

def analyze_excel(filepath):
    print(f"\n{'='*70}")
    print(f"Elemzés: {filepath.name}")
    print(f"{'='*70}")
    
    try:
        wb = openpyxl.load_workbook(filepath, data_only=True)
    except Exception as e:
        print(f"  HIBA: {e}")
        return []
    
    exclusions = []
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        print(f"\n  --- Lap: {sheet_name} ({ws.max_row} sor x {ws.max_column} oszlop) ---")
        
        # Olvassuk be az összes cellát és nézzük a kommenteket + tartalmakat
        sheet_exclusions = []
        
        # 1. Keressük a fejléc sort (általában az első vagy második sor ID-val)
        header_row = None
        id_col = None
        comment_col = None
        
        for row_idx in range(1, min(10, ws.max_row + 1)):
            for col_idx in range(1, min(20, ws.max_column + 1)):
                cell = ws.cell(row=row_idx, column=col_idx)
                if cell.value and isinstance(cell.value, str):
                    val_lower = cell.value.lower().strip()
                    if val_lower in ['id', 'animal id', 'animal_id', 'azonosító', 'rat id', 'rat_id']:
                        header_row = row_idx
                        id_col = col_idx
                    if val_lower in ['comment', 'megjegyzés', 'note', 'notes', 'remarks', 'megj']:
                        comment_col = col_idx
        
        if header_row:
            print(f"    Fejléc sor: {header_row}, ID oszlop: {id_col}, Megjegyzés oszlop: {comment_col}")
        
        # 2. Szkennel minden cellát kizárásra utaló szövegért
        for row in ws.iter_rows():
            for cell in row:
                found, kw = cell_has_exclusion_keyword(cell.value)
                if found:
                    # Próbáljuk megtalálni az ID-t ugyanabban a sorban
                    row_id = None
                    if id_col:
                        row_id = ws.cell(row=cell.row, column=id_col).value
                    
                    # Ha nincs dedikált ID oszlop, vesszük az első oszlopból
                    if not row_id:
                        row_id = ws.cell(row=cell.row, column=1).value
                    
                    entry = {
                        'sheet': sheet_name,
                        'sor': cell.row,
                        'id': row_id,
                        'cella': cell.coordinate,
                        'tartalom': str(cell.value)[:80],
                        'kulcsszó': kw,
                    }
                    sheet_exclusions.append(entry)
                    exclusions.append(entry)
        
        # 3. Ellenőrizzük a cellakommenteket (openpyxl comment property)
        # Újra betöltjük kommentekkel (data_only=False)
        wb2 = openpyxl.load_workbook(filepath, data_only=False)
        ws2 = wb2[sheet_name]
        for row in ws2.iter_rows():
            for cell in row:
                if cell.comment:
                    comment_text = cell.comment.text if cell.comment.text else ""
                    found, kw = cell_has_exclusion_keyword(comment_text)
                    if found:
                        row_id = ws2.cell(row=cell.row, column=1).value
                        entry = {
                            'sheet': sheet_name,
                            'sor': cell.row,
                            'id': row_id,
                            'cella': cell.coordinate,
                            'tartalom': f"[COMMENT] {comment_text[:80]}",
                            'kulcsszó': kw,
                        }
                        # Ne duplázzuk
                        if entry not in exclusions:
                            sheet_exclusions.append(entry)
                            exclusions.append(entry)
        wb2.close()
        
        if sheet_exclusions:
            print(f"    ⚠️  {len(sheet_exclusions)} kizárásra utaló bejegyzés:")
            seen = set()
            for e in sheet_exclusions:
                key = (e['id'], e['sheet'])
                if key not in seen:
                    seen.add(key)
                    print(f"       ID={e['id']:>10} | Sor={e['sor']:>4} | Kulcsszó='{e['kulcsszó']}' | Szöveg: {e['tartalom'][:60]}")
        else:
            print(f"    ✓  Nincs kizárásra utaló megjegyzés")
    
    wb.close()
    return exclusions

def main():
    files = [
        BASE_DIR / "animaldata_metabolism.xlsx",
        BASE_DIR / "animaldata_temperature.xlsx",
    ]
    
    all_exclusions = []
    
    for f in files:
        if f.exists():
            excl = analyze_excel(f)
            all_exclusions.extend(excl)
        else:
            print(f"⚠️  Fájl nem található: {f}")
    
    # Összesítő
    print(f"\n{'='*70}")
    print(f"ÖSSZESÍTŐ KIZÁRÁSI LISTA")
    print(f"{'='*70}")
    
    if not all_exclusions:
        print("Nem találtam kizárásra utaló megjegyzést.")
        return
    
    # Csoportosítva ID szerint
    by_id = {}
    for e in all_exclusions:
        key = str(e['id'])
        if key not in by_id:
            by_id[key] = []
        by_id[key].append(e)
    
    print(f"\nÖsszes egyedi állat-ID kizárásra jelölve: {len(by_id)}")
    print()
    for animal_id, entries in sorted(by_id.items()):
        sheets = list(set(e['sheet'] for e in entries))
        keywords = list(set(e['kulcsszó'] for e in entries))
        notes = list(set(e['tartalom'] for e in entries))
        print(f"  🔴 ID: {animal_id}")
        print(f"       Lapok: {', '.join(sheets)}")
        print(f"       Okok:  {', '.join(keywords)}")
        for n in notes[:3]:
            print(f"       Szöveg: {n[:70]}")
        print()
    
    # Mentés CSV-be
    out = BASE_DIR / "kizarasok_osszesito.csv"
    df = pd.DataFrame(all_exclusions)
    df.to_csv(out, index=False, encoding='utf-8-sig')
    print(f"✅  Részletes lista mentve: {out}")

if __name__ == "__main__":
    main()
