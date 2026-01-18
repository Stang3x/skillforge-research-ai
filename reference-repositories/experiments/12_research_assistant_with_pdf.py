#!/usr/bin/env python3
"""
Level 12: Research Assistant with PDF Integration

New capabilities:
- Extract text from local PDF files
- Download and analyze arXiv PDFs
- Summarize PDF content
- Search within PDF text
- Multi-agent system with PDF-aware researcher

Architecture:
┌─────────────────────────────────────────────────────────┐
│                      USER QUERY                          │
│  "Analyze this PDF" / "Download arXiv paper 2301.00001" │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    COORDINATOR                           │
└────────┬──────────────┬──────────────┬─────────────────┘
         ▼              ▼              ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│ RESEARCHER │  │  ANALYST   │  │   WRITER   │
│            │  │            │  │            │
│ + PDF      │  │ - Compare  │  │ - Reports  │
│   Extract  │  │ - Patterns │  │ - Summaries│
│ + arXiv    │  │ - Insights │  │ - Format   │
│   Download │  │            │  │            │
└────────────┘  └────────────┘  └────────────┘
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
from typing import Optional
from enum import Enum

# Rich library imports
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.markdown import Markdown
from rich import box
from rich.tree import Tree

# PDF library
try:
    from pypdf import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("[WARNING] pypdf not installed. Run: pip install pypdf")

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
CACHE_FILE = DATA_DIR / "api_cache.json"
PDF_CACHE_FILE = DATA_DIR / "pdf_cache.json"


# =============================================================================
# PDF EXTRACTION AND MANAGEMENT
# =============================================================================

class PDFManager:
    """
    Manages PDF extraction, caching, and analysis.
    """

    def __init__(self, pdf_dir: Path = PDF_DIR, cache_file: Path = PDF_CACHE_FILE):
        self.pdf_dir = pdf_dir
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"pdfs": {}}

    def _save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def extract_text(self, pdf_path: str, max_pages: int = None) -> dict:
        """
        Extract text from a PDF file.

        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to extract (None = all)

        Returns:
            dict with extracted text, metadata, and status
        """
        if not PDF_AVAILABLE:
            return {"success": False, "error": "pypdf not installed. Run: pip install pypdf"}

        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            return {"success": False, "error": f"File not found: {pdf_path}"}

        # Check cache
        cache_key = f"{pdf_path}:{max_pages}"
        if cache_key in self.cache["pdfs"]:
            cached = self.cache["pdfs"][cache_key]
            # Check if file hasn't been modified
            if cached.get("mtime") == os.path.getmtime(pdf_path):
                return {"success": True, "cached": True, **cached}

        try:
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)
            pages_to_extract = min(max_pages, total_pages) if max_pages else total_pages

            # Extract metadata
            metadata = {}
            if reader.metadata:
                metadata = {
                    "title": reader.metadata.get("/Title", ""),
                    "author": reader.metadata.get("/Author", ""),
                    "subject": reader.metadata.get("/Subject", ""),
                    "creator": reader.metadata.get("/Creator", ""),
                }

            # Extract table of contents
            toc = []
            if reader.outline:
                for item in reader.outline:
                    if isinstance(item, list):
                        for subitem in item:
                            if hasattr(subitem, 'title'):
                                toc.append(f"  - {subitem.title}")
                    elif hasattr(item, 'title'):
                        toc.append(f"- {item.title}")

            # Extract text with progress
            text_pages = []
            for i in range(pages_to_extract):
                page = reader.pages[i]
                text = page.extract_text() or ""
                text_pages.append({
                    "page": i + 1,
                    "text": text,
                    "char_count": len(text)
                })

            full_text = "\n\n".join([f"[Page {p['page']}]\n{p['text']}" for p in text_pages])

            result = {
                "success": True,
                "cached": False,
                "file_path": str(pdf_path),
                "file_name": pdf_path.name,
                "total_pages": total_pages,
                "extracted_pages": pages_to_extract,
                "metadata": metadata,
                "toc": toc,
                "text": full_text,
                "char_count": len(full_text),
                "mtime": os.path.getmtime(pdf_path),
                "extracted_at": datetime.now().isoformat()
            }

            # Cache the result (without full text to save space, just metadata)
            cache_entry = {k: v for k, v in result.items() if k != "text"}
            cache_entry["text_preview"] = full_text[:1000] + "..." if len(full_text) > 1000 else full_text
            self.cache["pdfs"][cache_key] = cache_entry
            self._save_cache()

            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    def download_arxiv_pdf(self, arxiv_id: str) -> dict:
        """
        Download a PDF from arXiv.

        Args:
            arxiv_id: arXiv ID (e.g., "2301.00001" or full URL)

        Returns:
            dict with download status and file path
        """
        # Extract ID from URL if needed
        if "arxiv.org" in arxiv_id:
            match = re.search(r'(\d{4}\.\d{4,5})(v\d+)?', arxiv_id)
            if match:
                arxiv_id = match.group(1)
            else:
                return {"success": False, "error": f"Could not extract arXiv ID from: {arxiv_id}"}

        # Clean ID
        arxiv_id = arxiv_id.strip()

        # Check if already downloaded
        pdf_path = self.pdf_dir / f"arxiv_{arxiv_id.replace('.', '_')}.pdf"
        if pdf_path.exists():
            return {
                "success": True,
                "cached": True,
                "file_path": str(pdf_path),
                "arxiv_id": arxiv_id
            }

        # Download PDF
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        try:
            response = requests.get(pdf_url, timeout=30, stream=True)

            if response.status_code == 404:
                return {"success": False, "error": f"arXiv paper not found: {arxiv_id}"}

            if response.status_code != 200:
                return {"success": False, "error": f"Download failed with status: {response.status_code}"}

            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'pdf' not in content_type.lower():
                return {"success": False, "error": f"Not a PDF: {content_type}"}

            # Save PDF
            with open(pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(pdf_path)

            return {
                "success": True,
                "cached": False,
                "file_path": str(pdf_path),
                "arxiv_id": arxiv_id,
                "url": pdf_url,
                "file_size_mb": file_size / (1024 * 1024)
            }

        except requests.Timeout:
            return {"success": False, "error": "Download timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_in_pdf(self, pdf_path: str, query: str, max_results: int = 5) -> dict:
        """
        Search for text within a PDF.

        Args:
            pdf_path: Path to PDF
            query: Search query
            max_results: Maximum number of matches to return

        Returns:
            dict with search results
        """
        extraction = self.extract_text(pdf_path)
        if not extraction["success"]:
            return extraction

        text = extraction["text"]
        query_lower = query.lower()

        # Find matches with context
        matches = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            if query_lower in line.lower():
                # Get context (2 lines before and after)
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = '\n'.join(lines[start:end])

                matches.append({
                    "line_number": i + 1,
                    "match": line.strip(),
                    "context": context
                })

                if len(matches) >= max_results:
                    break

        return {
            "success": True,
            "query": query,
            "file": extraction["file_name"],
            "total_matches": len(matches),
            "matches": matches
        }

    def get_pdf_summary(self, pdf_path: str, max_chars: int = 10000) -> dict:
        """
        Get a summary-ready excerpt from a PDF.
        Returns first N characters for summarization.
        """
        extraction = self.extract_text(pdf_path, max_pages=20)
        if not extraction["success"]:
            return extraction

        text = extraction["text"][:max_chars]

        return {
            "success": True,
            "file": extraction["file_name"],
            "total_pages": extraction["total_pages"],
            "metadata": extraction["metadata"],
            "toc": extraction["toc"],
            "text_excerpt": text,
            "char_count": len(text)
        }

    def list_pdfs(self) -> list:
        """List all PDFs in the pdf directory"""
        pdfs = []
        for f in self.pdf_dir.glob("*.pdf"):
            pdfs.append({
                "name": f.name,
                "path": str(f),
                "size_mb": f.stat().st_size / (1024 * 1024),
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })
        return sorted(pdfs, key=lambda x: x["modified"], reverse=True)


# Initialize PDF manager
pdf_manager = PDFManager()


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
            paper_id = entry.find('atom:id', ns).text
            arxiv_id = paper_id.split('/')[-1] if paper_id else ""
            papers.append({
                "title": entry.find('atom:title', ns).text.strip().replace('\n', ' '),
                "authors": [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)],
                "summary": entry.find('atom:summary', ns).text.strip()[:300] + "...",
                "published": entry.find('atom:published', ns).text[:10],
                "link": paper_id,
                "arxiv_id": arxiv_id
            })
        if not papers:
            return "No papers found.", False
        result = f"Found {len(papers)} papers:\n\n"
        for i, p in enumerate(papers, 1):
            result += f"{i}. {p['title']}\n   Authors: {', '.join(p['authors'][:3])}\n"
            result += f"   Published: {p['published']}\n   arXiv ID: {p['arxiv_id']}\n"
            result += f"   Link: {p['link']}\n\n"
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
# PDF TOOL FUNCTIONS
# =============================================================================

def extract_pdf(file_path: str, max_pages: int = None) -> str:
    """Extract text from a local PDF file"""
    result = pdf_manager.extract_text(file_path, max_pages)

    if not result["success"]:
        return f"Error: {result.get('error', 'Unknown error')}"

    output = f"PDF: {result['file_name']}\n"
    output += f"Pages: {result['extracted_pages']}/{result['total_pages']}\n"

    if result.get("metadata", {}).get("title"):
        output += f"Title: {result['metadata']['title']}\n"
    if result.get("metadata", {}).get("author"):
        output += f"Author: {result['metadata']['author']}\n"

    if result.get("toc"):
        output += f"\nTable of Contents:\n" + "\n".join(result["toc"][:10]) + "\n"

    output += f"\nCharacters extracted: {result['char_count']:,}\n"
    output += f"\n--- BEGIN CONTENT ---\n{result['text'][:8000]}"

    if result['char_count'] > 8000:
        output += f"\n\n[... truncated, {result['char_count'] - 8000:,} more characters ...]"

    return output


def download_arxiv(arxiv_id: str) -> str:
    """Download a PDF from arXiv"""
    display_agent_activity(AgentRole.RESEARCHER, f"Downloading arXiv paper: {arxiv_id}")

    result = pdf_manager.download_arxiv_pdf(arxiv_id)

    if not result["success"]:
        return f"Error: {result.get('error', 'Unknown error')}"

    if result.get("cached"):
        return f"arXiv paper already downloaded: {result['file_path']}"

    return f"Downloaded arXiv paper {result['arxiv_id']}\nSaved to: {result['file_path']}\nSize: {result.get('file_size_mb', 0):.2f} MB"


def analyze_arxiv_paper(arxiv_id: str, max_pages: int = 15) -> str:
    """Download and extract text from an arXiv paper"""
    # First download
    download_result = pdf_manager.download_arxiv_pdf(arxiv_id)

    if not download_result["success"]:
        return f"Error downloading: {download_result.get('error', 'Unknown error')}"

    # Then extract
    extract_result = pdf_manager.extract_text(download_result["file_path"], max_pages)

    if not extract_result["success"]:
        return f"Error extracting: {extract_result.get('error', 'Unknown error')}"

    output = f"arXiv Paper: {arxiv_id}\n"
    output += f"File: {download_result['file_path']}\n"
    output += f"Pages extracted: {extract_result['extracted_pages']}/{extract_result['total_pages']}\n"

    if extract_result.get("metadata", {}).get("title"):
        output += f"Title: {extract_result['metadata']['title']}\n"

    if extract_result.get("toc"):
        output += f"\nTable of Contents:\n" + "\n".join(extract_result["toc"][:10]) + "\n"

    output += f"\n--- PAPER CONTENT ---\n{extract_result['text'][:10000]}"

    if extract_result['char_count'] > 10000:
        output += f"\n\n[... truncated, {extract_result['char_count'] - 10000:,} more characters ...]"

    return output


def search_pdf(file_path: str, query: str) -> str:
    """Search for text within a PDF"""
    result = pdf_manager.search_in_pdf(file_path, query)

    if not result["success"]:
        return f"Error: {result.get('error', 'Unknown error')}"

    if not result["matches"]:
        return f"No matches found for '{query}' in {result['file']}"

    output = f"Found {result['total_matches']} matches for '{query}':\n\n"

    for i, match in enumerate(result["matches"], 1):
        output += f"Match {i} (line {match['line_number']}):\n"
        output += f"  {match['match']}\n"
        output += f"  Context:\n{match['context']}\n\n"

    return output


def list_downloaded_pdfs() -> str:
    """List all downloaded PDFs"""
    pdfs = pdf_manager.list_pdfs()

    if not pdfs:
        return "No PDFs downloaded yet."

    output = f"Downloaded PDFs ({len(pdfs)} files):\n\n"
    for p in pdfs:
        output += f"- {p['name']} ({p['size_mb']:.2f} MB)\n"
        output += f"  Path: {p['path']}\n\n"

    return output


# =============================================================================
# AGENT TYPES
# =============================================================================

class AgentRole(Enum):
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"


@dataclass
class TaskResult:
    agent: AgentRole
    success: bool
    result: str
    data: dict = field(default_factory=dict)
    execution_time_ms: float = 0


@dataclass
class ResearchPlan:
    query: str
    complexity: str
    steps: list
    agents_needed: list
    estimated_sources: list


# =============================================================================
# SPECIALIZED AGENTS
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
        return self.client.messages.create(**kwargs)

    def log_execution(self, task: str, result: str, time_ms: float):
        self.execution_history.append({
            "task": task, "result_length": len(result), "time_ms": time_ms,
            "timestamp": datetime.now().isoformat()
        })


class ResearcherAgent(BaseAgent):
    """RESEARCHER: Gathers information including PDF analysis"""

    SYSTEM_PROMPT = """You are a RESEARCHER agent specialized in gathering information.

Your capabilities:
- Search APIs: arXiv, Wikipedia, GitHub, HackerNews, StackOverflow
- PDF Analysis: Extract and analyze PDF documents
- arXiv Papers: Download and analyze arXiv papers by ID

For PDF tasks:
- Use extract_pdf for local files
- Use analyze_arxiv_paper with arXiv IDs (e.g., "2301.00001")
- Use search_pdf to find specific content in PDFs
- Use list_pdfs to see available PDFs

Guidelines:
1. Use multiple sources when appropriate
2. For academic research, search arXiv AND download relevant papers
3. Extract key information from PDFs
4. Return structured findings"""

    TOOLS = [
        {"name": "search_arxiv", "description": "Search arXiv for papers",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "default": 5}}, "required": ["query"]}},
        {"name": "search_wikipedia", "description": "Search Wikipedia",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "search_github_repos", "description": "Search GitHub",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "default": 5}}, "required": ["query"]}},
        {"name": "search_hackernews", "description": "Search HackerNews",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "default": 5}}, "required": ["query"]}},
        {"name": "search_stackoverflow", "description": "Search Stack Overflow",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "default": 5}}, "required": ["query"]}},
        {"name": "extract_pdf", "description": "Extract text from a local PDF file",
         "input_schema": {"type": "object", "properties": {"file_path": {"type": "string", "description": "Path to PDF file"}, "max_pages": {"type": "integer", "description": "Max pages to extract"}}, "required": ["file_path"]}},
        {"name": "analyze_arxiv_paper", "description": "Download and analyze an arXiv paper by ID",
         "input_schema": {"type": "object", "properties": {"arxiv_id": {"type": "string", "description": "arXiv ID (e.g., 2301.00001)"}, "max_pages": {"type": "integer", "default": 15}}, "required": ["arxiv_id"]}},
        {"name": "search_pdf", "description": "Search for text within a PDF",
         "input_schema": {"type": "object", "properties": {"file_path": {"type": "string"}, "query": {"type": "string"}}, "required": ["file_path", "query"]}},
        {"name": "list_pdfs", "description": "List all downloaded PDFs",
         "input_schema": {"type": "object", "properties": {}}}
    ]

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.RESEARCHER, client)

    def research(self, query: str, sources: list = None) -> TaskResult:
        start_time = time.time()
        if sources is None:
            sources = ["arxiv", "wikipedia", "github"]

        display_agent_activity(self.role, f"Researching: {query}")

        messages = [{"role": "user", "content": f"Research this topic: {query}\n\nUse these sources: {', '.join(sources)}"}]
        conversation = messages.copy()
        all_findings = []

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
                        name = block.name
                        inp = block.input

                        display_agent_activity(self.role, f"  -> {name}")

                        # Execute tool
                        if name == "search_arxiv":
                            result, _ = search_arxiv(inp["query"], inp.get("max_results", 5))
                        elif name == "search_wikipedia":
                            result, _ = search_wikipedia(inp["query"])
                        elif name == "search_github_repos":
                            result, _ = search_github_repos(inp["query"], inp.get("max_results", 5))
                        elif name == "search_hackernews":
                            result, _ = search_hackernews(inp["query"], inp.get("max_results", 5))
                        elif name == "search_stackoverflow":
                            result, _ = search_stackoverflow(inp["query"], inp.get("max_results", 5))
                        elif name == "extract_pdf":
                            result = extract_pdf(inp["file_path"], inp.get("max_pages"))
                        elif name == "analyze_arxiv_paper":
                            result = analyze_arxiv_paper(inp["arxiv_id"], inp.get("max_pages", 15))
                        elif name == "search_pdf":
                            result = search_pdf(inp["file_path"], inp["query"])
                        elif name == "list_pdfs":
                            result = list_downloaded_pdfs()
                        else:
                            result = f"Unknown tool: {name}"

                        all_findings.append(f"[{name}]\n{result}")
                        tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

                conversation.append({"role": "user", "content": tool_results})
            else:
                break

        elapsed = (time.time() - start_time) * 1000
        combined = "\n\n---\n\n".join(all_findings)
        self.log_execution(query, combined, elapsed)

        return TaskResult(agent=self.role, success=True, result=combined,
                         data={"sources_used": sources}, execution_time_ms=elapsed)


class AnalystAgent(BaseAgent):
    """ANALYST: Synthesizes information"""

    SYSTEM_PROMPT = """You are an ANALYST agent specialized in synthesizing information.

Analyze research findings and provide:
1. KEY FINDINGS: Most important discoveries
2. PATTERNS: Trends and connections
3. COMPARISONS: How sources align or differ
4. GAPS: What's missing
5. CONCLUSIONS: Evidence-based takeaways"""

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.ANALYST, client)

    def analyze(self, research_data: str, focus: str = None) -> TaskResult:
        start_time = time.time()
        display_agent_activity(self.role, "Analyzing findings...")

        focus_text = f"\n\nFocus on: {focus}" if focus else ""
        messages = [{"role": "user", "content": f"Analyze these findings:{focus_text}\n\n{research_data}"}]

        response = self._call_llm(self.SYSTEM_PROMPT, messages, max_tokens=2048)
        analysis = "".join(b.text for b in response.content if hasattr(b, "text"))

        elapsed = (time.time() - start_time) * 1000
        self.log_execution("analysis", analysis, elapsed)

        return TaskResult(agent=self.role, success=True, result=analysis, execution_time_ms=elapsed)


class WriterAgent(BaseAgent):
    """WRITER: Creates formatted reports"""

    SYSTEM_PROMPT = """You are a WRITER agent that creates clear, well-formatted content.

Output formats:
- SUMMARY: Brief 2-3 paragraph overview
- REPORT: Detailed document with sections
- BULLET_POINTS: Key takeaways as list
- EXECUTIVE_BRIEF: High-level summary"""

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.WRITER, client)

    def write(self, content: str, format_type: str = "REPORT", audience: str = "general") -> TaskResult:
        start_time = time.time()
        display_agent_activity(self.role, f"Writing {format_type}...")

        messages = [{"role": "user", "content": f"Create a {format_type} for {audience} audience:\n\n{content}"}]

        response = self._call_llm(self.SYSTEM_PROMPT, messages, max_tokens=3000)
        written = "".join(b.text for b in response.content if hasattr(b, "text"))

        elapsed = (time.time() - start_time) * 1000
        self.log_execution(f"{format_type}", written, elapsed)

        return TaskResult(agent=self.role, success=True, result=written,
                         data={"format": format_type}, execution_time_ms=elapsed)


class CoordinatorAgent(BaseAgent):
    """COORDINATOR: Orchestrates workflow"""

    SYSTEM_PROMPT = """You are the COORDINATOR that orchestrates a research team.

Team: RESEARCHER (gathers info, PDFs), ANALYST (synthesizes), WRITER (formats)

Analyze queries and create JSON execution plans:
{
    "complexity": "simple|moderate|complex",
    "plan": ["step1", "step2"],
    "agents": ["researcher", "analyst", "writer"],
    "sources": ["arxiv", "pdf", "github"],
    "output_format": "SUMMARY|REPORT"
}

For PDF-related queries, include "pdf" in sources.
For arXiv paper analysis, include both "arxiv" and "pdf"."""

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.COORDINATOR, client)
        self.researcher = ResearcherAgent(client)
        self.analyst = AnalystAgent(client)
        self.writer = WriterAgent(client)

    def create_plan(self, query: str) -> ResearchPlan:
        display_agent_activity(self.role, "Creating plan...")

        messages = [{"role": "user", "content": f"Create execution plan for: {query}\n\nReturn JSON only."}]
        response = self._call_llm(self.SYSTEM_PROMPT, messages, max_tokens=500)
        plan_text = "".join(b.text for b in response.content if hasattr(b, "text"))

        try:
            match = re.search(r'\{[^{}]*\}', plan_text, re.DOTALL)
            plan_data = json.loads(match.group()) if match else json.loads(plan_text)
        except:
            plan_data = {
                "complexity": "moderate",
                "plan": ["Research", "Analyze", "Write"],
                "agents": ["researcher", "analyst", "writer"],
                "sources": ["arxiv", "wikipedia"],
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
        start_time = time.time()

        plan = self.create_plan(query)
        display_plan(plan)

        results = []

        if "researcher" in plan.agents_needed:
            result = self.researcher.research(query, plan.estimated_sources)
            results.append(result)
            display_agent_result(result)

        if "analyst" in plan.agents_needed and results:
            result = self.analyst.analyze(results[-1].result)
            results.append(result)
            display_agent_result(result)

        if "writer" in plan.agents_needed:
            content = results[-1].result if results else query
            fmt = "REPORT" if plan.complexity == "complex" else "SUMMARY"
            result = self.writer.write(content, fmt)
            results.append(result)

        total_time = (time.time() - start_time) * 1000
        display_execution_summary(plan, results, total_time)

        return results[-1].result if results else "No results."


# =============================================================================
# UI HELPERS
# =============================================================================

def display_welcome():
    text = """[bold cyan]RESEARCH ASSISTANT + PDF[/bold cyan] [dim]v12.0[/dim]

[yellow]Knowledge Sources:[/yellow]
  [green]ARXIV[/green]     Academic papers          [green]WIKI[/green]      Wikipedia
  [green]GITHUB[/green]    Repositories             [green]HACKER[/green]    HackerNews
  [green]STACK[/green]     Stack Overflow           [magenta]PDF[/magenta]       Local & arXiv PDFs

[yellow]PDF Commands:[/yellow]
  [cyan]pdf <path>[/cyan]        Extract text from local PDF
  [cyan]arxiv <id>[/cyan]        Download & analyze arXiv paper (e.g., arxiv 2301.00001)
  [cyan]pdfs[/cyan]              List downloaded PDFs
  [cyan]search <path> <q>[/cyan] Search within a PDF

[yellow]Other Commands:[/yellow]
  [cyan]stats[/cyan]    Statistics    [cyan]agents[/cyan]   Agent status    [cyan]quit[/cyan]     Exit"""

    console.print(Panel(text, title="[bold white]Welcome[/bold white]", border_style="blue", box=box.DOUBLE))


def display_agent_activity(role: AgentRole, message: str):
    colors = {AgentRole.COORDINATOR: "blue", AgentRole.RESEARCHER: "green",
              AgentRole.ANALYST: "magenta", AgentRole.WRITER: "cyan"}
    console.print(f"  [{colors.get(role, 'white')}]{role.value.upper()}[/{colors.get(role, 'white')}] {message}")


def display_plan(plan: ResearchPlan):
    tree = Tree(f"[bold blue]Plan[/bold blue] ({plan.complexity})")
    tree.add("[yellow]Agents:[/yellow] " + ", ".join(plan.agents_needed))
    tree.add("[yellow]Sources:[/yellow] " + ", ".join(plan.estimated_sources))
    console.print(tree)
    console.print()


def display_agent_result(result: TaskResult):
    colors = {AgentRole.RESEARCHER: "green", AgentRole.ANALYST: "magenta", AgentRole.WRITER: "cyan"}
    color = colors.get(result.agent, "white")
    console.print(f"  [{color}]{result.agent.value.upper()}[/{color}] Done ({result.execution_time_ms:.0f}ms)")


def display_execution_summary(plan: ResearchPlan, results: list, total_time_ms: float):
    table = Table(title="Summary", box=box.ROUNDED, border_style="blue")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Complexity", plan.complexity)
    table.add_row("Agents", ", ".join(plan.agents_needed))
    table.add_row("Sources", ", ".join(plan.estimated_sources))
    table.add_row("Total Time", f"{total_time_ms:.0f}ms")
    console.print()
    console.print(table)


def display_response(text: str):
    console.print()
    console.print(Panel(Markdown(text), title="[cyan]Report[/cyan]", border_style="cyan", box=box.ROUNDED, padding=(1, 2)))


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

        if user_input.lower() == 'stats':
            cs = cache.get_stats()
            pdfs = pdf_manager.list_pdfs()
            console.print(f"[cyan]Cache:[/cyan] {cs['entries']} entries, {cs['hit_rate']} hit rate")
            console.print(f"[cyan]PDFs:[/cyan] {len(pdfs)} downloaded")
            continue

        if user_input.lower() == 'pdfs':
            result = list_downloaded_pdfs()
            console.print(result)
            continue

        if user_input.lower() == 'agents':
            table = Table(title="Agents", box=box.ROUNDED)
            table.add_column("Agent")
            table.add_column("Tasks")
            for agent in [coordinator, coordinator.researcher, coordinator.analyst, coordinator.writer]:
                table.add_row(agent.role.value.upper(), str(len(agent.execution_history)))
            console.print(table)
            continue

        # Direct PDF commands
        if user_input.lower().startswith('pdf '):
            path = user_input[4:].strip().strip('"\'')
            with Progress(SpinnerColumn(), TextColumn("[cyan]Extracting PDF...[/cyan]"), console=console, transient=True) as p:
                p.add_task("", total=None)
                result = extract_pdf(path)
            console.print(Panel(result[:3000] + ("..." if len(result) > 3000 else ""),
                               title="PDF Content", border_style="magenta"))
            continue

        if user_input.lower().startswith('arxiv '):
            arxiv_id = user_input[6:].strip()
            with Progress(SpinnerColumn(), TextColumn("[cyan]Downloading & analyzing arXiv paper...[/cyan]"), console=console, transient=True) as p:
                p.add_task("", total=None)
                result = analyze_arxiv_paper(arxiv_id)
            console.print(Panel(result[:3000] + ("..." if len(result) > 3000 else ""),
                               title=f"arXiv {arxiv_id}", border_style="magenta"))
            continue

        if user_input.lower().startswith('search '):
            parts = user_input[7:].strip().split(' ', 1)
            if len(parts) == 2:
                path, query = parts
                result = search_pdf(path.strip('"\''), query)
                console.print(Panel(result, title="Search Results", border_style="yellow"))
            else:
                console.print("[red]Usage: search <pdf_path> <query>[/red]")
            continue

        # Multi-agent workflow
        console.print()
        result = coordinator.execute(user_input)
        display_response(result)


if __name__ == "__main__":
    main()
