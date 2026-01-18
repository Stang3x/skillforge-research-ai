# Level 5: Research Assistant with Public APIs

A powerful research assistant that integrates **5 free public APIs** to help you learn about agentic workflows.

## What's New

This builds on the Level 4 research assistant by adding **external knowledge sources**:

- **Level 4:** Read files, calculate, save notes (local tools only)
- **Level 5:** + Search papers, Wikipedia, GitHub, books, definitions (internet-connected!)

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

Autonomous agents are systems that can perceive their environment, make decisions,
and take actions to achieve specific goals without continuous human guidance.

From Wikipedia: "In artificial intelligence, an intelligent agent is an autonomous
entity which acts, directing its activity towards achieving goals..."

I found 5 recent papers on arXiv:
1. "Autonomous Agents with Large Language Models" (2024)
2. "Multi-Agent Systems for Complex Task Solving" (2023)
...

And 5 GitHub repositories implementing agent frameworks:
1. **langchain-ai/langchain** ⭐ 95,000
   Python framework for building LLM applications

2. **Significant-Gravitas/AutoGPT** ⭐ 167,000
   An experimental autonomous GPT-4 agent
...

I've saved this as a research note for you!
```

### Example 2: Technical Terms

**You:** "What does 'heuristic' mean?"

**Assistant:**

```
[Using tool: define_term] Done.

**heuristic** (/hjʊˈrɪstɪk/)

*adjective*
1. Enabling someone to discover or learn something for themselves
   Example: "a 'hands-on' or heuristic approach to learning"

*noun*
1. A heuristic process or method
2. (computing) A rule of thumb or educated guess that reduces search time

In AI and computer science, heuristics are practical methods for problem-solving
that find approximate solutions when exact solutions are impractical.
```

### Example 3: Finding Implementation Code

**You:** "Find me Python libraries for building AI agents"

**Assistant:**

```
[Using tool: search_github_repos] Done.

Found 1,247 repositories (showing top 5):

1. **langchain-ai/langchain** ⭐ 95,234
   Build context-aware reasoning applications
   Language: Python
   Link: https://github.com/langchain-ai/langchain

2. **TransformerOptimus/SuperAGI** ⭐ 15,123
   A dev-first open source autonomous AI agent framework
   Language: Python
   Link: https://github.com/TransformerOptimus/SuperAGI

3. **microsoft/autogen** ⭐ 32,456
   A programming framework for agentic AI
   Language: Python
   Link: https://github.com/microsoft/autogen

...

These are great starting points! Would you like me to search for specific
features or compare these frameworks?
```

### Example 4: Academic Research

**You:** "Find the latest research on multi-agent reinforcement learning"

**Assistant:**

```
[Using tool: search_arxiv] Done.
[Using tool: save_research_note] Done.

Found 5 papers on arXiv:

1. **Multi-Agent Reinforcement Learning: A Selective Overview of Theories and Algorithms**
   Authors: Kaiqing Zhang, Zhuoran Yang, Tamer Başar
   Published: 2019-11-04
   Link: http://arxiv.org/abs/1911.10635
   Summary: Multi-agent reinforcement learning (MARL) has attracted significant
   attention from the artificial intelligence community in recent years...

2. **Deep Multi-Agent Reinforcement Learning for Decentralized Continuous
   Cooperative Control**
   Authors: Christian Schroeder de Witt et al.
   Published: 2020-02-15
   ...

I've saved these papers to your research notes!
```

### Example 5: Combined Research

**You:** "I want to learn about LangChain. Find papers, the GitHub repo, and books about building with LLMs."

**Assistant:**

```
[Using tool: search_github_repos] Done.
[Using tool: search_arxiv] Done.
[Using tool: search_books] Done.
[Using tool: save_research_note] Done.

Here's what I found about LangChain and building with LLMs:

**GitHub Repository:**
langchain-ai/langchain ⭐ 95,234
Build context-aware reasoning applications
https://github.com/langchain-ai/langchain

**Related Papers:**
1. "ReAct: Synergizing Reasoning and Acting in Language Models" (2022)
2. "Toolformer: Language Models Can Teach Themselves to Use Tools" (2023)
...

**Books:**
1. "Building LLM-Powered Applications" by Valentina Alto
2. "Designing LLM Agents for Production" (2024)
...

LangChain is a framework for developing applications powered by language models.
It connects LLMs to external data sources and APIs, enabling them to interact
with the real world through "tools" - exactly what you're learning in these
experiments!

I've saved all these resources to your research notes.
```

## Special Commands

- **"quit"** or **"exit"** - Exit the assistant
- **"notes"** - View your saved research notes

## Saved Research Notes

All research is automatically saved to `experiments/research_notes.json` with:

- Timestamp
- Category (paper, code, concept, resource)
- Title
- Content

### Viewing Notes

```bash
# Inside the assistant
You: notes

# Or view the JSON file directly
cat experiments/research_notes.json
```

## What This Demonstrates

This Level 5 agent shows you:

### 1. API Integration

```python
# Making HTTP requests
response = requests.get(url, params=params)
data = response.json()
```

### 2. Tool Design

Each API is wrapped as a tool Claude can use:

```python
{
    "name": "search_arxiv",
    "description": "Search academic papers...",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        }
    }
}
```

### 3. Error Handling

```python
try:
    response = requests.get(url, timeout=10)
    if response.status_code == 404:
        return "Not found"
    return response.json()
except Exception as e:
    return f"Error: {e}"
```

### 4. Data Formatting

Converting API responses into human-readable formats:

```python
result = f"Found {len(papers)} papers:\n\n"
for paper in papers:
    result += f"- {paper['title']}\n"
    result += f"  {paper['summary']}\n\n"
```

### 5. Persistent Storage

Saving research findings across sessions:

```python
notes = load_notes()
notes.append(new_note)
save_notes(notes)
```

## Limitations & Solutions

### GitHub API Rate Limit

**Problem:** 60 requests/hour without authentication

**Solution:** Add GitHub token (optional):

```python
headers = {
    "Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN')}"
}
```

Get free token at: https://github.com/settings/tokens

### arXiv XML Response

**Note:** arXiv returns XML, not JSON. The code parses it automatically.

### Network Issues

If requests fail:

- Check your internet connection
- Try again in a few seconds (temporary issues)
- Some APIs have rate limits (wait and retry)

## Cost Estimation

**API Calls:** FREE (all 5 APIs have no-auth free tiers)

**Claude API Usage:**

- Per query: $0.02-0.05 (depends on complexity)
- With 3 tool calls: $0.05-0.10
- Budget for 10 queries: ~$0.50-1.00

**Tips to reduce costs:**

- Ask focused questions
- Let the agent decide which tools to use (it's smart about it!)
- Use the saved notes to avoid re-researching

## Comparison to Other Levels

| Level | Tools | Knowledge Source | Complexity |
|-------|-------|------------------|------------|
| 1 | None | Claude's training | 12 lines |
| 2 | Calculator, File Reader | Local files | 80 lines |
| 3 | + Memory | Conversation history | 150 lines |
| 4 | + Save notes | Local filesystem | 200 lines |
| **5** | **+ 5 APIs** | **Internet (papers, Wikipedia, GitHub, books)** | **600 lines** |

## Next Steps

### Try These Queries

1. "What is reinforcement learning? Find papers and code examples."
2. "Define 'stochastic' and find books about probability"
3. "Find Python libraries for natural language processing"
4. "Search arXiv for papers about transformers in 2023"
5. "What are neural networks? Find me learning resources."

### Extend the Assistant

**Add more APIs:**

- News API (for AI news)
- GitHub Code Search (search code, not repos)
- Google Books (more book sources)
- Stack Overflow API (programming Q&A)

**Add more features:**

- Download arXiv PDFs automatically
- Create reading lists
- Track learning progress
- Generate summaries of multiple papers

### Build Your Own

Use this pattern to build agents for:

- **Stock research** (finance APIs)
- **Weather analysis** (weather APIs)
- **Travel planning** (maps, flights APIs)
- **Recipe finder** (food APIs)
- **News aggregator** (multiple news APIs)

The pattern is always the same:

1. Find free API
2. Write Python function to call it
3. Define it as a tool for Claude
4. Let Claude decide when to use it!

## Troubleshooting

**"ModuleNotFoundError: No module named 'requests'"**

```bash
pip install requests
```

**"JSONDecodeError" from arXiv**

arXiv returns XML, not JSON. The code handles this - if you see this error, it's a bug. Let me know!

**"Rate limit exceeded" from GitHub**

Wait 5-10 minutes, or add a GitHub token (see Limitations section).

**"No papers found"**

Try different search terms. arXiv uses academic language - try "reinforcement learning" instead of "RL".

## Files Created

- `experiments/05_research_assistant_with_apis.py` - The main assistant
- `experiments/research_notes.json` - Your saved research (auto-created)
- `experiments/README_API_TOOLS_COMPLETE.md` - This guide

## Learning Value

You've now built an agent that:

- ✅ **Integrates external APIs** (real-world data sources)
- ✅ **Makes HTTP requests** (core programming skill)
- ✅ **Parses different formats** (JSON, XML)
- ✅ **Handles errors gracefully** (timeouts, rate limits)
- ✅ **Synthesizes information** (combines multiple sources)
- ✅ **Provides real value** (actually useful for learning!)

This is the foundation for building production agents that interact with the real world!

---

**Ready to try it?**

```bash
pip install requests
python experiments/05_research_assistant_with_apis.py
```

Then ask: "Find papers about autonomous agents and their GitHub implementations"
