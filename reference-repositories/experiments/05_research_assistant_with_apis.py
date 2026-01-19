#!/usr/bin/env python3
"""
Level 5: Research Assistant with Public APIs
Integrates free APIs for enhanced research capabilities
"""

import os
import json
import requests
from anthropic import Anthropic
from datetime import datetime

# Initialize Anthropic client with API key
ANTHROPIC_API_KEY = "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"
client = Anthropic(api_key=ANTHROPIC_API_KEY)

# =============================================================================
# API HELPER FUNCTIONS (No API keys needed for these!)
# =============================================================================

def search_arxiv(query, max_results=5):
    """
    Search arXiv for academic papers
    API Docs: https://arxiv.org/help/api/
    """
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

        # Parse XML response (arxiv returns XML, not JSON)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)

        # Extract entries
        papers = []
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}

        for entry in root.findall('atom:entry', namespace):
            paper = {
                "title": entry.find('atom:title', namespace).text.strip().replace('\n', ' '),
                "authors": [author.find('atom:name', namespace).text
                           for author in entry.findall('atom:author', namespace)],
                "summary": entry.find('atom:summary', namespace).text.strip()[:300] + "...",
                "link": entry.find('atom:id', namespace).text,
                "published": entry.find('atom:published', namespace).text[:10]
            }
            papers.append(paper)

        if not papers:
            return f"No papers found for query: {query}"

        # Format results
        result = f"Found {len(papers)} papers on arXiv:\n\n"
        for i, paper in enumerate(papers, 1):
            result += f"{i}. **{paper['title']}**\n"
            result += f"   Authors: {', '.join(paper['authors'][:3])}"
            if len(paper['authors']) > 3:
                result += f" et al."
            result += f"\n   Published: {paper['published']}\n"
            result += f"   Link: {paper['link']}\n"
            result += f"   Summary: {paper['summary']}\n\n"

        return result

    except Exception as e:
        return f"Error searching arXiv: {str(e)}"


def search_wikipedia(query):
    """
    Search Wikipedia and get summary
    API Docs: https://www.mediawiki.org/wiki/API:Main_page
    """
    try:
        # First, search for the page
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "utf8": 1,
            "srlimit": 1
        }

        response = requests.get(search_url, params=search_params, timeout=10)
        data = response.json()

        if not data.get("query", {}).get("search"):
            return f"No Wikipedia page found for: {query}"

        # Get the page title
        page_title = data["query"]["search"][0]["title"]

        # Now get the summary
        summary_params = {
            "action": "query",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": page_title,
            "format": "json",
            "utf8": 1
        }

        response = requests.get(search_url, params=summary_params, timeout=10)
        data = response.json()

        pages = data["query"]["pages"]
        page_id = list(pages.keys())[0]

        if page_id == "-1":
            return f"Page not found: {query}"

        extract = pages[page_id].get("extract", "No summary available")

        # Get page URL
        page_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"

        result = f"**Wikipedia: {page_title}**\n\n"
        result += f"{extract[:800]}...\n\n"
        result += f"Read more: {page_url}"

        return result

    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"


def define_term(word):
    """
    Get dictionary definition
    API Docs: https://dictionaryapi.dev/
    """
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url, timeout=10)

        if response.status_code == 404:
            return f"No definition found for: {word}"

        data = response.json()

        if not data:
            return f"No definition found for: {word}"

        entry = data[0]
        result = f"**{entry['word']}**"

        # Phonetic
        if entry.get('phonetic'):
            result += f" ({entry['phonetic']})"

        result += "\n\n"

        # Meanings
        for meaning in entry['meanings'][:2]:  # First 2 parts of speech
            result += f"*{meaning['partOfSpeech']}*\n"

            for i, definition in enumerate(meaning['definitions'][:3], 1):  # First 3 definitions
                result += f"{i}. {definition['definition']}\n"

                if definition.get('example'):
                    result += f"   Example: \"{definition['example']}\"\n"

            result += "\n"

        return result

    except Exception as e:
        return f"Error getting definition: {str(e)}"


def search_github_repos(query, language=None, max_results=5):
    """
    Search GitHub repositories (no auth needed, but rate-limited)
    API Docs: https://docs.github.com/en/rest/search
    """
    try:
        search_query = query
        if language:
            search_query += f" language:{language}"

        url = "https://api.github.com/search/repositories"
        params = {
            "q": search_query,
            "sort": "stars",
            "order": "desc",
            "per_page": max_results
        }

        # Add User-Agent header (required by GitHub API)
        headers = {"User-Agent": "Research-Assistant"}

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 403:
            return "GitHub API rate limit reached. Try again in a few minutes."

        if response.status_code != 200:
            return f"Error: GitHub API returned status {response.status_code}"

        data = response.json()

        if data['total_count'] == 0:
            return f"No repositories found for: {query}"

        result = f"Found {data['total_count']} repositories (showing top {max_results}):\n\n"

        for i, repo in enumerate(data['items'], 1):
            result += f"{i}. **{repo['full_name']}** ⭐ {repo['stargazers_count']:,}\n"
            result += f"   {repo['description'] or 'No description'}\n"
            result += f"   Language: {repo['language'] or 'N/A'}\n"
            result += f"   Link: {repo['html_url']}\n\n"

        return result

    except Exception as e:
        return f"Error searching GitHub: {str(e)}"


def search_open_library(query, max_results=5):
    """
    Search Open Library for books
    API Docs: https://openlibrary.org/developers/api
    """
    try:
        url = "https://openlibrary.org/search.json"
        params = {
            "q": query,
            "limit": max_results
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data['numFound'] == 0:
            return f"No books found for: {query}"

        result = f"Found {data['numFound']} books (showing {max_results}):\n\n"

        for i, book in enumerate(data['docs'][:max_results], 1):
            title = book.get('title', 'Unknown Title')
            authors = book.get('author_name', ['Unknown Author'])
            year = book.get('first_publish_year', 'N/A')

            result += f"{i}. **{title}**\n"
            result += f"   By: {', '.join(authors[:3])}\n"
            result += f"   First published: {year}\n"

            if book.get('key'):
                result += f"   Link: https://openlibrary.org{book['key']}\n"

            result += "\n"

        return result

    except Exception as e:
        return f"Error searching Open Library: {str(e)}"


# =============================================================================
# TOOL DEFINITIONS FOR CLAUDE
# =============================================================================

TOOLS = [
    {
        "name": "search_arxiv",
        "description": "Search arXiv for academic papers on AI, ML, computer science, math, physics. Returns paper titles, authors, summaries, and links.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'autonomous agents', 'reinforcement learning')"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5, max: 10)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_wikipedia",
        "description": "Search Wikipedia and get article summary. Good for quick facts, definitions, overviews of topics.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Topic to search (e.g., 'multi-agent system', 'machine learning')"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "define_term",
        "description": "Get dictionary definition of a word, including pronunciation, parts of speech, definitions, and examples.",
        "input_schema": {
            "type": "object",
            "properties": {
                "word": {
                    "type": "string",
                    "description": "Word to define (e.g., 'algorithm', 'heuristic')"
                }
            },
            "required": ["word"]
        }
    },
    {
        "name": "search_github_repos",
        "description": "Search GitHub for code repositories. Find implementations, libraries, frameworks, and example code.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'autonomous agent python', 'LLM tools')"
                },
                "language": {
                    "type": "string",
                    "description": "Filter by programming language (e.g., 'python', 'javascript')"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_books",
        "description": "Search Open Library for books on a topic. Find technical books, textbooks, and references.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'artificial intelligence', 'python programming')"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "save_research_note",
        "description": "Save a research finding or learning note with timestamp and category.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Category (e.g., 'paper', 'code', 'concept', 'resource')"
                },
                "title": {
                    "type": "string",
                    "description": "Short title for this note"
                },
                "content": {
                    "type": "string",
                    "description": "The research note content"
                }
            },
            "required": ["category", "title", "content"]
        }
    }
]

# =============================================================================
# TOOL EXECUTION
# =============================================================================

def execute_tool(tool_name, tool_input):
    """Execute a tool and return the result"""

    if tool_name == "search_arxiv":
        return search_arxiv(
            tool_input["query"],
            tool_input.get("max_results", 5)
        )

    elif tool_name == "search_wikipedia":
        return search_wikipedia(tool_input["query"])

    elif tool_name == "define_term":
        return define_term(tool_input["word"])

    elif tool_name == "search_github_repos":
        return search_github_repos(
            tool_input["query"],
            tool_input.get("language"),
            tool_input.get("max_results", 5)
        )

    elif tool_name == "search_books":
        return search_open_library(
            tool_input["query"],
            tool_input.get("max_results", 5)
        )

    elif tool_name == "save_research_note":
        notes_file = "experiments/research_notes.json"
        notes = []

        if os.path.exists(notes_file):
            with open(notes_file, 'r') as f:
                notes = json.load(f)

        note = {
            "timestamp": datetime.now().isoformat(),
            "category": tool_input["category"],
            "title": tool_input["title"],
            "content": tool_input["content"]
        }

        notes.append(note)

        with open(notes_file, 'w') as f:
            json.dump(notes, f, indent=2)

        return f"Saved note: {tool_input['title']} (Category: {tool_input['category']})"

    else:
        return f"Unknown tool: {tool_name}"


# =============================================================================
# MAIN RESEARCH ASSISTANT
# =============================================================================

SYSTEM_PROMPT = """You are an AI research assistant helping a beginner programmer learn about agentic workflows and AI systems.

Your capabilities:
- Search arXiv for academic papers
- Look up Wikipedia articles
- Get dictionary definitions
- Search GitHub for code repositories
- Find books on Open Library
- Save research notes

When the user asks a question:
1. Use relevant tools to gather information
2. Synthesize the information into a clear, beginner-friendly explanation
3. Suggest related topics to explore
4. Save important findings as research notes

Be encouraging, explain concepts simply, and help the user build knowledge progressively."""


def research_assistant():
    """Main research assistant loop"""

    print("="*80)
    print("LEVEL 5: RESEARCH ASSISTANT WITH PUBLIC APIs")
    print("="*80)
    print("\nCapabilities:")
    print("  [ARXIV] Search arXiv for research papers")
    print("  [WIKI] Look up Wikipedia articles")
    print("  [DICT] Get dictionary definitions")
    print("  [GITHUB] Search GitHub repositories")
    print("  [BOOKS] Find books on any topic")
    print("  [NOTES] Save research notes")
    print("\nType 'quit' to exit, 'notes' to view saved research\n")

    conversation = []

    # Load previous research notes as context
    notes_file = "experiments/research_notes.json"
    if os.path.exists(notes_file):
        with open(notes_file, 'r') as f:
            notes = json.load(f)
            if notes:
                print(f"[Loaded {len(notes)} previous research notes]\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["quit", "exit"]:
            print("\nGoodbye! Your research notes are saved in experiments/research_notes.json")
            break

        if user_input.lower() == "notes":
            # Display saved notes
            if os.path.exists(notes_file):
                with open(notes_file, 'r') as f:
                    notes = json.load(f)

                if notes:
                    print(f"\n{'='*80}")
                    print(f"SAVED RESEARCH NOTES ({len(notes)} total)")
                    print(f"{'='*80}\n")

                    for note in notes[-10:]:  # Show last 10
                        print(f"[{note['category'].upper()}] {note['title']}")
                        print(f"  {note['timestamp'][:10]}")
                        print(f"  {note['content'][:200]}...\n")
                else:
                    print("\nNo research notes saved yet.\n")
            else:
                print("\nNo research notes saved yet.\n")
            continue

        conversation.append({"role": "user", "content": user_input})

        # Agent loop with tools
        print()
        while True:
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=conversation
            )

            # Check stop reason
            if response.stop_reason == "end_turn":
                # Get final text response
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text += block.text

                conversation.append({"role": "assistant", "content": response.content})
                print(f"Assistant: {final_text}\n")
                break

            elif response.stop_reason == "tool_use":
                # Agent wants to use tools
                conversation.append({"role": "assistant", "content": response.content})

                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        print(f"[Using tool: {block.name}]", end=" ", flush=True)

                        # Execute tool
                        result = execute_tool(block.name, block.input)

                        print("Done.")

                        # Add result
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })

                # Send tool results back
                conversation.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    research_assistant()
