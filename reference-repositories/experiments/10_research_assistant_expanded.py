#!/usr/bin/env python3
"""
Level 10: Research Assistant with Expanded APIs & Caching
- NEW: HackerNews API for tech news
- NEW: Stack Overflow API for programming Q&A
- NEW: Response caching to reduce API calls
- All previous features: Smart memory, topic tracking, Rich UI
"""

import os
import json
import requests
import time
import hashlib
from anthropic import Anthropic
from datetime import datetime, timedelta
from pathlib import Path

# Rich library imports
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

# Initialize Rich console
console = Console()

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
if not ANTHROPIC_API_KEY:
    ANTHROPIC_API_KEY = "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"

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Data directory for persistent storage
DATA_DIR = Path(__file__).parent / "research_data"
DATA_DIR.mkdir(exist_ok=True)

TOPICS_FILE = DATA_DIR / "topics.json"
SUMMARIES_FILE = DATA_DIR / "summaries.json"
CACHE_FILE = DATA_DIR / "api_cache.json"


# =============================================================================
# RESPONSE CACHE - Avoid redundant API calls
# =============================================================================

class ResponseCache:
    """
    Caches API responses to avoid redundant calls.
    Configurable TTL (time-to-live) per source.
    """

    DEFAULT_TTL = {
        "arxiv": 3600,        # 1 hour - papers don't change often
        "wikipedia": 3600,    # 1 hour
        "github": 300,        # 5 minutes - repos change more often
        "hackernews": 300,    # 5 minutes - news is time-sensitive
        "stackoverflow": 1800, # 30 minutes
        "books": 86400,       # 24 hours - books rarely change
        "dictionary": 86400,  # 24 hours - definitions don't change
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
                return {"entries": {}}
        return {"entries": {}}

    def _save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def _make_key(self, source: str, query: str) -> str:
        """Create a unique cache key"""
        normalized = f"{source}:{query.lower().strip()}"
        return hashlib.md5(normalized.encode()).hexdigest()

    def get(self, source: str, query: str) -> str | None:
        """Get cached response if valid"""
        key = self._make_key(source, query)
        entry = self.cache["entries"].get(key)

        if not entry:
            self.stats["misses"] += 1
            return None

        # Check TTL
        cached_at = datetime.fromisoformat(entry["cached_at"])
        ttl = self.DEFAULT_TTL.get(source, 3600)
        if datetime.now() - cached_at > timedelta(seconds=ttl):
            self.stats["misses"] += 1
            return None

        self.stats["hits"] += 1
        return entry["response"]

    def set(self, source: str, query: str, response: str):
        """Cache a response"""
        key = self._make_key(source, query)
        self.cache["entries"][key] = {
            "source": source,
            "query": query,
            "response": response,
            "cached_at": datetime.now().isoformat()
        }
        self._save()

    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": f"{hit_rate:.1f}%",
            "entries": len(self.cache["entries"])
        }

    def clear(self):
        """Clear all cached responses"""
        self.cache = {"entries": {}}
        self._save()


# Initialize global cache
cache = ResponseCache()


# =============================================================================
# TOPIC TRACKER (from Level 9)
# =============================================================================

class TopicTracker:
    def __init__(self, filepath: Path = TOPICS_FILE):
        self.filepath = filepath
        self.topics = self._load()

    def _load(self) -> dict:
        if self.filepath.exists():
            with open(self.filepath, 'r') as f:
                return json.load(f)
        return {"topics": {}, "created_at": datetime.now().isoformat()}

    def _save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.topics, f, indent=2)

    def add_topic(self, topic: str, query: str, sources: list = None):
        topic_lower = topic.lower().strip()
        if topic_lower not in self.topics["topics"]:
            self.topics["topics"][topic_lower] = {
                "count": 0, "first_accessed": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(), "queries": [], "sources_used": {}
            }
        data = self.topics["topics"][topic_lower]
        data["count"] += 1
        data["last_accessed"] = datetime.now().isoformat()
        if query not in data["queries"]:
            data["queries"].append(query)
            if len(data["queries"]) > 10:
                data["queries"].pop(0)
        if sources:
            for s in sources:
                data["sources_used"][s] = data["sources_used"].get(s, 0) + 1
        self._save()

    def get_all_topics(self) -> dict:
        return self.topics["topics"]

    def get_recent_topics(self, limit: int = 5) -> list:
        return sorted(self.topics["topics"].items(), key=lambda x: x[1]["last_accessed"], reverse=True)[:limit]

    def find_related_topics(self, query: str) -> list:
        query_words = set(query.lower().split())
        related = []
        for topic, data in self.topics["topics"].items():
            if query_words & set(topic.split()) or topic in query.lower():
                related.append((topic, data))
        return related


# =============================================================================
# CONVERSATION SUMMARIZER (from Level 9)
# =============================================================================

class ConversationSummarizer:
    def __init__(self, client: Anthropic, filepath: Path = SUMMARIES_FILE):
        self.client = client
        self.filepath = filepath
        self.summaries = self._load()
        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _load(self) -> dict:
        if self.filepath.exists():
            with open(self.filepath, 'r') as f:
                return json.load(f)
        return {"sessions": {}}

    def _save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.summaries, f, indent=2)

    def summarize_messages(self, messages: list) -> str:
        if not messages:
            return ""
        formatted = [f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content'][:500]}" for m in messages]
        with Progress(SpinnerColumn(), TextColumn("[dim]Summarizing...[/dim]"), console=console, transient=True) as p:
            p.add_task("", total=None)
            response = self.client.messages.create(
                model="claude-sonnet-4-5", max_tokens=300,
                messages=[{"role": "user", "content": f"Summarize this research conversation in 2-3 sentences:\n\n{chr(10).join(formatted)}\n\nSummary:"}]
            )
        summary = response.content[0].text.strip()
        if self.current_session_id not in self.summaries["sessions"]:
            self.summaries["sessions"][self.current_session_id] = {"summaries": [], "started_at": datetime.now().isoformat()}
        self.summaries["sessions"][self.current_session_id]["summaries"].append({
            "summary": summary, "message_count": len(messages), "created_at": datetime.now().isoformat()
        })
        self._save()
        return summary

    def get_session_context(self) -> str:
        if self.current_session_id not in self.summaries["sessions"]:
            return ""
        return "\n".join(s["summary"] for s in self.summaries["sessions"][self.current_session_id]["summaries"])

    def get_all_sessions(self) -> dict:
        return self.summaries["sessions"]


# =============================================================================
# SMART MEMORY (from Level 9)
# =============================================================================

class SmartMemory:
    def __init__(self, client: Anthropic, model: str = "claude-sonnet-4-5", max_tokens: int = 8000):
        self.client = client
        self.model = model
        self.max_tokens = max_tokens
        self.messages = []
        self.topic_tracker = TopicTracker()
        self.summarizer = ConversationSummarizer(client)
        self.token_stats = {"api_calls": 0, "total_time_ms": 0, "summaries_created": 0}

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self._trim_with_summary()

    def _count_tokens(self) -> int:
        if not self.messages:
            return 0
        start = time.time()
        try:
            response = self.client.messages.count_tokens(model=self.model, messages=self.messages)
            self.token_stats["api_calls"] += 1
            self.token_stats["total_time_ms"] += (time.time() - start) * 1000
            return response.input_tokens
        except:
            return sum(len(m["content"]) for m in self.messages) // 4

    def _trim_with_summary(self):
        current = self._count_tokens()
        if current > self.max_tokens and len(self.messages) > 4:
            to_prune = []
            while current > self.max_tokens * 0.7 and len(self.messages) > 4:
                if self.messages:
                    to_prune.append(self.messages.pop(0))
                if self.messages and self.messages[0]["role"] == "assistant":
                    to_prune.append(self.messages.pop(0))
                current = self._count_tokens()
            if to_prune:
                console.print(f"[dim][MEMORY] Pruning {len(to_prune)} messages...[/dim]")
                self.summarizer.summarize_messages(to_prune)
                self.token_stats["summaries_created"] += 1

    def get_messages(self) -> list:
        return self.messages.copy()

    def get_enriched_context(self, query: str) -> str:
        parts = []
        session = self.summarizer.get_session_context()
        if session:
            parts.append(f"Previous context:\n{session}")
        related = self.topic_tracker.find_related_topics(query)
        if related:
            topic_ctx = "Related past research:\n"
            for t, d in related[:3]:
                topic_ctx += f"- {t.title()}: {d['count']} times\n"
            parts.append(topic_ctx)
        return "\n\n".join(parts)

    def track_topic(self, topic: str, query: str, sources: list = None):
        self.topic_tracker.add_topic(topic, query, sources)

    def get_stats(self) -> dict:
        tokens = self._count_tokens()
        return {
            "message_count": len(self.messages), "current_tokens": tokens,
            "max_tokens": self.max_tokens, "utilization": tokens / self.max_tokens * 100,
            "summaries_created": self.token_stats["summaries_created"],
            "tracked_topics": len(self.topic_tracker.get_all_topics()),
            "session_id": self.summarizer.current_session_id
        }

    def clear(self):
        self.messages = []


# =============================================================================
# API FUNCTIONS - WITH CACHING
# =============================================================================

def search_arxiv(query, max_results=5):
    """Search arXiv for academic papers (cached)"""
    cached = cache.get("arxiv", query)
    if cached:
        console.print("[dim](cached)[/dim]", end=" ")
        return cached

    try:
        response = requests.get(
            "http://export.arxiv.org/api/query",
            params={"search_query": f"all:{query}", "start": 0, "max_results": max_results,
                    "sortBy": "relevance", "sortOrder": "descending"},
            timeout=10
        )
        if response.status_code != 200:
            return f"Error: status {response.status_code}"

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
            return "No papers found."

        result = f"Found {len(papers)} papers:\n\n"
        for i, p in enumerate(papers, 1):
            result += f"{i}. {p['title']}\n   Authors: {', '.join(p['authors'][:3])}\n"
            result += f"   Published: {p['published']}\n   {p['link']}\n\n"

        cache.set("arxiv", query, result)
        return result
    except Exception as e:
        return f"Error: {e}"


def search_wikipedia(query):
    """Search Wikipedia (cached)"""
    cached = cache.get("wikipedia", query)
    if cached:
        console.print("[dim](cached)[/dim]", end=" ")
        return cached

    try:
        response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "format": "json", "list": "search", "srsearch": query, "srlimit": 3},
            timeout=10
        )
        data = response.json()
        if not data.get('query', {}).get('search'):
            return "No articles found."

        result = f"Found {len(data['query']['search'])} articles:\n\n"
        for i, a in enumerate(data['query']['search'], 1):
            result += f"{i}. {a['title']}\n   {a['snippet']}\n"
            result += f"   https://en.wikipedia.org/wiki/{a['title'].replace(' ', '_')}\n\n"

        cache.set("wikipedia", query, result)
        return result
    except Exception as e:
        return f"Error: {e}"


def search_dictionary(word):
    """Dictionary lookup (cached)"""
    cached = cache.get("dictionary", word)
    if cached:
        console.print("[dim](cached)[/dim]", end=" ")
        return cached

    try:
        response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=10)
        if response.status_code == 404:
            return f"No definition for '{word}'"

        data = response.json()
        result = f"Definition of '{word}':\n\n"
        for meaning in data[0].get('meanings', []):
            result += f"{meaning['partOfSpeech'].upper()}:\n"
            for i, d in enumerate(meaning.get('definitions', [])[:3], 1):
                result += f"  {i}. {d['definition']}\n"
            result += "\n"

        cache.set("dictionary", word, result)
        return result
    except Exception as e:
        return f"Error: {e}"


def search_github_repos(query, max_results=5):
    """Search GitHub (cached)"""
    cached = cache.get("github", query)
    if cached:
        console.print("[dim](cached)[/dim]", end=" ")
        return cached

    try:
        response = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": query, "sort": "stars", "order": "desc", "per_page": max_results},
            headers={"User-Agent": "Research-Assistant"},
            timeout=10
        )
        if response.status_code == 403:
            return "GitHub rate limit reached."

        data = response.json()
        if data['total_count'] == 0:
            return f"No repos found for: {query}"

        result = f"Found {data['total_count']:,} repos:\n\n"
        for i, r in enumerate(data['items'], 1):
            result += f"{i}. {r['full_name']} ({r['stargazers_count']:,} stars)\n"
            result += f"   {r['description'] or 'No description'}\n   {r['html_url']}\n\n"

        cache.set("github", query, result)
        return result
    except Exception as e:
        return f"Error: {e}"


def search_books(query, max_results=5):
    """Search Open Library (cached)"""
    cached = cache.get("books", query)
    if cached:
        console.print("[dim](cached)[/dim]", end=" ")
        return cached

    try:
        response = requests.get(
            "https://openlibrary.org/search.json",
            params={"q": query, "limit": max_results},
            timeout=10
        )
        data = response.json()
        if not data.get('docs'):
            return f"No books found for: {query}"

        result = f"Found {data['numFound']:,} books:\n\n"
        for i, b in enumerate(data['docs'], 1):
            result += f"{i}. {b.get('title', 'Unknown')}\n"
            result += f"   Author: {', '.join(b.get('author_name', ['Unknown'])[:2])}\n"
            result += f"   Published: {b.get('first_publish_year', 'N/A')}\n\n"

        cache.set("books", query, result)
        return result
    except Exception as e:
        return f"Error: {e}"


# =============================================================================
# NEW APIs: HACKERNEWS & STACK OVERFLOW
# =============================================================================

def search_hackernews(query, max_results=5):
    """
    Search HackerNews for tech news and discussions.
    Uses the Algolia HN Search API.
    """
    cached = cache.get("hackernews", query)
    if cached:
        console.print("[dim](cached)[/dim]", end=" ")
        return cached

    try:
        # Algolia HN Search API
        response = requests.get(
            "https://hn.algolia.com/api/v1/search",
            params={
                "query": query,
                "tags": "story",  # Only stories, not comments
                "hitsPerPage": max_results
            },
            timeout=10
        )

        if response.status_code != 200:
            return f"Error: HackerNews API returned status {response.status_code}"

        data = response.json()
        hits = data.get('hits', [])

        if not hits:
            return f"No HackerNews stories found for: {query}"

        result = f"Found {data.get('nbHits', 0):,} HackerNews stories (showing top {len(hits)}):\n\n"

        for i, story in enumerate(hits, 1):
            title = story.get('title', 'No title')
            points = story.get('points', 0)
            comments = story.get('num_comments', 0)
            author = story.get('author', 'unknown')
            url = story.get('url', '')
            hn_url = f"https://news.ycombinator.com/item?id={story.get('objectID', '')}"
            created = story.get('created_at', '')[:10]

            result += f"{i}. {title}\n"
            result += f"   Points: {points} | Comments: {comments} | By: {author} | {created}\n"
            if url:
                result += f"   Link: {url}\n"
            result += f"   Discussion: {hn_url}\n\n"

        cache.set("hackernews", query, result)
        return result

    except Exception as e:
        return f"Error searching HackerNews: {str(e)}"


def search_stackoverflow(query, max_results=5):
    """
    Search Stack Overflow for programming Q&A.
    Uses the Stack Exchange API (no key required for basic usage).
    """
    cached = cache.get("stackoverflow", query)
    if cached:
        console.print("[dim](cached)[/dim]", end=" ")
        return cached

    try:
        response = requests.get(
            "https://api.stackexchange.com/2.3/search/advanced",
            params={
                "order": "desc",
                "sort": "relevance",
                "q": query,
                "site": "stackoverflow",
                "pagesize": max_results,
                "filter": "!nNPvSNdWme"  # Include body excerpt
            },
            timeout=10
        )

        if response.status_code != 200:
            return f"Error: Stack Overflow API returned status {response.status_code}"

        data = response.json()
        items = data.get('items', [])

        if not items:
            return f"No Stack Overflow questions found for: {query}"

        result = f"Found Stack Overflow questions for '{query}':\n\n"

        for i, q in enumerate(items, 1):
            title = q.get('title', 'No title')
            # Decode HTML entities
            title = title.replace('&#39;', "'").replace('&quot;', '"').replace('&amp;', '&')
            title = title.replace('&lt;', '<').replace('&gt;', '>')

            score = q.get('score', 0)
            answers = q.get('answer_count', 0)
            is_answered = q.get('is_answered', False)
            views = q.get('view_count', 0)
            link = q.get('link', '')
            tags = q.get('tags', [])[:4]

            status = "[SOLVED]" if is_answered else "[OPEN]"
            status_color = "green" if is_answered else "yellow"

            result += f"{i}. {title}\n"
            result += f"   {status} Score: {score} | Answers: {answers} | Views: {views:,}\n"
            result += f"   Tags: {', '.join(tags)}\n"
            result += f"   Link: {link}\n\n"

        # Check API quota
        quota = data.get('quota_remaining', 'unknown')
        result += f"[API quota remaining: {quota}]\n"

        cache.set("stackoverflow", query, result)
        return result

    except Exception as e:
        return f"Error searching Stack Overflow: {str(e)}"


def save_research_note(topic, content):
    """Save research notes"""
    notes_file = DATA_DIR / "research_notes.json"
    try:
        notes = {"notes": []}
        if notes_file.exists():
            with open(notes_file, 'r') as f:
                notes = json.load(f)
        notes["notes"].append({
            "topic": topic, "content": content, "timestamp": datetime.now().isoformat()
        })
        with open(notes_file, 'w') as f:
            json.dump(notes, f, indent=2)
        return f"Note saved: '{topic}'"
    except Exception as e:
        return f"Error: {e}"


# =============================================================================
# TOOL DEFINITIONS
# =============================================================================

TOOLS = [
    {
        "name": "search_arxiv",
        "description": "Search arXiv for academic papers. Use for AI/ML, physics, math, CS research.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_wikipedia",
        "description": "Search Wikipedia for general knowledge articles.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    },
    {
        "name": "search_dictionary",
        "description": "Look up word definitions.",
        "input_schema": {
            "type": "object",
            "properties": {"word": {"type": "string"}},
            "required": ["word"]
        }
    },
    {
        "name": "search_github_repos",
        "description": "Search GitHub for repositories and code projects.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_books",
        "description": "Search Open Library for books.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_hackernews",
        "description": "Search HackerNews for tech news, startup discussions, and programming articles. Great for current tech trends and community discussions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query for tech news"},
                "max_results": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_stackoverflow",
        "description": "Search Stack Overflow for programming questions and answers. Use for coding problems, error messages, how-to questions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Programming question or error message"},
                "max_results": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "save_research_note",
        "description": "Save research notes for later.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["topic", "content"]
        }
    }
]

SYSTEM_PROMPT = """You are a research assistant with access to multiple knowledge sources.

Your capabilities:
- Search arXiv for academic papers
- Look up Wikipedia articles
- Get dictionary definitions
- Search GitHub repositories
- Find books on any topic
- Search HackerNews for tech news and discussions
- Search Stack Overflow for programming Q&A
- Save research notes

When answering questions:
1. Choose the most appropriate sources for the query type
2. For programming questions, prefer Stack Overflow
3. For current tech news/trends, use HackerNews
4. For academic research, use arXiv
5. Synthesize information from multiple sources when helpful
6. Cite your sources

Be helpful, thorough, and accurate."""


# =============================================================================
# UI HELPERS
# =============================================================================

def display_welcome():
    text = """[bold cyan]RESEARCH ASSISTANT[/bold cyan] [dim]v10.0 - Expanded Edition[/dim]

[yellow]Knowledge Sources:[/yellow]
  [green]ARXIV[/green]     Academic papers          [green]WIKI[/green]      Wikipedia
  [green]GITHUB[/green]    Code repositories        [green]BOOKS[/green]     Open Library
  [blue]HACKER[/blue]    HackerNews tech news     [blue]STACK[/blue]     Stack Overflow Q&A
  [green]DICT[/green]      Dictionary               [green]NOTES[/green]     Save notes

[yellow]Smart Features:[/yellow]
  [magenta]Caching[/magenta]     Responses cached to reduce API calls
  [magenta]Topics[/magenta]      Research topics tracked across sessions
  [magenta]Summaries[/magenta]   Auto-summarizes when memory is pruned

[yellow]Commands:[/yellow]
  [cyan]stats[/cyan]    Memory stats    [cyan]cache[/cyan]    Cache stats    [cyan]topics[/cyan]   View topics
  [cyan]clear[/cyan]    Clear chat      [cyan]clearcache[/cyan] Clear cache  [cyan]quit[/cyan]     Exit"""

    console.print(Panel(text, title="[bold white]Welcome[/bold white]", border_style="blue", box=box.DOUBLE))


def display_stats(stats: dict, cache_stats: dict):
    table = Table(title="Statistics", box=box.ROUNDED, border_style="cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    util = stats['utilization']
    util_color = "green" if util < 50 else "yellow" if util < 80 else "red"

    table.add_row("Messages", str(stats['message_count']))
    table.add_row("Tokens", f"{stats['current_tokens']:,} / {stats['max_tokens']:,}")
    table.add_row("Utilization", f"[{util_color}]{util:.1f}%[/{util_color}]")
    table.add_row("Topics Tracked", str(stats['tracked_topics']))
    table.add_row("Summaries", str(stats['summaries_created']))
    table.add_row("", "")
    table.add_row("[bold]Cache[/bold]", "")
    table.add_row("Entries", str(cache_stats['entries']))
    table.add_row("Hit Rate", cache_stats['hit_rate'])
    table.add_row("Hits / Misses", f"{cache_stats['hits']} / {cache_stats['misses']}")

    console.print(table)


def display_topics(tracker: TopicTracker):
    topics = tracker.get_all_topics()
    if not topics:
        console.print("[yellow]No topics tracked yet.[/yellow]")
        return

    table = Table(title="Research Topics", box=box.ROUNDED, border_style="magenta")
    table.add_column("Topic", style="magenta")
    table.add_column("Count", style="green")
    table.add_column("Sources", style="dim")

    for topic, data in tracker.get_recent_topics(10):
        sources = ", ".join(data.get('sources_used', {}).keys()) or "-"
        table.add_row(topic.title(), str(data['count']), sources)

    console.print(table)


def display_tool_use(name: str, query: str = None):
    icons = {
        "search_arxiv": "[red]ARXIV[/red]",
        "search_wikipedia": "[blue]WIKI[/blue]",
        "search_dictionary": "[yellow]DICT[/yellow]",
        "search_github_repos": "[white]GITHUB[/white]",
        "search_books": "[magenta]BOOKS[/magenta]",
        "search_hackernews": "[cyan]HACKER[/cyan]",
        "search_stackoverflow": "[green]STACK[/green]",
        "save_research_note": "[green]NOTES[/green]"
    }
    icon = icons.get(name, "[bold]TOOL[/bold]")
    console.print(f"  {icon} {query or 'Processing...'}")


def display_response(text: str):
    console.print()
    console.print(Panel(text, title="[cyan]Assistant[/cyan]", border_style="cyan", box=box.ROUNDED, padding=(1, 2)))
    console.print()


def extract_topics(client: Anthropic, query: str) -> list:
    try:
        r = client.messages.create(
            model="claude-sonnet-4-5", max_tokens=100,
            messages=[{"role": "user", "content": f"Extract 1-3 main topics (lowercase, one per line):\n{query}\n\nTopics:"}]
        )
        return [t.strip().lower() for t in r.content[0].text.strip().split('\n') if t.strip()]
    except:
        return [w for w in query.lower().split() if len(w) > 4][:3]


# =============================================================================
# MAIN
# =============================================================================

def research_assistant():
    console.clear()
    display_welcome()
    console.print()

    memory = SmartMemory(client=client, model="claude-sonnet-4-5", max_tokens=8000)

    while True:
        console.print()
        user_input = console.input("[bold green]You:[/bold green] ").strip()

        if not user_input:
            continue

        if user_input.lower() == 'quit':
            console.print("\n[dim]Goodbye![/dim]")
            break

        if user_input.lower() == 'stats':
            display_stats(memory.get_stats(), cache.get_stats())
            continue

        if user_input.lower() == 'cache':
            cs = cache.get_stats()
            console.print(f"[cyan]Cache:[/cyan] {cs['entries']} entries, {cs['hit_rate']} hit rate ({cs['hits']} hits, {cs['misses']} misses)")
            continue

        if user_input.lower() == 'clearcache':
            cache.clear()
            console.print("[yellow]Cache cleared.[/yellow]")
            continue

        if user_input.lower() == 'topics':
            display_topics(memory.topic_tracker)
            continue

        if user_input.lower() == 'clear':
            memory.clear()
            console.print("[yellow]Conversation cleared.[/yellow]")
            continue

        # Extract topics
        topics = extract_topics(client, user_input)

        # Get context
        context = memory.get_enriched_context(user_input)
        system = SYSTEM_PROMPT
        if context:
            system += f"\n\nUser's past research context:\n{context}"

        memory.add_message("user", user_input)
        conversation = memory.get_messages()
        sources_used = []

        with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console, transient=True) as prog:
            task = prog.add_task("[cyan]Thinking...", total=None)

            while True:
                response = client.messages.create(
                    model="claude-sonnet-4-5", max_tokens=4096,
                    system=system, tools=TOOLS, messages=conversation
                )
                prog.stop()

                if response.stop_reason == "end_turn":
                    text = "".join(b.text for b in response.content if hasattr(b, "text"))
                    display_response(text)
                    memory.add_message("assistant", text)

                    for t in topics:
                        memory.track_topic(t, user_input, sources_used)

                    stats = memory.get_stats()
                    cs = cache.get_stats()
                    util = stats['utilization']
                    uc = "green" if util < 50 else "yellow" if util < 80 else "red"
                    console.print(f"[dim]Memory: [{uc}]{util:.1f}%[/{uc}] | Cache: {cs['hit_rate']} hit rate[/dim]")
                    break

                elif response.stop_reason == "tool_use":
                    conversation.append({"role": "assistant", "content": response.content})
                    results = []

                    for block in response.content:
                        if block.type == "tool_use":
                            name = block.name
                            inp = block.input

                            source_map = {
                                "search_arxiv": "arxiv", "search_wikipedia": "wikipedia",
                                "search_github_repos": "github", "search_books": "books",
                                "search_hackernews": "hackernews", "search_stackoverflow": "stackoverflow"
                            }
                            if name in source_map:
                                sources_used.append(source_map[name])

                            q = inp.get("query") or inp.get("word") or inp.get("topic")
                            display_tool_use(name, q)

                            with Progress(SpinnerColumn(), TextColumn("[dim]Fetching...[/dim]"), console=console, transient=True) as p2:
                                p2.add_task("", total=None)

                                if name == "search_arxiv":
                                    result = search_arxiv(inp["query"], inp.get("max_results", 5))
                                elif name == "search_wikipedia":
                                    result = search_wikipedia(inp["query"])
                                elif name == "search_dictionary":
                                    result = search_dictionary(inp["word"])
                                elif name == "search_github_repos":
                                    result = search_github_repos(inp["query"], inp.get("max_results", 5))
                                elif name == "search_books":
                                    result = search_books(inp["query"], inp.get("max_results", 5))
                                elif name == "search_hackernews":
                                    result = search_hackernews(inp["query"], inp.get("max_results", 5))
                                elif name == "search_stackoverflow":
                                    result = search_stackoverflow(inp["query"], inp.get("max_results", 5))
                                elif name == "save_research_note":
                                    result = save_research_note(inp["topic"], inp["content"])
                                else:
                                    result = f"Unknown tool: {name}"

                            results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

                    conversation.append({"role": "user", "content": results})
                    prog.start()
                    prog.update(task, description="[cyan]Processing...")

                else:
                    console.print(f"[yellow]Unexpected: {response.stop_reason}[/yellow]")
                    break


if __name__ == "__main__":
    research_assistant()
