#!/usr/bin/env python3
"""
Level 8: Research Assistant with Rich Console UI
Adds beautiful terminal output with colors, panels, tables, and progress indicators.
"""

import os
import json
import requests
import time
from anthropic import Anthropic
from datetime import datetime

# Rich library imports for beautiful console output
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich import box

# Initialize Rich console
console = Console()

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
if not ANTHROPIC_API_KEY:
    # Fallback for development - in production use environment variables
    ANTHROPIC_API_KEY = "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"

client = Anthropic(api_key=ANTHROPIC_API_KEY)


# =============================================================================
# PATTERN 4 LEVEL 2: ACCURATE TOKEN-AWARE MEMORY BUFFER (with Rich output)
# =============================================================================

class AccurateTokenBufferMemory:
    """
    Manages conversation history with accurate token counting via Anthropic API.
    Enhanced with Rich console output for better visibility.
    """

    def __init__(self, client: Anthropic, model: str = "claude-sonnet-4-5", max_tokens: int = 8000):
        self.client = client
        self.model = model
        self.max_tokens = max_tokens
        self.messages = []
        self.token_stats = {
            "counts": [],
            "api_calls": 0,
            "total_time_ms": 0
        }

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self._trim_to_limit()

    def _count_tokens_accurate(self) -> int:
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

            token_count = response.input_tokens
            self.token_stats["counts"].append({
                "timestamp": datetime.now().isoformat(),
                "token_count": token_count,
                "message_count": len(self.messages),
                "elapsed_ms": elapsed_ms
            })

            return token_count

        except Exception as e:
            console.print(f"[yellow]Warning: Token counting failed: {e}[/yellow]")
            total_chars = sum(len(msg["content"]) for msg in self.messages)
            return total_chars // 4

    def _trim_to_limit(self):
        current_tokens = self._count_tokens_accurate()

        while current_tokens > self.max_tokens and len(self.messages) > 2:
            console.print(f"[dim][MEMORY] Pruning old messages ({current_tokens} > {self.max_tokens} tokens)[/dim]")

            self.messages.pop(0)
            if len(self.messages) > 0 and self.messages[0]["role"] == "assistant":
                self.messages.pop(0)

            current_tokens = self._count_tokens_accurate()

    def get_messages(self) -> list:
        return self.messages.copy()

    def get_stats(self) -> dict:
        current_tokens = self._count_tokens_accurate()

        avg_latency = 0
        if self.token_stats["api_calls"] > 0:
            avg_latency = self.token_stats["total_time_ms"] / self.token_stats["api_calls"]

        return {
            "message_count": len(self.messages),
            "current_tokens": current_tokens,
            "max_tokens": self.max_tokens,
            "utilization": current_tokens / self.max_tokens * 100,
            "api_calls": self.token_stats["api_calls"],
            "avg_latency_ms": avg_latency,
            "total_api_time_ms": self.token_stats["total_time_ms"]
        }

    def compare_estimation_methods(self) -> dict:
        approx_tokens = sum(len(msg["content"]) for msg in self.messages) // 4
        accurate_tokens = self._count_tokens_accurate()

        difference = accurate_tokens - approx_tokens
        percent_diff = (difference / accurate_tokens * 100) if accurate_tokens > 0 else 0

        return {
            "approximation": approx_tokens,
            "accurate": accurate_tokens,
            "difference": difference,
            "percent_difference": percent_diff
        }

    def clear(self):
        self.messages = []
        self.token_stats["counts"] = []

    def save_to_file(self, filename: str):
        with open(filename, 'w') as f:
            json.dump({
                "messages": self.messages,
                "stats": self.get_stats(),
                "comparison": self.compare_estimation_methods(),
                "token_history": self.token_stats["counts"],
                "saved_at": datetime.now().isoformat()
            }, f, indent=2)


# =============================================================================
# API HELPER FUNCTIONS WITH RICH PROGRESS INDICATORS
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
            return f"Error: API returned status {response.status_code}"

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
            return "No papers found for your query."

        result = f"Found {len(papers)} papers on arXiv:\n\n"
        for i, paper in enumerate(papers, 1):
            result += f"{i}. {paper['title']}\n"
            result += f"   Authors: {', '.join(paper['authors'][:3])}\n"
            result += f"   Published: {paper['published']}\n"
            result += f"   Summary: {paper['summary']}\n"
            result += f"   Link: {paper['link']}\n\n"

        return result

    except Exception as e:
        return f"Error searching arXiv: {str(e)}"


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
    notes_file = "experiments/research_notes.json"

    try:
        if os.path.exists(notes_file):
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
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'machine learning', 'quantum computing')"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of papers to return (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_wikipedia",
        "description": "Search Wikipedia for articles on any topic. Good for general knowledge, historical facts, concepts, and explanations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Wikipedia search query"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_dictionary",
        "description": "Look up word definitions from a dictionary. Use for word meanings, parts of speech, and usage examples.",
        "input_schema": {
            "type": "object",
            "properties": {
                "word": {
                    "type": "string",
                    "description": "Word to look up"
                }
            },
            "required": ["word"]
        }
    },
    {
        "name": "search_github_repos",
        "description": "Search GitHub for open-source repositories and code projects. Use for finding libraries, frameworks, example code.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "GitHub search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum repositories to return (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_books",
        "description": "Search for books using Open Library. Find books by title, author, subject, or topic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Book search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum books to return (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "save_research_note",
        "description": "Save important research notes for later reference. Use this to record key findings, ideas, or summaries.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Topic or title of the note"
                },
                "content": {
                    "type": "string",
                    "description": "Content of the research note"
                }
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
- Save research notes

When answering questions:
1. Use appropriate tools to gather information
2. Synthesize information from multiple sources when helpful
3. Cite your sources
4. Save important findings as research notes when the user asks

Be helpful, thorough, and accurate."""


# =============================================================================
# RICH UI HELPER FUNCTIONS
# =============================================================================

def display_welcome():
    """Display a beautiful welcome banner"""
    welcome_text = """[bold cyan]RESEARCH ASSISTANT[/bold cyan] [dim]v8.0 - Rich UI Edition[/dim]

[yellow]Capabilities:[/yellow]
  [green]ARXIV[/green]    Search academic papers
  [green]WIKI[/green]     Look up Wikipedia articles
  [green]DICT[/green]     Get dictionary definitions
  [green]GITHUB[/green]   Search repositories
  [green]BOOKS[/green]    Find books on any topic
  [green]NOTES[/green]    Save research notes

[yellow]Commands:[/yellow]
  [cyan]stats[/cyan]     View memory statistics
  [cyan]compare[/cyan]   Compare token counting methods
  [cyan]save[/cyan]      Export conversation
  [cyan]clear[/cyan]     Clear conversation history
  [cyan]quit[/cyan]      Exit"""

    console.print(Panel(welcome_text, title="[bold white]Welcome[/bold white]", border_style="blue", box=box.DOUBLE))


def display_stats(stats: dict):
    """Display memory statistics in a beautiful table"""
    table = Table(title="Memory Statistics", box=box.ROUNDED, border_style="cyan")

    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    # Utilization color based on percentage
    util = stats['utilization']
    if util < 50:
        util_color = "green"
    elif util < 80:
        util_color = "yellow"
    else:
        util_color = "red"

    table.add_row("Messages", str(stats['message_count']))
    table.add_row("Current Tokens", f"{stats['current_tokens']:,}")
    table.add_row("Max Tokens", f"{stats['max_tokens']:,}")
    table.add_row("Utilization", f"[{util_color}]{util:.1f}%[/{util_color}]")
    table.add_row("API Calls", str(stats['api_calls']))
    table.add_row("Avg Latency", f"{stats['avg_latency_ms']:.1f} ms")
    table.add_row("Total API Time", f"{stats['total_api_time_ms']:.1f} ms")

    console.print(table)


def display_comparison(comparison: dict):
    """Display token counting comparison"""
    table = Table(title="Token Counting Comparison", box=box.ROUNDED, border_style="magenta")

    table.add_column("Method", style="magenta", no_wrap=True)
    table.add_column("Tokens", style="white")

    table.add_row("Approximation (4 chars = 1 token)", str(comparison['approximation']))
    table.add_row("Accurate (Anthropic API)", f"[bold]{comparison['accurate']}[/bold]")

    diff = comparison['difference']
    diff_color = "green" if abs(diff) < 100 else "yellow" if abs(diff) < 500 else "red"
    table.add_row("Difference", f"[{diff_color}]{diff:+} ({comparison['percent_difference']:.1f}%)[/{diff_color}]")

    console.print(table)


def display_tool_use(tool_name: str, query: str = None):
    """Display tool usage with icon and color"""
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
    """Display assistant response in a panel"""
    console.print()
    console.print(Panel(
        text,
        title="[bold cyan]Assistant[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    ))
    console.print()


def get_user_input():
    """Get user input with styled prompt"""
    console.print()
    return console.input("[bold green]You:[/bold green] ").strip()


# =============================================================================
# MAIN RESEARCH ASSISTANT WITH RICH UI
# =============================================================================

def research_assistant():
    """Main research assistant loop with Rich UI"""

    console.clear()
    display_welcome()
    console.print()

    # Initialize accurate memory buffer
    memory = AccurateTokenBufferMemory(client=client, model="claude-sonnet-4-5", max_tokens=8000)

    while True:
        user_input = get_user_input()

        if not user_input:
            continue

        if user_input.lower() == 'quit':
            console.print("\n[dim]Goodbye! Your research session has ended.[/dim]")
            break

        if user_input.lower() == 'stats':
            stats = memory.get_stats()
            display_stats(stats)
            continue

        if user_input.lower() == 'compare':
            comparison = memory.compare_estimation_methods()
            display_comparison(comparison)
            continue

        if user_input.lower() == 'save':
            filename = f"conversation_rich_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            memory.save_to_file(f"experiments/{filename}")
            console.print(f"[green]Conversation saved to {filename}[/green]")
            continue

        if user_input.lower() == 'clear':
            memory.clear()
            console.print("[yellow]Conversation history cleared.[/yellow]")
            continue

        # Add user message to memory
        memory.add_message("user", user_input)

        # Get conversation from memory
        conversation = memory.get_messages()

        # Agent loop with tools and progress indicator
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
                    system=SYSTEM_PROMPT,
                    tools=TOOLS,
                    messages=conversation
                )

                progress.stop()

                # Check stop reason
                if response.stop_reason == "end_turn":
                    # Get final text response
                    final_text = ""
                    for block in response.content:
                        if hasattr(block, "text"):
                            final_text += block.text

                    display_response(final_text)

                    # Add assistant response to memory
                    memory.add_message("assistant", final_text)

                    # Show memory status bar
                    stats = memory.get_stats()
                    util = stats['utilization']
                    util_color = "green" if util < 50 else "yellow" if util < 80 else "red"
                    console.print(f"[dim]Memory: {stats['current_tokens']:,}/{stats['max_tokens']:,} tokens ([{util_color}]{util:.1f}%[/{util_color}])[/dim]")

                    break

                elif response.stop_reason == "tool_use":
                    # Add assistant's response with tool calls to conversation
                    conversation.append({"role": "assistant", "content": response.content})

                    # Process each tool call
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            tool_name = block.name
                            tool_input = block.input

                            # Display tool usage
                            query = tool_input.get("query") or tool_input.get("word") or tool_input.get("topic")
                            display_tool_use(tool_name, query)

                            # Execute the tool with spinner
                            with Progress(
                                SpinnerColumn(),
                                TextColumn("[progress.description]{task.description}"),
                                console=console,
                                transient=True
                            ) as tool_progress:
                                tool_task = tool_progress.add_task(f"[dim]Fetching results...", total=None)

                                if tool_name == "search_arxiv":
                                    result = search_arxiv(tool_input["query"], tool_input.get("max_results", 5))
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

                    # Add tool results to conversation
                    conversation.append({"role": "user", "content": tool_results})

                    # Restart thinking spinner
                    progress.start()
                    progress.update(task, description="[cyan]Processing results...")

                else:
                    console.print(f"[yellow]Warning: Unexpected stop reason: {response.stop_reason}[/yellow]")
                    break


if __name__ == "__main__":
    research_assistant()
