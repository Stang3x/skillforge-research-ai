"""Research Assistant — simplified, secure, and cache-enabled.

Features:
- Prefer `GITHUB_PAT` environment secret (fallback to `GITHUB_TOKEN`).
- Integrates `context-optimization.SearchResultCache` for query caching.
- Uses `evaluation.token_tracker.TokenTracker` for local token accounting.
- Lightweight CLI for local testing (`--local-test`).

This file is intentionally self-contained and avoids embedding secrets.
"""

import asyncio
import os
import sys
import time
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# Prefer repository secret name `GITHUB_PAT`, fall back to older names for compatibility
GITHUB_TOKEN = os.getenv("GITHUB_PAT") or os.getenv("GITHUB_TOKEN")
MODEL_ID = os.getenv("MODEL_ID", "openai/gpt-4o-mini")

# Local-test mode bypasses external API requirements for safe demo runs
LOCAL_TEST = os.getenv("LOCAL_TEST", "0") == "1" or "--local-test" in sys.argv

if not GITHUB_TOKEN and not LOCAL_TEST:
    raise ValueError("GITHUB_PAT (preferred) or GITHUB_TOKEN must be set, or run with --local-test")

# Lazy imports for optional modules in repo
cache = None
try:
    from context_optimization.caching import SearchResultCache
    cache = SearchResultCache()
except Exception:
    # best-effort: continue without cache
    cache = None

# TokenTracker (best-effort)
try:
    from evaluation.token_tracker import TokenTracker
    from evaluation.alerts import notifier_from_env
    tracker = TokenTracker(notifier=notifier_from_env(os.getenv('SLACK_WEBHOOK_URL')))
except Exception:
    TokenTracker = None
    tracker = None


def _make_snippet(text: str, max_len: int = 240) -> str:
    s = " ".join(text.split())
    return s[:max_len] + ("..." if len(s) > max_len else "")


def _mock_search_engine(query: str) -> List[Dict]:
    """Return a small set of structured results (title, url, snippet).
    This is a safe local stub used for demos and for caching.
    """
    data = {
        "python": [
            {"title": "Python — Overview", "url": "https://python.org/", "snippet": "Python is a high-level, interpreted programming language."}
        ],
        "machine learning": [
            {"title": "Machine Learning — Intro", "url": "https://en.wikipedia.org/wiki/Machine_learning", "snippet": "Machine learning enables systems to learn from data."}
        ],
    }
    q = query.lower()
    for k in data:
        if k in q:
            return data[k]
    # fallback generic result
    return [{"title": f"Results for {query}", "url": "https://example.com/search", "snippet": f"No direct match for '{query}'. Consider refining the query."}]


def search_web(query: str) -> str:
    """Search wrapper: return a concise textual summary. Uses cache when available.

    The cache stores a list of result dicts (title/url/snippet). This function
    returns a textual rendering suitable for downstream synthesis.
    """
    # Try cache first
    try:
        if cache:
            cached = cache.get(query)
            if cached:
                parts = [f"{r.get('title')} — {r.get('snippet')} ({r.get('url')})" for r in cached]
                return "\n\n".join(parts)
    except Exception as e:
        print(f"[CACHE] lookup error: {e}")

    # Fetch fresh (mock or real integration point)
    results = _mock_search_engine(query)

    # Persist into cache
    try:
        if cache:
            cache.set(query, results)
    except Exception as e:
        print(f"[CACHE] write error: {e}")

    # Return rendered text
    return "\n\n".join([f"{r['title']} — {_make_snippet(r['snippet'])} ({r['url']})" for r in results])


def synthesize_findings(topic: str, sources: int = 3) -> str:
    """Create a short synthesis from search results.

    This function is intentionally brief to reduce token usage.
    """
    search_text = search_web(topic)
    summary = f"SYNTHESIS: Key points for '{topic}':\n"
    # heuristics: pick first 2-3 sentences from search_text
    lines = [l.strip() for l in search_text.split('\n') if l.strip()]
    bullets = []
    for l in lines[:min(3, sources)]:
        bullets.append(f"- {_make_snippet(l, max_len=180)}")

    out = summary + "\n".join(bullets)

    # TokenTracker record (best-effort)
    try:
        if tracker:
            tracker.record_request(topic, out, meta={"tool": "synthesize_findings"})
    except Exception:
        pass

    return out


async def interactive_loop():
    print("Research Assistant — interactive (type 'exit' to quit)")
    while True:
        try:
            user = await asyncio.get_event_loop().run_in_executor(None, input, "\nYou: ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return
        if not user:
            continue
        if user.strip().lower() in ("exit", "quit"):
            print("Goodbye.")
            return
        if user.strip().lower() in ("help", "h"):
            print("Commands: 'search <query>', 'synth <topic>' or free text research queries.")
            continue

        # simple command parsing
        text = user.strip()
        if text.startswith("search "):
            q = text[len("search "):].strip()
            res = search_web(q)
            print("\n" + res)
            continue
        if text.startswith("synth "):
            topic = text[len("synth "):].strip()
            out = synthesize_findings(topic)
            print("\n" + out)
            continue

        # fallback: treat as synth query
        out = synthesize_findings(text)
        print("\n" + out)


def main():
    if LOCAL_TEST:
        # small demo run
        print("LOCAL_TEST: running a brief demo")
        print(search_web("python caching"))
        print("\n--- Synthesizing 'research assistant' ---")
        print(synthesize_findings("research assistant"))
        return

    # run interactive event loop
    asyncio.run(interactive_loop())


if __name__ == "__main__":
    main()
