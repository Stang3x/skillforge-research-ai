#!/usr/bin/env python3
"""
Quick query to find Python libraries for building AI agents
"""

import sys
import io
import requests

# Force UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def search_github_repos(query, language=None, max_results=10):
    """Search GitHub repositories"""
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

        headers = {"User-Agent": "Research-Assistant"}

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 403:
            return "GitHub API rate limit reached. Try again in a few minutes."

        if response.status_code != 200:
            return f"Error: GitHub API returned status {response.status_code}"

        data = response.json()

        if data['total_count'] == 0:
            return f"No repositories found for: {query}"

        print(f"\n{'='*80}")
        print(f"PYTHON LIBRARIES FOR BUILDING AI AGENTS")
        print(f"{'='*80}")
        print(f"Found {data['total_count']:,} repositories (showing top {max_results}):\n")

        for i, repo in enumerate(data['items'], 1):
            print(f"{i}. {repo['full_name']}")
            print(f"   Stars: {repo['stargazers_count']:,}")
            print(f"   Description: {repo['description'] or 'No description'}")
            print(f"   Language: {repo['language'] or 'N/A'}")
            print(f"   Link: {repo['html_url']}")
            print()

        return f"Successfully found {len(data['items'])} repositories"

    except Exception as e:
        return f"Error searching GitHub: {str(e)}"


if __name__ == "__main__":
    result = search_github_repos("AI agent python", language="python", max_results=10)
    print(f"\n[STATUS] {result}")
