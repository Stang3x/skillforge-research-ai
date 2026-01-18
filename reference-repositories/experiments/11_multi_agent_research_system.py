#!/usr/bin/env python3
"""
Level 11: Multi-Agent Research System

A coordinated team of specialized AI agents:
- COORDINATOR: Routes tasks to appropriate specialists, orchestrates workflow
- RESEARCHER: Gathers information from multiple sources (APIs)
- ANALYST: Synthesizes data, identifies patterns, draws conclusions
- WRITER: Creates formatted reports, summaries, and documentation

Architecture:
┌─────────────────────────────────────────────────────────┐
│                      USER QUERY                          │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    COORDINATOR                           │
│  - Analyzes query complexity                            │
│  - Creates execution plan                               │
│  - Routes to specialists                                │
│  - Synthesizes final response                           │
└────────┬──────────────┬──────────────┬─────────────────┘
         ▼              ▼              ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│ RESEARCHER │  │  ANALYST   │  │   WRITER   │
│            │  │            │  │            │
│ - arXiv    │  │ - Compare  │  │ - Reports  │
│ - GitHub   │  │ - Patterns │  │ - Summaries│
│ - Wiki     │  │ - Insights │  │ - Format   │
│ - HN/SO    │  │ - Evaluate │  │ - Style    │
└────────────┘  └────────────┘  └────────────┘
"""

import os
import json
import requests
import time
import hashlib
from anthropic import Anthropic
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

# Rich library imports
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich import box
from rich.tree import Tree
from rich.live import Live

console = Console()

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
if not ANTHROPIC_API_KEY:
    ANTHROPIC_API_KEY = "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"

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Data directory
DATA_DIR = Path(__file__).parent / "research_data"
DATA_DIR.mkdir(exist_ok=True)
CACHE_FILE = DATA_DIR / "api_cache.json"


# =============================================================================
# AGENT TYPES AND DATA STRUCTURES
# =============================================================================

class AgentRole(Enum):
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"


@dataclass
class AgentMessage:
    """Message passed between agents"""
    from_agent: AgentRole
    to_agent: AgentRole
    content: str
    data: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TaskResult:
    """Result from an agent task"""
    agent: AgentRole
    success: bool
    result: str
    data: dict = field(default_factory=dict)
    execution_time_ms: float = 0


@dataclass
class ResearchPlan:
    """Execution plan created by coordinator"""
    query: str
    complexity: str  # simple, moderate, complex
    steps: list
    agents_needed: list
    estimated_sources: list


# =============================================================================
# RESPONSE CACHE (from Level 10)
# =============================================================================

class ResponseCache:
    DEFAULT_TTL = {
        "arxiv": 3600, "wikipedia": 3600, "github": 300,
        "hackernews": 300, "stackoverflow": 1800, "books": 86400, "dictionary": 86400
    }

    def __init__(self, filepath: Path = CACHE_FILE):
        self.filepath = filepath
        self.cache = self._load()
        self.stats = {"hits": 0, "misses": 0}

    def _load(self) -> dict:
        if self.filepath.exists():
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"entries": {}}

    def _save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def _make_key(self, source: str, query: str) -> str:
        return hashlib.md5(f"{source}:{query.lower().strip()}".encode()).hexdigest()

    def get(self, source: str, query: str) -> Optional[str]:
        key = self._make_key(source, query)
        entry = self.cache["entries"].get(key)
        if not entry:
            self.stats["misses"] += 1
            return None
        cached_at = datetime.fromisoformat(entry["cached_at"])
        ttl = self.DEFAULT_TTL.get(source, 3600)
        if datetime.now() - cached_at > timedelta(seconds=ttl):
            self.stats["misses"] += 1
            return None
        self.stats["hits"] += 1
        return entry["response"]

    def set(self, source: str, query: str, response: str):
        key = self._make_key(source, query)
        self.cache["entries"][key] = {
            "source": source, "query": query, "response": response,
            "cached_at": datetime.now().isoformat()
        }
        self._save()

    def get_stats(self) -> dict:
        total = self.stats["hits"] + self.stats["misses"]
        return {
            "hits": self.stats["hits"], "misses": self.stats["misses"],
            "hit_rate": f"{(self.stats['hits']/total*100):.1f}%" if total > 0 else "0%",
            "entries": len(self.cache["entries"])
        }


cache = ResponseCache()


# =============================================================================
# API FUNCTIONS (from Level 10)
# =============================================================================

def search_arxiv(query, max_results=5):
    cached = cache.get("arxiv", query)
    if cached:
        return cached, True
    try:
        response = requests.get(
            "http://export.arxiv.org/api/query",
            params={"search_query": f"all:{query}", "start": 0, "max_results": max_results,
                    "sortBy": "relevance", "sortOrder": "descending"},
            timeout=10
        )
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        papers = []
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        for entry in root.findall('atom:entry', ns):
            papers.append({
                "title": entry.find('atom:title', ns).text.strip().replace('\n', ' '),
                "authors": [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)],
                "summary": entry.find('atom:summary', ns).text.strip()[:300] + "...",
                "published": entry.find('atom:published', ns).text[:10],
                "link": entry.find('atom:id', ns).text
            })
        if not papers:
            return "No papers found.", False
        result = f"Found {len(papers)} papers:\n\n"
        for i, p in enumerate(papers, 1):
            result += f"{i}. {p['title']}\n   Authors: {', '.join(p['authors'][:3])}\n"
            result += f"   Published: {p['published']}\n   {p['link']}\n\n"
        cache.set("arxiv", query, result)
        return result, False
    except Exception as e:
        return f"Error: {e}", False


def search_wikipedia(query):
    cached = cache.get("wikipedia", query)
    if cached:
        return cached, True
    try:
        response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "format": "json", "list": "search", "srsearch": query, "srlimit": 3},
            timeout=10
        )
        data = response.json()
        if not data.get('query', {}).get('search'):
            return "No articles found.", False
        result = f"Found {len(data['query']['search'])} articles:\n\n"
        for i, a in enumerate(data['query']['search'], 1):
            result += f"{i}. {a['title']}\n   {a['snippet']}\n"
            result += f"   https://en.wikipedia.org/wiki/{a['title'].replace(' ', '_')}\n\n"
        cache.set("wikipedia", query, result)
        return result, False
    except Exception as e:
        return f"Error: {e}", False


def search_github_repos(query, max_results=5):
    cached = cache.get("github", query)
    if cached:
        return cached, True
    try:
        response = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": query, "sort": "stars", "order": "desc", "per_page": max_results},
            headers={"User-Agent": "Research-Assistant"},
            timeout=10
        )
        data = response.json()
        if data.get('total_count', 0) == 0:
            return f"No repos found.", False
        result = f"Found {data['total_count']:,} repos:\n\n"
        for i, r in enumerate(data['items'], 1):
            result += f"{i}. {r['full_name']} ({r['stargazers_count']:,} stars)\n"
            result += f"   {r['description'] or 'No description'}\n   {r['html_url']}\n\n"
        cache.set("github", query, result)
        return result, False
    except Exception as e:
        return f"Error: {e}", False


def search_hackernews(query, max_results=5):
    cached = cache.get("hackernews", query)
    if cached:
        return cached, True
    try:
        response = requests.get(
            "https://hn.algolia.com/api/v1/search",
            params={"query": query, "tags": "story", "hitsPerPage": max_results},
            timeout=10
        )
        data = response.json()
        hits = data.get('hits', [])
        if not hits:
            return f"No HN stories found.", False
        result = f"Found {data.get('nbHits', 0):,} stories:\n\n"
        for i, s in enumerate(hits, 1):
            result += f"{i}. {s.get('title', 'No title')}\n"
            result += f"   Points: {s.get('points', 0)} | Comments: {s.get('num_comments', 0)}\n"
            result += f"   {s.get('url', 'No URL')}\n\n"
        cache.set("hackernews", query, result)
        return result, False
    except Exception as e:
        return f"Error: {e}", False


def search_stackoverflow(query, max_results=5):
    cached = cache.get("stackoverflow", query)
    if cached:
        return cached, True
    try:
        response = requests.get(
            "https://api.stackexchange.com/2.3/search/advanced",
            params={"order": "desc", "sort": "relevance", "q": query,
                    "site": "stackoverflow", "pagesize": max_results},
            timeout=10
        )
        data = response.json()
        items = data.get('items', [])
        if not items:
            return f"No SO questions found.", False
        result = f"Found Stack Overflow questions:\n\n"
        for i, q in enumerate(items, 1):
            title = q.get('title', '').replace('&#39;', "'").replace('&quot;', '"')
            status = "[SOLVED]" if q.get('is_answered') else "[OPEN]"
            result += f"{i}. {title}\n"
            result += f"   {status} Score: {q.get('score', 0)} | Answers: {q.get('answer_count', 0)}\n"
            result += f"   {q.get('link', '')}\n\n"
        cache.set("stackoverflow", query, result)
        return result, False
    except Exception as e:
        return f"Error: {e}", False


# =============================================================================
# SPECIALIZED AGENTS
# =============================================================================

class BaseAgent:
    """Base class for all agents"""

    def __init__(self, role: AgentRole, client: Anthropic):
        self.role = role
        self.client = client
        self.execution_history = []

    def _call_llm(self, system: str, messages: list, tools: list = None, max_tokens: int = 2048) -> str:
        """Make LLM call with optional tools"""
        kwargs = {
            "model": "claude-sonnet-4-5",
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages
        }
        if tools:
            kwargs["tools"] = tools

        response = self.client.messages.create(**kwargs)
        return response

    def log_execution(self, task: str, result: str, time_ms: float):
        self.execution_history.append({
            "task": task, "result_length": len(result),
            "time_ms": time_ms, "timestamp": datetime.now().isoformat()
        })


class ResearcherAgent(BaseAgent):
    """
    RESEARCHER: Gathers information from multiple sources.
    Specializes in finding relevant data quickly and comprehensively.
    """

    SYSTEM_PROMPT = """You are a RESEARCHER agent specialized in gathering information.

Your role:
- Search multiple sources to find relevant information
- Cast a wide net to ensure comprehensive coverage
- Prioritize authoritative and recent sources
- Return raw findings without heavy analysis

Available tools:
- search_arxiv: Academic papers (AI, physics, math, CS)
- search_wikipedia: General knowledge
- search_github_repos: Code and projects
- search_hackernews: Tech news and discussions
- search_stackoverflow: Programming Q&A

Guidelines:
1. Use multiple sources when appropriate
2. Focus on relevance and quality
3. Note source credibility
4. Include publication dates when available
5. Return structured findings for the analyst"""

    TOOLS = [
        {"name": "search_arxiv", "description": "Search arXiv for papers",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "default": 5}}, "required": ["query"]}},
        {"name": "search_wikipedia", "description": "Search Wikipedia",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "search_github_repos", "description": "Search GitHub repos",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "default": 5}}, "required": ["query"]}},
        {"name": "search_hackernews", "description": "Search HackerNews",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "default": 5}}, "required": ["query"]}},
        {"name": "search_stackoverflow", "description": "Search Stack Overflow",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "default": 5}}, "required": ["query"]}}
    ]

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.RESEARCHER, client)

    def research(self, query: str, sources: list = None) -> TaskResult:
        """Execute research task"""
        start_time = time.time()

        if sources is None:
            sources = ["arxiv", "wikipedia", "github"]

        display_agent_activity(self.role, f"Researching: {query}")
        display_agent_activity(self.role, f"Sources: {', '.join(sources)}")

        messages = [{
            "role": "user",
            "content": f"""Research the following topic thoroughly:

TOPIC: {query}

Use these sources: {', '.join(sources)}

Gather comprehensive information and return your findings in a structured format."""
        }]

        all_findings = []
        conversation = messages.copy()

        # Agent loop with tools
        while True:
            response = self._call_llm(self.SYSTEM_PROMPT, conversation, self.TOOLS)

            if response.stop_reason == "end_turn":
                final_text = "".join(b.text for b in response.content if hasattr(b, "text"))
                all_findings.append(final_text)
                break

            elif response.stop_reason == "tool_use":
                conversation.append({"role": "assistant", "content": response.content})
                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input

                        display_agent_activity(self.role, f"  -> {tool_name}: {tool_input.get('query', '')[:40]}...")

                        # Execute tool
                        if tool_name == "search_arxiv":
                            result, cached = search_arxiv(tool_input["query"], tool_input.get("max_results", 5))
                        elif tool_name == "search_wikipedia":
                            result, cached = search_wikipedia(tool_input["query"])
                        elif tool_name == "search_github_repos":
                            result, cached = search_github_repos(tool_input["query"], tool_input.get("max_results", 5))
                        elif tool_name == "search_hackernews":
                            result, cached = search_hackernews(tool_input["query"], tool_input.get("max_results", 5))
                        elif tool_name == "search_stackoverflow":
                            result, cached = search_stackoverflow(tool_input["query"], tool_input.get("max_results", 5))
                        else:
                            result = f"Unknown tool: {tool_name}"
                            cached = False

                        if cached:
                            display_agent_activity(self.role, f"     (cached)")

                        all_findings.append(f"[{tool_name}] {result}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })

                conversation.append({"role": "user", "content": tool_results})
            else:
                break

        elapsed = (time.time() - start_time) * 1000
        combined_findings = "\n\n---\n\n".join(all_findings)

        self.log_execution(query, combined_findings, elapsed)

        return TaskResult(
            agent=self.role,
            success=True,
            result=combined_findings,
            data={"sources_used": sources, "findings_count": len(all_findings)},
            execution_time_ms=elapsed
        )


class AnalystAgent(BaseAgent):
    """
    ANALYST: Synthesizes information and identifies patterns.
    Takes raw research and extracts insights.
    """

    SYSTEM_PROMPT = """You are an ANALYST agent specialized in synthesizing information.

Your role:
- Analyze raw research findings
- Identify patterns, trends, and connections
- Compare and contrast different sources
- Draw conclusions based on evidence
- Highlight key insights and implications

Guidelines:
1. Be objective and evidence-based
2. Note areas of consensus and disagreement
3. Identify gaps in the research
4. Provide confidence levels for conclusions
5. Structure analysis clearly with sections"""

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.ANALYST, client)

    def analyze(self, research_data: str, analysis_focus: str = None) -> TaskResult:
        """Analyze research findings"""
        start_time = time.time()

        display_agent_activity(self.role, "Analyzing research findings...")

        focus_instruction = ""
        if analysis_focus:
            focus_instruction = f"\n\nFocus your analysis on: {analysis_focus}"

        messages = [{
            "role": "user",
            "content": f"""Analyze the following research findings and provide insights:

RESEARCH DATA:
{research_data}
{focus_instruction}

Provide:
1. KEY FINDINGS: Most important discoveries
2. PATTERNS: Trends and connections you observe
3. COMPARISONS: How different sources align or differ
4. GAPS: What's missing or needs more research
5. CONCLUSIONS: Evidence-based takeaways"""
        }]

        response = self._call_llm(self.SYSTEM_PROMPT, messages, max_tokens=2048)
        analysis = "".join(b.text for b in response.content if hasattr(b, "text"))

        elapsed = (time.time() - start_time) * 1000
        self.log_execution("analysis", analysis, elapsed)

        return TaskResult(
            agent=self.role,
            success=True,
            result=analysis,
            data={"focus": analysis_focus},
            execution_time_ms=elapsed
        )


class WriterAgent(BaseAgent):
    """
    WRITER: Creates polished reports and summaries.
    Formats content for different audiences and purposes.
    """

    SYSTEM_PROMPT = """You are a WRITER agent specialized in creating clear, engaging content.

Your role:
- Transform analysis into readable reports
- Adapt style for different audiences
- Create clear structure and flow
- Use appropriate formatting (headers, lists, etc.)
- Ensure accessibility without sacrificing accuracy

Output formats you can create:
- SUMMARY: Brief overview (2-3 paragraphs)
- REPORT: Detailed document with sections
- BULLET_POINTS: Key takeaways as a list
- EXECUTIVE_BRIEF: High-level summary for decision makers
- TECHNICAL_DOC: Detailed technical documentation

Guidelines:
1. Lead with the most important information
2. Use clear, concise language
3. Include relevant citations
4. Organize logically
5. Match tone to audience"""

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.WRITER, client)

    def write(self, content: str, format_type: str = "REPORT", audience: str = "general") -> TaskResult:
        """Create formatted output"""
        start_time = time.time()

        display_agent_activity(self.role, f"Writing {format_type} for {audience} audience...")

        messages = [{
            "role": "user",
            "content": f"""Transform this content into a {format_type} for a {audience} audience:

CONTENT:
{content}

FORMAT: {format_type}
AUDIENCE: {audience}

Create a polished, well-structured output appropriate for the specified format and audience."""
        }]

        response = self._call_llm(self.SYSTEM_PROMPT, messages, max_tokens=3000)
        written_content = "".join(b.text for b in response.content if hasattr(b, "text"))

        elapsed = (time.time() - start_time) * 1000
        self.log_execution(f"{format_type} writing", written_content, elapsed)

        return TaskResult(
            agent=self.role,
            success=True,
            result=written_content,
            data={"format": format_type, "audience": audience},
            execution_time_ms=elapsed
        )


class CoordinatorAgent(BaseAgent):
    """
    COORDINATOR: Orchestrates the multi-agent workflow.
    Analyzes queries, creates plans, and routes to specialists.
    """

    SYSTEM_PROMPT = """You are the COORDINATOR agent that orchestrates a research team.

Your team:
- RESEARCHER: Gathers information from APIs (arXiv, GitHub, Wikipedia, HackerNews, StackOverflow)
- ANALYST: Synthesizes findings, identifies patterns
- WRITER: Creates formatted reports and summaries

Your role:
1. Analyze incoming queries
2. Determine complexity (simple/moderate/complex)
3. Create an execution plan
4. Decide which agents to involve

For simple queries (definitions, single facts): May skip to WRITER
For moderate queries (comparisons, overviews): RESEARCHER -> WRITER
For complex queries (deep research, analysis): RESEARCHER -> ANALYST -> WRITER

Output a JSON plan with this structure:
{
    "complexity": "simple|moderate|complex",
    "plan": ["step1", "step2", ...],
    "agents": ["researcher", "analyst", "writer"],
    "sources": ["arxiv", "github", ...],
    "output_format": "SUMMARY|REPORT|BULLET_POINTS"
}"""

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.COORDINATOR, client)
        self.researcher = ResearcherAgent(client)
        self.analyst = AnalystAgent(client)
        self.writer = WriterAgent(client)

    def create_plan(self, query: str) -> ResearchPlan:
        """Create execution plan for a query"""
        display_agent_activity(self.role, "Creating execution plan...")

        messages = [{
            "role": "user",
            "content": f"""Analyze this query and create an execution plan:

QUERY: {query}

Return a JSON plan (no markdown, just raw JSON)."""
        }]

        response = self._call_llm(self.SYSTEM_PROMPT, messages, max_tokens=500)
        plan_text = "".join(b.text for b in response.content if hasattr(b, "text"))

        # Parse JSON from response
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[^{}]*\}', plan_text, re.DOTALL)
            if json_match:
                plan_data = json.loads(json_match.group())
            else:
                plan_data = json.loads(plan_text)
        except:
            # Default plan if parsing fails
            plan_data = {
                "complexity": "moderate",
                "plan": ["Research the topic", "Analyze findings", "Write report"],
                "agents": ["researcher", "analyst", "writer"],
                "sources": ["arxiv", "wikipedia", "github"],
                "output_format": "REPORT"
            }

        return ResearchPlan(
            query=query,
            complexity=plan_data.get("complexity", "moderate"),
            steps=plan_data.get("plan", []),
            agents_needed=plan_data.get("agents", ["researcher", "writer"]),
            estimated_sources=plan_data.get("sources", ["wikipedia"])
        )

    def execute(self, query: str) -> str:
        """Execute full multi-agent workflow"""
        start_time = time.time()

        # Step 1: Create plan
        plan = self.create_plan(query)
        display_plan(plan)

        results = []

        # Step 2: Research (if needed)
        if "researcher" in plan.agents_needed:
            research_result = self.researcher.research(query, plan.estimated_sources)
            results.append(research_result)
            display_agent_result(research_result)

        # Step 3: Analysis (if needed)
        if "analyst" in plan.agents_needed and results:
            research_data = results[-1].result
            analysis_result = self.analyst.analyze(research_data)
            results.append(analysis_result)
            display_agent_result(analysis_result)

        # Step 4: Writing
        if "writer" in plan.agents_needed:
            content_to_write = results[-1].result if results else query
            output_format = "REPORT" if plan.complexity == "complex" else "SUMMARY"
            write_result = self.writer.write(content_to_write, output_format)
            results.append(write_result)

        # Final output
        total_time = (time.time() - start_time) * 1000
        final_output = results[-1].result if results else "No results generated."

        # Summary stats
        display_execution_summary(plan, results, total_time)

        return final_output


# =============================================================================
# UI HELPERS
# =============================================================================

def display_welcome():
    text = """[bold cyan]MULTI-AGENT RESEARCH SYSTEM[/bold cyan] [dim]v11.0[/dim]

[yellow]Agent Team:[/yellow]
  [blue]COORDINATOR[/blue]  Orchestrates workflow and routes tasks
  [green]RESEARCHER[/green]   Gathers information from multiple sources
  [magenta]ANALYST[/magenta]     Synthesizes data and identifies patterns
  [cyan]WRITER[/cyan]       Creates formatted reports and summaries

[yellow]How It Works:[/yellow]
  1. You ask a question
  2. Coordinator analyzes complexity and creates a plan
  3. Specialists execute their tasks in sequence
  4. Final polished output is delivered

[yellow]Commands:[/yellow]
  [cyan]agents[/cyan]    Show agent status       [cyan]cache[/cyan]     Cache stats
  [cyan]history[/cyan]   Execution history       [cyan]quit[/cyan]      Exit"""

    console.print(Panel(text, title="[bold white]Welcome[/bold white]", border_style="blue", box=box.DOUBLE))


def display_agent_activity(role: AgentRole, message: str):
    """Display agent activity in real-time"""
    colors = {
        AgentRole.COORDINATOR: "blue",
        AgentRole.RESEARCHER: "green",
        AgentRole.ANALYST: "magenta",
        AgentRole.WRITER: "cyan"
    }
    color = colors.get(role, "white")
    console.print(f"  [{color}]{role.value.upper()}[/{color}] {message}")


def display_plan(plan: ResearchPlan):
    """Display execution plan"""
    tree = Tree(f"[bold blue]Execution Plan[/bold blue] [dim]({plan.complexity})[/dim]")

    agents_branch = tree.add("[yellow]Agents[/yellow]")
    for agent in plan.agents_needed:
        agents_branch.add(f"[green]{agent}[/green]")

    sources_branch = tree.add("[yellow]Sources[/yellow]")
    for source in plan.estimated_sources:
        sources_branch.add(f"[cyan]{source}[/cyan]")

    steps_branch = tree.add("[yellow]Steps[/yellow]")
    for i, step in enumerate(plan.steps, 1):
        steps_branch.add(f"{i}. {step}")

    console.print(tree)
    console.print()


def display_agent_result(result: TaskResult):
    """Display agent result summary"""
    colors = {
        AgentRole.RESEARCHER: "green",
        AgentRole.ANALYST: "magenta",
        AgentRole.WRITER: "cyan"
    }
    color = colors.get(result.agent, "white")
    status = "[green]SUCCESS[/green]" if result.success else "[red]FAILED[/red]"

    console.print(f"  [{color}]{result.agent.value.upper()}[/{color}] {status} ({result.execution_time_ms:.0f}ms, {len(result.result)} chars)")


def display_execution_summary(plan: ResearchPlan, results: list, total_time_ms: float):
    """Display execution summary"""
    table = Table(title="Execution Summary", box=box.ROUNDED, border_style="blue")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Query Complexity", plan.complexity)
    table.add_row("Agents Used", ", ".join(plan.agents_needed))
    table.add_row("Sources Queried", ", ".join(plan.estimated_sources))
    table.add_row("Total Time", f"{total_time_ms:.0f}ms")
    table.add_row("Cache Hit Rate", cache.get_stats()["hit_rate"])

    console.print()
    console.print(table)


def display_response(text: str):
    """Display final response"""
    console.print()
    console.print(Panel(
        Markdown(text),
        title="[bold cyan]Research Report[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    ))


# =============================================================================
# MAIN
# =============================================================================

def main():
    console.clear()
    display_welcome()
    console.print()

    coordinator = CoordinatorAgent(client)

    while True:
        console.print()
        user_input = console.input("[bold green]You:[/bold green] ").strip()

        if not user_input:
            continue

        if user_input.lower() == 'quit':
            console.print("\n[dim]Goodbye![/dim]")
            break

        if user_input.lower() == 'agents':
            table = Table(title="Agent Status", box=box.ROUNDED)
            table.add_column("Agent", style="cyan")
            table.add_column("Tasks", style="green")
            table.add_column("Last Task", style="dim")

            for agent in [coordinator, coordinator.researcher, coordinator.analyst, coordinator.writer]:
                history = agent.execution_history
                last = history[-1]["task"][:30] + "..." if history else "-"
                table.add_row(agent.role.value.upper(), str(len(history)), last)

            console.print(table)
            continue

        if user_input.lower() == 'cache':
            cs = cache.get_stats()
            console.print(f"[cyan]Cache:[/cyan] {cs['entries']} entries, {cs['hit_rate']} hit rate")
            continue

        if user_input.lower() == 'history':
            for agent in [coordinator.researcher, coordinator.analyst, coordinator.writer]:
                if agent.execution_history:
                    console.print(f"\n[bold]{agent.role.value.upper()}[/bold]")
                    for h in agent.execution_history[-3:]:
                        console.print(f"  - {h['task'][:50]}... ({h['time_ms']:.0f}ms)")
            continue

        # Execute multi-agent workflow
        console.print()
        with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console, transient=True) as progress:
            progress.add_task("[blue]Coordinating agents...", total=None)

        result = coordinator.execute(user_input)
        display_response(result)


if __name__ == "__main__":
    main()
