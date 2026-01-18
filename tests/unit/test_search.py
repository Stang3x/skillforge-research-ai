"""Unit tests for web search functionality."""

import pytest
from skillforge.search.web import SearchResult, WebSearcher, AcademicSearcher, search_all


@pytest.mark.asyncio
async def test_web_searcher_mock():
    """Test web searcher with mock data."""
    searcher = WebSearcher(use_mock=True)
    results = await searcher.search("machine learning", max_results=5)

    assert len(results) <= 5
    assert all(isinstance(r, SearchResult) for r in results)
    assert all(r.source == "web" for r in results)


@pytest.mark.asyncio
async def test_web_searcher_mock_respects_max_results():
    """Test that web searcher respects max_results parameter."""
    searcher = WebSearcher(use_mock=True)
    results = await searcher.search("test query", max_results=2)

    assert len(results) == 2


@pytest.mark.asyncio
async def test_academic_searcher_arxiv():
    """Test academic searcher for arXiv."""
    searcher = AcademicSearcher(use_mock=True)
    results = await searcher.search_arxiv("deep learning", max_results=3)

    assert len(results) <= 3
    assert all(isinstance(r, SearchResult) for r in results)
    assert all(r.source == "arxiv" for r in results)


@pytest.mark.asyncio
async def test_academic_searcher_pubmed():
    """Test academic searcher for PubMed."""
    searcher = AcademicSearcher(use_mock=True)
    results = await searcher.search_pubmed("cancer treatment", max_results=3)

    assert len(results) <= 3
    assert all(isinstance(r, SearchResult) for r in results)
    assert all(r.source == "pubmed" for r in results)


@pytest.mark.asyncio
async def test_search_all_combined():
    """Test combined search across all sources."""
    results = await search_all("quantum computing", web=True, academic=True, use_mock=True)

    assert len(results) > 0
    assert isinstance(results, list)
    assert all(isinstance(r, SearchResult) for r in results)

    # Should have results from multiple sources
    sources = {r.source for r in results}
    assert len(sources) > 1


@pytest.mark.asyncio
async def test_search_all_web_only():
    """Test search with only web sources."""
    results = await search_all("test query", web=True, academic=False, use_mock=True)

    assert len(results) > 0
    assert all(r.source == "web" for r in results)


@pytest.mark.asyncio
async def test_search_all_academic_only():
    """Test search with only academic sources."""
    results = await search_all("test query", web=False, academic=True, use_mock=True)

    assert len(results) > 0
    # Should only have academic sources
    sources = {r.source for r in results}
    assert "web" not in sources


def test_search_result_model():
    """Test SearchResult model creation."""
    result = SearchResult(
        title="Test Title",
        url="https://example.com",
        snippet="Test snippet",
        source="web",
    )

    assert result.title == "Test Title"
    assert result.url == "https://example.com"
    assert result.snippet == "Test snippet"
    assert result.source == "web"
