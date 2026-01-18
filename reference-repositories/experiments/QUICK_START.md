# Quick Start Guide - PDF Analysis Agent

Your PDFs are now in `e:\Downloads\Pdf Bank\` - here's how to analyze them with AI!

## What You Have

✅ **PDF Analysis Agent** - Analyzes PDFs chunk by chunk to find relevant content
✅ **PDF Extraction Tool** - Extracts text from large PDFs
✅ **Anthropic SDK** - Installed and ready

## Setup (One-Time)

### 1. Get Your API Key

Visit https://console.anthropic.com and get your API key.

### 2. Set Environment Variable

**Git Bash:**
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**PowerShell:**
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### 3. Test Installation

```bash
cd "c:\Users\Stang3x\Documents\Personal - Dan\Agentic Workflows"
python -c "from anthropic import Anthropic; print('Ready!')"
```

Should print: `Ready!`

---

## Usage Examples

### Example 1: Analyze a Single PDF

```bash
cd "c:\Users\Stang3x\Documents\Personal - Dan\Agentic Workflows"

python experiments/pdf_analysis_agent.py "/e/Downloads/Pdf Bank/Python.Complete.Manual..26th.Edition.2025/Python Complete Manual – 26th Edition, 2025.pdf"
```

**Output:**
- Relevance score (0-10)
- Key topics found
- Recommendation (read/skip/focus on sections)
- Saved to `experiments/pdf_analysis_results.json`

### Example 2: Batch Analyze All PDFs

```bash
cd "c:\Users\Stang3x\Documents\Personal - Dan\Agentic Workflows"

python experiments/pdf_analysis_agent.py "/e/Downloads/Pdf Bank" --batch
```

**This will:**
- Find all PDFs in the directory
- Analyze each one (30-90 seconds per PDF)
- Stop early if not relevant (saves money)
- Generate summary report

**Results:**
```
Highly Relevant (X PDFs):
  - document1.pdf (Score: 8.5/10)
  - document2.pdf (Score: 7.2/10)

Low/Not Relevant (Y PDFs):
  - magazine.pdf (Score: 2.0/10)
```

### Example 3: Extract Text from a PDF

If the agent finds a relevant PDF, extract specific sections:

```bash
# Extract pages 20-50
python experiments/extract_pdf.py "/e/Downloads/Pdf Bank/relevant.pdf" 30 "chapter.txt"

# Extract first 100 pages
python experiments/extract_pdf.py "/e/Downloads/Pdf Bank/relevant.pdf" 100

# Extract entire PDF
python experiments/extract_pdf.py "/e/Downloads/Pdf Bank/relevant.pdf"
```

---

## Understanding Your PDFs

### The Three Programming PDFs You Have

I already analyzed these - here's what I found:

**Python Complete Manual – 26th Edition, 2025** (54MB, 90 pages)
- ❌ Not relevant for agentic workflows
- Magazine-style layout with images
- General Python tutorials, not AI/agent content

**Coding Complete Manual – 26th Edition, 2025** (38MB, 68 pages)
- ❌ Not relevant for agentic workflows
- Magazine-style layout with images
- General coding best practices, not agent-specific

**Ultimate Linux Projects – 5th Edition, 2026** (81MB)
- ⚠️ Low relevance
- Linux system administration
- May have some automation scripts

### Recommendation

**Don't spend time on those three PDFs.** They're glossy magazines, not technical documentation about agentic systems.

**Instead:**
1. Start with the [hands-on experiments](../docs/BEGINNER_HANDS_ON_PATH.md)
2. Use the 24 reference repositories you have
3. If you download new PDFs about AI/agents/LLMs, use the analysis agent on those

---

## Cost Estimation

**Per PDF analyzed:**
- Image-based PDF: ~$0.01 (stops after 1 chunk)
- Text PDF (not relevant): ~$0.02-0.03 (stops after 2 chunks)
- Text PDF (relevant): ~$0.05-0.08 (analyzes 3+ chunks)

**Batch analyzing 10 PDFs:** ~$0.20-0.40

---

## What to Look For

The agent searches for these topics:
- ✅ AI agents, LLMs, Claude, GPT
- ✅ Agent architectures, loops, tools
- ✅ Multi-agent systems, coordination
- ✅ Memory management, state
- ✅ Autonomous systems, workflows
- ✅ Tool use, function calling

If a PDF gets a score of **7+ out of 10**, it's worth reading!

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"

```bash
pip install anthropic
```

### "No API key found"

Set your environment variable (see Setup section above).

### "PDF is all images - no text extracted"

This is normal for magazine-style PDFs. The agent will correctly report them as not relevant.

### "Analysis is too slow"

Edit `pdf_analysis_agent.py` and change:
```python
# Line ~216: Reduce pages per chunk
analyze_pdf_progressively(pdf_path, pages_per_chunk=20, max_chunks=2)
```

This analyzes only 40 pages total (2 chunks × 20 pages).

---

## Next Steps

### If You Want to Learn Agentic Workflows

**Don't analyze more PDFs yet.** Instead:

1. **Read the beginner guide**: [docs/BEGINNER_HANDS_ON_PATH.md](../docs/BEGINNER_HANDS_ON_PATH.md)

2. **Build the experiments**:
   - Level 1: Simplest agent (30 min)
   - Level 2: Agent with tools (1 hour)
   - Level 3: Agent with memory (1 hour)
   - Level 4: Complete research assistant (2 hours)

3. **Then** you'll understand the PDF analysis agent because you'll have built similar ones yourself!

### If You Download Agent-Related PDFs

Use the agent to filter them:

```bash
# Download papers from ArXiv about agents
# Then batch analyze
python experiments/pdf_analysis_agent.py "/e/Downloads/Pdf Bank/New Papers" --batch

# Read the highly relevant ones
cat experiments/pdf_analysis_results.json
```

---

## Files Created

- `experiments/pdf_analysis_agent.py` - The main agent
- `experiments/extract_pdf.py` - PDF text extractor
- `experiments/README_PDF_AGENT.md` - Detailed documentation
- `experiments/QUICK_START.md` - This file

---

## Learning Path

```
Current Step: You're here! ──────────────┐
                                         │
                                         ▼
                     ┌─────────────────────────────────┐
                     │  Install & Test PDF Agent       │
                     │  (5 minutes)                    │
                     └─────────────────────────────────┘
                                         │
                                         ▼
                     ┌─────────────────────────────────┐
                     │  Build Level 1-4 Experiments    │
                     │  (5 hours total)                │
                     └─────────────────────────────────┘
                                         │
                                         ▼
                     ┌─────────────────────────────────┐
                     │  Understand Reference Repos     │
                     │  (nanocode → SimpleMem → etc)   │
                     └─────────────────────────────────┘
                                         │
                                         ▼
                     ┌─────────────────────────────────┐
                     │  Build Your Own Agents!         │
                     └─────────────────────────────────┘
```

**Ready to start?** Run the first experiment:

```bash
cd "c:\Users\Stang3x\Documents\Personal - Dan\Agentic Workflows"
python experiments/01_simplest_agent.py
```
