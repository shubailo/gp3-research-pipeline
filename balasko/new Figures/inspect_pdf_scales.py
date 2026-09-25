import fitz
from pathlib import Path

pdf_dir = Path(r"C:\Users\shuba\Desktop\Researcher - Dóri\balasko\new Figures")

for f in sorted(pdf_dir.glob("*.pdf")):
    doc = fitz.open(f)
    print(f"==================================================")
    print(f"FILE: {f.name}")
    for i in range(len(doc)):
        page = doc[i]
        text_lines = [l.strip() for l in page.get_text().splitlines() if l.strip()]
        # find labels
        labels = [l for l in text_lines if any(k in l for k in ['Tc', 'VO2', 'HLI', 'T ('])]
        ticks = [l for l in text_lines if l.replace('.', '').replace('-', '').replace('\u2212', '').isdigit()]
        safe_labels = [l.encode('ascii', 'backslashreplace').decode('ascii') for l in labels]
        safe_ticks = [l.encode('ascii', 'backslashreplace').decode('ascii') for l in ticks[:20]]
        print(f"  Page {i+1} labels: {safe_labels}")
        print(f"  Page {i+1} numeric ticks: {safe_ticks}")
