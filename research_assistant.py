"""
Research Assistant — simplified, secure, and cache-enabled.

Features:
- Prefer GITHUB_PAT (or fallback to GITHUB_TOKEN) environment variable
- Persistent query caching with TTL via SearchResultCache
- Token usage tracking (optional)
- Local demo mode (--local-test) with mock search
- Interactive CLI for search and synthesis
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# ── Project root & sys.path setup ────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "context-optimization"))  # Handles hyphen in folder name

# ── Environment & Configuration ──────────────────────────────────────────────
GITHUB_TOKEN = os.getenv("GITHUB_PAT") or os.getenv("GITHUB_TOKEN")
MODEL_ID = os.getenv("MODEL_ID", "openai/gpt-4o-mini")
LOCAL_TEST = (
    os.getenv("LOCAL_TEST", "0") == "1"
    or "--local-test" in sys.argv
)

if not GITHUB_TOKEN and not LOCAL_TEST:
    raise ValueError(
        "GITHUB_PAT (preferred) or GITHUB_TOKEN must be set, "
        "or run with --local-test / LOCAL_TEST=1"
    )

# ── Optional dependencies with graceful fallback ─────────────────────────────
cache = None
try:
    from caching import SearchResultCache
    cache_dir = str(PROJECT_ROOT / "cache" / "search_results")
    os.makedirs(cache_dir, exist_ok=True)
    cache = SearchResultCache(cache_dir=cache_dir, ttl_days=7)
    print(f"[CACHE] Initialized with TTL=7 days, dir={cache_dir}")
except (ImportError, Exception) as e:
    print(f"Warning: Could not initialize SearchResultCache: {e}")
    print("      → Continuing without persistent caching")

tracker = None
try:
    from evaluation.token_tracker import TokenTracker
    from evaluation.alerts import notifier_from_env
    tracker = TokenTracker(notifier=notifier_from_env(os.getenv("SLACK_WEBHOOK_URL")))
except (ImportError, Exception) as e:
    print(f"Warning: Could not load TokenTracker: {e}")
    print("      → Continuing without token tracking")

# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_snippet(text: str, max_len: int = 240) -> str:
    """Truncate text to max_len with ellipsis if needed."""
    if not text:
        return ""
    s = " ".join(text.split())
    return s[:max_len] + ("..." if len(s) > max_len else "")


def _mock_search_engine(query: str) -> List[Dict]:
    """Simple local mock search engine for development/testing."""
    data = {
        "python": [
            {
                "title": "Python Official Website",
                "url": "https://www.python.org/",
                "snippet": "Python is a high-level, interpreted programming language known for its readability and versatility."
            }
        ],
        "machine learning": [
            {
                "title": "Machine Learning - Wikipedia",
                "url": "https://en.wikipedia.org/wiki/Machine_learning",
                "snippet": "Machine learning is a field of artificial intelligence that uses statistical techniques to give computer systems the ability to 'learn'."
            }
        ],
        "agent": [
            {
                "title": "AI Agent Frameworks Overview",
                "url": "https://example.com/ai-agents",
                "snippet": "Modern AI agents use orchestration frameworks like LangChain, CrewAI, or Microsoft AutoGen for complex workflows."
            }
        ],
    }

    q_lower = query.lower()
    for key in data:
        if key in q_lower:
            return data[key]

    return [{
        "title": f"Search results for '{query}'",
        "url": "https://example.com/search",
        "snippet": "No exact match found in local mock database. Try a different query."
    }]


def search_web(query: str) -> str:
    """
    Main search function: check cache first, fall back to mock, render consistently.
    """
    # Try cache
    if cache:
        try:
            cached = cache.get(query)
            if cached:
                parts = [
                    f"{r.get('title', 'Untitled')} — {_make_snippet(r.get('snippet', ''))} ({r.get('url', 'no-url')})"
                    for r in cached
                ]
                return "\n\n".join(parts)
        except Exception as e:
            print(f"[CACHE] Read error: {e}")

    # Fetch fresh results
    results = _mock_search_engine(query)

    # Save to cache
    if cache:
        try:
            cache.set(query, results)
            print(f"[CACHE] Stored results for: {query}")
        except Exception as e:
            print(f"[CACHE] Write error: {e}")

    # Consistent rendering
    return "\n\n".join(
        f"{r['title']} — {_make_snippet(r['snippet'])} ({r['url']})"
        for r in results
    )


def synthesize_findings(topic: str, sources: int = 3) -> str:
    """Generate a short synthesis from search results."""
    search_text = search_web(topic)
    summary = f"SYNTHESIS: Key points about '{topic}':\n"

    lines = [l.strip() for l in search_text.split("\n") if l.strip()]
    bullets = [
        f"- {_make_snippet(l, max_len=180)}"
        for l in lines[:sources]
    ]

    result = summary + "\n".join(bullets) if bullets else summary + "- No results available."

    # Optional token tracking
    if tracker:
        try:
            tracker.record_request(
                topic,
                result,
                meta={"tool": "synthesize_findings", "sources_used": min(sources, len(lines))}
            )
        except Exception:
            pass  # silent fail

    return result


# ── Interactive Mode ─────────────────────────────────────────────────────────

async def interactive_loop():
    print("Research Assistant CLI  (type 'exit', 'quit', or 'q' to leave)")
    print("Commands:")
    print("  search <query>     → Show raw search results")
    print("  synth <topic>      → Generate short summary")
    print("  (anything else)    → Treated as synthesis query")
    print("  help / h / ?       → Show this help\n")

    while True:
        try:
            user_input = await asyncio.get_event_loop().run_in_executor(None, input, "→ ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return

        text = user_input.strip()
        if not text:
            continue

        if text.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            return

        if text.lower() in ("help", "h", "?"):
            print("Commands: search <query> | synth <topic> | exit/quit/q | help/h/?")
            continue

        if text.lower().startswith("search "):
            query = text[7:].strip()
            print("\n" + search_web(query) + "\n")
        elif text.lower().startswith("synth "):
            topic = text[6:].strip()
            print("\n" + synthesize_findings(topic) + "\n")
        else:
            # Default: treat as synthesis request
            print("\n" + synthesize_findings(text) + "\n")


def main():
    if LOCAL_TEST:
        print("LOCAL_TEST mode — running quick demo...\n")
        print("Search: 'python caching'")
        print("─" * 70)
        print(search_web("python caching"))
        print("\n" + "═" * 70 + "\n")
        print("Synthesis: 'research assistant'")
        print("─" * 70)
        print(synthesize_findings("research assistant"))
        return

    # Normal interactive mode
    asyncio.run(interactive_loop())


if __name__ == "__main__":
    main()