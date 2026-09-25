import pandas as pd
import numpy as np
from pathlib import Path

base_dir = Path(r"C:\Users\shuba\Desktop\Researcher - Dóri\balasko")

for fn in ["animaldata_temperature.xlsx", "animaldata_metabolism.xlsx"]:
    filepath = base_dir / fn
    xl = pd.ExcelFile(filepath)
    df_meta = xl.parse("Animal_metadata")
    print(f"==================================================")
    print(f"FILE: {fn}")
    print(f"Metadata total rows: {len(df_meta)}")
    comments = df_meta[df_meta["Comment"].notna() & (df_meta["Comment"].astype(str).str.strip() != "")]
    print(f"Rows with non-empty comments: {len(comments)}")
    for idx, r in comments.iterrows():
        aid = r.get("Animal_ID")
        grp = r.get("Group")
        trt = r.get("Treatment")
        comm = str(r.get("Comment")).strip()
        print(f"  ID: {aid} | Grp: {grp} | Trt: {trt} | Comment: {comm}")

    print("\nSHEETS and their animal columns:")
    for s in xl.sheet_names:
        if s not in ["Summary", "Animal_metadata"]:
            df = xl.parse(s)
            fixed_cols = ['MEAN', 'SEM', 'n', 'Parameter', 'Time (min)']
            animals = [c for c in df.columns if c not in fixed_cols]
            print(f"  [{s}] (n={len(animals)}): {animals}")
    print("\n")
