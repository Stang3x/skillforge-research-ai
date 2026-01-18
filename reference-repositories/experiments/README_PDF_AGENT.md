# PDF Analysis Agent

An intelligent agent that analyzes large PDFs chunk by chunk to determine their relevance for learning agentic workflows.

## What It Does

The agent:
1. **Reads PDFs in chunks** (default: 30 pages at a time) to avoid memory issues
2. **Sends each chunk to Claude** for analysis
3. **Scores relevance** (0-10) for agentic workflow learning
4. **Stops early** if the PDF is not relevant (saves API costs)
5. **Generates a report** with recommendations

## Why This Is Useful

- **Smart filtering**: Don't waste time on irrelevant PDFs
- **Cost-efficient**: Stops analyzing after 2-3 chunks if not relevant
- **Handles large files**: Works with 100MB+ PDFs by processing in chunks
- **Actionable insights**: Tells you which sections to read

## Prerequisites

```bash
# Install dependencies
pip install anthropic pypdf

# Set API key
export ANTHROPIC_API_KEY="your-key-here"  # Git Bash
$env:ANTHROPIC_API_KEY="your-key-here"    # PowerShell
```

## Usage

### Analyze a Single PDF

```bash
python experiments/pdf_analysis_agent.py "e:\Downloads\Pdf Bank\SomeFolder\document.pdf"
```

**Example output:**
```
================================================================================
ANALYZING PDF: Python Complete Manual – 26th Edition, 2025.pdf
================================================================================

Total pages: 90
Pages per chunk: 30
Strategy: Analyze progressively, stop if not relevant

--- CHUNK 1: Pages 1-30 ---
Extracted 2847 characters
Sending to Claude for analysis...

  Relevance Score: 2/10
  Key Topics: general programming, python basics
  Recommendation: skip
  Reasoning: This appears to be a general Python tutorial magazine...

[DECISION] Claude recommends skipping this PDF. Stopping analysis.

================================================================================
FINAL ANALYSIS
================================================================================

PDF: Python Complete Manual – 26th Edition, 2025.pdf
Total Pages: 90
Chunks Analyzed: 1
Average Relevance: 2.0/10
Verdict: NOT RELEVANT - Skip this PDF
Topics Found: general programming, python basics

[SAVED] Analysis saved to experiments/pdf_analysis_results.json
```

### Batch Analyze a Directory

Analyze all PDFs in a directory:

```bash
python experiments/pdf_analysis_agent.py "e:\Downloads\Pdf Bank" --batch
```

This will:
- Find all PDFs in the directory (recursively)
- Analyze each one progressively
- Save results to `experiments/pdf_analysis_results.json`
- Print a summary at the end

**Example output:**
```
################################################################################
BATCH ANALYSIS SUMMARY
################################################################################

Highly Relevant (2 PDFs):
  - Autonomous Agents with LLMs.pdf (Score: 8.5/10)
  - Multi-Agent Systems Guide.pdf (Score: 7.8/10)

Moderately Relevant (1 PDFs):
  - Python for AI Development.pdf (Score: 5.2/10)

Low/Not Relevant (3 PDFs):
  - Python Complete Manual.pdf (Score: 2.0/10)
  - Coding Complete Manual.pdf (Score: 1.5/10)
  - Ultimate Linux Projects.pdf (Score: 3.1/10)

[SAVED] Complete results in experiments/pdf_analysis_results.json
```

## How It Works (Agentic Architecture)

This is a **Level 2 agent** (tools + analysis):

```python
# 1. Tool: Extract text chunk
chunk_text = extract_chunk(pdf_path, start_page=1, end_page=30)

# 2. Agent: Analyze with Claude
analysis = analyze_chunk_with_claude(chunk_text)

# 3. Decision: Should we continue?
if analysis["relevance_score"] < 3:
    stop_analyzing()
else:
    continue_to_next_chunk()
```

### Key Concepts Demonstrated

1. **Chunking**: Breaking large data into manageable pieces
2. **Progressive analysis**: Analyze a little, decide, repeat
3. **Early stopping**: Don't waste resources on irrelevant content
4. **Structured output**: JSON responses for programmatic use
5. **Context building**: Each chunk knows about previous chunks

## Configuration

Edit the script to customize:

```python
# Pages per chunk (default: 30)
analyze_pdf_progressively(pdf_path, pages_per_chunk=50)

# Maximum chunks to analyze (default: unlimited)
analyze_pdf_progressively(pdf_path, max_chunks=5)

# Model selection (in analyze_chunk_with_claude function)
model="claude-3-5-sonnet-20241022"  # Can change to haiku for cheaper/faster
```

## Understanding the Output

### Relevance Scores

- **8-10**: Highly relevant - Deep content on agentic systems, must read
- **5-7**: Moderately relevant - Has useful sections, review selectively
- **3-4**: Low relevance - Tangentially related, skim or skip
- **0-2**: Not relevant - Skip entirely

### Recommendations

- **"continue"**: Keep analyzing more chunks
- **"skip"**: Stop now, not worth reading
- **"focus on sections"**: Skip to specific page ranges

### Output Files

**experiments/pdf_analysis_results.json**:
```json
[
  {
    "pdf_name": "Document.pdf",
    "total_pages": 250,
    "chunks_analyzed": 3,
    "overall_relevance": 6.7,
    "verdict": "MODERATELY RELEVANT - Review specific sections",
    "topics_found": ["agents", "llms", "python"],
    "chunk_details": [...]
  }
]
```

## Examples

### Find Agent-Related PDFs

```bash
# Analyze your entire Pdf Bank
python experiments/pdf_analysis_agent.py "e:\Downloads\Pdf Bank" --batch

# Review results
cat experiments/pdf_analysis_results.json | grep -A 5 '"overall_relevance": [7-9]'
```

### Analyze a Research Paper

```bash
# Single deep-dive on a specific paper
python experiments/pdf_analysis_agent.py "paper.pdf"
```

### Quick Scan (First 60 Pages Only)

Edit the script temporarily:
```python
analyze_pdf_progressively(pdf_path, pages_per_chunk=30, max_chunks=2)
```

## Cost Estimation

- **Per chunk**: ~$0.01-0.02 (using Sonnet 3.5)
- **Image-based PDF**: ~$0.01 total (stops after 1 chunk)
- **Relevant PDF**: ~$0.03-0.06 (analyzes 3 chunks)
- **Batch of 10 PDFs**: ~$0.20-0.40

To reduce costs:
- Use `max_chunks=2` for quick scans
- Switch to Haiku model (3-4x cheaper, slightly less accurate)

## Comparing to Manual Review

**Without agent:**
- Download PDF → Open → Skim 20 pages → Realize it's not relevant → 15 minutes wasted

**With agent:**
- Run script → Get relevance score in 30 seconds → Only read relevant PDFs

## Next Steps

After finding relevant PDFs:

1. **Extract relevant sections**:
   ```bash
   python experiments/extract_pdf.py "relevant.pdf" 45 67 "chapter5.txt"
   ```

2. **Read with context**:
   ```bash
   # Read the extracted text
   cat chapter5.txt
   ```

3. **Ask Claude questions**:
   ```python
   # Use the text in prompts to your research assistant (Level 4 agent)
   ```

## Learning Value

This agent demonstrates:
- ✅ **Tool use** (PDF extraction)
- ✅ **Decision making** (early stopping)
- ✅ **Structured output** (JSON analysis)
- ✅ **Progressive refinement** (building context across chunks)
- ✅ **Cost optimization** (stop when not valuable)

Compare this to [experiments/02_agent_with_tools.py](./02_agent_with_tools.py) - it's the same pattern, just scaled up!

## Troubleshooting

**"ModuleNotFoundError: No module named 'anthropic'"**
```bash
pip install anthropic
```

**"No text extracted - PDF is all images"**
- The PDF is scanned/image-based
- Agent will correctly report it as not relevant
- Use OCR tools if you really need the content

**"Analysis gives low scores to relevant PDFs"**
- The first 30 pages might be intro/fluff
- Increase `pages_per_chunk` to 50
- Or manually skip to later chapters

**"Too expensive for batch analysis"**
- Use `max_chunks=1` for quick screening
- Switch to Haiku model in the code
- Filter by filename first before analyzing

## Related Experiments

- [01_simplest_agent.py](./01_simplest_agent.py) - Basic agent loop
- [02_agent_with_tools.py](./02_agent_with_tools.py) - Agent with tools (similar pattern)
- [03_agent_with_memory.py](./03_agent_with_memory.py) - Adding memory
- [04_research_assistant.py](./04_research_assistant.py) - Complete system
- [extract_pdf.py](./extract_pdf.py) - PDF text extraction tool

---

**Built as Level 3 learning material** - This agent combines tools (PDF extraction) + analysis (Claude) + decision-making (early stopping). It's a practical example of how agents add value beyond simple LLM calls.
