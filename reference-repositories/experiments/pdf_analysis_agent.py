#!/usr/bin/env python3
"""
PDF Analysis Agent
Analyzes large PDFs chunk by chunk to determine relevance for agentic workflows
"""

import os
import sys
from pypdf import PdfReader
from anthropic import Anthropic
import json

# Initialize Claude
client = Anthropic()

def extract_chunk(pdf_path, start_page, end_page):
    """Extract text from a specific page range"""
    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)

        # Adjust end_page if it exceeds total pages
        actual_end = min(end_page, total_pages)

        text_content = []
        for i in range(start_page - 1, actual_end):  # Convert to 0-indexed
            page = reader.pages[i]
            text = page.extract_text()
            text_content.append(f"\n--- PAGE {i+1} ---\n")
            text_content.append(text)

        return "".join(text_content), total_pages
    except Exception as e:
        return None, str(e)

def analyze_chunk_with_claude(chunk_text, chunk_number, pdf_name, analysis_context=""):
    """Send a chunk to Claude for analysis"""

    prompt = f"""You are analyzing PDF: "{pdf_name}"
This is chunk #{chunk_number}.

{analysis_context}

Here is the text from this chunk:

{chunk_text}

Analyze this content and answer:
1. **Relevance Score (0-10)**: How relevant is this content for learning agentic workflows (AI agents, LLMs, automation, agent architectures)?
2. **Key Topics**: What topics are covered?
3. **Specific Findings**: Any mentions of: agents, LLMs, Claude, GPT, automation, workflows, tools, memory, state management, multi-agent systems?
4. **Recommendation**: Should we continue reading this PDF, skip it, or focus on specific sections?
5. **Useful Sections**: If relevant, which page ranges look most valuable?

Return your analysis in JSON format:
{{
  "relevance_score": <0-10>,
  "key_topics": ["topic1", "topic2"],
  "specific_findings": "description of any agent-related content",
  "recommendation": "continue/skip/focus on sections",
  "useful_page_ranges": ["1-20", "45-67"] or null,
  "reasoning": "why this is or isn't relevant"
}}
"""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        analysis_text = response.content[0].text

        # Extract JSON from potential markdown code blocks
        if "```json" in analysis_text:
            analysis_text = analysis_text.split("```json")[1].split("```")[0]
        elif "```" in analysis_text:
            analysis_text = analysis_text.split("```")[1].split("```")[0]

        return json.loads(analysis_text.strip())

    except Exception as e:
        return {
            "relevance_score": 0,
            "key_topics": [],
            "specific_findings": f"Error: {e}",
            "recommendation": "error",
            "useful_page_ranges": None,
            "reasoning": f"Failed to analyze: {e}"
        }

def analyze_pdf_progressively(pdf_path, pages_per_chunk=30, max_chunks=None):
    """Analyze a PDF in chunks, stopping early if not relevant"""

    print(f"\n{'='*80}")
    print(f"ANALYZING PDF: {os.path.basename(pdf_path)}")
    print(f"{'='*80}\n")

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    print(f"Total pages: {total_pages}")
    print(f"Pages per chunk: {pages_per_chunk}")
    print(f"Strategy: Analyze progressively, stop if not relevant\n")

    all_analyses = []
    current_page = 1
    chunk_number = 1
    should_continue = True

    while current_page <= total_pages and should_continue:
        # Respect max_chunks limit if set
        if max_chunks and chunk_number > max_chunks:
            print(f"\n[INFO] Reached max chunks limit ({max_chunks})")
            break

        end_page = min(current_page + pages_per_chunk - 1, total_pages)

        print(f"\n--- CHUNK {chunk_number}: Pages {current_page}-{end_page} ---")

        # Extract chunk
        chunk_text, _ = extract_chunk(pdf_path, current_page, end_page)

        if not chunk_text or len(chunk_text.strip()) < 100:
            print("[WARNING] Chunk has minimal text (likely images). Skipping...")
            current_page = end_page + 1
            chunk_number += 1
            continue

        print(f"Extracted {len(chunk_text)} characters")
        print("Sending to Claude for analysis...")

        # Build context from previous analyses
        context = ""
        if all_analyses:
            avg_score = sum(a["relevance_score"] for a in all_analyses) / len(all_analyses)
            context = f"Previous chunks had average relevance score: {avg_score:.1f}/10"

        # Analyze with Claude
        analysis = analyze_chunk_with_claude(
            chunk_text,
            chunk_number,
            os.path.basename(pdf_path),
            context
        )

        all_analyses.append(analysis)

        # Display results
        print(f"\n  Relevance Score: {analysis['relevance_score']}/10")
        print(f"  Key Topics: {', '.join(analysis['key_topics'])}")
        print(f"  Recommendation: {analysis['recommendation']}")
        print(f"  Reasoning: {analysis['reasoning'][:150]}...")

        # Decide whether to continue
        if analysis["recommendation"] == "skip":
            print("\n[DECISION] Claude recommends skipping this PDF. Stopping analysis.")
            should_continue = False
        elif analysis["relevance_score"] < 3 and chunk_number >= 2:
            print("\n[DECISION] Low relevance score after multiple chunks. Stopping analysis.")
            should_continue = False
        elif analysis["recommendation"] == "focus on sections" and analysis["useful_page_ranges"]:
            print(f"\n[DECISION] Claude recommends focusing on specific sections: {analysis['useful_page_ranges']}")
            # Could implement targeted extraction here
            should_continue = False

        current_page = end_page + 1
        chunk_number += 1

    # Generate final report
    print(f"\n{'='*80}")
    print("FINAL ANALYSIS")
    print(f"{'='*80}\n")

    if not all_analyses:
        print("No text content found - PDF is likely all images")
        return {
            "pdf_name": os.path.basename(pdf_path),
            "total_pages": total_pages,
            "chunks_analyzed": 0,
            "overall_relevance": 0,
            "verdict": "NOT RELEVANT - Image-only PDF",
            "recommendations": []
        }

    avg_relevance = sum(a["relevance_score"] for a in all_analyses) / len(all_analyses)
    all_topics = []
    for a in all_analyses:
        all_topics.extend(a["key_topics"])
    unique_topics = list(set(all_topics))

    # Determine verdict
    if avg_relevance >= 7:
        verdict = "HIGHLY RELEVANT - Recommended for deep study"
    elif avg_relevance >= 5:
        verdict = "MODERATELY RELEVANT - Review specific sections"
    elif avg_relevance >= 3:
        verdict = "LOW RELEVANCE - Skim or skip"
    else:
        verdict = "NOT RELEVANT - Skip this PDF"

    report = {
        "pdf_name": os.path.basename(pdf_path),
        "total_pages": total_pages,
        "chunks_analyzed": len(all_analyses),
        "overall_relevance": round(avg_relevance, 1),
        "verdict": verdict,
        "topics_found": unique_topics,
        "chunk_details": all_analyses
    }

    print(f"PDF: {report['pdf_name']}")
    print(f"Total Pages: {report['total_pages']}")
    print(f"Chunks Analyzed: {report['chunks_analyzed']}")
    print(f"Average Relevance: {report['overall_relevance']}/10")
    print(f"Verdict: {report['verdict']}")
    print(f"Topics Found: {', '.join(unique_topics[:10])}")

    return report

def batch_analyze_pdfs(pdf_directory, output_file="experiments/pdf_analysis_results.json"):
    """Analyze multiple PDFs in a directory"""

    print(f"\n{'#'*80}")
    print("BATCH PDF ANALYSIS")
    print(f"{'#'*80}\n")

    # Find all PDFs
    pdf_files = []
    for root, dirs, files in os.walk(pdf_directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))

    print(f"Found {len(pdf_files)} PDF files\n")

    if not pdf_files:
        print("No PDFs found!")
        return

    all_reports = []

    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Analyzing: {os.path.basename(pdf_path)}")

        report = analyze_pdf_progressively(pdf_path, pages_per_chunk=30, max_chunks=3)
        all_reports.append(report)

        # Save incremental results
        with open(output_file, 'w') as f:
            json.dump(all_reports, f, indent=2)

        print(f"\n[SAVED] Results saved to {output_file}")

    # Print summary
    print(f"\n\n{'#'*80}")
    print("BATCH ANALYSIS SUMMARY")
    print(f"{'#'*80}\n")

    highly_relevant = [r for r in all_reports if r["overall_relevance"] >= 7]
    moderately_relevant = [r for r in all_reports if 5 <= r["overall_relevance"] < 7]
    low_relevant = [r for r in all_reports if r["overall_relevance"] < 5]

    print(f"Highly Relevant ({len(highly_relevant)} PDFs):")
    for r in highly_relevant:
        print(f"  - {r['pdf_name']} (Score: {r['overall_relevance']}/10)")

    print(f"\nModerately Relevant ({len(moderately_relevant)} PDFs):")
    for r in moderately_relevant:
        print(f"  - {r['pdf_name']} (Score: {r['overall_relevance']}/10)")

    print(f"\nLow/Not Relevant ({len(low_relevant)} PDFs):")
    for r in low_relevant:
        print(f"  - {r['pdf_name']} (Score: {r['overall_relevance']}/10)")

    print(f"\n[SAVED] Complete results in {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("PDF Analysis Agent - Analyze PDFs for agentic workflow relevance")
        print("\nUsage:")
        print("  Single PDF:  python pdf_analysis_agent.py <pdf_file>")
        print("  Directory:   python pdf_analysis_agent.py <directory> --batch")
        print("\nExamples:")
        print('  python pdf_analysis_agent.py "e:\\Downloads\\Pdf Bank\\Python.Complete.Manual..26th.Edition.2025\\Python Complete Manual - 26th Edition, 2025.pdf"')
        print('  python pdf_analysis_agent.py "e:\\Downloads\\Pdf Bank" --batch')
        sys.exit(1)

    path = sys.argv[1]

    if len(sys.argv) > 2 and sys.argv[2] == "--batch":
        # Batch mode - analyze all PDFs in directory
        batch_analyze_pdfs(path)
    else:
        # Single PDF mode
        report = analyze_pdf_progressively(path, pages_per_chunk=30, max_chunks=3)

        # Save report
        output_file = "experiments/pdf_analysis_results.json"
        with open(output_file, 'w') as f:
            json.dump([report], f, indent=2)

        print(f"\n[SAVED] Analysis saved to {output_file}")
