"""Web search functionality with privacy-focused implementation."""

from typing import List, Dict, Any, Optional
import aiohttp
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
import asyncio


class SearchResult(BaseModel):
    """A single search result."""

    title: str = Field(..., description="Title of the result")
    url: str = Field(..., description="URL of the result")
    snippet: str = Field(..., description="Brief description/snippet")
    source: str = Field(default="web", description="Source of the result (web, academic, etc.)")


class WebSearcher:
    """Privacy-focused web search using DuckDuckGo HTML."""

    def __init__(self, use_mock: bool = False):
        """
        Initialize the web searcher.

        Args:
            use_mock: If True, use mock data instead of real searches (for testing/offline)
        """
        self.use_mock = use_mock
        self.base_url = "https://html.duckduckgo.com/html/"

    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """
        Perform a web search.

        Args:
            query: The search query
            max_results: Maximum number of results to return

        Returns:
            List of search results
        """
        if self.use_mock:
            return self._mock_search(query, max_results)

        try:
            async with aiohttp.ClientSession() as session:
                data = {"q": query}
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }

                async with session.post(
                    self.base_url, data=data, headers=headers, timeout=10
                ) as response:
                    if response.status != 200:
                        return self._mock_search(query, max_results)

                    html = await response.text()
                    return self._parse_results(html, max_results)
        except Exception:
            # Fall back to mock data on any error
            return self._mock_search(query, max_results)

    def _parse_results(self, html: str, max_results: int) -> List[SearchResult]:
        """Parse search results from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        results = []

        for result_div in soup.find_all("div", class_="result", limit=max_results):
            try:
                title_elem = result_div.find("a", class_="result__a")
                snippet_elem = result_div.find("a", class_="result__snippet")

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get("href", "")
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    results.append(
                        SearchResult(title=title, url=url, snippet=snippet, source="web")
                    )
            except Exception:
                continue

        return results

    def _mock_search(self, query: str, max_results: int) -> List[SearchResult]:
        """Return mock search results for testing/offline use."""
        mock_results = [
            SearchResult(
                title=f"Research on {query} - Academic Paper",
                url=f"https://example.com/research/{query.replace(' ', '-')}",
                snippet=f"A comprehensive study on {query} with detailed analysis and findings.",
                source="web",
            ),
            SearchResult(
                title=f"{query}: A Complete Guide",
                url=f"https://example.com/guide/{query.replace(' ', '-')}",
                snippet=f"Everything you need to know about {query}, including latest developments.",
                source="web",
            ),
            SearchResult(
                title=f"Recent Advances in {query}",
                url=f"https://example.com/advances/{query.replace(' ', '-')}",
                snippet=f"Recent advances and breakthrough discoveries in {query} research.",
                source="web",
            ),
        ]
        return mock_results[:max_results]


class AcademicSearcher:
    """Academic search using arXiv and PubMed (with stubs for offline use)."""

    def __init__(self, use_mock: bool = True):
        """
        Initialize the academic searcher.

        Args:
            use_mock: If True, use mock data (default for privacy/offline)
        """
        self.use_mock = use_mock

    async def search_arxiv(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """
        Search arXiv for academic papers.

        Args:
            query: The search query
            max_results: Maximum number of results to return

        Returns:
            List of search results
        """
        if self.use_mock:
            return self._mock_arxiv_search(query, max_results)

        # Real arXiv API implementation would go here
        # For now, return mock data
        return self._mock_arxiv_search(query, max_results)

    async def search_pubmed(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """
        Search PubMed for medical/biological papers.

        Args:
            query: The search query
            max_results: Maximum number of results to return

        Returns:
            List of search results
        """
        if self.use_mock:
            return self._mock_pubmed_search(query, max_results)

        # Real PubMed API implementation would go here
        # For now, return mock data
        return self._mock_pubmed_search(query, max_results)

    def _mock_arxiv_search(self, query: str, max_results: int) -> List[SearchResult]:
        """Return mock arXiv search results."""
        mock_results = [
            SearchResult(
                title=f"Deep Learning Approaches to {query}",
                url=f"https://arxiv.org/abs/2024.12345",
                snippet=f"We present a novel deep learning framework for {query} with state-of-the-art results.",
                source="arxiv",
            ),
            SearchResult(
                title=f"A Survey on {query}",
                url=f"https://arxiv.org/abs/2024.12346",
                snippet=f"This survey provides a comprehensive overview of research on {query}.",
                source="arxiv",
            ),
        ]
        return mock_results[:max_results]

    def _mock_pubmed_search(self, query: str, max_results: int) -> List[SearchResult]:
        """Return mock PubMed search results."""
        mock_results = [
            SearchResult(
                title=f"Clinical Studies on {query}",
                url=f"https://pubmed.ncbi.nlm.nih.gov/12345678/",
                snippet=f"Clinical trial results demonstrating efficacy of {query} in treatment.",
                source="pubmed",
            ),
            SearchResult(
                title=f"Molecular Mechanisms of {query}",
                url=f"https://pubmed.ncbi.nlm.nih.gov/12345679/",
                snippet=f"Investigation of molecular pathways involved in {query}.",
                source="pubmed",
            ),
        ]
        return mock_results[:max_results]


async def search_all(
    query: str, web: bool = True, academic: bool = True, use_mock: bool = False
) -> List[SearchResult]:
    """
    Search across multiple sources.

    Args:
        query: The search query
        web: Include web search results
        academic: Include academic search results
        use_mock: Use mock data for testing/offline use

    Returns:
        Combined list of search results
    """
    tasks = []
    results = []

    if web:
        web_searcher = WebSearcher(use_mock=use_mock)
        tasks.append(web_searcher.search(query))

    if academic:
        academic_searcher = AcademicSearcher(use_mock=True)
        tasks.append(academic_searcher.search_arxiv(query))
        tasks.append(academic_searcher.search_pubmed(query))

    if tasks:
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in search_results:
            if isinstance(result, list):
                results.extend(result)

    return results
