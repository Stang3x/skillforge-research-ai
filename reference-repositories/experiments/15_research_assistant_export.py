#!/usr/bin/env python3
"""
Level 15: Research Assistant with Export Functionality

New capabilities:
- Export research sessions as Markdown files
- Export to PDF format (requires weasyprint or markdown2pdf)
- Auto-save research notes with metadata
- Export with included diagrams
- Session history browser

Architecture:
┌─────────────────────────────────────────────────────────────┐
│                      EXPORT MANAGER                          │
│  - Markdown export    - PDF export    - Session history     │
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
import subprocess
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

# PDF library for reading
try:
    from pypdf import PdfReader
    PDF_READ_AVAILABLE = True
except ImportError:
    PDF_READ_AVAILABLE = False

# Markdown library
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

# PDF generation - try multiple options
PDF_WRITE_METHOD = None

# Option 1: fpdf2 (pure Python, easy install)
try:
    from fpdf import FPDF
    PDF_WRITE_METHOD = "fpdf"
except ImportError:
    pass

# Option 2: weasyprint (requires GTK on Windows)
if not PDF_WRITE_METHOD:
    try:
        from weasyprint import HTML, CSS
        PDF_WRITE_METHOD = "weasyprint"
    except (ImportError, OSError):
        pass

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
EXPORTS_DIR = DATA_DIR / "exports"
EXPORTS_DIR.mkdir(exist_ok=True)
CACHE_FILE = DATA_DIR / "api_cache.json"
TOKEN_HISTORY_FILE = DATA_DIR / "token_history.json"
NOTES_FILE = DATA_DIR / "research_notes.json"


# =============================================================================
# RESEARCH NOTE & EXPORT MANAGER
# =============================================================================

@dataclass
class ResearchNote:
    """A single research note/entry"""
    query: str
    result: str
    sources_used: List[str]
    agents_used: List[str]
    tokens_used: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    diagrams: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "result": self.result,
            "sources_used": self.sources_used,
            "agents_used": self.agents_used,
            "tokens_used": self.tokens_used,
            "timestamp": self.timestamp,
            "diagrams": self.diagrams,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ResearchNote':
        return cls(
            query=data["query"],
            result=data["result"],
            sources_used=data.get("sources_used", []),
            agents_used=data.get("agents_used", []),
            tokens_used=data.get("tokens_used", 0),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            diagrams=data.get("diagrams", []),
            tags=data.get("tags", [])
        )


class ExportManager:
    """
    Manages research notes and exports.

    Features:
    - Save research notes automatically
    - Export to Markdown format
    - Export to PDF format
    - Include diagrams in exports
    - Session history browsing
    """

    # CSS for PDF styling
    PDF_CSS = """
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        max-width: 800px;
        margin: 0 auto;
        padding: 40px;
        color: #333;
    }
    h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
    h2 { color: #34495e; margin-top: 30px; }
    h3 { color: #7f8c8d; }
    code {
        background: #f4f4f4;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Consolas', monospace;
    }
    pre {
        background: #2d2d2d;
        color: #f8f8f2;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
    }
    blockquote {
        border-left: 4px solid #3498db;
        margin: 20px 0;
        padding: 10px 20px;
        background: #f9f9f9;
    }
    .metadata {
        background: #ecf0f1;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 30px;
        font-size: 0.9em;
    }
    .metadata strong { color: #2c3e50; }
    .sources { color: #27ae60; }
    .agents { color: #8e44ad; }
    .diagram {
        background: #fff;
        border: 1px solid #ddd;
        padding: 20px;
        margin: 20px 0;
        border-radius: 5px;
    }
    hr { border: none; border-top: 1px solid #eee; margin: 30px 0; }
    """

    def __init__(self, notes_file: Path = NOTES_FILE, exports_dir: Path = EXPORTS_DIR):
        self.notes_file = notes_file
        self.exports_dir = exports_dir
        self.session_notes: List[ResearchNote] = []
        self.all_notes = self._load_notes()

    def _load_notes(self) -> List[ResearchNote]:
        """Load all saved research notes"""
        if self.notes_file.exists():
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [ResearchNote.from_dict(n) for n in data.get("notes", [])]
            except:
                pass
        return []

    def _save_notes(self):
        """Save all notes to file"""
        data = {"notes": [n.to_dict() for n in self.all_notes]}
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_note(self, note: ResearchNote):
        """Add a new research note"""
        self.session_notes.append(note)
        self.all_notes.append(note)
        self._save_notes()

    def get_session_notes(self) -> List[ResearchNote]:
        """Get notes from current session"""
        return self.session_notes

    def get_all_notes(self, limit: int = None) -> List[ResearchNote]:
        """Get all saved notes"""
        notes = sorted(self.all_notes, key=lambda n: n.timestamp, reverse=True)
        return notes[:limit] if limit else notes

    def search_notes(self, query: str) -> List[ResearchNote]:
        """Search notes by query text"""
        query_lower = query.lower()
        return [n for n in self.all_notes
                if query_lower in n.query.lower() or query_lower in n.result.lower()]

    def get_notes_by_tag(self, tag: str) -> List[ResearchNote]:
        """Get notes with a specific tag"""
        return [n for n in self.all_notes if tag in n.tags]

    def export_to_markdown(self, notes: List[ResearchNote] = None,
                          filename: str = None, include_metadata: bool = True) -> str:
        """
        Export notes to Markdown format.

        Args:
            notes: Notes to export (default: session notes)
            filename: Output filename (auto-generated if None)
            include_metadata: Include metadata section

        Returns:
            Path to exported file
        """
        notes = notes or self.session_notes
        if not notes:
            return None

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_notes_{timestamp}.md"

        filepath = self.exports_dir / filename

        # Build markdown content
        lines = []

        # Title
        lines.append("# Research Notes")
        lines.append("")
        lines.append(f"*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Table of Contents
        lines.append("## Table of Contents")
        lines.append("")
        for i, note in enumerate(notes, 1):
            query_short = note.query[:50] + "..." if len(note.query) > 50 else note.query
            anchor = f"query-{i}"
            lines.append(f"{i}. [{query_short}](#{anchor})")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Each note
        for i, note in enumerate(notes, 1):
            lines.append(f"## Query {i}")
            lines.append(f"<a name=\"query-{i}\"></a>")
            lines.append("")
            lines.append(f"### {note.query}")
            lines.append("")

            if include_metadata:
                lines.append("> **Metadata**")
                lines.append(f"> - **Time:** {note.timestamp}")
                lines.append(f"> - **Sources:** {', '.join(note.sources_used) or 'N/A'}")
                lines.append(f"> - **Agents:** {', '.join(note.agents_used) or 'N/A'}")
                lines.append(f"> - **Tokens:** {note.tokens_used:,}")
                if note.tags:
                    lines.append(f"> - **Tags:** {', '.join(note.tags)}")
                lines.append("")

            lines.append("### Response")
            lines.append("")
            lines.append(note.result)
            lines.append("")

            # Include diagrams if any
            if note.diagrams:
                lines.append("### Diagrams")
                lines.append("")
                for diagram in note.diagrams:
                    lines.append("```mermaid")
                    lines.append(diagram)
                    lines.append("```")
                    lines.append("")

            lines.append("---")
            lines.append("")

        # Summary section
        lines.append("## Session Summary")
        lines.append("")
        total_tokens = sum(n.tokens_used for n in notes)
        all_sources = set()
        all_agents = set()
        for n in notes:
            all_sources.update(n.sources_used)
            all_agents.update(n.agents_used)

        lines.append(f"- **Total Queries:** {len(notes)}")
        lines.append(f"- **Total Tokens:** {total_tokens:,}")
        lines.append(f"- **Sources Used:** {', '.join(sorted(all_sources)) or 'N/A'}")
        lines.append(f"- **Agents Used:** {', '.join(sorted(all_agents)) or 'N/A'}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Generated by Research Assistant v15*")

        # Write file
        content = "\n".join(lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(filepath)

    def export_to_pdf(self, notes: List[ResearchNote] = None, filename: str = None) -> str:
        """
        Export notes to PDF format.

        Args:
            notes: Notes to export (default: session notes)
            filename: Output filename (auto-generated if None)

        Returns:
            Path to exported file or error message
        """
        # First export to markdown
        md_filename = filename.replace('.pdf', '.md') if filename else None
        md_path = self.export_to_markdown(notes, md_filename)

        if not md_path:
            return None

        # Determine PDF filename
        if filename is None:
            filename = Path(md_path).stem + ".pdf"
        pdf_path = self.exports_dir / filename

        # Try different PDF generation methods
        if PDF_WRITE_METHOD == "fpdf":
            return self._export_pdf_fpdf(md_path, str(pdf_path))
        elif PDF_WRITE_METHOD == "weasyprint" and MARKDOWN_AVAILABLE:
            return self._export_pdf_weasyprint(md_path, str(pdf_path))
        else:
            # Fallback: Try pandoc
            return self._export_pdf_pandoc(md_path, str(pdf_path))

    def _export_pdf_fpdf(self, md_path: str, pdf_path: str) -> str:
        """Export using fpdf2 (pure Python)"""
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # Create PDF with safe margins
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=20)
            pdf.set_margins(20, 20, 20)
            pdf.add_page()
            pdf.set_font('Helvetica', size=10)

            def safe_text(text):
                """Make text safe for PDF"""
                return ''.join(c if ord(c) < 256 else '?' for c in text.replace('\r', ''))

            def write_text(text, size=10, bold=False, color=(0, 0, 0), prefix=''):
                """Write text with error handling"""
                try:
                    pdf.set_font('Helvetica', 'B' if bold else '', size)
                    pdf.set_text_color(*color)
                    pdf.multi_cell(0, size * 0.5, safe_text(prefix + text))
                except Exception:
                    pass

            for line in md_content.split('\n'):
                line = line.rstrip()
                if not line:
                    pdf.ln(2)
                elif line.startswith('# '):
                    write_text(line[2:], 16, True, (44, 62, 80))
                    pdf.ln(3)
                elif line.startswith('## '):
                    write_text(line[3:], 13, True, (52, 73, 94))
                    pdf.ln(2)
                elif line.startswith('### '):
                    write_text(line[4:], 11, True, (100, 100, 100))
                elif line.startswith('---'):
                    pdf.ln(2)
                    pdf.set_draw_color(200, 200, 200)
                    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
                    pdf.ln(2)
                elif line.startswith('> '):
                    write_text(line[2:], 9, False, (100, 100, 100), '   ')
                elif line.startswith('- ') or line.startswith('* '):
                    write_text(line[2:], 10, False, (0, 0, 0), '  - ')
                elif line.startswith('**'):
                    write_text(line.replace('**', ''), 10, True)
                elif line.startswith('```'):
                    continue
                else:
                    write_text(line, 10)

            pdf.output(pdf_path)
            return pdf_path
        except Exception as e:
            return f"Error: {e}. Markdown saved to: {md_path}"

    def _export_pdf_weasyprint(self, md_path: str, pdf_path: str) -> str:
        """Export using weasyprint"""
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            html_content = markdown.markdown(
                md_content,
                extensions=['tables', 'fenced_code', 'toc']
            )

            full_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
            <title>Research Notes</title></head><body>{html_content}</body></html>"""

            HTML(string=full_html).write_pdf(pdf_path, stylesheets=[CSS(string=self.PDF_CSS)])
            return pdf_path
        except Exception as e:
            return f"Error: {e}"

    def _export_pdf_pandoc(self, md_path: str, pdf_path: str) -> str:
        """Export using pandoc (if available)"""
        try:
            result = subprocess.run(
                ['pandoc', md_path, '-o', pdf_path, '-V', 'geometry:margin=1in'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return pdf_path
            return f"Pandoc error: {result.stderr}"
        except FileNotFoundError:
            return f"PDF requires fpdf2, weasyprint, or pandoc. Markdown saved to: {md_path}"

    def export_single_note(self, note: ResearchNote, format: str = "md") -> str:
        """Export a single note"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_slug = re.sub(r'[^\w\s-]', '', note.query[:30]).strip().replace(' ', '_')
        filename = f"note_{query_slug}_{timestamp}.{format}"

        if format == "md":
            return self.export_to_markdown([note], filename)
        elif format == "pdf":
            return self.export_to_pdf([note], filename)
        return None

    def list_exports(self) -> List[dict]:
        """List all exported files"""
        exports = []
        for f in self.exports_dir.glob("*"):
            if f.suffix in ['.md', '.pdf']:
                exports.append({
                    "name": f.name,
                    "path": str(f),
                    "type": f.suffix[1:].upper(),
                    "size_kb": f.stat().st_size / 1024,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                })
        return sorted(exports, key=lambda x: x["modified"], reverse=True)

    def display_notes_list(self, notes: List[ResearchNote] = None, title: str = "Research Notes"):
        """Display notes in a table"""
        notes = notes or self.session_notes
        if not notes:
            console.print("[dim]No notes to display.[/dim]")
            return

        table = Table(title=title, box=box.ROUNDED, border_style="cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Query", style="cyan", max_width=40)
        table.add_column("Sources", style="green", max_width=20)
        table.add_column("Tokens", style="yellow", justify="right")
        table.add_column("Time", style="dim", max_width=16)

        for i, note in enumerate(notes, 1):
            query_short = note.query[:37] + "..." if len(note.query) > 40 else note.query
            sources = ", ".join(note.sources_used[:2])
            if len(note.sources_used) > 2:
                sources += f" +{len(note.sources_used)-2}"
            time_str = note.timestamp[11:19] if len(note.timestamp) > 19 else note.timestamp

            table.add_row(str(i), query_short, sources, f"{note.tokens_used:,}", time_str)

        console.print(table)


# Initialize export manager
export_manager = ExportManager()


# =============================================================================
# TOKEN USAGE TRACKER
# =============================================================================

@dataclass
class TokenUsage:
    input_tokens: int
    output_tokens: int
    model: str
    agent: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class TokenTracker:
    PRICING = {
        "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
        "default": {"input": 3.00, "output": 15.00}
    }

    def __init__(self):
        self.session_usage: List[TokenUsage] = []
        self.session_start = datetime.now()

    def track(self, response, agent: str = "unknown") -> TokenUsage:
        usage = response.usage
        token_usage = TokenUsage(
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            model=response.model,
            agent=agent
        )
        self.session_usage.append(token_usage)
        return token_usage

    @property
    def total_tokens(self) -> int:
        return sum(u.total_tokens for u in self.session_usage)

    @property
    def total_input(self) -> int:
        return sum(u.input_tokens for u in self.session_usage)

    @property
    def total_output(self) -> int:
        return sum(u.output_tokens for u in self.session_usage)

    def estimate_cost(self) -> float:
        total = 0.0
        for u in self.session_usage:
            p = self.PRICING.get(u.model, self.PRICING["default"])
            total += (u.input_tokens / 1_000_000) * p["input"]
            total += (u.output_tokens / 1_000_000) * p["output"]
        return total

    def display_compact(self):
        cost = self.estimate_cost()
        color = "green" if cost < 0.10 else "yellow" if cost < 0.50 else "red"
        console.print(
            f"[dim]Tokens:[/dim] [cyan]{self.total_tokens:,}[/cyan] "
            f"[dim]({self.total_input:,}↓ {self.total_output:,}↑)[/dim] "
            f"[dim]Cost:[/dim] [{color}]${cost:.4f}[/{color}]"
        )

    def display_stats(self):
        table = Table(title="Token Usage", box=box.ROUNDED, border_style="cyan")
        table.add_column("Metric", style="yellow")
        table.add_column("Value", style="green", justify="right")
        table.add_row("Total Tokens", f"{self.total_tokens:,}")
        table.add_row("  Input", f"{self.total_input:,}")
        table.add_row("  Output", f"{self.total_output:,}")
        table.add_row("API Calls", f"{len(self.session_usage)}")
        table.add_row("Est. Cost", f"${self.estimate_cost():.4f}")
        console.print(table)


token_tracker = TokenTracker()


# =============================================================================
# DIAGRAM GENERATOR
# =============================================================================

class DiagramType(Enum):
    FLOWCHART = "flowchart"
    SEQUENCE = "sequence"
    MINDMAP = "mindmap"


@dataclass
class Diagram:
    diagram_type: DiagramType
    title: str
    mermaid_code: str
    description: str


class DiagramGenerator:
    def __init__(self, client: Anthropic, diagrams_dir: Path = DIAGRAMS_DIR):
        self.client = client
        self.diagrams_dir = diagrams_dir
        self.generated_diagrams: List[Diagram] = []

    def _call_llm(self, system: str, prompt: str, max_tokens: int = 2048) -> str:
        response = self.client.messages.create(
            model="claude-sonnet-4-5", max_tokens=max_tokens,
            system=system, messages=[{"role": "user", "content": prompt}]
        )
        token_tracker.track(response, agent="diagrammer")
        return "".join(b.text for b in response.content if hasattr(b, "text"))

    def generate_flowchart(self, description: str, direction: str = "TD") -> Diagram:
        system = "Generate ONLY valid Mermaid flowchart code. Output ONLY the mermaid code."
        code = self._call_llm(system, f"Create flowchart ({direction}):\n{description}")
        code = self._clean(code)
        diagram = Diagram(DiagramType.FLOWCHART, f"Flowchart: {description[:50]}", code, description)
        self.generated_diagrams.append(diagram)
        return diagram

    def generate_mindmap(self, topic: str, subtopics: str = None) -> Diagram:
        system = "Generate ONLY valid Mermaid mindmap code. Output ONLY the mermaid code."
        desc = f"Topic: {topic}" + (f"\nSubtopics: {subtopics}" if subtopics else "")
        code = self._call_llm(system, f"Create mindmap:\n{desc}")
        code = self._clean(code)
        diagram = Diagram(DiagramType.MINDMAP, f"Mindmap: {topic}", code, desc)
        self.generated_diagrams.append(diagram)
        return diagram

    def _clean(self, code: str) -> str:
        code = re.sub(r'^```mermaid\s*', '', code, flags=re.MULTILINE)
        code = re.sub(r'^```\s*$', '', code, flags=re.MULTILINE)
        return code.strip()

    def save_diagram(self, diagram: Diagram, filename: str = None) -> str:
        if not filename:
            filename = f"{diagram.diagram_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filepath = self.diagrams_dir / f"{filename}.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {diagram.title}\n\n```mermaid\n{diagram.mermaid_code}\n```\n")
        return str(filepath)

    def list_diagrams(self) -> List[dict]:
        return [{"name": f.name, "path": str(f)} for f in self.diagrams_dir.glob("*.md")]


diagram_generator = DiagramGenerator(client)


# =============================================================================
# PDF & CACHE MANAGEMENT
# =============================================================================

class PDFManager:
    def __init__(self, pdf_dir: Path = PDF_DIR):
        self.pdf_dir = pdf_dir

    def extract_text(self, pdf_path: str, max_pages: int = None) -> dict:
        if not PDF_READ_AVAILABLE:
            return {"success": False, "error": "pypdf not installed"}
        path = Path(pdf_path)
        if not path.exists():
            return {"success": False, "error": f"File not found: {path}"}
        try:
            reader = PdfReader(str(path))
            pages = min(max_pages, len(reader.pages)) if max_pages else len(reader.pages)
            text = "\n\n".join([f"[Page {i+1}]\n{reader.pages[i].extract_text() or ''}" for i in range(pages)])
            return {"success": True, "file_name": path.name, "total_pages": len(reader.pages),
                   "extracted_pages": pages, "text": text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def download_arxiv_pdf(self, arxiv_id: str) -> dict:
        pdf_path = self.pdf_dir / f"arxiv_{arxiv_id.replace('.', '_')}.pdf"
        if pdf_path.exists():
            return {"success": True, "cached": True, "file_path": str(pdf_path)}
        try:
            resp = requests.get(f"https://arxiv.org/pdf/{arxiv_id}.pdf", timeout=30, stream=True)
            if resp.status_code != 200:
                return {"success": False, "error": f"Download failed: {resp.status_code}"}
            with open(pdf_path, 'wb') as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            return {"success": True, "cached": False, "file_path": str(pdf_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_pdfs(self) -> list:
        return [{"name": f.name, "path": str(f)} for f in self.pdf_dir.glob("*.pdf")]


pdf_manager = PDFManager()


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

    def get(self, source: str, query: str) -> Optional[str]:
        key = hashlib.md5(f"{source}:{query.lower()}".encode()).hexdigest()
        entry = self.cache["entries"].get(key)
        if not entry:
            self.stats["misses"] += 1
            return None
        if datetime.now() - datetime.fromisoformat(entry["cached_at"]) > timedelta(seconds=self.DEFAULT_TTL.get(source, 3600)):
            self.stats["misses"] += 1
            return None
        self.stats["hits"] += 1
        return entry["response"]

    def set(self, source: str, query: str, response: str):
        key = hashlib.md5(f"{source}:{query.lower()}".encode()).hexdigest()
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
        resp = requests.get("http://export.arxiv.org/api/query",
            params={"search_query": f"all:{query}", "max_results": max_results}, timeout=10)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        papers = [{"title": e.find('atom:title', ns).text.strip().replace('\n', ' '),
                   "arxiv_id": e.find('atom:id', ns).text.split('/')[-1]}
                  for e in root.findall('atom:entry', ns)]
        if not papers:
            return "No papers found.", False
        result = f"Found {len(papers)} papers:\n\n" + "\n".join(
            f"{i}. {p['title']}\n   arXiv: {p['arxiv_id']}" for i, p in enumerate(papers, 1))
        cache.set("arxiv", query, result)
        return result, False
    except Exception as e:
        return f"Error: {e}", False

def search_wikipedia(query):
    cached = cache.get("wikipedia", query)
    if cached:
        return cached, True
    try:
        resp = requests.get("https://en.wikipedia.org/w/api.php",
            params={"action": "query", "format": "json", "list": "search", "srsearch": query, "srlimit": 3}, timeout=10)
        data = resp.json()
        articles = data.get('query', {}).get('search', [])
        if not articles:
            return "No articles found.", False
        result = "Found articles:\n\n" + "\n".join(f"{i}. {a['title']}" for i, a in enumerate(articles, 1))
        cache.set("wikipedia", query, result)
        return result, False
    except Exception as e:
        return f"Error: {e}", False

def search_github_repos(query, max_results=5):
    cached = cache.get("github", query)
    if cached:
        return cached, True
    try:
        resp = requests.get("https://api.github.com/search/repositories",
            params={"q": query, "sort": "stars", "per_page": max_results},
            headers={"User-Agent": "Research-Assistant"}, timeout=10)
        data = resp.json()
        if data.get('total_count', 0) == 0:
            return "No repos found.", False
        result = f"Found {data['total_count']:,} repos:\n\n" + "\n".join(
            f"{i}. {r['full_name']} ({r['stargazers_count']:,} stars)" for i, r in enumerate(data['items'], 1))
        cache.set("github", query, result)
        return result, False
    except Exception as e:
        return f"Error: {e}", False

def search_hackernews(query, max_results=5):
    cached = cache.get("hackernews", query)
    if cached:
        return cached, True
    try:
        resp = requests.get("https://hn.algolia.com/api/v1/search",
            params={"query": query, "tags": "story", "hitsPerPage": max_results}, timeout=10)
        hits = resp.json().get('hits', [])
        if not hits:
            return "No stories found.", False
        result = "HackerNews:\n\n" + "\n".join(
            f"{i}. {h.get('title', 'No title')} ({h.get('points', 0)} pts)" for i, h in enumerate(hits, 1))
        cache.set("hackernews", query, result)
        return result, False
    except Exception as e:
        return f"Error: {e}", False

def search_stackoverflow(query, max_results=5):
    cached = cache.get("stackoverflow", query)
    if cached:
        return cached, True
    try:
        resp = requests.get("https://api.stackexchange.com/2.3/search/advanced",
            params={"q": query, "site": "stackoverflow", "pagesize": max_results}, timeout=10)
        items = resp.json().get('items', [])
        if not items:
            return "No questions found.", False
        result = "Stack Overflow:\n\n" + "\n".join(
            f"{i}. {q.get('title', '')} {'[SOLVED]' if q.get('is_answered') else '[OPEN]'}"
            for i, q in enumerate(items, 1))
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

def create_flowchart(description: str) -> str:
    diagram = diagram_generator.generate_flowchart(description)
    diagram_generator.save_diagram(diagram)
    return f"```mermaid\n{diagram.mermaid_code}\n```"

def create_mindmap(topic: str, subtopics: str = None) -> str:
    diagram = diagram_generator.generate_mindmap(topic, subtopics)
    diagram_generator.save_diagram(diagram)
    return f"```mermaid\n{diagram.mermaid_code}\n```"


# =============================================================================
# AGENTS
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
    tokens_used: int = 0
    sources_used: List[str] = field(default_factory=list)
    diagrams: List[str] = field(default_factory=list)


@dataclass
class ResearchPlan:
    query: str
    complexity: str
    agents_needed: list
    estimated_sources: list


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
        token_tracker.track(response, agent=self.role.value)
        return response


class ResearcherAgent(BaseAgent):
    SYSTEM_PROMPT = "You are a RESEARCHER. Use tools to gather information from multiple sources."
    TOOLS = [
        {"name": "search_arxiv", "description": "Search arXiv",
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
        sources = sources or ["arxiv", "wikipedia"]
        display_agent_activity(self.role, f"Researching: {query}")

        messages = [{"role": "user", "content": f"Research: {query}\nSources: {', '.join(sources)}"}]
        conversation = messages.copy()
        findings = []
        total_tokens = 0
        sources_used = []

        while True:
            response = self._call_llm(self.SYSTEM_PROMPT, conversation, self.TOOLS)
            total_tokens += response.usage.input_tokens + response.usage.output_tokens

            if response.stop_reason == "end_turn":
                findings.append("".join(b.text for b in response.content if hasattr(b, "text")))
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
                            sources_used.append("arxiv")
                        elif name == "search_wikipedia":
                            result, _ = search_wikipedia(inp["query"])
                            sources_used.append("wikipedia")
                        elif name == "search_github_repos":
                            result, _ = search_github_repos(inp["query"])
                            sources_used.append("github")
                        elif name == "search_hackernews":
                            result, _ = search_hackernews(inp["query"])
                            sources_used.append("hackernews")
                        elif name == "search_stackoverflow":
                            result, _ = search_stackoverflow(inp["query"])
                            sources_used.append("stackoverflow")
                        else:
                            result = f"Unknown: {name}"

                        findings.append(f"[{name}]\n{result}")
                        tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

                conversation.append({"role": "user", "content": tool_results})
            else:
                break

        return TaskResult(self.role, True, "\n\n---\n\n".join(findings), total_tokens, list(set(sources_used)))


class AnalystAgent(BaseAgent):
    SYSTEM_PROMPT = "You are an ANALYST. Synthesize findings: KEY FINDINGS, PATTERNS, CONCLUSIONS."

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.ANALYST, client)

    def analyze(self, data: str) -> TaskResult:
        display_agent_activity(self.role, "Analyzing...")
        response = self._call_llm(self.SYSTEM_PROMPT, [{"role": "user", "content": f"Analyze:\n\n{data}"}])
        result = "".join(b.text for b in response.content if hasattr(b, "text"))
        return TaskResult(self.role, True, result, response.usage.input_tokens + response.usage.output_tokens)


class WriterAgent(BaseAgent):
    SYSTEM_PROMPT = "You are a WRITER. Create clear, formatted reports."

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.WRITER, client)

    def write(self, content: str, format_type: str = "REPORT") -> TaskResult:
        display_agent_activity(self.role, f"Writing {format_type}...")
        response = self._call_llm(self.SYSTEM_PROMPT,
                                  [{"role": "user", "content": f"Create {format_type}:\n\n{content}"}],
                                  max_tokens=3000)
        result = "".join(b.text for b in response.content if hasattr(b, "text"))
        return TaskResult(self.role, True, result, response.usage.input_tokens + response.usage.output_tokens)


class CoordinatorAgent(BaseAgent):
    SYSTEM_PROMPT = """You are the COORDINATOR. Create JSON execution plans:
{"complexity": "simple|moderate|complex", "agents": ["researcher", "analyst", "writer"], "sources": ["arxiv", "wikipedia"]}"""

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.COORDINATOR, client)
        self.researcher = ResearcherAgent(client)
        self.analyst = AnalystAgent(client)
        self.writer = WriterAgent(client)

    def create_plan(self, query: str) -> ResearchPlan:
        display_agent_activity(self.role, "Planning...")
        response = self._call_llm(self.SYSTEM_PROMPT,
                                  [{"role": "user", "content": f"Plan for: {query}\nJSON only."}],
                                  max_tokens=500)
        text = "".join(b.text for b in response.content if hasattr(b, "text"))
        try:
            match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            data = json.loads(match.group()) if match else {}
        except:
            data = {"complexity": "moderate", "agents": ["researcher", "writer"], "sources": ["wikipedia"]}

        return ResearchPlan(query, data.get("complexity", "moderate"),
                           data.get("agents", ["researcher", "writer"]),
                           data.get("sources", ["wikipedia"]))

    def execute(self, query: str) -> TaskResult:
        plan = self.create_plan(query)
        display_plan(plan)

        results = []
        total_tokens = 0
        all_sources = []
        all_agents = [self.role.value]

        if "researcher" in plan.agents_needed:
            r = self.researcher.research(query, plan.estimated_sources)
            results.append(r)
            total_tokens += r.tokens_used
            all_sources.extend(r.sources_used)
            all_agents.append("researcher")
            display_agent_result(r)

        if "analyst" in plan.agents_needed and results:
            r = self.analyst.analyze(results[-1].result)
            results.append(r)
            total_tokens += r.tokens_used
            all_agents.append("analyst")
            display_agent_result(r)

        if "writer" in plan.agents_needed:
            content = results[-1].result if results else query
            fmt = "REPORT" if plan.complexity == "complex" else "SUMMARY"
            r = self.writer.write(content, fmt)
            results.append(r)
            total_tokens += r.tokens_used
            all_agents.append("writer")
            display_agent_result(r)

        final_result = results[-1].result if results else "No results."

        # Create and save research note
        note = ResearchNote(
            query=query,
            result=final_result,
            sources_used=list(set(all_sources)),
            agents_used=list(set(all_agents)),
            tokens_used=total_tokens
        )
        export_manager.add_note(note)

        display_execution_summary(plan, total_tokens)
        return TaskResult(self.role, True, final_result, total_tokens, list(set(all_sources)), all_agents)


# =============================================================================
# UI HELPERS
# =============================================================================

def display_welcome():
    text = """[bold cyan]RESEARCH ASSISTANT + EXPORT[/bold cyan] [dim]v15.0[/dim]

[yellow]Knowledge Sources:[/yellow]
  [green]ARXIV[/green]     Academic papers          [green]WIKI[/green]      Wikipedia
  [green]GITHUB[/green]    Repositories             [green]HACKER[/green]    HackerNews
  [green]STACK[/green]     Stack Overflow           [magenta]PDF[/magenta]       Local PDFs

[yellow]Export Commands:[/yellow]
  [cyan]export[/cyan]           Export session notes to Markdown
  [cyan]export pdf[/cyan]       Export session notes to PDF
  [cyan]export all[/cyan]       Export all saved notes
  [cyan]notes[/cyan]            Show session notes
  [cyan]notes all[/cyan]        Show all saved notes
  [cyan]exports[/cyan]          List exported files

[yellow]Other Commands:[/yellow]
  [cyan]tokens[/cyan]   Token usage    [cyan]stats[/cyan]    Statistics    [cyan]quit[/cyan]     Exit"""

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
    console.print(f"  [{colors.get(result.agent, 'white')}]{result.agent.value.upper()}[/{colors.get(result.agent, 'white')}] "
                 f"Done ({result.tokens_used:,} tokens)")


def display_execution_summary(plan: ResearchPlan, total_tokens: int):
    table = Table(title="Summary", box=box.ROUNDED, border_style="blue")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Complexity", plan.complexity)
    table.add_row("Tokens", f"{total_tokens:,}")
    table.add_row("Cost", f"${token_tracker.estimate_cost():.4f}")
    table.add_row("Notes Saved", f"{len(export_manager.session_notes)}")
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

    while True:
        if token_tracker.total_tokens > 0:
            token_tracker.display_compact()

        console.print()
        user_input = console.input("[bold green]You:[/bold green] ").strip()

        if not user_input:
            continue

        if user_input.lower() == 'quit':
            if export_manager.session_notes:
                console.print(f"\n[dim]You have {len(export_manager.session_notes)} unsaved notes.[/dim]")
                save = console.input("[dim]Export before quitting? (y/n): [/dim]").strip().lower()
                if save == 'y':
                    path = export_manager.export_to_markdown()
                    console.print(f"[green]Exported to: {path}[/green]")
            console.print("[dim]Goodbye![/dim]")
            break

        # Export commands
        if user_input.lower() == 'export':
            if not export_manager.session_notes:
                console.print("[yellow]No notes to export yet.[/yellow]")
                continue
            with Progress(SpinnerColumn(), TextColumn("[cyan]Exporting...[/cyan]"), console=console, transient=True) as p:
                p.add_task("", total=None)
                path = export_manager.export_to_markdown()
            console.print(f"[green]Exported {len(export_manager.session_notes)} notes to:[/green] {path}")
            continue

        if user_input.lower() == 'export pdf':
            if not export_manager.session_notes:
                console.print("[yellow]No notes to export yet.[/yellow]")
                continue
            with Progress(SpinnerColumn(), TextColumn("[cyan]Generating PDF...[/cyan]"), console=console, transient=True) as p:
                p.add_task("", total=None)
                path = export_manager.export_to_pdf()
            console.print(f"[green]Exported to:[/green] {path}")
            continue

        if user_input.lower() == 'export all':
            notes = export_manager.get_all_notes()
            if not notes:
                console.print("[yellow]No saved notes found.[/yellow]")
                continue
            with Progress(SpinnerColumn(), TextColumn("[cyan]Exporting all notes...[/cyan]"), console=console, transient=True) as p:
                p.add_task("", total=None)
                path = export_manager.export_to_markdown(notes, "all_research_notes.md")
            console.print(f"[green]Exported {len(notes)} notes to:[/green] {path}")
            continue

        if user_input.lower() == 'notes':
            export_manager.display_notes_list(title="Session Notes")
            continue

        if user_input.lower() == 'notes all':
            export_manager.display_notes_list(export_manager.get_all_notes(20), "All Notes (Last 20)")
            continue

        if user_input.lower() == 'exports':
            exports = export_manager.list_exports()
            if not exports:
                console.print("[dim]No exports yet.[/dim]")
                continue
            table = Table(title="Exported Files", box=box.ROUNDED)
            table.add_column("File", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Size", justify="right")
            for e in exports[:10]:
                table.add_row(e["name"], e["type"], f"{e['size_kb']:.1f} KB")
            console.print(table)
            continue

        if user_input.lower() == 'tokens':
            token_tracker.display_stats()
            continue

        if user_input.lower() == 'stats':
            cs = cache.get_stats()
            console.print(f"[cyan]Cache:[/cyan] {cs['entries']} entries, {cs['hit_rate']} hit rate")
            console.print(f"[cyan]Notes:[/cyan] {len(export_manager.session_notes)} session, {len(export_manager.all_notes)} total")
            console.print(f"[cyan]Exports:[/cyan] {len(export_manager.list_exports())} files")
            continue

        if user_input.lower().startswith('flowchart '):
            result = create_flowchart(user_input[10:].strip())
            console.print(Panel(result, title="Flowchart", border_style="yellow"))
            continue

        if user_input.lower().startswith('mindmap '):
            result = create_mindmap(user_input[8:].strip())
            console.print(Panel(result, title="Mindmap", border_style="yellow"))
            continue

        if user_input.lower().startswith('pdf '):
            result = extract_pdf(user_input[4:].strip().strip('"\''))
            console.print(Panel(result[:3000], title="PDF", border_style="magenta"))
            continue

        if user_input.lower().startswith('arxiv '):
            result = analyze_arxiv_paper(user_input[6:].strip())
            console.print(Panel(result[:3000], title="arXiv", border_style="magenta"))
            continue

        # Multi-agent workflow
        console.print()
        result = coordinator.execute(user_input)
        display_response(result.result)


if __name__ == "__main__":
    main()
