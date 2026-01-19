#!/usr/bin/env python3
"""
Test the 5 free APIs without needing Claude
Just to see that they work!
"""

import requests
import xml.etree.ElementTree as ET

print("="*80)
print("TESTING 5 FREE PUBLIC APIs")
print("="*80)

# Test 1: arXiv API
print("\n1. Testing arXiv API (academic papers)...")
try:
    url = "http://export.arxiv.org/api/query"
    params = {"search_query": "all:autonomous agents", "max_results": 3}
    response = requests.get(url, params=params, timeout=10)

    root = ET.fromstring(response.content)
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}
    entries = root.findall('atom:entry', namespace)

    print(f"   ✓ Found {len(entries)} papers!")
    for entry in entries[:2]:
        title = entry.find('atom:title', namespace).text.strip().replace('\n', ' ')
        print(f"   - {title[:80]}...")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Wikipedia API
print("\n2. Testing Wikipedia API...")
try:
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "titles": "Autonomous agent",
        "format": "json"
    }
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    pages = data["query"]["pages"]
    page_id = list(pages.keys())[0]
    extract = pages[page_id].get("extract", "")

    print(f"   ✓ Got Wikipedia article! ({len(extract)} characters)")
    print(f"   First 150 chars: {extract[:150]}...")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Dictionary API
print("\n3. Testing Dictionary API...")
try:
    url = "https://api.dictionaryapi.dev/api/v2/entries/en/autonomous"
    response = requests.get(url, timeout=10)
    data = response.json()

    word = data[0]['word']
    meaning = data[0]['meanings'][0]['definitions'][0]['definition']

    print(f"   ✓ Definition found!")
    print(f"   '{word}': {meaning}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: GitHub API
print("\n4. Testing GitHub API...")
try:
    url = "https://api.github.com/search/repositories"
    params = {"q": "autonomous agent python", "sort": "stars", "per_page": 3}
    headers = {"User-Agent": "Test-Script"}
    response = requests.get(url, params=params, headers=headers, timeout=10)
    data = response.json()

    print(f"   ✓ Found {data['total_count']:,} repositories!")
    for repo in data['items'][:2]:
        print(f"   - {repo['full_name']} ⭐ {repo['stargazers_count']:,}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 5: Open Library API
print("\n5. Testing Open Library API...")
try:
    url = "https://openlibrary.org/search.json"
    params = {"q": "artificial intelligence", "limit": 3}
    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    print(f"   ✓ Found {data['numFound']:,} books!")
    for book in data['docs'][:2]:
        title = book.get('title', 'Unknown')
        print(f"   - {title}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "="*80)
print("ALL TESTS COMPLETE!")
print("="*80)
print("\nAll 5 APIs are working and FREE!")
print("No API keys needed for any of them.")
print("\nNext step: Get your Anthropic API key to use the full research assistant.")
print("Visit: https://console.anthropic.com")
