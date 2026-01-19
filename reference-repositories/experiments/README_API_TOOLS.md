# Level 5: Research Assistant with Public APIs

A powerful research assistant that integrates **5 free public APIs** to help you learn about agentic workflows.

## What's New

This builds on the Level 4 research assistant by adding **external knowledge sources**:

**Level 4:** Read files, calculate, save notes (local tools only)
**Level 5:** + Search papers, Wikipedia, GitHub, books, definitions (internet-connected!)

## The 5 Free APIs

### 1. arXiv API ⭐⭐⭐⭐⭐
- **What:** Academic research papers (AI, ML, computer science, math, physics)
- **Auth:** None required
- **Why useful:** Latest research on autonomous agents, LLMs, multi-agent systems
- **Example:** "Find papers about autonomous agents"

### 2. Wikipedia API ⭐⭐⭐⭐⭐
- **What:** Encyclopedia articles with summaries
- **Auth:** None required
- **Why useful:** Quick overviews of concepts, definitions, background
- **Example:** "What is reinforcement learning?"

### 3. Dictionary API ⭐⭐⭐⭐
- **What:** Word definitions, pronunciation, examples
- **Auth:** None required
- **Why useful:** Understand technical terms (heuristic, stochastic, etc.)
- **Example:** "Define 'autonomous'"

### 4. GitHub API ⭐⭐⭐⭐
- **What:** Search code repositories
- **Auth:** None (but rate-limited to 60 requests/hour without auth)
- **Why useful:** Find implementation examples, libraries, frameworks
- **Example:** "Find Python agent frameworks on GitHub"

### 5. Open Library API ⭐⭐⭐⭐
- **What:** Books from Project Gutenberg and other sources
- **Auth:** None required
- **Why useful:** Find textbooks, programming books, references
- **Example:** "Find books about artificial intelligence"

## Installation

```bash
# Install required package for HTTP requests
pip install requests

# You already have anthropic installed
```

## Usage

```bash
cd "c:\Users\Stang3x\Documents\Personal - Dan\Agentic Workflows"
python experiments/05_research_assistant_with_apis.py
```

## Example Interactions

### Example 1: Learning About Agents

**You:** "What are autonomous agents? Find me papers and examples."

**Assistant:**
```
[Using tool: search_wikipedia] Done.
[Using tool: search_arxiv] Done.
[Using tool: search_github_repos] Done.
[Using tool: save_research_note] Done.