#!/usr/bin/env python3
"""
Level 13: Research Assistant with Diagram Generation

New capabilities:
- Auto-generate Mermaid flowcharts from research workflows
- Create sequence diagrams for API interactions
- Build class diagrams from code analysis
- Generate mindmaps from topics/concepts
- Export diagrams to markdown files

Architecture:
┌─────────────────────────────────────────────────────────────┐
│                      USER QUERY                              │
│  "Create a diagram of..." / "Visualize the flow..."         │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    COORDINATOR                               │
└────────┬──────────────┬──────────────┬──────────────┬───────┘
         ▼              ▼              ▼              ▼
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│ RESEARCHER │  │  ANALYST   │  │   WRITER   │  │ DIAGRAMMER │
│            │  │            │  │            │  │            │
│ + PDF      │  │ - Compare  │  │ - Reports  │  │ - Flowchart│
│   Extract  │  │ - Patterns │  │ - Summaries│  │ - Sequence │
│ + arXiv    │  │ - Insights │  │ - Format   │  │ - Class    │
│   Download │  │            │  │            │  │ - Mindmap  │
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
from typing import Optional, List
from enum import Enum

# Rich library imports
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.markdown import Markdown
from rich import box
from rich.tree import Tree
from rich.syntax import Syntax

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
DIAGRAMS_DIR = DATA_DIR / "diagrams"
DIAGRAMS_DIR.mkdir(exist_ok=True)
CACHE_FILE = DATA_DIR / "api_cache.json"
PDF_CACHE_FILE = DATA_DIR / "pdf_cache.json"


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
    GANTT = "gantt"
    PIE = "pie"


@dataclass
class Diagram:
    """Represents a generated diagram"""
    diagram_type: DiagramType
    title: str
    mermaid_code: str
    description: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    file_path: Optional[str] = None


# =============================================================================
# DIAGRAM GENERATOR
# =============================================================================

class DiagramGenerator:
    """
    Generates Mermaid diagrams from various inputs.

    Capabilities:
    - Flowcharts from process descriptions
    - Sequence diagrams from API/interaction flows
    - Class diagrams from code or concepts
    - Mindmaps from topic hierarchies
    - State diagrams from state machine descriptions
    """

    def __init__(self, client: Anthropic, diagrams_dir: Path = DIAGRAMS_DIR):
        self.client = client
        self.diagrams_dir = diagrams_dir
        self.generated_diagrams: List[Diagram] = []

    def _call_llm(self, system: str, prompt: str, max_tokens: int = 2048) -> str:
        """Call Claude to generate diagram code"""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        return "".join(b.text for b in response.content if hasattr(b, "text"))

    def generate_flowchart(self, description: str, direction: str = "TD") -> Diagram:
        """
        Generate a flowchart from a process description.

        Args:
            description: Text description of the process/workflow
            direction: TD (top-down), LR (left-right), BT, RL
        """
        system = """You are a diagram expert. Generate ONLY valid Mermaid flowchart code.

Rules:
1. Start with: flowchart {direction}
2. Use meaningful node IDs (A, B, C or descriptive like START, PROCESS, END)
3. Use proper node shapes:
   - [text] for rectangles (processes)
   - (text) for rounded (terminals)
   - {text} for diamonds (decisions)
   - [(text)] for database
   - ((text)) for circles
4. Use proper arrows: -->, --text-->, -.->
5. Use subgraphs for grouping related steps
6. Add styling for important nodes

Output ONLY the mermaid code block, nothing else."""

        prompt = f"""Create a flowchart for this process:

{description}

Direction: {direction}

Generate the Mermaid flowchart code:"""

        mermaid_code = self._call_llm(system, prompt)

        # Clean up the code
        mermaid_code = self._clean_mermaid_code(mermaid_code)

        diagram = Diagram(
            diagram_type=DiagramType.FLOWCHART,
            title=f"Flowchart: {description[:50]}...",
            mermaid_code=mermaid_code,
            description=description
        )

        self.generated_diagrams.append(diagram)
        return diagram

    def generate_sequence(self, interaction_description: str) -> Diagram:
        """
        Generate a sequence diagram from interaction description.

        Args:
            interaction_description: Description of participant interactions
        """
        system = """You are a diagram expert. Generate ONLY valid Mermaid sequence diagram code.

Rules:
1. Start with: sequenceDiagram
2. Define participants with: participant A as Name
3. Use proper arrow types:
   - ->> for solid with arrowhead
   - -->> for dotted with arrowhead
   - -) for async (open arrow)
4. Use activations: +/- after arrows
5. Add notes: Note right of A: text
6. Use loops, alt/else, opt, par blocks
7. Keep participant names short but meaningful

Output ONLY the mermaid code block, nothing else."""

        prompt = f"""Create a sequence diagram for these interactions:

{interaction_description}

Generate the Mermaid sequence diagram code:"""

        mermaid_code = self._call_llm(system, prompt)
        mermaid_code = self._clean_mermaid_code(mermaid_code)

        diagram = Diagram(
            diagram_type=DiagramType.SEQUENCE,
            title=f"Sequence: {interaction_description[:50]}...",
            mermaid_code=mermaid_code,
            description=interaction_description
        )

        self.generated_diagrams.append(diagram)
        return diagram

    def generate_class_diagram(self, class_description: str) -> Diagram:
        """
        Generate a class diagram from class/concept description.

        Args:
            class_description: Description of classes and relationships
        """
        system = """You are a diagram expert. Generate ONLY valid Mermaid class diagram code.

Rules:
1. Start with: classDiagram
2. Define classes with members:
   class ClassName {
       +publicAttr type
       -privateAttr type
       #protectedAttr type
       +method() returnType
   }
3. Use proper relationships:
   - <|-- inheritance
   - *-- composition
   - o-- aggregation
   - --> association
   - ..> dependency
   - ..|> realization
4. Add cardinality: "1" --> "*"
5. Use <<interface>>, <<abstract>>, <<enumeration>>

Output ONLY the mermaid code block, nothing else."""

        prompt = f"""Create a class diagram for:

{class_description}

Generate the Mermaid class diagram code:"""

        mermaid_code = self._call_llm(system, prompt)
        mermaid_code = self._clean_mermaid_code(mermaid_code)

        diagram = Diagram(
            diagram_type=DiagramType.CLASS,
            title=f"Class Diagram: {class_description[:50]}...",
            mermaid_code=mermaid_code,
            description=class_description
        )

        self.generated_diagrams.append(diagram)
        return diagram

    def generate_mindmap(self, topic: str, subtopics: str = None) -> Diagram:
        """
        Generate a mindmap from a topic and subtopics.

        Args:
            topic: Central topic
            subtopics: Description of subtopics/branches
        """
        system = """You are a diagram expert. Generate ONLY valid Mermaid mindmap code.

Rules:
1. Start with: mindmap
2. Root node uses double parentheses: root((Central Topic))
3. Branches use indentation (4 spaces per level)
4. Node shapes:
   - (text) for rounded
   - ((text)) for circle
   - ))text(( for cloud
   - [text] for square
5. Keep it hierarchical and balanced
6. Use 3-5 main branches
7. 2-4 sub-items per branch

Output ONLY the mermaid code block, nothing else."""

        full_description = f"Central topic: {topic}"
        if subtopics:
            full_description += f"\n\nSubtopics/branches to include:\n{subtopics}"

        prompt = f"""Create a mindmap for:

{full_description}

Generate the Mermaid mindmap code:"""

        mermaid_code = self._call_llm(system, prompt)
        mermaid_code = self._clean_mermaid_code(mermaid_code)

        diagram = Diagram(
            diagram_type=DiagramType.MINDMAP,
            title=f"Mindmap: {topic}",
            mermaid_code=mermaid_code,
            description=full_description
        )

        self.generated_diagrams.append(diagram)
        return diagram

    def generate_state_diagram(self, state_description: str) -> Diagram:
        """
        Generate a state diagram from state machine description.

        Args:
            state_description: Description of states and transitions
        """
        system = """You are a diagram expert. Generate ONLY valid Mermaid state diagram code.

Rules:
1. Start with: stateDiagram-v2
2. Initial state: [*] --> FirstState
3. Final state: LastState --> [*]
4. Transitions: State1 --> State2: event
5. Composite states:
   state CompositeName {
       [*] --> SubState1
       SubState1 --> SubState2
   }
6. Fork/Join: state fork_state <<fork>>
7. Choice: state check <<choice>>
8. Notes: note right of State1: text

Output ONLY the mermaid code block, nothing else."""

        prompt = f"""Create a state diagram for:

{state_description}

Generate the Mermaid state diagram code:"""

        mermaid_code = self._call_llm(system, prompt)
        mermaid_code = self._clean_mermaid_code(mermaid_code)

        diagram = Diagram(
            diagram_type=DiagramType.STATE,
            title=f"State Diagram: {state_description[:50]}...",
            mermaid_code=mermaid_code,
            description=state_description
        )

        self.generated_diagrams.append(diagram)
        return diagram

    def generate_er_diagram(self, entity_description: str) -> Diagram:
        """
        Generate an ER diagram from entity description.

        Args:
            entity_description: Description of entities and relationships
        """
        system = """You are a diagram expert. Generate ONLY valid Mermaid ER diagram code.

Rules:
1. Start with: erDiagram
2. Define relationships:
   - ||--o{ one to many
   - ||--|| one to one
   - }o--o{ many to many
3. Entity attributes:
   ENTITY {
       type name PK
       type name FK
       type name
   }
4. Relationship labels: CUSTOMER ||--o{ ORDER : places

Output ONLY the mermaid code block, nothing else."""

        prompt = f"""Create an ER diagram for:

{entity_description}

Generate the Mermaid ER diagram code:"""

        mermaid_code = self._call_llm(system, prompt)
        mermaid_code = self._clean_mermaid_code(mermaid_code)

        diagram = Diagram(
            diagram_type=DiagramType.ER,
            title=f"ER Diagram: {entity_description[:50]}...",
            mermaid_code=mermaid_code,
            description=entity_description
        )

        self.generated_diagrams.append(diagram)
        return diagram

    def generate_from_research(self, research_text: str, diagram_type: DiagramType = None) -> Diagram:
        """
        Automatically generate an appropriate diagram from research findings.

        Args:
            research_text: Research text to visualize
            diagram_type: Optional specific type, otherwise auto-detected
        """
        # Auto-detect best diagram type if not specified
        if diagram_type is None:
            diagram_type = self._detect_best_diagram_type(research_text)

        if diagram_type == DiagramType.FLOWCHART:
            return self.generate_flowchart(research_text)
        elif diagram_type == DiagramType.SEQUENCE:
            return self.generate_sequence(research_text)
        elif diagram_type == DiagramType.CLASS:
            return self.generate_class_diagram(research_text)
        elif diagram_type == DiagramType.MINDMAP:
            # Extract main topic for mindmap
            topic = research_text.split('\n')[0][:100]
            return self.generate_mindmap(topic, research_text)
        elif diagram_type == DiagramType.STATE:
            return self.generate_state_diagram(research_text)
        elif diagram_type == DiagramType.ER:
            return self.generate_er_diagram(research_text)
        else:
            # Default to mindmap for general content
            topic = "Research Findings"
            return self.generate_mindmap(topic, research_text)

    def _detect_best_diagram_type(self, text: str) -> DiagramType:
        """Detect the best diagram type for the given text"""
        text_lower = text.lower()

        # Keywords for each diagram type
        flow_keywords = ['process', 'workflow', 'step', 'flow', 'procedure', 'algorithm']
        seq_keywords = ['request', 'response', 'api', 'call', 'message', 'interaction', 'communicate']
        class_keywords = ['class', 'object', 'inherit', 'method', 'attribute', 'interface']
        state_keywords = ['state', 'transition', 'event', 'lifecycle', 'status']
        er_keywords = ['entity', 'table', 'database', 'relationship', 'schema', 'foreign key']

        # Count matches
        scores = {
            DiagramType.FLOWCHART: sum(1 for k in flow_keywords if k in text_lower),
            DiagramType.SEQUENCE: sum(1 for k in seq_keywords if k in text_lower),
            DiagramType.CLASS: sum(1 for k in class_keywords if k in text_lower),
            DiagramType.STATE: sum(1 for k in state_keywords if k in text_lower),
            DiagramType.ER: sum(1 for k in er_keywords if k in text_lower),
        }

        best_type = max(scores, key=scores.get)

        # If no clear winner, default to mindmap
        if scores[best_type] == 0:
            return DiagramType.MINDMAP

        return best_type

    def _clean_mermaid_code(self, code: str) -> str:
        """Clean and validate Mermaid code"""
        # Remove markdown code fences if present
        code = re.sub(r'^```mermaid\s*', '', code, flags=re.MULTILINE)
        code = re.sub(r'^```\s*$', '', code, flags=re.MULTILINE)
        code = code.strip()
        return code

    def save_diagram(self, diagram: Diagram, filename: str = None) -> str:
        """
        Save diagram to a markdown file.

        Args:
            diagram: Diagram to save
            filename: Optional filename (without extension)

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{diagram.diagram_type.value}_{timestamp}"

        filepath = self.diagrams_dir / f"{filename}.md"

        content = f"""# {diagram.title}

**Type:** {diagram.diagram_type.value}
**Created:** {diagram.created_at}

## Description

{diagram.description}

## Diagram

```mermaid
{diagram.mermaid_code}
```

---
*Generated by Research Assistant v13*
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        diagram.file_path = str(filepath)
        return str(filepath)

    def list_diagrams(self) -> List[dict]:
        """List all saved diagram files"""
        diagrams = []
        for f in self.diagrams_dir.glob("*.md"):
            diagrams.append({
                "name": f.name,
                "path": str(f),
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })
        return sorted(diagrams, key=lambda x: x["modified"], reverse=True)

    def get_session_diagrams(self) -> List[Diagram]:
        """Get all diagrams generated in this session"""
        return self.generated_diagrams


# Initialize diagram generator
diagram_generator = DiagramGenerator(client)


# =============================================================================
# PDF MANAGEMENT (from Level 12)
# =============================================================================

class PDFManager:
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
        if not PDF_AVAILABLE:
            return {"success": False, "error": "pypdf not installed"}
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            return {"success": False, "error": f"File not found: {pdf_path}"}

        cache_key = f"{pdf_path}:{max_pages}"
        if cache_key in self.cache["pdfs"]:
            cached = self.cache["pdfs"][cache_key]
            if cached.get("mtime") == os.path.getmtime(pdf_path):
                return {"success": True, "cached": True, **cached}

        try:
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)
            pages_to_extract = min(max_pages, total_pages) if max_pages else total_pages

            metadata = {}
            if reader.metadata:
                metadata = {
                    "title": reader.metadata.get("/Title", ""),
                    "author": reader.metadata.get("/Author", ""),
                }

            text_pages = []
            for i in range(pages_to_extract):
                page = reader.pages[i]
                text = page.extract_text() or ""
                text_pages.append({"page": i + 1, "text": text})

            full_text = "\n\n".join([f"[Page {p['page']}]\n{p['text']}" for p in text_pages])

            result = {
                "success": True, "cached": False, "file_path": str(pdf_path),
                "file_name": pdf_path.name, "total_pages": total_pages,
                "extracted_pages": pages_to_extract, "metadata": metadata,
                "text": full_text, "char_count": len(full_text),
                "mtime": os.path.getmtime(pdf_path)
            }

            cache_entry = {k: v for k, v in result.items() if k != "text"}
            cache_entry["text_preview"] = full_text[:1000]
            self.cache["pdfs"][cache_key] = cache_entry
            self._save_cache()
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def download_arxiv_pdf(self, arxiv_id: str) -> dict:
        if "arxiv.org" in arxiv_id:
            match = re.search(r'(\d{4}\.\d{4,5})(v\d+)?', arxiv_id)
            if match:
                arxiv_id = match.group(1)
        arxiv_id = arxiv_id.strip()
        pdf_path = self.pdf_dir / f"arxiv_{arxiv_id.replace('.', '_')}.pdf"

        if pdf_path.exists():
            return {"success": True, "cached": True, "file_path": str(pdf_path), "arxiv_id": arxiv_id}

        try:
            response = requests.get(f"https://arxiv.org/pdf/{arxiv_id}.pdf", timeout=30, stream=True)
            if response.status_code != 200:
                return {"success": False, "error": f"Download failed: {response.status_code}"}

            with open(pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return {"success": True, "cached": False, "file_path": str(pdf_path), "arxiv_id": arxiv_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_pdfs(self) -> list:
        return [{"name": f.name, "path": str(f), "size_mb": f.stat().st_size / (1024*1024)}
                for f in self.pdf_dir.glob("*.pdf")]


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
            arxiv_id = paper_id.split('/')[-1] if paper_id else ""
            papers.append({
                "title": entry.find('atom:title', ns).text.strip().replace('\n', ' '),
                "authors": [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)],
                "summary": entry.find('atom:summary', ns).text.strip()[:300] + "...",
                "arxiv_id": arxiv_id, "link": paper_id
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
        result = f"Found articles:\n\n"
        for i, a in enumerate(data['query']['search'], 1):
            result += f"{i}. {a['title']}\n   {a['snippet'][:100]}...\n\n"
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
        result = "HackerNews stories:\n\n"
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
# PDF TOOL FUNCTIONS
# =============================================================================

def extract_pdf(file_path: str, max_pages: int = None) -> str:
    result = pdf_manager.extract_text(file_path, max_pages)
    if not result["success"]:
        return f"Error: {result.get('error')}"
    output = f"PDF: {result['file_name']}\nPages: {result['extracted_pages']}/{result['total_pages']}\n"
    output += f"\n{result['text'][:8000]}"
    return output

def analyze_arxiv_paper(arxiv_id: str, max_pages: int = 15) -> str:
    download = pdf_manager.download_arxiv_pdf(arxiv_id)
    if not download["success"]:
        return f"Error: {download.get('error')}"
    extract = pdf_manager.extract_text(download["file_path"], max_pages)
    if not extract["success"]:
        return f"Error: {extract.get('error')}"
    return f"arXiv {arxiv_id}:\n\n{extract['text'][:10000]}"


# =============================================================================
# DIAGRAM TOOL FUNCTIONS
# =============================================================================

def create_flowchart(description: str, direction: str = "TD") -> str:
    """Create a flowchart from description"""
    display_agent_activity(AgentRole.DIAGRAMMER, f"Creating flowchart...")
    diagram = diagram_generator.generate_flowchart(description, direction)
    filepath = diagram_generator.save_diagram(diagram)
    return f"Flowchart created and saved to: {filepath}\n\n```mermaid\n{diagram.mermaid_code}\n```"

def create_sequence_diagram(description: str) -> str:
    """Create a sequence diagram"""
    display_agent_activity(AgentRole.DIAGRAMMER, f"Creating sequence diagram...")
    diagram = diagram_generator.generate_sequence(description)
    filepath = diagram_generator.save_diagram(diagram)
    return f"Sequence diagram saved to: {filepath}\n\n```mermaid\n{diagram.mermaid_code}\n```"

def create_class_diagram(description: str) -> str:
    """Create a class diagram"""
    display_agent_activity(AgentRole.DIAGRAMMER, f"Creating class diagram...")
    diagram = diagram_generator.generate_class_diagram(description)
    filepath = diagram_generator.save_diagram(diagram)
    return f"Class diagram saved to: {filepath}\n\n```mermaid\n{diagram.mermaid_code}\n```"

def create_mindmap(topic: str, subtopics: str = None) -> str:
    """Create a mindmap"""
    display_agent_activity(AgentRole.DIAGRAMMER, f"Creating mindmap for: {topic}")
    diagram = diagram_generator.generate_mindmap(topic, subtopics)
    filepath = diagram_generator.save_diagram(diagram)
    return f"Mindmap saved to: {filepath}\n\n```mermaid\n{diagram.mermaid_code}\n```"

def create_state_diagram(description: str) -> str:
    """Create a state diagram"""
    display_agent_activity(AgentRole.DIAGRAMMER, f"Creating state diagram...")
    diagram = diagram_generator.generate_state_diagram(description)
    filepath = diagram_generator.save_diagram(diagram)
    return f"State diagram saved to: {filepath}\n\n```mermaid\n{diagram.mermaid_code}\n```"

def create_er_diagram(description: str) -> str:
    """Create an ER diagram"""
    display_agent_activity(AgentRole.DIAGRAMMER, f"Creating ER diagram...")
    diagram = diagram_generator.generate_er_diagram(description)
    filepath = diagram_generator.save_diagram(diagram)
    return f"ER diagram saved to: {filepath}\n\n```mermaid\n{diagram.mermaid_code}\n```"

def visualize_research(research_text: str, diagram_type: str = None) -> str:
    """Auto-generate diagram from research findings"""
    display_agent_activity(AgentRole.DIAGRAMMER, f"Visualizing research...")

    dtype = None
    if diagram_type:
        try:
            dtype = DiagramType(diagram_type.lower())
        except ValueError:
            pass

    diagram = diagram_generator.generate_from_research(research_text, dtype)
    filepath = diagram_generator.save_diagram(diagram)
    return f"Generated {diagram.diagram_type.value} diagram saved to: {filepath}\n\n```mermaid\n{diagram.mermaid_code}\n```"

def list_diagrams() -> str:
    """List all generated diagrams"""
    diagrams = diagram_generator.list_diagrams()
    if not diagrams:
        return "No diagrams generated yet."
    result = f"Generated Diagrams ({len(diagrams)} files):\n\n"
    for d in diagrams:
        result += f"- {d['name']}\n  Path: {d['path']}\n\n"
    return result


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
    data: dict = field(default_factory=dict)
    execution_time_ms: float = 0


@dataclass
class ResearchPlan:
    query: str
    complexity: str
    steps: list
    agents_needed: list
    estimated_sources: list
    include_diagram: bool = False
    diagram_type: str = None


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
        self.execution_history.append({"task": task, "time_ms": time_ms, "timestamp": datetime.now().isoformat()})


class ResearcherAgent(BaseAgent):
    """RESEARCHER: Gathers information"""

    SYSTEM_PROMPT = """You are a RESEARCHER agent. Gather information from multiple sources.
Use the tools available to search arXiv, Wikipedia, GitHub, HackerNews, StackOverflow.
For PDF tasks, use extract_pdf or analyze_arxiv_paper.
Return structured findings."""

    TOOLS = [
        {"name": "search_arxiv", "description": "Search arXiv papers",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "default": 5}}, "required": ["query"]}},
        {"name": "search_wikipedia", "description": "Search Wikipedia",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "search_github_repos", "description": "Search GitHub",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "search_hackernews", "description": "Search HackerNews",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "search_stackoverflow", "description": "Search Stack Overflow",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "extract_pdf", "description": "Extract PDF text",
         "input_schema": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}},
        {"name": "analyze_arxiv_paper", "description": "Analyze arXiv paper by ID",
         "input_schema": {"type": "object", "properties": {"arxiv_id": {"type": "string"}}, "required": ["arxiv_id"]}},
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

        while True:
            response = self._call_llm(self.SYSTEM_PROMPT, conversation, self.TOOLS)

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
                            result, _ = search_arxiv(inp["query"], inp.get("max_results", 5))
                        elif name == "search_wikipedia":
                            result, _ = search_wikipedia(inp["query"])
                        elif name == "search_github_repos":
                            result, _ = search_github_repos(inp["query"])
                        elif name == "search_hackernews":
                            result, _ = search_hackernews(inp["query"])
                        elif name == "search_stackoverflow":
                            result, _ = search_stackoverflow(inp["query"])
                        elif name == "extract_pdf":
                            result = extract_pdf(inp["file_path"])
                        elif name == "analyze_arxiv_paper":
                            result = analyze_arxiv_paper(inp["arxiv_id"])
                        else:
                            result = f"Unknown: {name}"

                        findings.append(f"[{name}]\n{result}")
                        tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

                conversation.append({"role": "user", "content": tool_results})
            else:
                break

        elapsed = (time.time() - start_time) * 1000
        combined = "\n\n---\n\n".join(findings)
        self.log_execution(query, combined, elapsed)
        return TaskResult(agent=self.role, success=True, result=combined, execution_time_ms=elapsed)


class AnalystAgent(BaseAgent):
    """ANALYST: Synthesizes information"""

    SYSTEM_PROMPT = """You are an ANALYST. Synthesize findings and provide:
1. KEY FINDINGS
2. PATTERNS
3. COMPARISONS
4. GAPS
5. CONCLUSIONS"""

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.ANALYST, client)

    def analyze(self, research_data: str) -> TaskResult:
        start_time = time.time()
        display_agent_activity(self.role, "Analyzing...")

        response = self._call_llm(self.SYSTEM_PROMPT,
                                  [{"role": "user", "content": f"Analyze:\n\n{research_data}"}])
        analysis = "".join(b.text for b in response.content if hasattr(b, "text"))

        elapsed = (time.time() - start_time) * 1000
        self.log_execution("analysis", analysis, elapsed)
        return TaskResult(agent=self.role, success=True, result=analysis, execution_time_ms=elapsed)


class WriterAgent(BaseAgent):
    """WRITER: Creates formatted content"""

    SYSTEM_PROMPT = """You are a WRITER. Create clear, well-formatted content.
Formats: SUMMARY (brief), REPORT (detailed), BULLET_POINTS (key takeaways)"""

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.WRITER, client)

    def write(self, content: str, format_type: str = "REPORT") -> TaskResult:
        start_time = time.time()
        display_agent_activity(self.role, f"Writing {format_type}...")

        response = self._call_llm(self.SYSTEM_PROMPT,
                                  [{"role": "user", "content": f"Create {format_type}:\n\n{content}"}],
                                  max_tokens=3000)
        written = "".join(b.text for b in response.content if hasattr(b, "text"))

        elapsed = (time.time() - start_time) * 1000
        self.log_execution(format_type, written, elapsed)
        return TaskResult(agent=self.role, success=True, result=written, execution_time_ms=elapsed)


class DiagrammerAgent(BaseAgent):
    """DIAGRAMMER: Creates visual diagrams from content"""

    SYSTEM_PROMPT = """You are a DIAGRAMMER agent that creates Mermaid diagrams.

Available diagram tools:
- create_flowchart: Process flows, workflows, algorithms
- create_sequence_diagram: API interactions, message flows
- create_class_diagram: OOP structures, data models
- create_mindmap: Topic hierarchies, concepts
- create_state_diagram: State machines, lifecycles
- create_er_diagram: Database schemas
- visualize_research: Auto-detect best diagram type

Choose the appropriate diagram type based on the content."""

    TOOLS = [
        {"name": "create_flowchart", "description": "Create flowchart from process description",
         "input_schema": {"type": "object", "properties": {
             "description": {"type": "string", "description": "Process description"},
             "direction": {"type": "string", "enum": ["TD", "LR", "BT", "RL"], "default": "TD"}
         }, "required": ["description"]}},
        {"name": "create_sequence_diagram", "description": "Create sequence diagram",
         "input_schema": {"type": "object", "properties": {
             "description": {"type": "string", "description": "Interaction description"}
         }, "required": ["description"]}},
        {"name": "create_class_diagram", "description": "Create class diagram",
         "input_schema": {"type": "object", "properties": {
             "description": {"type": "string", "description": "Class/concept description"}
         }, "required": ["description"]}},
        {"name": "create_mindmap", "description": "Create mindmap",
         "input_schema": {"type": "object", "properties": {
             "topic": {"type": "string", "description": "Central topic"},
             "subtopics": {"type": "string", "description": "Subtopics to include"}
         }, "required": ["topic"]}},
        {"name": "create_state_diagram", "description": "Create state diagram",
         "input_schema": {"type": "object", "properties": {
             "description": {"type": "string", "description": "State machine description"}
         }, "required": ["description"]}},
        {"name": "create_er_diagram", "description": "Create ER diagram",
         "input_schema": {"type": "object", "properties": {
             "description": {"type": "string", "description": "Entity description"}
         }, "required": ["description"]}},
        {"name": "visualize_research", "description": "Auto-generate diagram from research",
         "input_schema": {"type": "object", "properties": {
             "research_text": {"type": "string", "description": "Research text to visualize"},
             "diagram_type": {"type": "string", "description": "Optional: flowchart, sequence, class, mindmap, state, er"}
         }, "required": ["research_text"]}},
    ]

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.DIAGRAMMER, client)

    def create_diagram(self, content: str, diagram_type: str = None) -> TaskResult:
        start_time = time.time()
        display_agent_activity(self.role, "Creating diagram...")

        type_hint = f"\nCreate a {diagram_type} diagram." if diagram_type else ""
        messages = [{"role": "user", "content": f"Create a diagram for this content:{type_hint}\n\n{content}"}]
        conversation = messages.copy()
        diagram_result = None

        while True:
            response = self._call_llm(self.SYSTEM_PROMPT, conversation, self.TOOLS)

            if response.stop_reason == "end_turn":
                text = "".join(b.text for b in response.content if hasattr(b, "text"))
                if diagram_result:
                    diagram_result += f"\n\n{text}"
                else:
                    diagram_result = text
                break
            elif response.stop_reason == "tool_use":
                conversation.append({"role": "assistant", "content": response.content})
                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        name, inp = block.name, block.input

                        if name == "create_flowchart":
                            result = create_flowchart(inp["description"], inp.get("direction", "TD"))
                        elif name == "create_sequence_diagram":
                            result = create_sequence_diagram(inp["description"])
                        elif name == "create_class_diagram":
                            result = create_class_diagram(inp["description"])
                        elif name == "create_mindmap":
                            result = create_mindmap(inp["topic"], inp.get("subtopics"))
                        elif name == "create_state_diagram":
                            result = create_state_diagram(inp["description"])
                        elif name == "create_er_diagram":
                            result = create_er_diagram(inp["description"])
                        elif name == "visualize_research":
                            result = visualize_research(inp["research_text"], inp.get("diagram_type"))
                        else:
                            result = f"Unknown: {name}"

                        diagram_result = result
                        tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

                conversation.append({"role": "user", "content": tool_results})
            else:
                break

        elapsed = (time.time() - start_time) * 1000
        self.log_execution("diagram", diagram_result or "", elapsed)
        return TaskResult(agent=self.role, success=True, result=diagram_result or "No diagram created",
                         execution_time_ms=elapsed)


class CoordinatorAgent(BaseAgent):
    """COORDINATOR: Orchestrates the research team"""

    SYSTEM_PROMPT = """You are the COORDINATOR orchestrating a research team.

Team members:
- RESEARCHER: Gathers info from APIs, PDFs
- ANALYST: Synthesizes and finds patterns
- WRITER: Creates formatted reports
- DIAGRAMMER: Creates visual diagrams (NEW!)

Analyze queries and return JSON execution plans:
{
    "complexity": "simple|moderate|complex",
    "plan": ["step1", "step2"],
    "agents": ["researcher", "analyst", "writer", "diagrammer"],
    "sources": ["arxiv", "wikipedia", "github"],
    "include_diagram": true/false,
    "diagram_type": "flowchart|sequence|class|mindmap|state|er|auto"
}

Include diagrammer when:
- User asks for visualization/diagram
- Content describes processes (flowchart)
- Content involves interactions (sequence)
- Content involves data models (class/ER)
- Content involves concepts (mindmap)
- Content involves states (state diagram)"""

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.COORDINATOR, client)
        self.researcher = ResearcherAgent(client)
        self.analyst = AnalystAgent(client)
        self.writer = WriterAgent(client)
        self.diagrammer = DiagrammerAgent(client)

    def create_plan(self, query: str) -> ResearchPlan:
        display_agent_activity(self.role, "Creating plan...")

        response = self._call_llm(self.SYSTEM_PROMPT,
                                  [{"role": "user", "content": f"Plan for: {query}\n\nReturn JSON only."}],
                                  max_tokens=500)
        plan_text = "".join(b.text for b in response.content if hasattr(b, "text"))

        try:
            match = re.search(r'\{[^{}]*\}', plan_text, re.DOTALL)
            plan_data = json.loads(match.group()) if match else json.loads(plan_text)
        except:
            plan_data = {"complexity": "moderate", "agents": ["researcher", "writer"],
                        "sources": ["wikipedia"], "include_diagram": False}

        return ResearchPlan(
            query=query,
            complexity=plan_data.get("complexity", "moderate"),
            steps=plan_data.get("plan", []),
            agents_needed=plan_data.get("agents", ["researcher", "writer"]),
            estimated_sources=plan_data.get("sources", ["wikipedia"]),
            include_diagram=plan_data.get("include_diagram", False),
            diagram_type=plan_data.get("diagram_type")
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
            display_agent_result(result)

        if "diagrammer" in plan.agents_needed or plan.include_diagram:
            content = results[-1].result if results else query
            result = self.diagrammer.create_diagram(content, plan.diagram_type)
            results.append(result)
            display_agent_result(result)

        total_time = (time.time() - start_time) * 1000
        display_execution_summary(plan, results, total_time)

        # Combine final output
        final_output = results[-2].result if len(results) > 1 and "diagrammer" in plan.agents_needed else ""
        if "diagrammer" in plan.agents_needed or plan.include_diagram:
            final_output += "\n\n---\n\n## Diagram\n\n" + results[-1].result

        return final_output if final_output else (results[-1].result if results else "No results.")


# =============================================================================
# UI HELPERS
# =============================================================================

def display_welcome():
    text = """[bold cyan]RESEARCH ASSISTANT + DIAGRAMS[/bold cyan] [dim]v13.0[/dim]

[yellow]Knowledge Sources:[/yellow]
  [green]ARXIV[/green]     Academic papers          [green]WIKI[/green]      Wikipedia
  [green]GITHUB[/green]    Repositories             [green]HACKER[/green]    HackerNews
  [green]STACK[/green]     Stack Overflow           [magenta]PDF[/magenta]       Local & arXiv PDFs

[yellow]Diagram Commands:[/yellow]
  [cyan]flowchart <desc>[/cyan]   Create flowchart
  [cyan]sequence <desc>[/cyan]    Create sequence diagram
  [cyan]class <desc>[/cyan]       Create class diagram
  [cyan]mindmap <topic>[/cyan]    Create mindmap
  [cyan]state <desc>[/cyan]       Create state diagram
  [cyan]er <desc>[/cyan]          Create ER diagram
  [cyan]diagrams[/cyan]           List saved diagrams

[yellow]PDF Commands:[/yellow]
  [cyan]pdf <path>[/cyan]         Extract text from PDF
  [cyan]arxiv <id>[/cyan]         Download & analyze arXiv paper

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
    if plan.include_diagram:
        tree.add(f"[yellow]Diagram:[/yellow] {plan.diagram_type or 'auto'}")
    console.print(tree)
    console.print()


def display_agent_result(result: TaskResult):
    colors = {AgentRole.RESEARCHER: "green", AgentRole.ANALYST: "magenta",
              AgentRole.WRITER: "cyan", AgentRole.DIAGRAMMER: "yellow"}
    color = colors.get(result.agent, "white")
    console.print(f"  [{color}]{result.agent.value.upper()}[/{color}] Done ({result.execution_time_ms:.0f}ms)")


def display_execution_summary(plan: ResearchPlan, results: list, total_time_ms: float):
    table = Table(title="Summary", box=box.ROUNDED, border_style="blue")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Complexity", plan.complexity)
    table.add_row("Agents", ", ".join(plan.agents_needed))
    table.add_row("Sources", ", ".join(plan.estimated_sources))
    if plan.include_diagram:
        table.add_row("Diagram", plan.diagram_type or "auto")
    table.add_row("Total Time", f"{total_time_ms:.0f}ms")
    console.print()
    console.print(table)


def display_response(text: str):
    console.print()
    console.print(Panel(Markdown(text), title="[cyan]Report[/cyan]", border_style="cyan", box=box.ROUNDED, padding=(1, 2)))


def display_diagram(mermaid_code: str):
    """Display diagram code with syntax highlighting"""
    console.print()
    console.print(Panel(
        Syntax(mermaid_code, "text", theme="monokai", line_numbers=False),
        title="[yellow]Mermaid Diagram[/yellow]",
        border_style="yellow",
        box=box.ROUNDED
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

        if user_input.lower() == 'stats':
            cs = cache.get_stats()
            console.print(f"[cyan]Cache:[/cyan] {cs['entries']} entries, {cs['hit_rate']} hit rate")
            console.print(f"[cyan]Diagrams:[/cyan] {len(diagram_generator.list_diagrams())} saved")
            continue

        if user_input.lower() == 'diagrams':
            result = list_diagrams()
            console.print(result)
            continue

        if user_input.lower() == 'agents':
            table = Table(title="Agents", box=box.ROUNDED)
            table.add_column("Agent")
            table.add_column("Tasks")
            for agent in [coordinator, coordinator.researcher, coordinator.analyst,
                         coordinator.writer, coordinator.diagrammer]:
                table.add_row(agent.role.value.upper(), str(len(agent.execution_history)))
            console.print(table)
            continue

        # Direct diagram commands
        if user_input.lower().startswith('flowchart '):
            desc = user_input[10:].strip()
            with Progress(SpinnerColumn(), TextColumn("[yellow]Creating flowchart...[/yellow]"), console=console, transient=True) as p:
                p.add_task("", total=None)
                result = create_flowchart(desc)
            display_diagram(result.split("```mermaid\n")[1].split("\n```")[0] if "```mermaid" in result else result)
            console.print(f"[dim]Saved to research_data/diagrams/[/dim]")
            continue

        if user_input.lower().startswith('sequence '):
            desc = user_input[9:].strip()
            with Progress(SpinnerColumn(), TextColumn("[yellow]Creating sequence diagram...[/yellow]"), console=console, transient=True) as p:
                p.add_task("", total=None)
                result = create_sequence_diagram(desc)
            display_diagram(result.split("```mermaid\n")[1].split("\n```")[0] if "```mermaid" in result else result)
            continue

        if user_input.lower().startswith('class '):
            desc = user_input[6:].strip()
            with Progress(SpinnerColumn(), TextColumn("[yellow]Creating class diagram...[/yellow]"), console=console, transient=True) as p:
                p.add_task("", total=None)
                result = create_class_diagram(desc)
            display_diagram(result.split("```mermaid\n")[1].split("\n```")[0] if "```mermaid" in result else result)
            continue

        if user_input.lower().startswith('mindmap '):
            topic = user_input[8:].strip()
            with Progress(SpinnerColumn(), TextColumn("[yellow]Creating mindmap...[/yellow]"), console=console, transient=True) as p:
                p.add_task("", total=None)
                result = create_mindmap(topic)
            display_diagram(result.split("```mermaid\n")[1].split("\n```")[0] if "```mermaid" in result else result)
            continue

        if user_input.lower().startswith('state '):
            desc = user_input[6:].strip()
            with Progress(SpinnerColumn(), TextColumn("[yellow]Creating state diagram...[/yellow]"), console=console, transient=True) as p:
                p.add_task("", total=None)
                result = create_state_diagram(desc)
            display_diagram(result.split("```mermaid\n")[1].split("\n```")[0] if "```mermaid" in result else result)
            continue

        if user_input.lower().startswith('er '):
            desc = user_input[3:].strip()
            with Progress(SpinnerColumn(), TextColumn("[yellow]Creating ER diagram...[/yellow]"), console=console, transient=True) as p:
                p.add_task("", total=None)
                result = create_er_diagram(desc)
            display_diagram(result.split("```mermaid\n")[1].split("\n```")[0] if "```mermaid" in result else result)
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
            with Progress(SpinnerColumn(), TextColumn("[cyan]Analyzing arXiv paper...[/cyan]"), console=console, transient=True) as p:
                p.add_task("", total=None)
                result = analyze_arxiv_paper(arxiv_id)
            console.print(Panel(result[:3000] + ("..." if len(result) > 3000 else ""),
                               title=f"arXiv {arxiv_id}", border_style="magenta"))
            continue

        # Multi-agent workflow
        console.print()
        result = coordinator.execute(user_input)
        display_response(result)


if __name__ == "__main__":
    main()
