"""Citation formatting for different academic styles."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class CitationStyle(str, Enum):
    """Supported citation styles."""

    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"


class Source(BaseModel):
    """Information about a source to be cited."""

    title: str = Field(..., description="Title of the source")
    url: Optional[str] = Field(None, description="URL of the source")
    authors: list[str] = Field(default_factory=list, description="List of authors")
    publication_date: Optional[str] = Field(None, description="Publication date")
    publisher: Optional[str] = Field(None, description="Publisher name")
    journal: Optional[str] = Field(None, description="Journal name")
    volume: Optional[str] = Field(None, description="Volume number")
    issue: Optional[str] = Field(None, description="Issue number")
    pages: Optional[str] = Field(None, description="Page numbers")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    access_date: Optional[str] = Field(None, description="Date accessed (for online sources)")


class CitationGenerator:
    """Generate citations in various academic formats."""

    def __init__(self, style: CitationStyle = CitationStyle.APA):
        """
        Initialize the citation generator.

        Args:
            style: The citation style to use (default: APA)
        """
        self.style = style

    def generate(self, source: Source) -> str:
        """
        Generate a citation for the given source.

        Args:
            source: The source to cite

        Returns:
            Formatted citation string
        """
        if self.style == CitationStyle.APA:
            return self._format_apa(source)
        elif self.style == CitationStyle.MLA:
            return self._format_mla(source)
        elif self.style == CitationStyle.CHICAGO:
            return self._format_chicago(source)
        else:
            return self._format_apa(source)

    def _format_apa(self, source: Source) -> str:
        """Format citation in APA style."""
        parts = []

        # Authors
        if source.authors:
            if len(source.authors) == 1:
                parts.append(f"{source.authors[0]}.")
            elif len(source.authors) == 2:
                parts.append(f"{source.authors[0]}, & {source.authors[1]}.")
            else:
                parts.append(f"{source.authors[0]}, et al.")
        else:
            parts.append("Author Unknown.")

        # Year
        if source.publication_date:
            try:
                year = source.publication_date.split("-")[0]
                parts.append(f"({year}).")
            except Exception:
                parts.append(f"({source.publication_date}).")
        else:
            parts.append("(n.d.).")

        # Title
        parts.append(f"{source.title}.")

        # Journal/Publisher
        if source.journal:
            journal_part = f"<em>{source.journal}</em>"
            if source.volume:
                journal_part += f", <em>{source.volume}</em>"
            if source.issue:
                journal_part += f"({source.issue})"
            if source.pages:
                journal_part += f", {source.pages}"
            parts.append(journal_part + ".")
        elif source.publisher:
            parts.append(f"{source.publisher}.")

        # DOI or URL
        if source.doi:
            parts.append(f"https://doi.org/{source.doi}")
        elif source.url:
            parts.append(f"Retrieved from {source.url}")

        return " ".join(parts)

    def _format_mla(self, source: Source) -> str:
        """Format citation in MLA style."""
        parts = []

        # Authors
        if source.authors:
            if len(source.authors) == 1:
                # Last, First format
                author_name = source.authors[0]
                if "," in author_name:
                    parts.append(f"{author_name}.")
                else:
                    # Simple format if not already formatted
                    parts.append(f"{author_name}.")
            else:
                parts.append(f"{source.authors[0]}, et al.")
        else:
            parts.append("Author Unknown.")

        # Title in quotes
        parts.append(f'"{source.title}."')

        # Journal/Publisher
        if source.journal:
            journal_part = f"<em>{source.journal}</em>"
            if source.volume:
                journal_part += f", vol. {source.volume}"
            if source.issue:
                journal_part += f", no. {source.issue}"
            if source.publication_date:
                journal_part += f", {source.publication_date}"
            if source.pages:
                journal_part += f", pp. {source.pages}"
            parts.append(journal_part + ".")
        elif source.publisher:
            parts.append(f"{source.publisher},")
            if source.publication_date:
                parts.append(f"{source.publication_date}.")

        # URL
        if source.url:
            parts.append(f"{source.url}.")

        return " ".join(parts)

    def _format_chicago(self, source: Source) -> str:
        """Format citation in Chicago style."""
        parts = []

        # Authors
        if source.authors:
            if len(source.authors) == 1:
                parts.append(f"{source.authors[0]}.")
            elif len(source.authors) == 2:
                parts.append(f"{source.authors[0]} and {source.authors[1]}.")
            else:
                parts.append(f"{source.authors[0]} et al.")
        else:
            parts.append("Author Unknown.")

        # Title in quotes
        parts.append(f'"{source.title}."')

        # Journal/Publisher
        if source.journal:
            journal_part = f"<em>{source.journal}</em>"
            if source.volume:
                journal_part += f" {source.volume}"
            if source.issue:
                journal_part += f", no. {source.issue}"
            if source.publication_date:
                journal_part += f" ({source.publication_date})"
            if source.pages:
                journal_part += f": {source.pages}"
            parts.append(journal_part + ".")
        elif source.publisher:
            if source.publication_date:
                parts.append(f"{source.publisher}, {source.publication_date}.")
            else:
                parts.append(f"{source.publisher}.")

        # DOI or URL
        if source.doi:
            parts.append(f"https://doi.org/{source.doi}.")
        elif source.url:
            parts.append(f"{source.url}.")

        return " ".join(parts)

    def generate_bibliography(self, sources: list[Source]) -> str:
        """
        Generate a complete bibliography from multiple sources.

        Args:
            sources: List of sources to cite

        Returns:
            Formatted bibliography string
        """
        citations = [self.generate(source) for source in sources]
        return "\n\n".join(citations)


def create_source_from_search_result(
    title: str, url: str, snippet: str, access_date: Optional[str] = None
) -> Source:
    """
    Create a Source object from search result data.

    Args:
        title: Title of the source
        url: URL of the source
        snippet: Brief description
        access_date: Date the source was accessed

    Returns:
        Source object
    """
    if access_date is None:
        access_date = datetime.now().strftime("%Y-%m-%d")

    return Source(
        title=title,
        url=url,
        access_date=access_date,
        publication_date=datetime.now().strftime("%Y"),
    )
