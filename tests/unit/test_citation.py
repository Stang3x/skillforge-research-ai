"""Unit tests for citation formatting."""

import pytest
from skillforge.citation import (
    CitationStyle,
    CitationGenerator,
    Source,
    create_source_from_search_result,
)


def test_source_creation():
    """Test creating a Source object."""
    source = Source(
        title="Test Article",
        url="https://example.com",
        authors=["Smith, J.", "Doe, A."],
        publication_date="2024",
        publisher="Test Publisher",
    )

    assert source.title == "Test Article"
    assert source.url == "https://example.com"
    assert len(source.authors) == 2


def test_create_source_from_search_result():
    """Test creating a source from search result data."""
    source = create_source_from_search_result(
        title="Test Article",
        url="https://example.com",
        snippet="Test snippet",
    )

    assert source.title == "Test Article"
    assert source.url == "https://example.com"
    assert source.access_date is not None


def test_citation_generator_apa():
    """Test APA citation generation."""
    generator = CitationGenerator(style=CitationStyle.APA)
    source = Source(
        title="Machine Learning Fundamentals",
        authors=["Smith, J."],
        publication_date="2024",
        journal="AI Journal",
        volume="10",
        issue="2",
        pages="123-145",
    )

    citation = generator.generate(source)

    assert "Smith, J." in citation
    assert "(2024)" in citation
    assert "Machine Learning Fundamentals" in citation


def test_citation_generator_mla():
    """Test MLA citation generation."""
    generator = CitationGenerator(style=CitationStyle.MLA)
    source = Source(
        title="Machine Learning Fundamentals",
        authors=["Smith, J."],
        publication_date="2024",
        journal="AI Journal",
    )

    citation = generator.generate(source)

    assert "Smith, J." in citation
    assert "Machine Learning Fundamentals" in citation


def test_citation_generator_chicago():
    """Test Chicago citation generation."""
    generator = CitationGenerator(style=CitationStyle.CHICAGO)
    source = Source(
        title="Machine Learning Fundamentals",
        authors=["Smith, J."],
        publication_date="2024",
        publisher="Tech Press",
    )

    citation = generator.generate(source)

    assert "Smith, J." in citation
    assert "Machine Learning Fundamentals" in citation


def test_citation_generator_multiple_authors():
    """Test citation with multiple authors."""
    generator = CitationGenerator(style=CitationStyle.APA)
    source = Source(
        title="Test Article",
        authors=["Smith, J.", "Doe, A.", "Brown, B."],
        publication_date="2024",
    )

    citation = generator.generate(source)

    assert "et al." in citation


def test_citation_generator_with_doi():
    """Test citation with DOI."""
    generator = CitationGenerator(style=CitationStyle.APA)
    source = Source(
        title="Test Article",
        authors=["Smith, J."],
        publication_date="2024",
        doi="10.1234/test.2024",
    )

    citation = generator.generate(source)

    assert "10.1234/test.2024" in citation


def test_generate_bibliography():
    """Test generating a complete bibliography."""
    generator = CitationGenerator(style=CitationStyle.APA)
    sources = [
        Source(title="Article 1", authors=["Smith, J."], publication_date="2024"),
        Source(title="Article 2", authors=["Doe, A."], publication_date="2023"),
    ]

    bibliography = generator.generate_bibliography(sources)

    assert "Article 1" in bibliography
    assert "Article 2" in bibliography
    assert "\n\n" in bibliography


def test_citation_no_author():
    """Test citation with no author."""
    generator = CitationGenerator(style=CitationStyle.APA)
    source = Source(
        title="Test Article",
        publication_date="2024",
    )

    citation = generator.generate(source)

    assert "Author Unknown" in citation
