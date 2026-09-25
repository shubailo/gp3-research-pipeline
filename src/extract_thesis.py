import pdfplumber

pdf_path = r"c:\Users\shuba\Desktop\Researcher - Dóri\garami.andras_142_23_doktori_mu.pdf"
output_path = r"c:\Users\shuba\AppData\Local\Temp\garami_thesis.txt"

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    with open(output_path, "w", encoding="utf-8") as f:
        for i, page in enumerate(pdf.pages):
            if i % 10 == 0:
                print(f"Processing page {i}...")
            text = page.extract_text()
            if text:
                f.write(text + "\n\n")

print(f"Extracted text to {output_path}")
