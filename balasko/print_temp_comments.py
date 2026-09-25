import pandas as pd
from pathlib import Path

base_dir = Path(r"C:\Users\shuba\Desktop\Researcher - Dóri\balasko")
xl_t = pd.ExcelFile(base_dir / "animaldata_temperature.xlsx")
df_t = xl_t.parse("Animal_metadata")

comm_t = df_t[df_t['Comment'].notna() & (df_t['Comment'].astype(str).str.strip() != '')]
print(f"Total temp comments: {len(comm_t)}")
for idx, r in comm_t.iterrows():
    aid = r.get('Animal_ID')
    grp = r.get('Group')
    trt = r.get('Treatment')
    comm = str(r.get('Comment')).strip()
    date = str(r.get('Date')).split()[0]
    print(f"row={idx:3d} | Date: {date} | ID: {aid} | Grp: {grp} | Trt: {trt} | Comment: {comm}")
