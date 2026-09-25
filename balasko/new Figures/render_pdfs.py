import fitz
from pathlib import Path

pdf_dir = Path(r"C:\Users\shuba\Desktop\Researcher - Dóri\balasko\new Figures")
out_dir = pdf_dir / "rendered_preview"
out_dir.mkdir(exist_ok=True)

for pdf_file in pdf_dir.glob("*.pdf"):
    doc = fitz.open(pdf_file)
    print(f"File: {pdf_file.name}, pages: {len(doc)}")
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=150)
        img_path = out_dir / f"{pdf_file.stem}_p{i+1}.png"
        pix.save(img_path)
        print(f"  Saved: {img_path.name}")
        # print some text from the page
        text = page.get_text()
        first_lines = [line.strip() for line in text.splitlines() if line.strip()][:15]
        clean_preview = [line.encode('ascii', 'backslashreplace').decode('ascii') for line in first_lines]
        print(f"  Text preview: {clean_preview}")
