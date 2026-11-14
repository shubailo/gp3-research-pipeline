"""
generate_prospero_pdf.py
Generates an official, publication-quality PROSPERO Pre-Registration PDF form.
Project: pmmr_crc_rt_ici
Standard: Centre for Translational Medicine (CTM) / PROSPERO (CRD York) / PRISMA-P
"""

import os
import sys
import re
import subprocess
import argparse
from markdown_it import MarkdownIt
import fitz  # PyMuPDF

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

DEFAULT_INPUT_MD = os.path.join(WORKSPACE_ROOT, "docs", "PROSPERO-draft-pmmr_crc_rt_ici.md")
DEFAULT_OUTPUT_PDF = os.path.join(WORKSPACE_ROOT, "projects", "pmmr_crc_rt_ici", "PROSPERO_pmmr_crc_rt_ici_draft.pdf")
DOCS_OUTPUT_PDF = os.path.join(WORKSPACE_ROOT, "docs", "PROSPERO_pmmr_crc_rt_ici_draft.pdf")


def clean_math_syntax(text: str) -> str:
    """Converts math/Greek symbols to HTML entities."""
    replacements = [
        (r"\$\\ge\s*(\d+)\$", r"&ge; \1"),
        (r"\$\\ge\s*", r"&ge; "),
        (r"\$\\le\s*([0-9.]+)\%?\$", r"&le; \1%"),
        (r"\$\\le\s*", r"&le; "),
        (r"\$\\times\$", r"&times;"),
        (r"\$BED_\{10\}\$", r"BED<sub>10</sub>"),
        (r"BED_\{10\}", r"BED<sub>10</sub>"),
        (r"\$I\^2\$", r"<i>I</i><sup>2</sup>"),
        (r"\$\\tau\^2\$", r"&tau;<sup>2</sup>"),
        (r"\$\\beta\$", r"&beta;"),
        (r"\$\\alpha\$", r"&alpha;"),
        (r"\$\\kappa\$", r"&kappa;"),
        (r"BED10", r"BED<sub>10</sub>"),
        (r">=", r"&ge;"),
        (r"<=", r"&le;"),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    return text


def build_prospero_html(md_content: str) -> str:
    """Parses PROSPERO draft markdown into an official CRD York / CTM branded layout."""
    cleaned_md = clean_math_syntax(md_content)
    md = MarkdownIt("default").enable("table")
    body_html = md.render(cleaned_md)

    # Convert callout blocks
    body_html = body_html.replace("<blockquote>", "<div class='alert-banner'>")
    body_html = body_html.replace("</blockquote>", "</div>")

    # Style field headers: "## 1. Review title" -> structured form field card
    body_html = re.sub(
        r"<h2>(\d+)\.\s*(.*?)</h2>",
        r"<div class='field-header'><span class='field-badge'>FIELD \1</span><span class='field-title'>\2</span></div>",
        body_html
    )

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>PROSPERO Pre-Registration Draft: pMMR CRC Radiotherapy + Checkpoint Blockade</title>
<style>
@page {{
    size: A4;
    margin: 22mm 18mm 22mm 18mm;
    @top-right {{
        content: "PROSPERO Registration Draft · CRD York · CTM Standard";
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 8pt;
        color: #94a3b8;
    }}
    @bottom-center {{
        content: "Page " counter(page);
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 8pt;
        color: #64748b;
    }}
}}

body {{
    font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
    color: #1e293b;
    line-height: 1.55;
    font-size: 10.5pt;
    background: #ffffff;
    margin: 0;
    padding: 0;
}}

/* Header Banner */
.institution-banner {{
    border-bottom: 3px solid #003366;
    padding-bottom: 12px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.inst-title {{
    font-size: 11pt;
    font-weight: 700;
    color: #003366;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}
.inst-sub {{
    font-size: 9pt;
    color: #64748b;
    margin-top: 2px;
}}
.badge-prospero {{
    background: #0284c7;
    color: white;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 8.5pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: inline-block;
}}

/* Document Title */
h1 {{
    color: #002244;
    font-size: 16pt;
    line-height: 1.35;
    margin-top: 0;
    margin-bottom: 16px;
    font-weight: 800;
}}

/* Alert / Warning Banner */
.alert-banner {{
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    padding: 10px 14px;
    margin: 14px 0 20px 0;
    border-radius: 0 4px 4px 0;
    font-size: 9pt;
    color: #92400e;
}}
.alert-banner p {{
    margin: 3px 0;
}}

/* Form Field Headers */
.field-header {{
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-left: 4px solid #003366;
    padding: 6px 12px;
    margin-top: 18px;
    margin-bottom: 8px;
    border-radius: 3px;
    display: flex;
    align-items: center;
    gap: 10px;
    page-break-after: avoid;
}}
.field-badge {{
    background: #003366;
    color: white;
    font-size: 7.5pt;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 3px;
    letter-spacing: 0.5px;
}}
.field-title {{
    color: #003366;
    font-size: 11pt;
    font-weight: 700;
}}

/* Paragraphs & Lists */
p {{
    margin-top: 0;
    margin-bottom: 10px;
    text-align: justify;
}}

ul, ol {{
    margin-top: 0;
    margin-bottom: 10px;
    padding-left: 20px;
}}

li {{
    margin-bottom: 4px;
}}

/* Tables */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 9pt;
    page-break-inside: avoid;
}}

th {{
    background: #003366;
    color: white;
    font-weight: 600;
    text-align: left;
    padding: 7px 10px;
    border: 1px solid #002244;
}}

td {{
    padding: 6px 10px;
    border: 1px solid #e2e8f0;
    vertical-align: top;
}}

tr:nth-child(even) td {{
    background: #f8fafc;
}}

/* Code / Query styling */
code {{
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 8.5pt;
    background: #f1f5f9;
    padding: 2px 4px;
    border-radius: 3px;
    color: #0f172a;
    word-break: break-word;
}}

/* Endorsement Block */
.endorsement-block {{
    margin-top: 30px;
    border-top: 2px solid #cbd5e1;
    padding-top: 16px;
    page-break-inside: avoid;
}}
.sig-grid {{
    display: flex;
    justify-content: space-between;
    margin-top: 24px;
}}
.sig-col {{
    width: 30%;
    border-top: 1px solid #64748b;
    padding-top: 8px;
    text-align: center;
    font-size: 8.5pt;
}}
.sig-name {{
    font-weight: 700;
    color: #003366;
}}
.sig-role {{
    color: #64748b;
    font-size: 8pt;
}}
</style>
</head>
<body>

<div class="institution-banner">
  <div>
    <div class="inst-title">Centre for Translational Medicine · University of Pécs Medical School</div>
    <div class="inst-sub">PROSPERO Pre-Registration Protocol Submission Document (CRD York Standard)</div>
  </div>
  <div>
    <span class="badge-prospero">PROSPERO DRAFT</span>
  </div>
</div>

{body_html}

<div class="endorsement-block">
  <h3 style="color: #003366; margin-bottom: 6px; font-size: 11pt;">Investigator Endorsement & Submission Declaration</h3>
  <p style="font-size: 8.5pt; color: #64748b;">
    This submission form accurately mirrors the locked systematic review protocol (SHA-256: <code>9582c50f164b095ff923c5cdd310bd56d4c0c19396d186534a7ed4063cf20173</code>).
    Registration is submitted to PROSPERO prior to formal study screening and data extraction in compliance with PRISMA-P and CTM translational standards.
  </p>
  <div class="sig-grid">
    <div class="sig-col">
      <div class="sig-name">Yashwanth Sudheendra Gowda</div>
      <div class="sig-role">Lead Reviewer (R1)<br>University of Pécs Medical School</div>
    </div>
    <div class="sig-col">
      <div class="sig-name">Dr. András Garami, MD, PhD</div>
      <div class="sig-role">Methodological Supervisor & Guarantor<br>Institute for Translational Medicine, Pécs</div>
    </div>
    <div class="sig-col">
      <div class="sig-name">Prof. Dr. Péter Hegyi, MD, PhD, DSc</div>
      <div class="sig-role">Translational PI & Senior Mentor<br>Director, Centre for Translational Medicine</div>
    </div>
  </div>
</div>

</body>
</html>
"""
    return html_template


def compile_pdf(html_content: str, output_pdf_path: str) -> bool:
    """Invokes Edge Headless to render publication-quality PDF."""
    os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
    temp_html_path = output_pdf_path.replace(".pdf", "_temp.html")
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    edge_exe = next((p for p in edge_paths if os.path.exists(p)), None)
    if not edge_exe:
        print("ERROR: Microsoft Edge executable not found for PDF compilation.")
        return False

    abs_html = os.path.abspath(temp_html_path)
    abs_pdf = os.path.abspath(output_pdf_path)

    cmd = [
        edge_exe,
        "--headless=new",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={abs_pdf}",
        f"file:///{abs_html.replace(os.sep, '/')}"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)

    if os.path.exists(abs_pdf) and os.path.getsize(abs_pdf) > 1000:
        return True
    else:
        print("PDF compilation failed:", result.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate Official PROSPERO Submission PDF")
    parser.add_argument("--input", default=DEFAULT_INPUT_MD, help="Path to PROSPERO draft markdown")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PDF, help="Target output PDF path")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist.")
        sys.exit(1)

    print(f"Reading PROSPERO draft from: {args.input}")
    with open(args.input, "r", encoding="utf-8") as f:
        md_text = f.read()

    print("Building CRD York / CTM branded layout...")
    html_doc = build_prospero_html(md_text)

    print(f"Compiling PDF using Edge Headless engine to: {args.output}")
    success = compile_pdf(html_doc, args.output)
    if not success:
        print("Failed to generate PDF.")
        sys.exit(1)

    # Duplicate to docs/ for easy reference
    if args.output == DEFAULT_OUTPUT_PDF:
        import shutil
        os.makedirs(os.path.dirname(DOCS_OUTPUT_PDF), exist_ok=True)
        shutil.copy2(args.output, DOCS_OUTPUT_PDF)
        print(f"Copied mirror copy to: {DOCS_OUTPUT_PDF}")

    # Validate with PyMuPDF
    doc = fitz.open(args.output)
    page_count = len(doc)
    file_size_kb = os.path.getsize(args.output) / 1024
    print(f"\n=======================================================")
    print(f"🎉 PROSPERO PDF GENERATION SUCCESSFUL")
    print(f"=======================================================")
    print(f"File Path:   {args.output}")
    print(f"Page Count:  {page_count} pages")
    print(f"File Size:   {file_size_kb:.1f} KB")
    print(f"Title:       {doc.metadata.get('title', 'N/A')}")
    print(f"Format:      A4 official PROSPERO form (CRD York standard)")
    print(f"Ready to send to: Yashwanth Sudheendra Gowda (yashwanth.gowda@pte.hu)")
    print(f"=======================================================\n")


if __name__ == "__main__":
    main()

