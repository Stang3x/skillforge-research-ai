#!/usr/bin/env python3
"""
Level 17: Research Assistant with Semantic Scholar API

New capabilities:
- Semantic Scholar API integration (200M+ academic papers)
- Citation data and influence metrics
- Author information and affiliations
- Paper abstracts and publication venues
- Cross-referencing with arXiv papers

Architecture:
┌─────────────────────────────────────────────────────────────┐
│                    SEMANTIC SCHOLAR                          │
│  - Paper search    - Citations    - Authors    - Abstracts  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    OBSIDIAN EXPORTER                         │
│  - Frontmatter    - Wikilinks    - Daily logs    - MOCs     │
└─────────────────────────────────────────────────────────────┘
                              │
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
from typing import Optional, List, Dict, Set
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
OBSIDIAN_DIR = DATA_DIR / "obsidian_vault"
OBSIDIAN_DIR.mkdir(exist_ok=True)
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


# =============================================================================
# OBSIDIAN EXPORTER
# =============================================================================

class ObsidianExporter:
    """
    Export research notes in Obsidian-flavored Markdown format.

    Features:
    - YAML frontmatter with metadata
    - Wikilinks [[concept]] for cross-referencing
    - Callouts for highlights
    - Daily notes integration
    - MOC (Map of Content) generation
    - Automatic concept extraction
    """

    # Common concepts to auto-link
    CONCEPT_PATTERNS = {
        # AI/ML concepts
        r'\b(machine learning|ML)\b': 'Machine Learning',
        r'\b(deep learning|DL)\b': 'Deep Learning',
        r'\b(neural network|NN)s?\b': 'Neural Networks',
        r'\b(natural language processing|NLP)\b': 'Natural Language Processing',
        r'\b(large language model|LLM)s?\b': 'Large Language Models',
        r'\b(artificial intelligence|AI)\b': 'Artificial Intelligence',
        r'\b(transformer)s?\b': 'Transformers',
        r'\b(attention mechanism)s?\b': 'Attention Mechanism',
        r'\b(reinforcement learning|RL)\b': 'Reinforcement Learning',
        r'\b(supervised learning)\b': 'Supervised Learning',
        r'\b(unsupervised learning)\b': 'Unsupervised Learning',
        # Agent concepts
        r'\b(agent)s?\b': 'Agents',
        r'\b(multi-agent|multiagent)\b': 'Multi-Agent Systems',
        r'\b(agentic)\b': 'Agentic Systems',
        r'\b(orchestration)\b': 'Orchestration',
        r'\b(tool use|tool-use)\b': 'Tool Use',
        # Programming concepts
        r'\b(API)s?\b': 'APIs',
        r'\b(Python)\b': 'Python',
        r'\b(JavaScript|JS)\b': 'JavaScript',
        r'\b(TypeScript|TS)\b': 'TypeScript',
        # Frameworks
        r'\b(LangChain)\b': 'LangChain',
        r'\b(LangGraph)\b': 'LangGraph',
        r'\b(AutoGPT)\b': 'AutoGPT',
        r'\b(CrewAI)\b': 'CrewAI',
    }

    def __init__(self, vault_dir: Path = OBSIDIAN_DIR):
        self.vault_dir = vault_dir
        self._setup_vault_structure()
        self.extracted_concepts: Set[str] = set()

    def _setup_vault_structure(self):
        """Create standard Obsidian vault structure"""
        dirs = [
            "Research",
            "Research/Notes",
            "Research/Daily",
            "Research/MOCs",
            "Research/Sources",
            "Research/Concepts",
            "Templates",
        ]
        for d in dirs:
            (self.vault_dir / d).mkdir(parents=True, exist_ok=True)

    def _generate_frontmatter(self, note: ResearchNote, note_type: str = "research") -> str:
        """Generate YAML frontmatter for a note"""
        # Parse timestamp
        try:
            dt = datetime.fromisoformat(note.timestamp)
        except:
            dt = datetime.now()

        # Generate tags from sources and agents
        tags = ["research"]
        tags.extend([f"source/{s}" for s in note.sources_used])
        tags.extend([f"agent/{a}" for a in note.agents_used])
        tags.extend(note.tags)

        frontmatter = f"""---
title: "{note.query[:60]}"
date: {dt.strftime('%Y-%m-%d')}
time: {dt.strftime('%H:%M:%S')}
type: {note_type}
sources:
{self._format_yaml_list(note.sources_used)}
agents:
{self._format_yaml_list(note.agents_used)}
tokens: {note.tokens_used}
tags:
{self._format_yaml_list(tags)}
status: complete
---
"""
        return frontmatter

    def _format_yaml_list(self, items: List[str]) -> str:
        """Format a list for YAML"""
        if not items:
            return "  - none"
        return "\n".join(f"  - {item}" for item in items)

    def _extract_concepts(self, text: str) -> Set[str]:
        """Extract concepts from text for wikilinks"""
        concepts = set()
        for pattern, concept in self.CONCEPT_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                concepts.add(concept)
        return concepts

    def _add_wikilinks(self, text: str, concepts: Set[str] = None) -> str:
        """Add wikilinks to recognized concepts in text"""
        if concepts is None:
            concepts = self._extract_concepts(text)

        result = text
        for pattern, concept in self.CONCEPT_PATTERNS.items():
            # Only link if concept was found
            if concept in concepts:
                # Replace first occurrence with wikilink (avoid over-linking)
                def replace_first(match):
                    return f"[[{concept}|{match.group(0)}]]"
                result = re.sub(pattern, replace_first, result, count=1, flags=re.IGNORECASE)

        return result

    def _format_callout(self, content: str, callout_type: str = "info", title: str = None) -> str:
        """Format content as an Obsidian callout"""
        title_str = f" {title}" if title else ""
        lines = content.split('\n')
        callout_lines = [f"> [!{callout_type}]{title_str}"]
        for line in lines:
            callout_lines.append(f"> {line}")
        return '\n'.join(callout_lines)

    def export_note(self, note: ResearchNote, filename: str = None) -> str:
        """
        Export a single research note to Obsidian format.

        Args:
            note: The research note to export
            filename: Optional filename (auto-generated if None)

        Returns:
            Path to the exported file
        """
        # Generate filename
        if filename is None:
            dt = datetime.fromisoformat(note.timestamp) if note.timestamp else datetime.now()
            query_slug = re.sub(r'[^\w\s-]', '', note.query[:40]).strip().replace(' ', '-').lower()
            filename = f"{dt.strftime('%Y%m%d_%H%M')}_{query_slug}.md"

        filepath = self.vault_dir / "Research" / "Notes" / filename

        # Extract concepts for wikilinks
        all_text = note.query + " " + note.result
        concepts = self._extract_concepts(all_text)
        self.extracted_concepts.update(concepts)

        # Build content
        lines = []

        # Frontmatter
        lines.append(self._generate_frontmatter(note))

        # Title
        lines.append(f"# {note.query}")
        lines.append("")

        # Metadata callout
        metadata = f"""**Query:** {note.query}
**Date:** {note.timestamp[:10]}
**Sources:** {', '.join(note.sources_used) or 'N/A'}
**Agents:** {', '.join(note.agents_used) or 'N/A'}
**Tokens:** {note.tokens_used:,}"""
        lines.append(self._format_callout(metadata, "abstract", "Research Metadata"))
        lines.append("")

        # Main content with wikilinks
        lines.append("## Research Findings")
        lines.append("")
        result_with_links = self._add_wikilinks(note.result, concepts)
        lines.append(result_with_links)
        lines.append("")

        # Diagrams if any
        if note.diagrams:
            lines.append("## Diagrams")
            lines.append("")
            for i, diagram in enumerate(note.diagrams, 1):
                lines.append(f"### Diagram {i}")
                lines.append("")
                lines.append("```mermaid")
                lines.append(diagram)
                lines.append("```")
                lines.append("")

        # Related concepts
        if concepts:
            lines.append("## Related Concepts")
            lines.append("")
            for concept in sorted(concepts):
                lines.append(f"- [[{concept}]]")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append(f"*Generated by Research Assistant v17 on {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

        # Write file
        content = "\n".join(lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(filepath)

    def export_daily_log(self, notes: List[ResearchNote], date: datetime = None) -> str:
        """
        Create a daily research log linking all notes from a date.

        Args:
            notes: Notes to include in the log
            date: Date for the log (default: today)

        Returns:
            Path to the daily log file
        """
        date = date or datetime.now()
        filename = f"{date.strftime('%Y-%m-%d')}.md"
        filepath = self.vault_dir / "Research" / "Daily" / filename

        lines = []

        # Frontmatter
        lines.append(f"""---
title: "Research Log - {date.strftime('%Y-%m-%d')}"
date: {date.strftime('%Y-%m-%d')}
type: daily-log
tags:
  - daily
  - research-log
---
""")

        # Title
        lines.append(f"# Research Log - {date.strftime('%A, %B %d, %Y')}")
        lines.append("")

        # Summary
        total_tokens = sum(n.tokens_used for n in notes)
        all_sources = set()
        all_concepts = set()
        for n in notes:
            all_sources.update(n.sources_used)
            all_concepts.update(self._extract_concepts(n.query + " " + n.result))

        summary = f"""**Queries:** {len(notes)}
**Total Tokens:** {total_tokens:,}
**Sources Used:** {', '.join(sorted(all_sources)) or 'None'}"""
        lines.append(self._format_callout(summary, "summary", "Daily Summary"))
        lines.append("")

        # Research entries
        lines.append("## Research Queries")
        lines.append("")

        for i, note in enumerate(notes, 1):
            dt = datetime.fromisoformat(note.timestamp) if note.timestamp else date
            query_slug = re.sub(r'[^\w\s-]', '', note.query[:40]).strip().replace(' ', '-').lower()
            note_filename = f"{dt.strftime('%Y%m%d_%H%M')}_{query_slug}"

            lines.append(f"### {i}. {note.query[:60]}")
            lines.append("")
            lines.append(f"**Time:** {dt.strftime('%H:%M')}")
            lines.append(f"**Link:** [[{note_filename}]]")
            lines.append("")

            # Brief excerpt
            excerpt = note.result[:200] + "..." if len(note.result) > 200 else note.result
            lines.append(f"> {excerpt}")
            lines.append("")

        # Concepts discovered
        if all_concepts:
            lines.append("## Concepts Explored")
            lines.append("")
            for concept in sorted(all_concepts):
                lines.append(f"- [[{concept}]]")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append(f"<- [[{(date - timedelta(days=1)).strftime('%Y-%m-%d')}|Previous Day]] | [[{(date + timedelta(days=1)).strftime('%Y-%m-%d')}|Next Day]] ->")

        # Write file
        content = "\n".join(lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(filepath)

    def generate_moc(self, notes: List[ResearchNote], title: str = "Research Index") -> str:
        """
        Generate a Map of Content (MOC) for all notes.

        Args:
            notes: All research notes
            title: Title for the MOC

        Returns:
            Path to the MOC file
        """
        filename = f"{title.lower().replace(' ', '-')}.md"
        filepath = self.vault_dir / "Research" / "MOCs" / filename

        lines = []

        # Frontmatter
        lines.append(f"""---
title: "{title}"
date: {datetime.now().strftime('%Y-%m-%d')}
type: moc
tags:
  - moc
  - index
---
""")

        # Title
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        lines.append("")

        # Group notes by source
        by_source: Dict[str, List[ResearchNote]] = {}
        for note in notes:
            for source in note.sources_used or ['general']:
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(note)

        # Statistics
        all_concepts = set()
        for n in notes:
            all_concepts.update(self._extract_concepts(n.query + " " + n.result))

        stats = f"""**Total Notes:** {len(notes)}
**Sources:** {len(by_source)}
**Concepts:** {len(all_concepts)}
**Total Tokens:** {sum(n.tokens_used for n in notes):,}"""
        lines.append(self._format_callout(stats, "info", "Statistics"))
        lines.append("")

        # Notes by source
        lines.append("## By Source")
        lines.append("")

        for source, source_notes in sorted(by_source.items()):
            lines.append(f"### {source.title()}")
            lines.append("")
            for note in source_notes:
                dt = datetime.fromisoformat(note.timestamp) if note.timestamp else datetime.now()
                query_slug = re.sub(r'[^\w\s-]', '', note.query[:40]).strip().replace(' ', '-').lower()
                note_filename = f"{dt.strftime('%Y%m%d_%H%M')}_{query_slug}"
                lines.append(f"- [[{note_filename}|{note.query[:50]}]]")
            lines.append("")

        # All concepts
        lines.append("## Concepts Index")
        lines.append("")
        for concept in sorted(all_concepts):
            lines.append(f"- [[{concept}]]")
        lines.append("")

        # Recent notes
        lines.append("## Recent Research")
        lines.append("")
        recent = sorted(notes, key=lambda n: n.timestamp, reverse=True)[:10]
        for note in recent:
            dt = datetime.fromisoformat(note.timestamp) if note.timestamp else datetime.now()
            query_slug = re.sub(r'[^\w\s-]', '', note.query[:40]).strip().replace(' ', '-').lower()
            note_filename = f"{dt.strftime('%Y%m%d_%H%M')}_{query_slug}"
            lines.append(f"- {dt.strftime('%Y-%m-%d')} - [[{note_filename}|{note.query[:40]}]]")
        lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*This MOC is auto-generated by Research Assistant*")

        # Write file
        content = "\n".join(lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(filepath)

    def create_concept_stub(self, concept: str) -> str:
        """Create a stub note for a concept"""
        filename = f"{concept.lower().replace(' ', '-')}.md"
        filepath = self.vault_dir / "Research" / "Concepts" / filename

        if filepath.exists():
            return str(filepath)

        lines = []
        lines.append(f"""---
title: "{concept}"
date: {datetime.now().strftime('%Y-%m-%d')}
type: concept
tags:
  - concept
  - stub
status: stub
---
""")
        lines.append(f"# {concept}")
        lines.append("")
        lines.append("> [!todo] This is a stub")
        lines.append("> This concept page was auto-generated and needs content.")
        lines.append("")
        lines.append("## Overview")
        lines.append("")
        lines.append("*Add description here*")
        lines.append("")
        lines.append("## Related Notes")
        lines.append("")
        lines.append("*Notes that mention this concept will be linked here*")
        lines.append("")

        content = "\n".join(lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(filepath)

    def export_session(self, notes: List[ResearchNote]) -> Dict[str, str]:
        """
        Export an entire research session.

        Args:
            notes: Session notes to export

        Returns:
            Dict with paths to all created files
        """
        result = {
            "notes": [],
            "daily_log": None,
            "moc": None,
            "concepts": []
        }

        if not notes:
            return result

        # Export each note
        for note in notes:
            path = self.export_note(note)
            result["notes"].append(path)

        # Create daily log
        result["daily_log"] = self.export_daily_log(notes)

        # Update MOC
        result["moc"] = self.generate_moc(notes)

        # Create concept stubs
        for concept in self.extracted_concepts:
            path = self.create_concept_stub(concept)
            result["concepts"].append(path)

        return result

    def list_vault_contents(self) -> Dict[str, List[str]]:
        """List all files in the vault"""
        contents = {}
        for subdir in ["Notes", "Daily", "MOCs", "Concepts"]:
            path = self.vault_dir / "Research" / subdir
            if path.exists():
                contents[subdir] = [f.name for f in path.glob("*.md")]
        return contents


# Initialize Obsidian exporter
obsidian_exporter = ObsidianExporter()


class ExportManager:
    """
    Manages research notes and exports.
    """

    PDF_CSS = """
    body { font-family: 'Segoe UI', sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 40px; }
    h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }
    h2 { color: #34495e; }
    code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
    pre { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; }
    blockquote { border-left: 4px solid #3498db; margin: 20px 0; padding: 10px 20px; background: #f9f9f9; }
    """

    def __init__(self, notes_file: Path = NOTES_FILE, exports_dir: Path = EXPORTS_DIR):
        self.notes_file = notes_file
        self.exports_dir = exports_dir
        self.session_notes: List[ResearchNote] = []
        self.all_notes = self._load_notes()

    def _load_notes(self) -> List[ResearchNote]:
        if self.notes_file.exists():
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [ResearchNote.from_dict(n) for n in data.get("notes", [])]
            except:
                pass
        return []

    def _save_notes(self):
        data = {"notes": [n.to_dict() for n in self.all_notes]}
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_note(self, note: ResearchNote):
        self.session_notes.append(note)
        self.all_notes.append(note)
        self._save_notes()

    def get_session_notes(self) -> List[ResearchNote]:
        return self.session_notes

    def get_all_notes(self, limit: int = None) -> List[ResearchNote]:
        notes = sorted(self.all_notes, key=lambda n: n.timestamp, reverse=True)
        return notes[:limit] if limit else notes

    def search_notes(self, query: str) -> List[ResearchNote]:
        query_lower = query.lower()
        return [n for n in self.all_notes if query_lower in n.query.lower() or query_lower in n.result.lower()]

    def export_to_markdown(self, notes: List[ResearchNote] = None, filename: str = None) -> str:
        notes = notes or self.session_notes
        if not notes:
            return None

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_notes_{timestamp}.md"

        filepath = self.exports_dir / filename
        lines = ["# Research Notes", "", f"*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*", "", "---", ""]

        for i, note in enumerate(notes, 1):
            lines.append(f"## Query {i}: {note.query}")
            lines.append("")
            lines.append(f"> Sources: {', '.join(note.sources_used)}")
            lines.append(f"> Tokens: {note.tokens_used:,}")
            lines.append("")
            lines.append(note.result)
            lines.append("")
            lines.append("---")
            lines.append("")

        content = "\n".join(lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(filepath)

    def export_to_pdf(self, notes: List[ResearchNote] = None, filename: str = None) -> str:
        md_filename = filename.replace('.pdf', '.md') if filename else None
        md_path = self.export_to_markdown(notes, md_filename)
        if not md_path:
            return None

        if filename is None:
            filename = Path(md_path).stem + ".pdf"
        pdf_path = self.exports_dir / filename

        if PDF_WRITE_METHOD == "fpdf":
            return self._export_pdf_fpdf(md_path, str(pdf_path))
        return f"PDF not available. Markdown saved to: {md_path}"

    def _export_pdf_fpdf(self, md_path: str, pdf_path: str) -> str:
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=20)
            pdf.set_margins(20, 20, 20)
            pdf.add_page()
            pdf.set_font('Helvetica', size=10)

            def safe_text(text):
                return ''.join(c if ord(c) < 256 else '?' for c in text.replace('\r', ''))

            for line in md_content.split('\n'):
                line = line.rstrip()
                if not line:
                    pdf.ln(2)
                elif line.startswith('# '):
                    pdf.set_font('Helvetica', 'B', 16)
                    pdf.multi_cell(0, 8, safe_text(line[2:]))
                    pdf.ln(3)
                elif line.startswith('## '):
                    pdf.set_font('Helvetica', 'B', 13)
                    pdf.multi_cell(0, 6, safe_text(line[3:]))
                    pdf.ln(2)
                else:
                    pdf.set_font('Helvetica', '', 10)
                    pdf.multi_cell(0, 5, safe_text(line))

            pdf.output(pdf_path)
            return pdf_path
        except Exception as e:
            return f"Error: {e}. Markdown saved to: {md_path}"

    def export_to_obsidian(self, notes: List[ResearchNote] = None) -> Dict[str, str]:
        """Export notes to Obsidian vault format"""
        notes = notes or self.session_notes
        return obsidian_exporter.export_session(notes)

    def list_exports(self) -> List[dict]:
        exports = []
        for f in self.exports_dir.glob("*"):
            if f.suffix in ['.md', '.pdf']:
                exports.append({
                    "name": f.name, "path": str(f), "type": f.suffix[1:].upper(),
                    "size_kb": f.stat().st_size / 1024,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                })
        return sorted(exports, key=lambda x: x["modified"], reverse=True)

    def display_notes_list(self, notes: List[ResearchNote] = None, title: str = "Research Notes"):
        notes = notes or self.session_notes
        if not notes:
            console.print("[dim]No notes to display.[/dim]")
            return

        table = Table(title=title, box=box.ROUNDED, border_style="cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Query", style="cyan", max_width=40)
        table.add_column("Sources", style="green", max_width=20)
        table.add_column("Tokens", style="yellow", justify="right")

        for i, note in enumerate(notes, 1):
            query_short = note.query[:37] + "..." if len(note.query) > 40 else note.query
            sources = ", ".join(note.sources_used[:2])
            table.add_row(str(i), query_short, sources, f"{note.tokens_used:,}")

        console.print(table)


export_manager = ExportManager()


# =============================================================================
# TOKEN TRACKER
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
    PRICING = {"claude-sonnet-4-5": {"input": 3.00, "output": 15.00}, "default": {"input": 3.00, "output": 15.00}}

    def __init__(self):
        self.session_usage: List[TokenUsage] = []
        self.session_start = datetime.now()

    def track(self, response, agent: str = "unknown") -> TokenUsage:
        usage = response.usage
        token_usage = TokenUsage(input_tokens=usage.input_tokens, output_tokens=usage.output_tokens,
                                 model=response.model, agent=agent)
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
        console.print(f"[dim]Tokens:[/dim] [cyan]{self.total_tokens:,}[/cyan] "
                     f"[dim]({self.total_input:,}in {self.total_output:,}out)[/dim] "
                     f"[dim]Cost:[/dim] [{color}]${cost:.4f}[/{color}]")

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
        response = self.client.messages.create(model="claude-sonnet-4-5", max_tokens=max_tokens,
                                               system=system, messages=[{"role": "user", "content": prompt}])
        token_tracker.track(response, agent="diagrammer")
        return "".join(b.text for b in response.content if hasattr(b, "text"))

    def generate_flowchart(self, description: str) -> Diagram:
        system = "Generate ONLY valid Mermaid flowchart code. Output ONLY the mermaid code."
        code = self._call_llm(system, f"Create flowchart:\n{description}")
        code = re.sub(r'^```mermaid\s*', '', code, flags=re.MULTILINE)
        code = re.sub(r'^```\s*$', '', code, flags=re.MULTILINE).strip()
        diagram = Diagram(DiagramType.FLOWCHART, f"Flowchart: {description[:50]}", code, description)
        self.generated_diagrams.append(diagram)
        return diagram

    def generate_mindmap(self, topic: str) -> Diagram:
        system = "Generate ONLY valid Mermaid mindmap code. Output ONLY the mermaid code."
        code = self._call_llm(system, f"Create mindmap for: {topic}")
        code = re.sub(r'^```mermaid\s*', '', code, flags=re.MULTILINE)
        code = re.sub(r'^```\s*$', '', code, flags=re.MULTILINE).strip()
        diagram = Diagram(DiagramType.MINDMAP, f"Mindmap: {topic}", code, topic)
        self.generated_diagrams.append(diagram)
        return diagram

    def save_diagram(self, diagram: Diagram) -> str:
        filename = f"{diagram.diagram_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.diagrams_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {diagram.title}\n\n```mermaid\n{diagram.mermaid_code}\n```\n")
        return str(filepath)


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


pdf_manager = PDFManager()


class ResponseCache:
    DEFAULT_TTL = {
        "arxiv": 3600,
        "wikipedia": 3600,
        "github": 300,
        "hackernews": 300,
        "stackoverflow": 1800,
        "semantic_scholar": 3600,  # 1 hour cache for Semantic Scholar
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
        articles = resp.json().get('query', {}).get('search', [])
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
# SEMANTIC SCHOLAR API - NEW!
# =============================================================================

# Semantic Scholar API key (optional but recommended for higher rate limits)
# Get your free API key at: https://www.semanticscholar.org/product/api#api-key-form
SEMANTIC_SCHOLAR_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")

# Rate limiting: track last request time to avoid 429 errors
_last_semantic_scholar_request = 0
_SEMANTIC_SCHOLAR_MIN_INTERVAL = 1.0  # Minimum seconds between requests (without API key)


def _get_semantic_scholar_headers() -> dict:
    """Get headers for Semantic Scholar API requests"""
    headers = {"User-Agent": "Research-Assistant/1.0"}
    if SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY
    return headers


def _rate_limit_semantic_scholar():
    """Apply rate limiting for Semantic Scholar API"""
    global _last_semantic_scholar_request
    if not SEMANTIC_SCHOLAR_API_KEY:
        # Without API key, wait between requests
        elapsed = time.time() - _last_semantic_scholar_request
        if elapsed < _SEMANTIC_SCHOLAR_MIN_INTERVAL:
            time.sleep(_SEMANTIC_SCHOLAR_MIN_INTERVAL - elapsed)
    _last_semantic_scholar_request = time.time()


def search_semantic_scholar(query: str, max_results: int = 5, fields: str = None) -> tuple[str, bool]:
    """
    Search Semantic Scholar for academic papers.

    API Documentation: https://api.semanticscholar.org/api-docs/

    Features:
    - Access to 200M+ academic papers
    - Citation counts and influence metrics
    - Author information
    - Publication venue data
    - Open access PDF links when available

    Args:
        query: Search query string
        max_results: Maximum number of papers to return (1-100)
        fields: Comma-separated list of fields to return

    Returns:
        Tuple of (result_string, is_cached)
    """
    cached = cache.get("semantic_scholar", query)
    if cached:
        return cached, True

    try:
        # Default fields to return (comprehensive but not all)
        if fields is None:
            fields = "paperId,title,abstract,year,citationCount,influentialCitationCount,authors,venue,openAccessPdf,externalIds"

        # Semantic Scholar API endpoint for paper search
        url = "https://api.semanticscholar.org/graph/v1/paper/search"

        params = {
            "query": query,
            "limit": min(max_results, 100),  # API max is 100
            "fields": fields
        }

        headers = _get_semantic_scholar_headers()
        _rate_limit_semantic_scholar()

        resp = requests.get(url, params=params, headers=headers, timeout=15)

        # Handle rate limiting
        if resp.status_code == 429:
            return "Semantic Scholar API rate limit reached. Please try again later.", False

        resp.raise_for_status()
        data = resp.json()

        papers = data.get('data', [])
        total = data.get('total', 0)

        if not papers:
            return "No papers found on Semantic Scholar.", False

        # Format results
        lines = [f"Semantic Scholar: Found {total:,} papers (showing {len(papers)})\n"]

        for i, paper in enumerate(papers, 1):
            # Basic info
            title = paper.get('title', 'Untitled')
            year = paper.get('year', 'N/A')
            citations = paper.get('citationCount', 0)
            influential = paper.get('influentialCitationCount', 0)
            venue = paper.get('venue', '')

            # Authors (limit to first 3)
            authors = paper.get('authors', [])
            author_names = [a.get('name', '') for a in authors[:3]]
            author_str = ', '.join(author_names)
            if len(authors) > 3:
                author_str += f" et al. ({len(authors)} authors)"

            # Paper ID for linking
            paper_id = paper.get('paperId', '')

            # External IDs (arXiv, DOI, etc.)
            ext_ids = paper.get('externalIds', {})
            arxiv_id = ext_ids.get('ArXiv', '')
            doi = ext_ids.get('DOI', '')

            # Open access PDF
            open_access = paper.get('openAccessPdf', {})
            pdf_url = open_access.get('url', '') if open_access else ''

            # Abstract (truncated)
            abstract = paper.get('abstract', '')
            if abstract:
                abstract = abstract[:200] + '...' if len(abstract) > 200 else abstract

            # Build paper entry
            lines.append(f"{i}. {title}")
            lines.append(f"   Year: {year} | Citations: {citations:,} ({influential} influential)")
            if author_str:
                lines.append(f"   Authors: {author_str}")
            if venue:
                lines.append(f"   Venue: {venue}")
            if arxiv_id:
                lines.append(f"   arXiv: {arxiv_id}")
            if doi:
                lines.append(f"   DOI: {doi}")
            if pdf_url:
                lines.append(f"   PDF: {pdf_url}")
            if abstract:
                lines.append(f"   Abstract: {abstract}")
            lines.append("")  # Blank line between papers

        result = "\n".join(lines)
        cache.set("semantic_scholar", query, result)
        return result, False

    except requests.exceptions.Timeout:
        return "Semantic Scholar API request timed out. Please try again.", False
    except requests.exceptions.RequestException as e:
        return f"Semantic Scholar API error: {e}", False
    except Exception as e:
        return f"Error searching Semantic Scholar: {e}", False


def get_semantic_scholar_paper(paper_id: str) -> tuple[str, bool]:
    """
    Get detailed information about a specific paper by its Semantic Scholar ID.

    Args:
        paper_id: Semantic Scholar paper ID (e.g., "649def34f8be52c8b66281af98ae884c09aef38b")
                  Can also be arXiv ID with prefix (e.g., "arXiv:2106.09685")
                  or DOI with prefix (e.g., "DOI:10.1234/example")

    Returns:
        Tuple of (result_string, is_cached)
    """
    cache_key = f"paper:{paper_id}"
    cached = cache.get("semantic_scholar", cache_key)
    if cached:
        return cached, True

    try:
        fields = "paperId,title,abstract,year,citationCount,influentialCitationCount,authors,venue,openAccessPdf,externalIds,references,citations,fieldsOfStudy,publicationTypes"

        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"

        params = {"fields": fields}
        headers = _get_semantic_scholar_headers()
        _rate_limit_semantic_scholar()

        resp = requests.get(url, params=params, headers=headers, timeout=15)

        if resp.status_code == 404:
            return f"Paper not found: {paper_id}", False
        if resp.status_code == 429:
            return "Semantic Scholar API rate limit reached.", False

        resp.raise_for_status()
        paper = resp.json()

        # Format detailed paper info
        lines = ["=" * 60]
        lines.append(f"PAPER: {paper.get('title', 'Untitled')}")
        lines.append("=" * 60)

        # Basic metadata
        lines.append(f"\nYear: {paper.get('year', 'N/A')}")
        lines.append(f"Venue: {paper.get('venue', 'N/A')}")

        # Citation metrics
        citations = paper.get('citationCount', 0)
        influential = paper.get('influentialCitationCount', 0)
        lines.append(f"\nCitations: {citations:,} total, {influential} influential")

        # Authors
        authors = paper.get('authors', [])
        if authors:
            lines.append(f"\nAuthors ({len(authors)}):")
            for a in authors[:10]:
                lines.append(f"  - {a.get('name', 'Unknown')}")
            if len(authors) > 10:
                lines.append(f"  ... and {len(authors) - 10} more")

        # Fields of study
        fields = paper.get('fieldsOfStudy', [])
        if fields:
            lines.append(f"\nFields: {', '.join(fields)}")

        # Publication types
        pub_types = paper.get('publicationTypes', [])
        if pub_types:
            lines.append(f"Type: {', '.join(pub_types)}")

        # External IDs
        ext_ids = paper.get('externalIds', {})
        if ext_ids:
            lines.append("\nExternal IDs:")
            for id_type, id_val in ext_ids.items():
                if id_val:
                    lines.append(f"  {id_type}: {id_val}")

        # Open Access PDF
        open_access = paper.get('openAccessPdf', {})
        if open_access and open_access.get('url'):
            lines.append(f"\nOpen Access PDF: {open_access['url']}")

        # Abstract
        abstract = paper.get('abstract', '')
        if abstract:
            lines.append(f"\nAbstract:\n{abstract}")

        # References and citations counts
        refs = paper.get('references', [])
        cites = paper.get('citations', [])
        if refs or cites:
            lines.append(f"\nReferences: {len(refs)} papers")
            lines.append(f"Cited by: {len(cites)} papers in database")

        result = "\n".join(lines)
        cache.set("semantic_scholar", cache_key, result)
        return result, False

    except Exception as e:
        return f"Error getting paper details: {e}", False


def search_semantic_scholar_author(author_name: str, max_results: int = 5) -> tuple[str, bool]:
    """
    Search for authors on Semantic Scholar.

    Args:
        author_name: Author name to search for
        max_results: Maximum number of authors to return

    Returns:
        Tuple of (result_string, is_cached)
    """
    cache_key = f"author:{author_name}"
    cached = cache.get("semantic_scholar", cache_key)
    if cached:
        return cached, True

    try:
        url = "https://api.semanticscholar.org/graph/v1/author/search"

        params = {
            "query": author_name,
            "limit": max_results,
            "fields": "authorId,name,affiliations,paperCount,citationCount,hIndex"
        }

        headers = _get_semantic_scholar_headers()
        _rate_limit_semantic_scholar()

        resp = requests.get(url, params=params, headers=headers, timeout=15)

        if resp.status_code == 429:
            return "Semantic Scholar API rate limit reached.", False

        resp.raise_for_status()
        data = resp.json()

        authors = data.get('data', [])
        total = data.get('total', 0)

        if not authors:
            return f"No authors found matching '{author_name}'.", False

        lines = [f"Semantic Scholar Authors: Found {total:,} (showing {len(authors)})\n"]

        for i, author in enumerate(authors, 1):
            name = author.get('name', 'Unknown')
            author_id = author.get('authorId', '')
            papers = author.get('paperCount', 0)
            citations = author.get('citationCount', 0)
            h_index = author.get('hIndex', 'N/A')
            affiliations = author.get('affiliations', [])

            lines.append(f"{i}. {name}")
            lines.append(f"   ID: {author_id}")
            lines.append(f"   Papers: {papers:,} | Citations: {citations:,} | h-index: {h_index}")
            if affiliations:
                lines.append(f"   Affiliations: {', '.join(affiliations[:2])}")
            lines.append("")

        result = "\n".join(lines)
        cache.set("semantic_scholar", cache_key, result)
        return result, False

    except Exception as e:
        return f"Error searching authors: {e}", False


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

    def _call_llm(self, system: str, messages: list, tools: list = None, max_tokens: int = 2048):
        kwargs = {"model": "claude-sonnet-4-5", "max_tokens": max_tokens, "system": system, "messages": messages}
        if tools:
            kwargs["tools"] = tools
        response = self.client.messages.create(**kwargs)
        token_tracker.track(response, agent=self.role.value)
        return response


class ResearcherAgent(BaseAgent):
    SYSTEM_PROMPT = "You are a RESEARCHER. Use tools to gather information from multiple sources. Semantic Scholar is excellent for academic papers with citation data."
    TOOLS = [
        {"name": "search_arxiv", "description": "Search arXiv for preprints",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "search_wikipedia", "description": "Search Wikipedia",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "search_github_repos", "description": "Search GitHub repositories",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "search_hackernews", "description": "Search HackerNews stories",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "search_stackoverflow", "description": "Search Stack Overflow Q&A",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        # NEW: Semantic Scholar tools
        {"name": "search_semantic_scholar", "description": "Search Semantic Scholar for academic papers with citation data, abstracts, and author info. Best for finding influential papers.",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string", "description": "Search query"}, "max_results": {"type": "integer", "description": "Max papers to return (1-100)", "default": 5}}, "required": ["query"]}},
        {"name": "get_semantic_scholar_paper", "description": "Get detailed info about a specific paper by ID (Semantic Scholar ID, arXiv:ID, or DOI:ID)",
         "input_schema": {"type": "object", "properties": {"paper_id": {"type": "string", "description": "Paper ID (e.g., 'arXiv:2106.09685' or DOI)"}}, "required": ["paper_id"]}},
        {"name": "search_semantic_scholar_author", "description": "Search for academic authors and their publication metrics",
         "input_schema": {"type": "object", "properties": {"author_name": {"type": "string", "description": "Author name to search"}}, "required": ["author_name"]}},
    ]

    def __init__(self, client: Anthropic):
        super().__init__(AgentRole.RESEARCHER, client)

    def research(self, query: str, sources: list = None) -> TaskResult:
        sources = sources or ["arxiv", "wikipedia"]
        display_agent_activity(self.role, f"Researching: {query}")

        messages = [{"role": "user", "content": f"Research: {query}\nSources to use: {', '.join(sources)}\n\nUse the available tools to gather comprehensive information."}]
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
                        # NEW: Semantic Scholar tools
                        elif name == "search_semantic_scholar":
                            max_results = inp.get("max_results", 5)
                            result, _ = search_semantic_scholar(inp["query"], max_results)
                            sources_used.append("semantic_scholar")
                        elif name == "get_semantic_scholar_paper":
                            result, _ = get_semantic_scholar_paper(inp["paper_id"])
                            sources_used.append("semantic_scholar")
                        elif name == "search_semantic_scholar_author":
                            result, _ = search_semantic_scholar_author(inp["author_name"])
                            sources_used.append("semantic_scholar")
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
    SYSTEM_PROMPT = """You are the COORDINATOR. Create JSON execution plans.
Available sources: arxiv, wikipedia, github, hackernews, stackoverflow, semantic_scholar
semantic_scholar is best for academic papers with citation metrics and author info.
{"complexity": "simple|moderate|complex", "agents": ["researcher", "analyst", "writer"], "sources": ["arxiv", "semantic_scholar"]}"""

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
            data = {"complexity": "moderate", "agents": ["researcher", "writer"], "sources": ["wikipedia", "semantic_scholar"]}

        return ResearchPlan(query, data.get("complexity", "moderate"),
                           data.get("agents", ["researcher", "writer"]),
                           data.get("sources", ["wikipedia", "semantic_scholar"]))

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

        note = ResearchNote(query=query, result=final_result, sources_used=list(set(all_sources)),
                           agents_used=list(set(all_agents)), tokens_used=total_tokens)
        export_manager.add_note(note)

        display_execution_summary(plan, total_tokens)
        return TaskResult(self.role, True, final_result, total_tokens, list(set(all_sources)), all_agents)


# =============================================================================
# UI HELPERS
# =============================================================================

def display_welcome():
    text = """[bold cyan]RESEARCH ASSISTANT + SEMANTIC SCHOLAR[/bold cyan] [dim]v17.0[/dim]

[yellow]Knowledge Sources:[/yellow]
  [green]ARXIV[/green]     Academic papers          [green]WIKI[/green]      Wikipedia
  [green]GITHUB[/green]    Repositories             [green]HACKER[/green]    HackerNews
  [green]STACK[/green]     Stack Overflow           [magenta]PDF[/magenta]       Local PDFs
  [blue]SCHOLAR[/blue]   Semantic Scholar (200M+ papers with citations!)

[yellow]Direct Commands:[/yellow]
  [cyan]scholar <query>[/cyan]     Search Semantic Scholar directly
  [cyan]paper <id>[/cyan]          Get paper details (ID, arXiv:ID, or DOI:ID)
  [cyan]author <name>[/cyan]       Search for academic authors

[yellow]Export Commands:[/yellow]
  [cyan]export[/cyan]           Export to Markdown
  [cyan]export pdf[/cyan]       Export to PDF
  [cyan]obsidian[/cyan]         Export to Obsidian vault
  [cyan]vault[/cyan]            Show Obsidian vault contents

[yellow]Other Commands:[/yellow]
  [cyan]notes[/cyan]   Session notes    [cyan]tokens[/cyan]   Token usage    [cyan]quit[/cyan]     Exit"""

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


def display_obsidian_export(result: Dict[str, any]):
    """Display Obsidian export results"""
    console.print()
    table = Table(title="[magenta]Obsidian Export[/magenta]", box=box.ROUNDED, border_style="magenta")
    table.add_column("Type", style="cyan")
    table.add_column("Count/Path", style="green")

    table.add_row("Notes", f"{len(result.get('notes', []))} files")
    table.add_row("Daily Log", result.get('daily_log', 'N/A'))
    table.add_row("MOC", result.get('moc', 'N/A'))
    table.add_row("Concepts", f"{len(result.get('concepts', []))} stubs created")

    console.print(table)
    console.print(f"\n[dim]Vault location:[/dim] {OBSIDIAN_DIR}")


def display_scholar_results(results: str):
    """Display Semantic Scholar results in a nice format"""
    console.print()
    console.print(Panel(results, title="[blue]Semantic Scholar[/blue]", border_style="blue", box=box.ROUNDED))


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
                console.print(f"\n[dim]You have {len(export_manager.session_notes)} notes.[/dim]")
                save = console.input("[dim]Export to Obsidian before quitting? (y/n): [/dim]").strip().lower()
                if save == 'y':
                    result = export_manager.export_to_obsidian()
                    display_obsidian_export(result)
            console.print("[dim]Goodbye![/dim]")
            break

        # Direct Semantic Scholar commands
        if user_input.lower().startswith('scholar '):
            query = user_input[8:].strip()
            with Progress(SpinnerColumn(), TextColumn("[blue]Searching Semantic Scholar...[/blue]"),
                         console=console, transient=True) as p:
                p.add_task("", total=None)
                result, cached = search_semantic_scholar(query)
            if cached:
                console.print("[dim](cached)[/dim]")
            display_scholar_results(result)
            continue

        if user_input.lower().startswith('paper '):
            paper_id = user_input[6:].strip()
            with Progress(SpinnerColumn(), TextColumn("[blue]Fetching paper details...[/blue]"),
                         console=console, transient=True) as p:
                p.add_task("", total=None)
                result, cached = get_semantic_scholar_paper(paper_id)
            if cached:
                console.print("[dim](cached)[/dim]")
            display_scholar_results(result)
            continue

        if user_input.lower().startswith('author '):
            author_name = user_input[7:].strip()
            with Progress(SpinnerColumn(), TextColumn("[blue]Searching authors...[/blue]"),
                         console=console, transient=True) as p:
                p.add_task("", total=None)
                result, cached = search_semantic_scholar_author(author_name)
            if cached:
                console.print("[dim](cached)[/dim]")
            display_scholar_results(result)
            continue

        # Export commands
        if user_input.lower() == 'export':
            if not export_manager.session_notes:
                console.print("[yellow]No notes to export yet.[/yellow]")
                continue
            path = export_manager.export_to_markdown()
            console.print(f"[green]Exported {len(export_manager.session_notes)} notes to:[/green] {path}")
            continue

        if user_input.lower() == 'export pdf':
            if not export_manager.session_notes:
                console.print("[yellow]No notes to export yet.[/yellow]")
                continue
            path = export_manager.export_to_pdf()
            console.print(f"[green]Exported to:[/green] {path}")
            continue

        if user_input.lower() == 'obsidian':
            if not export_manager.session_notes:
                console.print("[yellow]No notes to export yet.[/yellow]")
                continue
            with Progress(SpinnerColumn(), TextColumn("[magenta]Exporting to Obsidian...[/magenta]"),
                         console=console, transient=True) as p:
                p.add_task("", total=None)
                result = export_manager.export_to_obsidian()
            display_obsidian_export(result)
            continue

        if user_input.lower() == 'obsidian all':
            notes = export_manager.get_all_notes()
            if not notes:
                console.print("[yellow]No saved notes found.[/yellow]")
                continue
            with Progress(SpinnerColumn(), TextColumn("[magenta]Exporting all to Obsidian...[/magenta]"),
                         console=console, transient=True) as p:
                p.add_task("", total=None)
                result = obsidian_exporter.export_session(notes)
            display_obsidian_export(result)
            continue

        if user_input.lower() == 'vault':
            contents = obsidian_exporter.list_vault_contents()
            console.print()
            tree = Tree(f"[magenta]Obsidian Vault[/magenta] ({OBSIDIAN_DIR})")
            for subdir, files in contents.items():
                branch = tree.add(f"[cyan]{subdir}[/cyan] ({len(files)} files)")
                for f in files[:5]:
                    branch.add(f"[dim]{f}[/dim]")
                if len(files) > 5:
                    branch.add(f"[dim]... and {len(files) - 5} more[/dim]")
            console.print(tree)
            continue

        if user_input.lower() == 'notes':
            export_manager.display_notes_list(title="Session Notes")
            continue

        if user_input.lower() == 'notes all':
            export_manager.display_notes_list(export_manager.get_all_notes(20), "All Notes (Last 20)")
            continue

        if user_input.lower() == 'tokens':
            token_tracker.display_stats()
            continue

        if user_input.lower() == 'stats':
            cs = cache.get_stats()
            console.print(f"[cyan]Cache:[/cyan] {cs['entries']} entries, {cs['hit_rate']} hit rate")
            console.print(f"[cyan]Notes:[/cyan] {len(export_manager.session_notes)} session, {len(export_manager.all_notes)} total")
            continue

        if user_input.lower().startswith('flowchart '):
            diagram = diagram_generator.generate_flowchart(user_input[10:].strip())
            diagram_generator.save_diagram(diagram)
            console.print(Panel(f"```mermaid\n{diagram.mermaid_code}\n```", title="Flowchart", border_style="yellow"))
            continue

        if user_input.lower().startswith('mindmap '):
            diagram = diagram_generator.generate_mindmap(user_input[8:].strip())
            diagram_generator.save_diagram(diagram)
            console.print(Panel(f"```mermaid\n{diagram.mermaid_code}\n```", title="Mindmap", border_style="yellow"))
            continue

        if user_input.lower().startswith('pdf '):
            result = pdf_manager.extract_text(user_input[4:].strip().strip('"\''))
            if result["success"]:
                console.print(Panel(result["text"][:3000], title="PDF", border_style="magenta"))
            else:
                console.print(f"[red]Error: {result['error']}[/red]")
            continue

        # Multi-agent workflow
        console.print()
        result = coordinator.execute(user_input)
        display_response(result.result)


if __name__ == "__main__":
    main()
