import pandas as pd
from pathlib import Path

base_dir = Path(r"C:\Users\shuba\Desktop\Researcher - Dóri\balasko")
xl_t = pd.ExcelFile(base_dir / "animaldata_temperature.xlsx")
df_t = xl_t.parse("Animal_metadata")
xl_m = pd.ExcelFile(base_dir / "animaldata_metabolism.xlsx")
df_m = xl_m.parse("Animal_metadata")

print("Temperature metadata rows:", len(df_t))
print("Metabolism metadata rows:", len(df_m))

comm_t = df_t[df_t['Comment'].notna() & (df_t['Comment'].astype(str).str.strip() != '')]
comm_m = df_m[df_m['Comment'].notna() & (df_m['Comment'].astype(str).str.strip() != '')]
print("Temp non-empty comments count:", len(comm_t))
print("Metab non-empty comments count:", len(comm_m))

print("\n--- ALL TEMP METADATA WITH COMMENTS ---")
for idx, r in comm_t.iterrows():
    aid = r.get('Animal_ID')
    grp = r.get('Group')
    trt = r.get('Treatment')
    comm = str(r.get('Comment')).strip()
    print(f"  [TEMP] ID: {aid} (Grp: {grp}, Trt: {trt}) -> Comment: {comm}")

print("\n--- ALL METAB METADATA WITH COMMENTS ---")
for idx, r in comm_m.iterrows():
    aid = r.get('Animal_ID')
    grp = r.get('Group')
    trt = r.get('Treatment')
    comm = str(r.get('Comment')).strip()
    print(f"  [METAB] ID: {aid} (Grp: {grp}, Trt: {trt}) -> Comment: {comm}")
