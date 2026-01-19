#!/usr/bin/env python3
"""
PDF Text Extractor
Extracts text from large PDFs and saves to readable text files
"""

import sys
from pypdf import PdfReader
import os

def extract_pdf_text(pdf_path, output_path=None, max_pages=None):
    """
    Extract text from a PDF file.

    Args:
        pdf_path: Path to the PDF file
        output_path: Optional path to save extracted text (default: same name as PDF but .txt)
        max_pages: Optional limit on number of pages to extract (default: all)
    """
    try:
        print(f"Opening PDF: {pdf_path}")
        reader = PdfReader(pdf_path)

        total_pages = len(reader.pages)
        print(f"Total pages: {total_pages}")

        # Determine how many pages to extract
        pages_to_extract = min(max_pages, total_pages) if max_pages else total_pages
        print(f"Extracting {pages_to_extract} pages...")

        # Extract text from each page
        text_content = []
        for i in range(pages_to_extract):
            page = reader.pages[i]
            text = page.extract_text()
            text_content.append(f"\n{'='*80}\n")
            text_content.append(f"PAGE {i+1}\n")
            text_content.append(f"{'='*80}\n\n")
            text_content.append(text)

            if (i + 1) % 10 == 0:
                print(f"  Processed {i+1}/{pages_to_extract} pages...")

        full_text = "".join(text_content)

        # Determine output path
        if output_path is None:
            output_path = pdf_path.rsplit('.', 1)[0] + '.txt'

        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)

        print(f"\n[SUCCESS]")
        print(f"   Extracted {pages_to_extract} pages")
        print(f"   Total characters: {len(full_text):,}")
        print(f"   Saved to: {output_path}")

        # Show file size
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"   File size: {size_mb:.2f} MB")

        return output_path

    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def extract_table_of_contents(pdf_path):
    """Extract table of contents / outline from PDF"""
    try:
        reader = PdfReader(pdf_path)

        if reader.outline:
            print("\n[TABLE OF CONTENTS]")
            print("="*80)
            for item in reader.outline:
                if isinstance(item, list):
                    for subitem in item:
                        print(f"  - {subitem.title}")
                else:
                    print(f"- {item.title}")
            print("="*80)
        else:
            print("[WARNING] No table of contents found in PDF")

    except Exception as e:
        print(f"[ERROR] Error extracting TOC: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python extract_pdf.py <pdf_file> [max_pages] [output_file]")
        print("\nExamples:")
        print('  python extract_pdf.py "e:\\Downloads\\complete\\Python.Complete.Manual..26th.Edition.2025\\Python Complete Manual – 26th Edition, 2025.pdf"')
        print('  python extract_pdf.py "manual.pdf" 50')
        print('  python extract_pdf.py "manual.pdf" 100 "output.txt"')
        sys.exit(1)

    pdf_path = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else None
    output_path = sys.argv[3] if len(sys.argv) > 3 else None

    # First show table of contents if available
    extract_table_of_contents(pdf_path)

    # Then extract text
    print()
    extract_pdf_text(pdf_path, output_path, max_pages)
