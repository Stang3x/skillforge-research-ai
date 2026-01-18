#!/usr/bin/env python3
"""Test export functionality"""
import json
from pathlib import Path
from datetime import datetime

try:
    from fpdf import FPDF
    print("fpdf2: OK")
except ImportError:
    print("fpdf2: NOT INSTALLED")
    exit(1)

DATA_DIR = Path(__file__).parent / "research_data"
EXPORTS_DIR = DATA_DIR / "exports"
EXPORTS_DIR.mkdir(exist_ok=True)

# Read a markdown file and convert to PDF
md_files = list(EXPORTS_DIR.glob("*.md"))
if not md_files:
    print("No markdown files to convert")
    exit(1)

md_path = md_files[0]
print(f"Converting: {md_path.name}")

with open(md_path, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Create PDF
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.set_margins(20, 20, 20)
pdf.add_page()
pdf.set_font('Helvetica', size=10)

def safe_text(text):
    """Make text safe for PDF"""
    return ''.join(c if ord(c) < 256 else '?' for c in text.replace('\r', ''))

def write_text(text, size=10, bold=False, color=(0, 0, 0), indent=0):
    """Write text with error handling"""
    try:
        pdf.set_font('Helvetica', 'B' if bold else '', size)
        pdf.set_text_color(*color)
        if indent:
            pdf.cell(indent, size * 0.5, '')
        pdf.multi_cell(0, size * 0.5, safe_text(text))
    except Exception as e:
        print(f"  Skip line: {e}")

for line in md_content.split('\n'):
    line = line.rstrip()
    if not line:
        pdf.ln(2)
    elif line.startswith('# '):
        write_text(line[2:], 16, True, (44, 62, 80))
        pdf.ln(3)
    elif line.startswith('## '):
        write_text(line[3:], 13, True, (52, 73, 94))
        pdf.ln(2)
    elif line.startswith('### '):
        write_text(line[4:], 11, True, (100, 100, 100))
    elif line.startswith('---'):
        pdf.ln(2)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(2)
    elif line.startswith('> '):
        write_text(line[2:], 9, False, (100, 100, 100), 5)
    elif line.startswith('- ') or line.startswith('* '):
        write_text('- ' + line[2:], 10, False, (0, 0, 0), 5)
    elif line.startswith('**'):
        write_text(line.replace('**', ''), 10, True)
    elif line.startswith('```'):
        continue
    else:
        write_text(line, 10)

pdf_path = EXPORTS_DIR / f"test_{datetime.now().strftime('%H%M%S')}.pdf"
pdf.output(str(pdf_path))
print(f"PDF created: {pdf_path}")
print("SUCCESS!")
