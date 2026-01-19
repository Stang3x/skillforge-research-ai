"""Research Assistant — simplified, secure, and cache-enabled.

This file is a direct rename of research_assistant.py to remove the underscore
from the filename as requested. Content preserved.
"""

import asyncio
import os
import sys
import time
import json
import hashlib
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


def _apply_cli_bootstrap_args():
    argv = list(sys.argv)
    mapping = {
        "--cache-dir": "CACHE_DIR",
        "--cache-ttl": "CACHE_TTL_SECONDS",
        "--google-cse-key": "GOOGLE_CSE_API_KEY",
        "--google-cse-cx": "GOOGLE_CSE_CX",
    }
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--local-test":
            os.environ["LOCAL_TEST"] = "1"
            try:
                sys.argv.remove("--local-test")
            except Exception:
                pass
            i += 1
            continue
        if a in mapping:
            if i + 1 < len(argv):
                os.environ[mapping[a]] = argv[i + 1]
                try:
                    sys.argv.remove(a)
                    sys.argv.remove(argv[i + 1])
                except Exception:
                    pass
            i += 2
            continue
        i += 1


_apply_cli_bootstrap_args()

# Prefer repository secret name `GITHUB_PAT`, fall back to older names for compatibility
GITHUB_TOKEN = os.getenv("GITHUB_PAT") or os.getenv("GITHUB_TOKEN")
MODEL_ID = os.getenv("MODEL_ID", "openai/gpt-4o-mini")

# Local-test mode bypasses external API requirements for safe demo runs
LOCAL_TEST = os.getenv("LOCAL_TEST", "0") == "1" or "--local-test" in sys.argv

if not GITHUB_TOKEN and not LOCAL_TEST:
    raise ValueError("GITHUB_PAT (preferred) or GITHUB_TOKEN must be set, or run with --local-test")


# Project root handling (helps import modules from sibling folders)
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "context-optimization"))

# Cache TTL (seconds)
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))


class SimpleFileCache:
    def __init__(self, dirpath: str = ".simple_cache", ttl: int = 3600):
        import pathlib

        self.dir = pathlib.Path(dirpath)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.ttl = int(os.getenv("CACHE_TTL_SECONDS", ttl))

    def _key_path(self, key: str):
        name = hashlib.sha256(key.encode("utf-8")).hexdigest() + ".json"
        return self.dir / name

    def get(self, key: str):
        p = self._key_path(key)
        if not p.exists():
            return None
        try:
            text = p.read_text(encoding="utf-8")
            data = json.loads(text)
            ts = float(data.get("_ts", 0))
            if time.time() - ts > self.ttl:
                try:
                    p.unlink()
                except Exception:
                    pass
                return None
            return data.get("value")
        except Exception:
            return None

    def set(self, key: str, value):
        p = self._key_path(key)
        try:
            data = {"_ts": time.time(), "value": value}
            p.write_text(json.dumps(data), encoding="utf-8")
        except Exception:
            pass


# Lazy imports for optional modules in repo; prefer project-local `caching` or
# `context_optimization.caching`, falling back to file cache.
cache = None
cache_dir = os.getenv("CACHE_DIR") or str(PROJECT_ROOT / "cache" / "search_results")
try:
    from caching import SearchResultCache

    try:
        os.makedirs(cache_dir, exist_ok=True)
    except Exception:
        pass
    cache = SearchResultCache(cache_dir=cache_dir)
except Exception:
    try:
        from context_optimization.caching import SearchResultCache

        try:
            os.makedirs(cache_dir, exist_ok=True)
        except Exception:
            pass
        cache = SearchResultCache(cache_dir=cache_dir)
    except Exception:
        try:
            cache = SimpleFileCache(dirpath=os.getenv("CACHE_DIR", ".simple_cache"), ttl=CACHE_TTL_SECONDS)
        except Exception:
            cache = None


# TokenTracker (best-effort)
try:
    from evaluation.token_tracker import TokenTracker
    from evaluation.alerts import notifier_from_env

    tracker = TokenTracker(notifier=notifier_from_env(os.getenv("SLACK_WEBHOOK_URL")))
except Exception:
    TokenTracker = None
    tracker = None


def _make_snippet(text: str, max_len: int = 240) -> str:
    s = " ".join(text.split())
    return s[:max_len] + ("..." if len(s) > max_len else "")


def _mock_search_engine(query: str) -> List[Dict]:
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
    return [{"title": f"Results for {query}", "url": "https://example.com/search", "snippet": f"No direct match for '{query}'. Consider refining the query."}]


def _google_search(query: str) -> List[Dict]:
    try:
        api_key = os.getenv("GOOGLE_CSE_API_KEY")
        cx = os.getenv("GOOGLE_CSE_CX")
        if not api_key or not cx:
            raise RuntimeError("Google CSE not configured")
        import requests

        params = {"key": api_key, "cx": cx, "q": query}
        resp = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        results = []
        for it in items[:5]:
            results.append({"title": it.get("title", "")[:180], "url": it.get("link", ""), "snippet": it.get("snippet", "")})
        return results or []
    except Exception:
        return []


def search_web(query: str) -> str:
    try:
        if cache:
            cached = cache.get(query)
            if cached:
                parts = []
                for r in (cached[:3] if isinstance(cached, list) else [cached]):
                    title = r.get("title") if isinstance(r, dict) else str(r)
                    snippet = _make_snippet(r.get("snippet") if isinstance(r, dict) else str(r), max_len=180)
                    url = r.get("url") if isinstance(r, dict) else ""
                    parts.append(f"{title} — {snippet} ({url})")
                rendered = "\n\n".join(parts)
                try:
                    if tracker:
                        tracker.record_request(query, rendered, meta={"tool": "search_web_cached"})
                except Exception:
                    pass
                return rendered
    except Exception as e:
        print(f"[CACHE] lookup error: {e}")

    results = _mock_search_engine(query)
    try:
        if os.getenv("GOOGLE_CSE_API_KEY") and os.getenv("GOOGLE_CSE_CX"):
            g = _google_search(query)
            if g:
                results = g
    except Exception:
        pass

    try:
        if cache:
            cache.set(query, results[:3])
    except Exception as e:
        print(f"[CACHE] write error: {e}")

    rendered = "\n\n".join([f"{r['title']} — {_make_snippet(r['snippet'])} ({r['url']})" for r in results])
    try:
        if tracker:
            resp = tracker.record_request(query, rendered, meta={'tool': 'search_web'})
            if isinstance(resp, dict) and resp.get('alert'):
                print(f"[TOKEN TRACKER] Alert: {resp}")
    except Exception:
        pass

    return rendered


def synthesize_findings(topic: str, sources: int = 3) -> str:
    search_text = search_web(topic)
    summary = f"SYNTHESIS: Key points for '{topic}':\n"
    lines = [l.strip() for l in search_text.split('\n') if l.strip()]
    bullets = []
    for l in lines[:min(3, sources)]:
        bullets.append(f"- {_make_snippet(l, max_len=180)}")

    out = summary + "\n".join(bullets)

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

        text = user.strip()
        if text.startswith("search "):
            q = text[len("search ") :].strip()
            res = search_web(q)
            print("\n" + res)
            continue
        if text.startswith("synth "):
            topic = text[len("synth ") :].strip()
            out = synthesize_findings(topic)
            print("\n" + out)
            continue

        out = synthesize_findings(text)
        print("\n" + out)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Research Assistant CLI")
    parser.add_argument("--local-test", action="store_true", help="Run the local demo and exit")
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache for this run")
    parser.add_argument("--cache-clear", action="store_true", help="Clear file cache on startup")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    if args.cache_clear:
        try:
            d = os.getenv("CACHE_DIR", ".simple_cache")
            import shutil

            if os.path.exists(d):
                shutil.rmtree(d)
                if args.verbose:
                    print(f"Cleared cache directory: {d}")
        except Exception as e:
            if args.verbose:
                print(f"Failed to clear cache: {e}")

    if args.no_cache:
        try:
            cache = None
        except Exception:
            pass

    if args.local_test or LOCAL_TEST:
        print("LOCAL_TEST: running a brief demo")
        print(search_web("python caching"))
        print("\n--- Synthesizing 'research assistant' ---")
        print(synthesize_findings("research assistant"))
        return

    asyncio.run(interactive_loop())


if __name__ == "__main__":
    main()
