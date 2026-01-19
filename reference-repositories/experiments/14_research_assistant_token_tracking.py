#!/usr/bin/env python3
"""
Level 14: Research Assistant with Token Usage Tracking

New capabilities:
- Track input/output tokens per API call
- Session-wide token usage statistics
- Cost estimation based on model pricing
- Token budget warnings
- Usage history and trends

Architecture:
┌─────────────────────────────────────────────────────────────┐
│                      TOKEN TRACKER                           │
│  - Per-call tracking    - Session totals    - Cost estimate │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    COORDINATOR                               │
└────────┬──────────────┬──────────────┬──────────────┬───────┘
         ▼              ▼              ▼              ▼
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│ RESEARCHER │  │  ANALYST   │  │   WRITER   │  │ DIAGRAMMER │
└────────────┘  └────────────┘  └────────────┘  └────────────┘
"""

import os
import sys
import json
import requests
import time
import hashlib
import re
from anthropic import Anthropic
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum

# Rich library imports
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich import box
from rich.tree import Tree
from rich.syntax import Syntax
from rich.live import Live
from rich.layout import Layout

# PDF library
try:
    from pypdf import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

console = Console()

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
if not ANTHROPIC_API_KEY:
    ANTHROPIC_API_KEY = "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"

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Data directories
DATA_DIR = Path(__file__).parent / "research_data"
DATA_DIR.mkdir(exist_ok=True)
PDF_DIR = DATA_DIR / "pdfs"
PDF_DIR.mkdir(exist_ok=True)
DIAGRAMS_DIR = DATA_DIR / "diagrams"
DIAGRAMS_DIR.mkdir(exist_ok=True)
CACHE_FILE = DATA_DIR / "api_cache.json"
TOKEN_HISTORY_FILE = DATA_DIR / "token_history.json"


# =============================================================================
# TOKEN USAGE TRACKER
# =============================================================================

@dataclass
class TokenUsage:
    """Single API call token usage"""
    input_tokens: int
    output_tokens: int
    model: str
    agent: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> dict:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_read_tokens": self.cache_read_tokens,
            "cache_creation_tokens": self.cache_creation_tokens,
            "model": self.model,
            "agent": self.agent,
            "timestamp": self.timestamp
        }


class TokenTracker:
    """
    Tracks token usage across all API calls in a session.

    Features:
    - Per-call tracking with agent attribution
    - Session totals and averages
    - Cost estimation based on current pricing
    - Token budget warnings
    - Historical usage persistence
    """

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        "default": {"input": 3.00, "output": 15.00}
    }

    def __init__(self, history_file: Path = TOKEN_HISTORY_FILE, budget: int = None):
        """
        Initialize token tracker.

        Args:
            history_file: Path to save usage history
            budget: Optional token budget for warnings
        """
        self.history_file = history_file
        self.budget = budget
        self.session_usage: List[TokenUsage] = []
        self.session_start = datetime.now()
        self._load_history()

    def _load_history(self):
        """Load historical usage data"""
        self.history = {"sessions": []}
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except:
                pass

    def _save_history(self):
        """Save usage history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def track(self, response, agent: str = "unknown") -> TokenUsage:
        """
        Track token usage from an API response.

        Args:
            response: Anthropic API response object
            agent: Name of the agent making the call

        Returns:
            TokenUsage object with usage details
        """
        usage = response.usage
        model = response.model

        token_usage = TokenUsage(
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cache_read_tokens=getattr(usage, 'cache_read_input_tokens', 0) or 0,
            cache_creation_tokens=getattr(usage, 'cache_creation_input_tokens', 0) or 0,
            model=model,
            agent=agent
        )

        self.session_usage.append(token_usage)

        # Check budget
        if self.budget and self.total_tokens > self.budget:
            console.print(f"[bold red]⚠ TOKEN BUDGET EXCEEDED![/bold red] "
                         f"{self.total_tokens:,} / {self.budget:,}")

        return token_usage

    @property
    def total_input_tokens(self) -> int:
        return sum(u.input_tokens for u in self.session_usage)

    @property
    def total_output_tokens(self) -> int:
        return sum(u.output_tokens for u in self.session_usage)

    @property
    def total_tokens(self) -> int:
        return self.total_input_tokens + self.total_output_tokens

    @property
    def total_cache_read(self) -> int:
        return sum(u.cache_read_tokens for u in self.session_usage)

    @property
    def total_cache_creation(self) -> int:
        return sum(u.cache_creation_tokens for u in self.session_usage)

    @property
    def api_calls(self) -> int:
        return len(self.session_usage)

    def estimate_cost(self) -> float:
        """Estimate total cost in USD"""
        total_cost = 0.0

        for usage in self.session_usage:
            pricing = self.PRICING.get(usage.model, self.PRICING["default"])
            input_cost = (usage.input_tokens / 1_000_000) * pricing["input"]
            output_cost = (usage.output_tokens / 1_000_000) * pricing["output"]
            total_cost += input_cost + output_cost

        return total_cost

    def get_usage_by_agent(self) -> Dict[str, Dict]:
        """Get token usage breakdown by agent"""
        by_agent = {}

        for usage in self.session_usage:
            if usage.agent not in by_agent:
                by_agent[usage.agent] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "calls": 0,
                    "cost": 0.0
                }

            by_agent[usage.agent]["input_tokens"] += usage.input_tokens
            by_agent[usage.agent]["output_tokens"] += usage.output_tokens
            by_agent[usage.agent]["calls"] += 1

            pricing = self.PRICING.get(usage.model, self.PRICING["default"])
            by_agent[usage.agent]["cost"] += (
                (usage.input_tokens / 1_000_000) * pricing["input"] +
                (usage.output_tokens / 1_000_000) * pricing["output"]
            )

        return by_agent

    def get_session_stats(self) -> dict:
        """Get comprehensive session statistics"""
        duration = (datetime.now() - self.session_start).total_seconds()

        return {
            "api_calls": self.api_calls,
            "total_tokens": self.total_tokens,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "cache_read_tokens": self.total_cache_read,
            "cache_creation_tokens": self.total_cache_creation,
            "estimated_cost_usd": self.estimate_cost(),
            "avg_tokens_per_call": self.total_tokens / self.api_calls if self.api_calls > 0 else 0,
            "tokens_per_minute": (self.total_tokens / duration * 60) if duration > 0 else 0,
            "session_duration_minutes": duration / 60,
            "budget": self.budget,
            "budget_remaining": (self.budget - self.total_tokens) if self.budget else None,
            "by_agent": self.get_usage_by_agent()
        }

    def save_session(self):
        """Save current session to history"""
        if self.api_calls == 0:
            return

        session_data = {
            "start": self.session_start.isoformat(),
            "end": datetime.now().isoformat(),
            "stats": self.get_session_stats(),
            "usage": [u.to_dict() for u in self.session_usage]
        }

        self.history["sessions"].append(session_data)

        # Keep last 100 sessions
        if len(self.history["sessions"]) > 100:
            self.history["sessions"] = self.history["sessions"][-100:]

        self._save_history()

    def get_historical_stats(self, days: int = 7) -> dict:
        """Get usage statistics for the past N days"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_sessions = []

        for session in self.history.get("sessions", []):
            try:
                session_start = datetime.fromisoformat(session["start"])
                if session_start >= cutoff:
                    recent_sessions.append(session)
            except:
                continue

        if not recent_sessions:
            return {"sessions": 0, "total_tokens": 0, "total_cost": 0.0}

        total_tokens = sum(s["stats"]["total_tokens"] for s in recent_sessions)
        total_cost = sum(s["stats"]["estimated_cost_usd"] for s in recent_sessions)

        return {
            "sessions": len(recent_sessions),
            "days": days,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "avg_tokens_per_session": total_tokens / len(recent_sessions),
            "avg_cost_per_session": total_cost / len(recent_sessions)
        }

    def display_stats(self):
        """Display token usage statistics in a rich table"""
        stats = self.get_session_stats()

        # Main stats table
        table = Table(title="[bold cyan]Token Usage[/bold cyan]", box=box.ROUNDED, border_style="cyan")
        table.add_column("Metric", style="yellow")
        table.add_column("Value", style="green", justify="right")

        table.add_row("API Calls", f"{stats['api_calls']:,}")
        table.add_row("Total Tokens", f"{stats['total_tokens']:,}")
        table.add_row("  ├─ Input", f"{stats['input_tokens']:,}")
        table.add_row("  └─ Output", f"{stats['output_tokens']:,}")

        if stats['cache_read_tokens'] > 0:
            table.add_row("Cache Read", f"{stats['cache_read_tokens']:,}")
        if stats['cache_creation_tokens'] > 0:
            table.add_row("Cache Created", f"{stats['cache_creation_tokens']:,}")

        table.add_row("Estimated Cost", f"${stats['estimated_cost_usd']:.4f}")
        table.add_row("Avg Tokens/Call", f"{stats['avg_tokens_per_call']:.0f}")
        table.add_row("Session Duration", f"{stats['session_duration_minutes']:.1f} min")

        if stats['budget']:
            remaining = stats['budget_remaining']
            color = "green" if remaining > stats['budget'] * 0.2 else "yellow" if remaining > 0 else "red"
            table.add_row("Budget Remaining", f"[{color}]{remaining:,}[/{color}]")

        console.print(table)

        # Agent breakdown if multiple agents
        if len(stats['by_agent']) > 1:
            agent_table = Table(title="[bold]By Agent[/bold]", box=box.SIMPLE)
            agent_table.add_column("Agent", style="cyan")
            agent_table.add_column("Calls", justify="right")
            agent_table.add_column("Tokens", justify="right")
            agent_table.add_column("Cost", justify="right")

            for agent, data in sorted(stats['by_agent'].items()):
                agent_table.add_row(
                    agent.upper(),
                    str(data['calls']),
                    f"{data['input_tokens'] + data['output_tokens']:,}",
                    f"${data['cost']:.4f}"
                )

            console.print(agent_table)

    def display_compact(self):
        """Display compact token usage in status bar format"""
        stats = self.get_session_stats()
        cost_color = "green" if stats['estimated_cost_usd'] < 0.10 else "yellow" if stats['estimated_cost_usd'] < 0.50 else "red"

        console.print(
            f"[dim]Tokens:[/dim] [cyan]{stats['total_tokens']:,}[/cyan] "
            f"[dim]({stats['input_tokens']:,}↓ {stats['output_tokens']:,}↑)[/dim] "
            f"[dim]Cost:[/dim] [{cost_color}]${stats['estimated_cost_usd']:.4f}[/{cost_color}] "
            f"[dim]Calls:[/dim] {stats['api_calls']}"
        )


# Initialize global token tracker
token_tracker = TokenTracker()


# =============================================================================
# DIAGRAM TYPES
# =============================================================================

class DiagramType(Enum):
    FLOWCHART = "flowchart"
    SEQUENCE = "sequence"
    CLASS = "class"
    STATE = "state"
    MINDMAP = "mindmap"
    ER = "er"


@dataclass
class Diagram:
    diagram_type: DiagramType
    title: str
    mermaid_code: str
    description: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    file_path: Optional[str] = None


# =============================================================================
# DIAGRAM GENERATOR (with token tracking)
# =============================================================================

class DiagramGenerator:
    def __init__(self, client: Anthropic, diagrams_dir: Path = DIAGRAMS_DIR):
        self.client = client
        self.diagrams_dir = diagrams_dir
        self.generated_diagrams: List[Diagram] = []

    def _call_llm(self, system: str, prompt: str, max_tokens: int = 2048) -> str:
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        token_tracker.track(response, agent="diagrammer")
        return "".join(b.text for b in response.content if hasattr(b, "text"))

    def generate_flowchart(self, description: str, direction: str = "TD") -> Diagram:
        system = """Generate ONLY valid Mermaid flowchart code. Start with: flowchart {direction}
Use node shapes: [rect], (rounded), {diamond}, [(database)], ((circle))
Use arrows: -->, -.->. Output ONLY the mermaid code."""

        mermaid_code = self._call_llm(system, f"Create flowchart ({direction}):\n{description}")
        mermaid_code = self._clean_mermaid_code(mermaid_code)

        diagram = Diagram(DiagramType.FLOWCHART, f"Flowchart: {description[:50]}...",
                         mermaid_code, description)
        self.generated_diagrams.append(diagram)
        return diagram

    def generate_sequence(self, description: str) -> Diagram:
        system = """Generate ONLY valid Mermaid sequence diagram code. Start with: sequenceDiagram
Use: participant, ->>, -->>. Output ONLY the mermaid code."""

        mermaid_code = self._call_llm(system, f"Create sequence diagram:\n{description}")
        mermaid_code = self._clean_mermaid_code(mermaid_code)

        diagram = Diagram(DiagramType.SEQUENCE, f"Sequence: {description[:50]}...",
                         mermaid_code, description)
        self.generated_diagrams.append(diagram)
        return diagram

    def generate_mindmap(self, topic: str, subtopics: str = None) -> Diagram:
        system = """Generate ONLY valid Mermaid mindmap code. Start with: mindmap
Use indentation for hierarchy. Root: root((topic)). Output ONLY the mermaid code."""

        full_desc = f"Topic: {topic}" + (f"\nSubtopics: {subtopics}" if subtopics else "")
        mermaid_code = self._call_llm(system, f"Create mindmap:\n{full_desc}")
        mermaid_code = self._clean_mermaid_code(mermaid_code)

        diagram = Diagram(DiagramType.MINDMAP, f"Mindmap: {topic}", mermaid_code, full_desc)
        self.generated_diagrams.append(diagram)
        return diagram

    def _clean_mermaid_code(self, code: str) -> str:
        code = re.sub(r'^```mermaid\s*', '', code, flags=re.MULTILINE)
        code = re.sub(r'^```\s*$', '', code, flags=re.MULTILINE)
        return code.strip()

    def save_diagram(self, diagram: Diagram, filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{diagram.diagram_type.value}_{timestamp}"

        filepath = self.diagrams_dir / f"{filename}.md"
        content = f"# {diagram.title}\n\n```mermaid\n{diagram.mermaid_code}\n```\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        diagram.file_path = str(filepath)
        return str(filepath)

    def list_diagrams(self) -> List[dict]:
        return [{"name": f.name, "path": str(f)} for f in self.diagrams_dir.glob("*.md")]


diagram_generator = DiagramGenerator(client)


# =============================================================================
# PDF MANAGEMENT
# =============================================================================

class PDFManager:
    def __init__(self, pdf_dir: Path = PDF_DIR):
        self.pdf_dir = pdf_dir

    def extract_text(self, pdf_path: str, max_pages: int = None) -> dict:
        if not PDF_AVAILABLE:
            return {"success": False, "error": "pypdf not installed"}
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            return {"success": False, "error": f"File not found: {pdf_path}"}

        try:
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)
            pages_to_extract = min(max_pages, total_pages) if max_pages else total_pages

            text_pages = []
            for i in range(pages_to_extract):
                text = reader.pages[i].extract_text() or ""
                text_pages.append(f"[Page {i+1}]\n{text}")

            full_text = "\n\n".join(text_pages)
            return {"success": True, "file_name": pdf_path.name, "total_pages": total_pages,
                   "extracted_pages": pages_to_extract, "text": full_text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def download_arxiv_pdf(self, arxiv_id: str) -> dict:
        arxiv_id = arxiv_id.strip()
        pdf_path = self.pdf_dir / f"arxiv_{arxiv_id.replace('.', '_')}.pdf"

        if pdf_path.exists():
            return {"success": True, "cached": True, "file_path": str(pdf_path)}

        try:
            response = requests.get(f"https://arxiv.org/pdf/{arxiv_id}.pdf", timeout=30, stream=True)
            if response.status_code != 200:
                return {"success": False, "error": f"Download failed: {response.status_code}"}

            with open(pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return {"success": True, "cached": False, "file_path": str(pdf_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_pdfs(self) -> list:
        return [{"name": f.name, "path": str(f)} for f in self.pdf_dir.glob("*.pdf")]


pdf_manager = PDFManager()


# =============================================================================
# RESPONSE CACHE
# =============================================================================

class ResponseCache:
    DEFAULT_TTL = {"arxiv": 3600, "wikipedia": 3600, "github": 300, "hackernews": 300, "stackoverflow": 1800}

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
        if datetime.now() - cached_at > timedelta(seconds=self.DEFAULT_TTL.get(source, 3600)):
            self.stats["misses"] += 1
            return None
        self.stats["hits"] += 1
        return entry["response"]

    def set(self, source: str, query: str, response: str):
        key = self._make_key(source, query)
        self.cache["entries"][key] = {"source": source, "query": query, "response": response,
                                      "cached_at": datetime.now().isoformat()}
        self._save()

    def get_stats(self) -> dict:
        total = self.stats["hits"] + self.stats["misses"]
        return {"hits": self.stats["hits"], "misses": self.stats["misses"],
                "hit_rate": f"{(self.stats['hits']/total*100):.1f}%" if total > 0 else "0%",
                "entries": len(self.cache["entries"])}


cache = ResponseCache()


# =============================================================================
# API FUNCTIONS
# =============================================================================

def search_arxiv(query, max_results=5):
    cached = cache.get("arxiv", query)
    if cached:
        return cached, True
    try:
        response = requests.get("http://export.arxiv.org/api/query",
            params={"search_query": f"all:{query}", "max_results": max_results}, timeout=10)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        papers = []
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        for entry in root.findall('atom:entry', ns):
            paper_id = entry.find('atom:id', ns).text
            papers.append({
                "title": entry.find('atom:title', ns).text.strip().replace('\n', ' '),
                "arxiv_id": paper_id.split('/')[-1] if paper_id else ""
            })
        if not papers:
            return "No papers found.", False
        result = f"Found {len(papers)} papers:\n\n"
        for i, p in enumerate(papers, 1):
            result += f"{i}. {p['title']}\n   arXiv: {p['arxiv_id']}\n\n"
        cache.set("arxiv", query, result)
        return result, False
    except Exception as e:
        return f"Error: {e}", False

def search_wikipedia(query):
    cached = cache.get("wikipedia", query)
    if cached:
        return cached, True
    try:
        response = requests.get("https://en.wikipedia.org/w/api.php",
            params={"action": "query", "format": "json", "list": "search", "srsearch": query, "srlimit": 3}, timeout=10)
        data = response.json()
        if not data.get('query', {}).get('search'):
            return "No articles found.", False
        result = "Found articles:\n\n"
        for i, a in enumerate(data['query']['search'], 1):
            result += f"{i}. {a['title']}\n\n"
        cache.set("wikipedia", query, result)
        return result, False
    except Exception as e:
        return f"Error: {e}", False

def search_github_repos(query, max_results=5):
    cached = cache.get("github", query)
    if cached:
        return cached, True
    try:
        response = requests.get("https://api.github.com/search/repositories",
            params={"q": query, "sort": "stars", "per_page": max_results},
            headers={"User-Agent": "Research-Assistant"}, timeout=10)
        data = response.json()
        if data.get('total_count', 0) == 0:
            return "No repos found.", False
        result = f"Found {data['total_count']:,} repos:\n\n"
        for i, r in enumerate(data['items'], 1):
            result += f"{i}. {r['full_name']} ({r['stargazers_count']:,} stars)\n"
        cache.set("github", query, result)
        return result, False
    except Exception as e:
        return f"Error: {e}", False

def search_hackernews(query, max_results=5):
    cached = cache.get("hackernews", query)
    if cached:
        return cached, True
    try:
        response = requests.get("https://hn.algolia.com/api/v1/search",
            params={"query": query, "tags": "story", "hitsPerPage": max_results}, timeout=10)
        hits = response.json().get('hits', [])
        if not hits:
            return "No stories found.", False
        result = "HackerNews:\n\n"
        for i, s in enumerate(hits, 1):
            result += f"{i}. {s.get('title', 'No title')} ({s.get('points', 0)} pts)\n"
        cache.set("hackernews", query, result)
        return result, False
    except Exception as e:
        return f"Error: {e}", False

def search_stackoverflow(query, max_results=5):
    cached = cache.get("stackoverflow", query)
    if cached:
        return cached, True
    try:
        response = requests.get("https://api.stackexchange.com/2.3/search/advanced",
            params={"q": query, "site": "stackoverflow", "pagesize": max_results}, timeout=10)
        items = response.json().get('items', [])
        if not items:
            return "No questions found.", False
        result = "Stack Overflow:\n\n"
        for i, q in enumerate(items, 1):
            status = "[SOLVED]" if q.get('is_answered') else "[OPEN]"
            result += f"{i}. {q.get('title', '')} {status}\n"
        cache.set("stackoverflow", query, result)
        return result, False
    except Exception as e:
        return f"Error: {e}", False


# =============================================================================
# TOOL FUNCTIONS
# =============================================================================

def extract_pdf(file_path: str, max_pages: int = None) -> str:
    result = pdf_manager.extract_text(file_path, max_pages)
    if not result["success"]:
        return f"Error: {result.get('error')}"
    return f"PDF: {result['file_name']}\nPages: {result['extracted_pages']}/{result['total_pages']}\n\n{result['text'][:8000]}"

def analyze_arxiv_paper(arxiv_id: str, max_pages: int = 15) -> str:
    download = pdf_manager.download_arxiv_pdf(arxiv_id)
    if not download["success"]:
        return f"Error: {download.get('error')}"
    extract = pdf_manager.extract_text(download["file_path"], max_pages)
    if not extract["success"]:
        return f"Error: {extract.get('error')}"
    return f"arXiv {arxiv_id}:\n\n{extract['text'][:10000]}"

def create_flowchart(description: str, direction: str = "TD") -> str:
    diagram = diagram_generator.generate_flowchart(description, direction)
    filepath = diagram_generator.save_diagram(diagram)
    return f"Flowchart saved to: {filepath}\n\n```mermaid\n{diagram.mermaid_code}\n```"

def create_mindmap(topic: str, subtopics: str = None) -> str:
    diagram = diagram_generator.generate_mindmap(topic, subtopics)
    filepath = diagram_generator.save_diagram(diagram)
    return f"Mindmap saved to: {filepath}\n\n```mermaid\n{diagram.mermaid_code}\n```"


# =============================================================================
# AGENT TYPES
# =============================================================================

class AgentRole(Enum):
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"
    DIAGRAMMER = "diagrammer"


@dataclass
class TaskResult:
    agent: AgentRole
    success: bool
    result: str
    tokens_used: int = 0
    execution_time_ms: float = 0


@dataclass
class ResearchPlan:
    query: str
    complexity: str
    steps: list
    agents_needed: list
    estimated_sources: list
    include_diagram: bool = False


# =============================================================================
# SPECIALIZED AGENTS (with token tracking)
# =============================================================================

class BaseAgent:
    def __init__(self, role: AgentRole, client: Anthropic):
        self.role = role
        self.client = client
        self.execution_history = []

    def _call_llm(self, system: str, messages: list, tools: list = None, max_tokens: int = 2048):
        kwargs = {"model": "claude-sonnet-4-5", "max_tokens": max_tokens, "system": system, "messages": messages}
        if tools:
            kwargs["tools"] = tools
        response = self.client.messages.create(**kwargs)

        # Track tokens
        token_tracker.track(response, agent=self.role.value)

        return response

    def log_execution(self, task: str, time_ms: float):
        self.execution_history.append({"task": task, "time_ms": time_ms})


class ResearcherAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a RESEARCHER agent. Gather information from APIs and PDFs.
Use tools to search arXiv, Wikipedia, GitHub, HackerNews, StackOverflow."""

    TOOLS = [
        {"name": "search_arxiv", "description": "Search arXiv papers",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "search_wikipedia", "description": "Search Wikipedia",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "search_github_repos", "description": "Search GitHub",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "search_hackernews", "description": "Search HackerNews",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "search_stackoverflow", "description": "Search Stack Overflow",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    ]

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.RESEARCHER, client)

    def research(self, query: str, sources: list = None) -> TaskResult:
        start_time = time.time()
        sources = sources or ["arxiv", "wikipedia"]
        display_agent_activity(self.role, f"Researching: {query}")

        messages = [{"role": "user", "content": f"Research: {query}\nSources: {', '.join(sources)}"}]
        conversation = messages.copy()
        findings = []
        total_tokens = 0

        while True:
            response = self._call_llm(self.SYSTEM_PROMPT, conversation, self.TOOLS)
            total_tokens += response.usage.input_tokens + response.usage.output_tokens

            if response.stop_reason == "end_turn":
                final_text = "".join(b.text for b in response.content if hasattr(b, "text"))
                findings.append(final_text)
                break
            elif response.stop_reason == "tool_use":
                conversation.append({"role": "assistant", "content": response.content})
                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        name, inp = block.name, block.input
                        display_agent_activity(self.role, f"  -> {name}")

                        if name == "search_arxiv":
                            result, _ = search_arxiv(inp["query"])
                        elif name == "search_wikipedia":
                            result, _ = search_wikipedia(inp["query"])
                        elif name == "search_github_repos":
                            result, _ = search_github_repos(inp["query"])
                        elif name == "search_hackernews":
                            result, _ = search_hackernews(inp["query"])
                        elif name == "search_stackoverflow":
                            result, _ = search_stackoverflow(inp["query"])
                        else:
                            result = f"Unknown: {name}"

                        findings.append(f"[{name}]\n{result}")
                        tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

                conversation.append({"role": "user", "content": tool_results})
            else:
                break

        elapsed = (time.time() - start_time) * 1000
        self.log_execution(query, elapsed)
        return TaskResult(self.role, True, "\n\n---\n\n".join(findings), total_tokens, elapsed)


class AnalystAgent(BaseAgent):
    SYSTEM_PROMPT = """You are an ANALYST. Synthesize findings: KEY FINDINGS, PATTERNS, CONCLUSIONS."""

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.ANALYST, client)

    def analyze(self, research_data: str) -> TaskResult:
        start_time = time.time()
        display_agent_activity(self.role, "Analyzing...")

        response = self._call_llm(self.SYSTEM_PROMPT,
                                  [{"role": "user", "content": f"Analyze:\n\n{research_data}"}])
        analysis = "".join(b.text for b in response.content if hasattr(b, "text"))
        tokens = response.usage.input_tokens + response.usage.output_tokens

        elapsed = (time.time() - start_time) * 1000
        self.log_execution("analysis", elapsed)
        return TaskResult(self.role, True, analysis, tokens, elapsed)


class WriterAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a WRITER. Create clear, formatted content: SUMMARY or REPORT."""

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.WRITER, client)

    def write(self, content: str, format_type: str = "REPORT") -> TaskResult:
        start_time = time.time()
        display_agent_activity(self.role, f"Writing {format_type}...")

        response = self._call_llm(self.SYSTEM_PROMPT,
                                  [{"role": "user", "content": f"Create {format_type}:\n\n{content}"}],
                                  max_tokens=3000)
        written = "".join(b.text for b in response.content if hasattr(b, "text"))
        tokens = response.usage.input_tokens + response.usage.output_tokens

        elapsed = (time.time() - start_time) * 1000
        self.log_execution(format_type, elapsed)
        return TaskResult(self.role, True, written, tokens, elapsed)


class CoordinatorAgent(BaseAgent):
    SYSTEM_PROMPT = """You are the COORDINATOR. Create JSON execution plans:
{"complexity": "simple|moderate|complex", "agents": ["researcher", "analyst", "writer"],
"sources": ["arxiv", "wikipedia"], "include_diagram": false}"""

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.COORDINATOR, client)
        self.researcher = ResearcherAgent(client)
        self.analyst = AnalystAgent(client)
        self.writer = WriterAgent(client)

    def create_plan(self, query: str) -> ResearchPlan:
        display_agent_activity(self.role, "Creating plan...")

        response = self._call_llm(self.SYSTEM_PROMPT,
                                  [{"role": "user", "content": f"Plan for: {query}\n\nJSON only."}],
                                  max_tokens=500)
        plan_text = "".join(b.text for b in response.content if hasattr(b, "text"))

        try:
            match = re.search(r'\{[^{}]*\}', plan_text, re.DOTALL)
            plan_data = json.loads(match.group()) if match else {}
        except:
            plan_data = {"complexity": "moderate", "agents": ["researcher", "writer"], "sources": ["wikipedia"]}

        return ResearchPlan(
            query=query,
            complexity=plan_data.get("complexity", "moderate"),
            steps=plan_data.get("plan", []),
            agents_needed=plan_data.get("agents", ["researcher", "writer"]),
            estimated_sources=plan_data.get("sources", ["wikipedia"]),
            include_diagram=plan_data.get("include_diagram", False)
        )

    def execute(self, query: str) -> str:
        start_time = time.time()
        plan = self.create_plan(query)
        display_plan(plan)

        results = []
        total_tokens = 0

        if "researcher" in plan.agents_needed:
            result = self.researcher.research(query, plan.estimated_sources)
            results.append(result)
            total_tokens += result.tokens_used
            display_agent_result(result)

        if "analyst" in plan.agents_needed and results:
            result = self.analyst.analyze(results[-1].result)
            results.append(result)
            total_tokens += result.tokens_used
            display_agent_result(result)

        if "writer" in plan.agents_needed:
            content = results[-1].result if results else query
            fmt = "REPORT" if plan.complexity == "complex" else "SUMMARY"
            result = self.writer.write(content, fmt)
            results.append(result)
            total_tokens += result.tokens_used
            display_agent_result(result)

        total_time = (time.time() - start_time) * 1000
        display_execution_summary(plan, results, total_time, total_tokens)

        return results[-1].result if results else "No results."


# =============================================================================
# UI HELPERS
# =============================================================================

def display_welcome():
    text = """[bold cyan]RESEARCH ASSISTANT + TOKEN TRACKING[/bold cyan] [dim]v14.0[/dim]

[yellow]Knowledge Sources:[/yellow]
  [green]ARXIV[/green]     Academic papers          [green]WIKI[/green]      Wikipedia
  [green]GITHUB[/green]    Repositories             [green]HACKER[/green]    HackerNews
  [green]STACK[/green]     Stack Overflow           [magenta]PDF[/magenta]       Local PDFs

[yellow]Token Commands:[/yellow]
  [cyan]tokens[/cyan]           Show detailed token usage
  [cyan]cost[/cyan]             Show cost breakdown
  [cyan]budget <n>[/cyan]       Set token budget warning

[yellow]Diagram Commands:[/yellow]
  [cyan]flowchart <desc>[/cyan]   Create flowchart
  [cyan]mindmap <topic>[/cyan]    Create mindmap

[yellow]Other Commands:[/yellow]
  [cyan]stats[/cyan]    Statistics    [cyan]agents[/cyan]   Agent status    [cyan]quit[/cyan]     Exit"""

    console.print(Panel(text, title="[bold white]Welcome[/bold white]", border_style="blue", box=box.DOUBLE))


def display_agent_activity(role: AgentRole, message: str):
    colors = {AgentRole.COORDINATOR: "blue", AgentRole.RESEARCHER: "green",
              AgentRole.ANALYST: "magenta", AgentRole.WRITER: "cyan",
              AgentRole.DIAGRAMMER: "yellow"}
    console.print(f"  [{colors.get(role, 'white')}]{role.value.upper()}[/{colors.get(role, 'white')}] {message}")


def display_plan(plan: ResearchPlan):
    tree = Tree(f"[bold blue]Plan[/bold blue] ({plan.complexity})")
    tree.add("[yellow]Agents:[/yellow] " + ", ".join(plan.agents_needed))
    tree.add("[yellow]Sources:[/yellow] " + ", ".join(plan.estimated_sources))
    console.print(tree)
    console.print()


def display_agent_result(result: TaskResult):
    colors = {AgentRole.RESEARCHER: "green", AgentRole.ANALYST: "magenta",
              AgentRole.WRITER: "cyan", AgentRole.DIAGRAMMER: "yellow"}
    color = colors.get(result.agent, "white")
    console.print(f"  [{color}]{result.agent.value.upper()}[/{color}] Done "
                 f"({result.execution_time_ms:.0f}ms, {result.tokens_used:,} tokens)")


def display_execution_summary(plan: ResearchPlan, results: list, total_time_ms: float, total_tokens: int):
    table = Table(title="Summary", box=box.ROUNDED, border_style="blue")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Complexity", plan.complexity)
    table.add_row("Agents", ", ".join(plan.agents_needed))
    table.add_row("Total Time", f"{total_time_ms:.0f}ms")
    table.add_row("Tokens Used", f"{total_tokens:,}")
    table.add_row("Est. Cost", f"${token_tracker.estimate_cost():.4f}")
    console.print()
    console.print(table)


def display_response(text: str):
    console.print()
    console.print(Panel(Markdown(text), title="[cyan]Report[/cyan]", border_style="cyan", box=box.ROUNDED))


# =============================================================================
# MAIN
# =============================================================================

def main():
    console.clear()
    display_welcome()
    console.print()

    coordinator = CoordinatorAgent(client)

    try:
        while True:
            # Show compact token stats
            if token_tracker.api_calls > 0:
                token_tracker.display_compact()

            console.print()
            user_input = console.input("[bold green]You:[/bold green] ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'quit':
                console.print("\n[dim]Saving session...[/dim]")
                token_tracker.save_session()
                console.print("[dim]Goodbye![/dim]")
                break

            if user_input.lower() == 'tokens':
                token_tracker.display_stats()
                continue

            if user_input.lower() == 'cost':
                stats = token_tracker.get_session_stats()
                console.print(f"\n[bold]Session Cost:[/bold] ${stats['estimated_cost_usd']:.4f}")
                console.print(f"[dim]Input: {stats['input_tokens']:,} tokens[/dim]")
                console.print(f"[dim]Output: {stats['output_tokens']:,} tokens[/dim]")

                # Show historical stats
                hist = token_tracker.get_historical_stats(7)
                if hist['sessions'] > 0:
                    console.print(f"\n[bold]Last 7 Days:[/bold]")
                    console.print(f"  Sessions: {hist['sessions']}")
                    console.print(f"  Total: {hist['total_tokens']:,} tokens (${hist['total_cost']:.2f})")
                continue

            if user_input.lower().startswith('budget '):
                try:
                    budget = int(user_input[7:].strip())
                    token_tracker.budget = budget
                    console.print(f"[green]Budget set to {budget:,} tokens[/green]")
                except:
                    console.print("[red]Usage: budget <number>[/red]")
                continue

            if user_input.lower() == 'stats':
                cs = cache.get_stats()
                console.print(f"[cyan]Cache:[/cyan] {cs['entries']} entries, {cs['hit_rate']} hit rate")
                console.print(f"[cyan]Diagrams:[/cyan] {len(diagram_generator.list_diagrams())} saved")
                console.print(f"[cyan]PDFs:[/cyan] {len(pdf_manager.list_pdfs())} downloaded")
                continue

            if user_input.lower() == 'agents':
                table = Table(title="Agents", box=box.ROUNDED)
                table.add_column("Agent")
                table.add_column("Tasks")
                for agent in [coordinator, coordinator.researcher, coordinator.analyst, coordinator.writer]:
                    table.add_row(agent.role.value.upper(), str(len(agent.execution_history)))
                console.print(table)
                continue

            if user_input.lower().startswith('flowchart '):
                desc = user_input[10:].strip()
                result = create_flowchart(desc)
                console.print(Panel(result, title="Flowchart", border_style="yellow"))
                continue

            if user_input.lower().startswith('mindmap '):
                topic = user_input[8:].strip()
                result = create_mindmap(topic)
                console.print(Panel(result, title="Mindmap", border_style="yellow"))
                continue

            if user_input.lower().startswith('pdf '):
                path = user_input[4:].strip().strip('"\'')
                result = extract_pdf(path)
                console.print(Panel(result[:3000], title="PDF", border_style="magenta"))
                continue

            if user_input.lower().startswith('arxiv '):
                arxiv_id = user_input[6:].strip()
                result = analyze_arxiv_paper(arxiv_id)
                console.print(Panel(result[:3000], title=f"arXiv {arxiv_id}", border_style="magenta"))
                continue

            # Multi-agent workflow
            console.print()
            result = coordinator.execute(user_input)
            display_response(result)

    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted. Saving session...[/dim]")
        token_tracker.save_session()


if __name__ == "__main__":
    main()
