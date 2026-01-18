#!/usr/bin/env python3
"""
Level 9: Research Assistant with Smart Memory
- Conversation Summaries: Auto-generate summaries when context is pruned
- Topic Tracking: Track which topics user has researched across sessions
- Session Persistence: Remember past research sessions
"""

import os
import json
import requests
import time
from anthropic import Anthropic
from datetime import datetime
from pathlib import Path

# Rich library imports
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
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
SESSIONS_FILE = DATA_DIR / "sessions.json"
SUMMARIES_FILE = DATA_DIR / "summaries.json"


# =============================================================================
# TOPIC TRACKER - Tracks research topics across sessions
# =============================================================================

class TopicTracker:
    """
    Tracks topics the user has researched across sessions.
    Provides context about past research to enhance responses.
    """

    def __init__(self, filepath: Path = TOPICS_FILE):
        self.filepath = filepath
        self.topics = self._load()

    def _load(self) -> dict:
        """Load topics from file"""
        if self.filepath.exists():
            with open(self.filepath, 'r') as f:
                return json.load(f)
        return {
            "topics": {},  # topic -> {count, last_accessed, related_queries, sources}
            "created_at": datetime.now().isoformat()
        }

    def _save(self):
        """Save topics to file"""
        with open(self.filepath, 'w') as f:
            json.dump(self.topics, f, indent=2)

    def add_topic(self, topic: str, query: str, sources: list = None):
        """
        Add or update a topic with a new query.

        Args:
            topic: The main topic (e.g., "machine learning", "quantum computing")
            query: The specific query related to this topic
            sources: List of sources used (e.g., ["arxiv", "wikipedia"])
        """
        topic_lower = topic.lower().strip()

        if topic_lower not in self.topics["topics"]:
            self.topics["topics"][topic_lower] = {
                "count": 0,
                "first_accessed": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "queries": [],
                "sources_used": {}
            }

        topic_data = self.topics["topics"][topic_lower]
        topic_data["count"] += 1
        topic_data["last_accessed"] = datetime.now().isoformat()

        # Store query (keep last 10)
        if query not in topic_data["queries"]:
            topic_data["queries"].append(query)
            if len(topic_data["queries"]) > 10:
                topic_data["queries"].pop(0)

        # Track sources
        if sources:
            for source in sources:
                topic_data["sources_used"][source] = topic_data["sources_used"].get(source, 0) + 1

        self._save()

    def get_topic_context(self, topic: str) -> dict | None:
        """Get context about a previously researched topic"""
        topic_lower = topic.lower().strip()
        return self.topics["topics"].get(topic_lower)

    def get_all_topics(self) -> dict:
        """Get all tracked topics"""
        return self.topics["topics"]

    def get_recent_topics(self, limit: int = 5) -> list:
        """Get most recently accessed topics"""
        topics = self.topics["topics"]
        sorted_topics = sorted(
            topics.items(),
            key=lambda x: x[1]["last_accessed"],
            reverse=True
        )
        return sorted_topics[:limit]

    def get_frequent_topics(self, limit: int = 5) -> list:
        """Get most frequently accessed topics"""
        topics = self.topics["topics"]
        sorted_topics = sorted(
            topics.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        return sorted_topics[:limit]

    def find_related_topics(self, query: str) -> list:
        """Find topics that might be related to a query"""
        query_words = set(query.lower().split())
        related = []

        for topic, data in self.topics["topics"].items():
            topic_words = set(topic.lower().split())
            # Check if any words match
            if query_words & topic_words:
                related.append((topic, data))
            # Check if query contains the topic
            elif topic.lower() in query.lower():
                related.append((topic, data))

        return related


# =============================================================================
# CONVERSATION SUMMARIZER - Creates summaries when context is pruned
# =============================================================================

class ConversationSummarizer:
    """
    Creates and manages conversation summaries.
    When messages are pruned from memory, creates a summary to preserve context.
    """

    def __init__(self, client: Anthropic, filepath: Path = SUMMARIES_FILE):
        self.client = client
        self.filepath = filepath
        self.summaries = self._load()
        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _load(self) -> dict:
        """Load summaries from file"""
        if self.filepath.exists():
            with open(self.filepath, 'r') as f:
                return json.load(f)
        return {"sessions": {}}

    def _save(self):
        """Save summaries to file"""
        with open(self.filepath, 'w') as f:
            json.dump(self.summaries, f, indent=2)

    def summarize_messages(self, messages: list) -> str:
        """
        Generate a summary of messages being pruned.

        Args:
            messages: List of messages to summarize

        Returns:
            Summary string
        """
        if not messages:
            return ""

        # Format messages for summarization
        formatted = []
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"][:500]  # Truncate long messages
            formatted.append(f"{role}: {content}")

        messages_text = "\n".join(formatted)

        # Use Claude to generate summary
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            progress.add_task("[dim]Summarizing pruned conversation...", total=None)

            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": f"""Summarize this research conversation in 2-3 sentences. Focus on:
- Topics discussed
- Key findings or information discovered
- Any saved notes or conclusions

Conversation:
{messages_text}

Summary:"""
                }]
            )

        summary = response.content[0].text.strip()

        # Store the summary
        if self.current_session_id not in self.summaries["sessions"]:
            self.summaries["sessions"][self.current_session_id] = {
                "summaries": [],
                "started_at": datetime.now().isoformat()
            }

        self.summaries["sessions"][self.current_session_id]["summaries"].append({
            "summary": summary,
            "message_count": len(messages),
            "created_at": datetime.now().isoformat()
        })

        self._save()
        return summary

    def get_session_context(self) -> str:
        """Get accumulated context from current session summaries"""
        if self.current_session_id not in self.summaries["sessions"]:
            return ""

        session = self.summaries["sessions"][self.current_session_id]
        if not session["summaries"]:
            return ""

        summaries = [s["summary"] for s in session["summaries"]]
        return "\n".join(summaries)

    def get_all_sessions(self) -> dict:
        """Get all session summaries"""
        return self.summaries["sessions"]


# =============================================================================
# SMART MEMORY - Combines token buffer with summaries and topic tracking
# =============================================================================

class SmartMemory:
    """
    Advanced memory system that combines:
    - Accurate token counting
    - Automatic summarization when pruning
    - Topic tracking across sessions
    - Context injection from past research
    """

    def __init__(self, client: Anthropic, model: str = "claude-sonnet-4-5", max_tokens: int = 8000):
        self.client = client
        self.model = model
        self.max_tokens = max_tokens
        self.messages = []

        # Components
        self.topic_tracker = TopicTracker()
        self.summarizer = ConversationSummarizer(client)

        # Stats
        self.token_stats = {
            "api_calls": 0,
            "total_time_ms": 0,
            "summaries_created": 0
        }

    def add_message(self, role: str, content: str):
        """Add message with automatic pruning and summarization"""
        self.messages.append({"role": role, "content": content})
        self._trim_with_summary()

    def _count_tokens(self) -> int:
        """Get accurate token count"""
        if not self.messages:
            return 0

        start_time = time.time()
        try:
            response = self.client.messages.count_tokens(
                model=self.model,
                messages=self.messages
            )
            elapsed_ms = (time.time() - start_time) * 1000
            self.token_stats["api_calls"] += 1
            self.token_stats["total_time_ms"] += elapsed_ms
            return response.input_tokens
        except Exception as e:
            console.print(f"[yellow]Warning: Token counting failed: {e}[/yellow]")
            return sum(len(msg["content"]) for msg in self.messages) // 4

    def _trim_with_summary(self):
        """Prune messages with summarization to preserve context"""
        current_tokens = self._count_tokens()

        if current_tokens > self.max_tokens and len(self.messages) > 4:
            # Calculate how many messages to prune
            messages_to_prune = []

            while current_tokens > self.max_tokens * 0.7 and len(self.messages) > 4:
                # Remove oldest pair
                if self.messages:
                    messages_to_prune.append(self.messages.pop(0))
                if self.messages and self.messages[0]["role"] == "assistant":
                    messages_to_prune.append(self.messages.pop(0))
                current_tokens = self._count_tokens()

            # Create summary of pruned messages
            if messages_to_prune:
                console.print(f"[dim][MEMORY] Pruning {len(messages_to_prune)} messages and creating summary...[/dim]")
                summary = self.summarizer.summarize_messages(messages_to_prune)
                self.token_stats["summaries_created"] += 1
                console.print(f"[dim][MEMORY] Summary created: {summary[:100]}...[/dim]")

    def get_messages(self) -> list:
        """Get current conversation history"""
        return self.messages.copy()

    def get_enriched_context(self, query: str) -> str:
        """
        Get enriched context including:
        - Session summaries
        - Related topic history
        """
        context_parts = []

        # Add session summaries
        session_context = self.summarizer.get_session_context()
        if session_context:
            context_parts.append(f"Previous conversation context:\n{session_context}")

        # Add related topic history
        related_topics = self.topic_tracker.find_related_topics(query)
        if related_topics:
            topic_context = "User has previously researched related topics:\n"
            for topic, data in related_topics[:3]:
                topic_context += f"- {topic.title()}: researched {data['count']} times, "
                topic_context += f"last accessed {data['last_accessed'][:10]}\n"
                if data['queries']:
                    topic_context += f"  Previous queries: {', '.join(data['queries'][:3])}\n"
            context_parts.append(topic_context)

        return "\n\n".join(context_parts) if context_parts else ""

    def track_topic(self, topic: str, query: str, sources: list = None):
        """Track a researched topic"""
        self.topic_tracker.add_topic(topic, query, sources)

    def get_stats(self) -> dict:
        """Get memory statistics"""
        current_tokens = self._count_tokens()
        return {
            "message_count": len(self.messages),
            "current_tokens": current_tokens,
            "max_tokens": self.max_tokens,
            "utilization": current_tokens / self.max_tokens * 100,
            "api_calls": self.token_stats["api_calls"],
            "summaries_created": self.token_stats["summaries_created"],
            "tracked_topics": len(self.topic_tracker.get_all_topics()),
            "session_id": self.summarizer.current_session_id
        }

    def clear(self):
        """Clear current conversation (keeps topics and summaries)"""
        self.messages = []


# =============================================================================
# API HELPER FUNCTIONS (Same as before)
# =============================================================================

def search_arxiv(query, max_results=5):
    """Search arXiv for academic papers"""
    try:
        base_url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }

        response = requests.get(base_url, params=params, timeout=10)
        if response.status_code != 200:
            return f"Error: API returned status {response.status_code}", []

        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        papers = []
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}

        for entry in root.findall('atom:entry', namespace):
            paper = {
                "title": entry.find('atom:title', namespace).text.strip().replace('\n', ' '),
                "authors": [author.find('atom:name', namespace).text
                           for author in entry.findall('atom:author', namespace)],
                "summary": entry.find('atom:summary', namespace).text.strip()[:300] + "...",
                "published": entry.find('atom:published', namespace).text[:10],
                "link": entry.find('atom:id', namespace).text
            }
            papers.append(paper)

        if not papers:
            return "No papers found for your query.", []

        result = f"Found {len(papers)} papers on arXiv:\n\n"
        for i, paper in enumerate(papers, 1):
            result += f"{i}. {paper['title']}\n"
            result += f"   Authors: {', '.join(paper['authors'][:3])}\n"
            result += f"   Published: {paper['published']}\n"
            result += f"   Summary: {paper['summary']}\n"
            result += f"   Link: {paper['link']}\n\n"

        return result, papers

    except Exception as e:
        return f"Error searching arXiv: {str(e)}", []


def search_wikipedia(query):
    """Search Wikipedia"""
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": 3
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if not data.get('query', {}).get('search'):
            return "No Wikipedia articles found."

        result = f"Found {len(data['query']['search'])} Wikipedia articles:\n\n"
        for i, article in enumerate(data['query']['search'], 1):
            result += f"{i}. {article['title']}\n"
            result += f"   {article['snippet']}\n"
            result += f"   https://en.wikipedia.org/wiki/{article['title'].replace(' ', '_')}\n\n"

        return result

    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"


def search_dictionary(word):
    """Get dictionary definition"""
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url, timeout=10)

        if response.status_code == 404:
            return f"No definition found for '{word}'"

        data = response.json()
        if not data:
            return f"No definition found for '{word}'"

        entry = data[0]
        result = f"Definition of '{word}':\n\n"

        for meaning in entry.get('meanings', []):
            result += f"{meaning['partOfSpeech'].upper()}:\n"
            for i, definition in enumerate(meaning.get('definitions', [])[:3], 1):
                result += f"  {i}. {definition['definition']}\n"
                if 'example' in definition:
                    result += f"     Example: {definition['example']}\n"
            result += "\n"

        return result

    except Exception as e:
        return f"Error looking up dictionary: {str(e)}"


def search_github_repos(query, max_results=5):
    """Search GitHub repositories"""
    try:
        url = "https://api.github.com/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": max_results
        }
        headers = {"User-Agent": "Research-Assistant"}

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 403:
            return "GitHub API rate limit reached."

        data = response.json()
        if data['total_count'] == 0:
            return f"No repositories found for: {query}"

        result = f"Found {data['total_count']:,} repositories (showing top {max_results}):\n\n"
        for i, repo in enumerate(data['items'], 1):
            result += f"{i}. {repo['full_name']}\n"
            result += f"   Stars: {repo['stargazers_count']:,}\n"
            result += f"   Description: {repo['description'] or 'No description'}\n"
            result += f"   Link: {repo['html_url']}\n\n"

        return result

    except Exception as e:
        return f"Error searching GitHub: {str(e)}"


def search_books(query, max_results=5):
    """Search for books using Open Library API"""
    try:
        url = "https://openlibrary.org/search.json"
        params = {
            "q": query,
            "limit": max_results
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if not data.get('docs'):
            return f"No books found for: {query}"

        result = f"Found {data['numFound']:,} books (showing top {max_results}):\n\n"
        for i, book in enumerate(data['docs'], 1):
            title = book.get('title', 'Unknown')
            authors = book.get('author_name', ['Unknown'])
            year = book.get('first_publish_year', 'N/A')

            result += f"{i}. {title}\n"
            result += f"   Author(s): {', '.join(authors[:3])}\n"
            result += f"   First Published: {year}\n"
            if 'isbn' in book and book['isbn']:
                result += f"   ISBN: {book['isbn'][0]}\n"
            result += "\n"

        return result

    except Exception as e:
        return f"Error searching books: {str(e)}"


def save_research_note(topic, content):
    """Save research notes to JSON file"""
    notes_file = DATA_DIR / "research_notes.json"

    try:
        if notes_file.exists():
            with open(notes_file, 'r') as f:
                notes = json.load(f)
        else:
            notes = {"notes": []}

        notes["notes"].append({
            "topic": topic,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        with open(notes_file, 'w') as f:
            json.dump(notes, f, indent=2)

        return f"Note saved: '{topic}' ({len(content)} characters)"

    except Exception as e:
        return f"Error saving note: {str(e)}"


# =============================================================================
# TOOL DEFINITIONS
# =============================================================================

TOOLS = [
    {
        "name": "search_arxiv",
        "description": "Search arXiv for academic papers and research articles. Use this for scientific topics, AI/ML research, physics, math, computer science papers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "description": "Maximum papers to return", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_wikipedia",
        "description": "Search Wikipedia for articles on any topic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Wikipedia search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_dictionary",
        "description": "Look up word definitions from a dictionary.",
        "input_schema": {
            "type": "object",
            "properties": {
                "word": {"type": "string", "description": "Word to look up"}
            },
            "required": ["word"]
        }
    },
    {
        "name": "search_github_repos",
        "description": "Search GitHub for open-source repositories.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "GitHub search query"},
                "max_results": {"type": "integer", "description": "Maximum repos to return", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_books",
        "description": "Search for books using Open Library.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Book search query"},
                "max_results": {"type": "integer", "description": "Maximum books to return", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "save_research_note",
        "description": "Save important research notes for later reference.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Topic or title of the note"},
                "content": {"type": "string", "description": "Content of the research note"}
            },
            "required": ["topic", "content"]
        }
    }
]


# =============================================================================
# RICH UI HELPER FUNCTIONS
# =============================================================================

def display_welcome():
    """Display welcome banner"""
    welcome_text = """[bold cyan]RESEARCH ASSISTANT[/bold cyan] [dim]v9.0 - Smart Memory Edition[/dim]

[yellow]Capabilities:[/yellow]
  [green]ARXIV[/green]    Search academic papers    [green]WIKI[/green]     Wikipedia articles
  [green]GITHUB[/green]   Search repositories       [green]BOOKS[/green]    Find books
  [green]DICT[/green]     Dictionary definitions    [green]NOTES[/green]    Save research notes

[yellow]Smart Memory Features:[/yellow]
  [magenta]Summaries[/magenta]   Auto-summarizes pruned conversations
  [magenta]Topics[/magenta]      Tracks your research topics across sessions
  [magenta]Context[/magenta]     Injects relevant past research into responses

[yellow]Commands:[/yellow]
  [cyan]stats[/cyan]      Memory statistics         [cyan]topics[/cyan]     View tracked topics
  [cyan]history[/cyan]    Session summaries         [cyan]clear[/cyan]      Clear conversation
  [cyan]save[/cyan]       Export conversation       [cyan]quit[/cyan]       Exit"""

    console.print(Panel(welcome_text, title="[bold white]Welcome[/bold white]", border_style="blue", box=box.DOUBLE))


def display_stats(stats: dict):
    """Display memory statistics"""
    table = Table(title="Smart Memory Statistics", box=box.ROUNDED, border_style="cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    util = stats['utilization']
    util_color = "green" if util < 50 else "yellow" if util < 80 else "red"

    table.add_row("Session ID", stats['session_id'])
    table.add_row("Messages", str(stats['message_count']))
    table.add_row("Current Tokens", f"{stats['current_tokens']:,}")
    table.add_row("Max Tokens", f"{stats['max_tokens']:,}")
    table.add_row("Utilization", f"[{util_color}]{util:.1f}%[/{util_color}]")
    table.add_row("Summaries Created", str(stats['summaries_created']))
    table.add_row("Topics Tracked", str(stats['tracked_topics']))

    console.print(table)


def display_topics(topic_tracker: TopicTracker):
    """Display tracked topics"""
    topics = topic_tracker.get_all_topics()

    if not topics:
        console.print("[yellow]No topics tracked yet. Start researching![/yellow]")
        return

    # Recent topics
    recent = topic_tracker.get_recent_topics(5)
    if recent:
        table = Table(title="Recent Research Topics", box=box.ROUNDED, border_style="magenta")
        table.add_column("Topic", style="magenta")
        table.add_column("Times", style="green")
        table.add_column("Last Accessed", style="dim")
        table.add_column("Recent Queries", style="white")

        for topic, data in recent:
            queries = ", ".join(data['queries'][-2:]) if data['queries'] else "-"
            table.add_row(
                topic.title(),
                str(data['count']),
                data['last_accessed'][:10],
                queries[:50] + "..." if len(queries) > 50 else queries
            )

        console.print(table)

    # Most frequent
    frequent = topic_tracker.get_frequent_topics(5)
    if frequent and frequent != recent:
        table = Table(title="Most Researched Topics", box=box.ROUNDED, border_style="green")
        table.add_column("Topic", style="green")
        table.add_column("Times", style="bold")
        table.add_column("Sources Used", style="dim")

        for topic, data in frequent:
            sources = ", ".join(data['sources_used'].keys()) if data['sources_used'] else "-"
            table.add_row(topic.title(), str(data['count']), sources)

        console.print(table)


def display_history(summarizer: ConversationSummarizer):
    """Display session summaries"""
    sessions = summarizer.get_all_sessions()

    if not sessions:
        console.print("[yellow]No session history yet.[/yellow]")
        return

    # Show recent sessions
    recent_sessions = list(sessions.items())[-5:]

    for session_id, data in reversed(recent_sessions):
        is_current = session_id == summarizer.current_session_id
        title = f"Session {session_id}" + (" [current]" if is_current else "")

        if data['summaries']:
            summaries_text = "\n\n".join([
                f"[dim]{s['created_at'][:19]}[/dim]\n{s['summary']}"
                for s in data['summaries']
            ])
            console.print(Panel(
                summaries_text,
                title=title,
                border_style="green" if is_current else "dim",
                box=box.ROUNDED
            ))
        else:
            console.print(f"[dim]{title}: No summaries yet[/dim]")


def display_tool_use(tool_name: str, query: str = None):
    """Display tool usage"""
    tool_icons = {
        "search_arxiv": "[bold red]ARXIV[/bold red]",
        "search_wikipedia": "[bold blue]WIKI[/bold blue]",
        "search_dictionary": "[bold yellow]DICT[/bold yellow]",
        "search_github_repos": "[bold white]GITHUB[/bold white]",
        "search_books": "[bold magenta]BOOKS[/bold magenta]",
        "save_research_note": "[bold green]NOTES[/bold green]"
    }
    icon = tool_icons.get(tool_name, "[bold]TOOL[/bold]")
    if query:
        console.print(f"  {icon} Searching: [italic]{query}[/italic]")
    else:
        console.print(f"  {icon} Processing...")


def display_response(text: str):
    """Display assistant response"""
    console.print()
    console.print(Panel(text, title="[bold cyan]Assistant[/bold cyan]", border_style="cyan", box=box.ROUNDED, padding=(1, 2)))
    console.print()


def display_context_used(context: str):
    """Display when past context is being used"""
    if context:
        console.print(Panel(
            f"[dim]{context[:200]}{'...' if len(context) > 200 else ''}[/dim]",
            title="[magenta]Using Past Research Context[/magenta]",
            border_style="magenta",
            box=box.SIMPLE
        ))


def get_user_input():
    """Get user input"""
    console.print()
    return console.input("[bold green]You:[/bold green] ").strip()


# =============================================================================
# TOPIC EXTRACTION HELPER
# =============================================================================

def extract_topics_from_query(client: Anthropic, query: str) -> list:
    """
    Use Claude to extract main topics from a user query.
    Returns list of topic strings.
    """
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": f"""Extract 1-3 main research topics from this query. Return only the topics, one per line, lowercase.

Query: {query}

Topics:"""
            }]
        )

        topics = response.content[0].text.strip().split('\n')
        return [t.strip().lower() for t in topics if t.strip()]
    except:
        # Fallback: extract key words
        words = query.lower().split()
        return [w for w in words if len(w) > 4][:3]


# =============================================================================
# MAIN RESEARCH ASSISTANT
# =============================================================================

def research_assistant():
    """Main research assistant with smart memory"""

    console.clear()
    display_welcome()
    console.print()

    # Initialize smart memory
    memory = SmartMemory(client=client, model="claude-sonnet-4-5", max_tokens=8000)

    # Build system prompt with topic awareness
    base_system = """You are a research assistant with access to multiple knowledge sources.

Your capabilities:
- Search arXiv for academic papers
- Look up Wikipedia articles
- Get dictionary definitions
- Search GitHub repositories
- Find books on any topic
- Save research notes

When answering questions:
1. Use appropriate tools to gather information
2. Synthesize information from multiple sources when helpful
3. Cite your sources
4. Save important findings as research notes when the user asks

Be helpful, thorough, and accurate."""

    while True:
        user_input = get_user_input()

        if not user_input:
            continue

        if user_input.lower() == 'quit':
            console.print("\n[dim]Goodbye! Your research has been saved.[/dim]")
            break

        if user_input.lower() == 'stats':
            display_stats(memory.get_stats())
            continue

        if user_input.lower() == 'topics':
            display_topics(memory.topic_tracker)
            continue

        if user_input.lower() == 'history':
            display_history(memory.summarizer)
            continue

        if user_input.lower() == 'clear':
            memory.clear()
            console.print("[yellow]Conversation cleared. Topics and summaries preserved.[/yellow]")
            continue

        if user_input.lower() == 'save':
            filename = f"conversation_smart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = DATA_DIR / filename
            with open(filepath, 'w') as f:
                json.dump({
                    "messages": memory.get_messages(),
                    "stats": memory.get_stats(),
                    "topics": memory.topic_tracker.get_all_topics(),
                    "saved_at": datetime.now().isoformat()
                }, f, indent=2)
            console.print(f"[green]Conversation saved to {filepath}[/green]")
            continue

        # Extract topics from query for tracking
        topics = extract_topics_from_query(client, user_input)

        # Get enriched context from past research
        enriched_context = memory.get_enriched_context(user_input)
        if enriched_context:
            display_context_used(enriched_context)

        # Build system prompt with context
        system_prompt = base_system
        if enriched_context:
            system_prompt += f"\n\nContext from user's past research:\n{enriched_context}"

        # Add user message to memory
        memory.add_message("user", user_input)

        # Get conversation
        conversation = memory.get_messages()

        # Agent loop
        sources_used = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("[cyan]Thinking...", total=None)

            while True:
                response = client.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=4096,
                    system=system_prompt,
                    tools=TOOLS,
                    messages=conversation
                )

                progress.stop()

                if response.stop_reason == "end_turn":
                    final_text = ""
                    for block in response.content:
                        if hasattr(block, "text"):
                            final_text += block.text

                    display_response(final_text)
                    memory.add_message("assistant", final_text)

                    # Track topics with sources used
                    for topic in topics:
                        memory.track_topic(topic, user_input, sources_used)

                    # Show memory status
                    stats = memory.get_stats()
                    util = stats['utilization']
                    util_color = "green" if util < 50 else "yellow" if util < 80 else "red"
                    topics_str = ", ".join(topics[:3]) if topics else "general"
                    console.print(f"[dim]Memory: {stats['current_tokens']:,}/{stats['max_tokens']:,} ([{util_color}]{util:.1f}%[/{util_color}]) | Topics: {topics_str}[/dim]")

                    break

                elif response.stop_reason == "tool_use":
                    conversation.append({"role": "assistant", "content": response.content})

                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            tool_name = block.name
                            tool_input = block.input

                            # Track source
                            source_map = {
                                "search_arxiv": "arxiv",
                                "search_wikipedia": "wikipedia",
                                "search_github_repos": "github",
                                "search_books": "openlibrary",
                                "search_dictionary": "dictionary"
                            }
                            if tool_name in source_map:
                                sources_used.append(source_map[tool_name])

                            query = tool_input.get("query") or tool_input.get("word") or tool_input.get("topic")
                            display_tool_use(tool_name, query)

                            with Progress(
                                SpinnerColumn(),
                                TextColumn("[progress.description]{task.description}"),
                                console=console,
                                transient=True
                            ) as tool_progress:
                                tool_progress.add_task("[dim]Fetching results...", total=None)

                                if tool_name == "search_arxiv":
                                    result, _ = search_arxiv(tool_input["query"], tool_input.get("max_results", 5))
                                elif tool_name == "search_wikipedia":
                                    result = search_wikipedia(tool_input["query"])
                                elif tool_name == "search_dictionary":
                                    result = search_dictionary(tool_input["word"])
                                elif tool_name == "search_github_repos":
                                    result = search_github_repos(tool_input["query"], tool_input.get("max_results", 5))
                                elif tool_name == "search_books":
                                    result = search_books(tool_input["query"], tool_input.get("max_results", 5))
                                elif tool_name == "save_research_note":
                                    result = save_research_note(tool_input["topic"], tool_input["content"])
                                else:
                                    result = f"Unknown tool: {tool_name}"

                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result
                            })

                    conversation.append({"role": "user", "content": tool_results})
                    progress.start()
                    progress.update(task, description="[cyan]Processing results...")

                else:
                    console.print(f"[yellow]Warning: Unexpected stop reason: {response.stop_reason}[/yellow]")
                    break


if __name__ == "__main__":
    research_assistant()
