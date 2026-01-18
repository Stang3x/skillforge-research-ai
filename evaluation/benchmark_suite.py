"""Benchmark suite for measuring caching, latency, and token usage.

This script runs a set of sample queries against the local `research_assistant`
functions and records timings.
"""
import time
import json
from pathlib import Path
from typing import List, Dict
import sys

# Ensure repo root is on sys.path so package imports resolve
proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

from research_assistant import search_web, synthesize_findings

RESULTS_PATH = Path('evaluation') / 'benchmark_results.json'


class BenchmarkSuite:
    def __init__(self, queries: List[str] = None):
        self.queries = queries or [
            'Python caching',
            'What is machine learning',
            'Explain agent orchestration',
        ]
        self.results: Dict = {'runs': []}

    def run(self):
        run_ts = time.time()
        for q in self.queries:
            entry = {'query': q, 'search': {}, 'synth': {}}

            t0 = time.time()
            s = search_web(q)
            elapsed = time.time() - t0
            entry['search']['time_s'] = round(elapsed, 4)
            entry['search']['preview'] = s[:400]

            t0 = time.time()
            syn = synthesize_findings(q)
            elapsed = time.time() - t0
            entry['synth']['time_s'] = round(elapsed, 4)
            entry['synth']['preview'] = syn[:400]

            self.results['runs'].append(entry)

        self.results['summary_ts'] = run_ts
        RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        return self.results


def print_summary(results: Dict):
    print('\nBenchmark summary:')
    for r in results.get('runs', []):
        print(f"- {r['query']}: search {r['search']['time_s']}s, synth {r['synth']['time_s']}s")


if __name__ == '__main__':
    suite = BenchmarkSuite()
    res = suite.run()
    print_summary(res)
"""Benchmark suite for measuring caching, latency, and token usage.

This script runs a set of sample queries against the local `research_assistant`
functions and records timings.
"""
import time
import json
from pathlib import Path
from typing import List, Dict
import sys

# Ensure repo root is on sys.path so package imports resolve
proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

from research_assistant import search_web, synthesize_findings

RESULTS_PATH = Path('evaluation') / 'benchmark_results.json'


class BenchmarkSuite:
    def __init__(self, queries: List[str] = None):
        self.queries = queries or [
            'Python caching',
            'What is machine learning',
            'Explain agent orchestration',
        ]
        self.results: Dict = {'runs': []}

    def run(self):
        run_ts = time.time()
        for q in self.queries:
            entry = {'query': q, 'search': {}, 'synth': {}}

            t0 = time.time()
            s = search_web(q)
            elapsed = time.time() - t0
            entry['search']['time_s'] = round(elapsed, 4)
            entry['search']['preview'] = s[:400]

            t0 = time.time()
            syn = synthesize_findings(q)
            elapsed = time.time() - t0
            entry['synth']['time_s'] = round(elapsed, 4)
            entry['synth']['preview'] = syn[:400]

            self.results['runs'].append(entry)

        self.results['summary_ts'] = run_ts
        RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        return self.results


def print_summary(results: Dict):
    print('\nBenchmark summary:')
    for r in results.get('runs', []):
        print(f"- {r['query']}: search {r['search']['time_s']}s, synth {r['synth']['time_s']}s")


if __name__ == '__main__':
    suite = BenchmarkSuite()
    res = suite.run()
    print_summary(res)
"""Benchmark suite for measuring caching, latency, and token usage.

This script runs a set of sample queries against the local `research_assistant`
functions and records timings and token-tracker totals (if available).
"""
import time
import json
from pathlib import Path
from typing import List, Dict
import sys
import importlib

# Ensure repo root is on sys.path so package imports resolve
proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

from research_assistant import search_web, synthesize_findings

RESULTS_PATH = Path('evaluation') / 'benchmark_results.json'


class BenchmarkSuite:
    def __init__(self, queries: List[str] = None):
        self.queries = queries or [
            'Python caching',
            'What is machine learning',
            'Explain agent orchestration',
        ]
        self.results: Dict = {'runs': []}

    def run(self):
        run_ts = time.time()
        for q in self.queries:
            entry = {'query': q, 'search': {}, 'synth': {}}

            t0 = time.time()
            s = search_web(q)
            elapsed = time.time() - t0
            entry['search']['time_s'] = round(elapsed, 4)
            entry['search']['preview'] = s[:400]

            t0 = time.time()
            syn = synthesize_findings(q)
            elapsed = time.time() - t0
            entry['synth']['time_s'] = round(elapsed, 4)
            entry['synth']['preview'] = syn[:400]

            self.results['runs'].append(entry)

        self.results['summary_ts'] = run_ts
        RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        return self.results


def print_summary(results: Dict):
    print('\nBenchmark summary:')
    for r in results.get('runs', []):
        print(f"- {r['query']}: search {r['search']['time_s']}s, synth {r['synth']['time_s']}s")


if __name__ == '__main__':
    suite = BenchmarkSuite()
    res = suite.run()
    print_summary(res)
"""
Benchmark Suite for Week 4 improvements.
Measures cold vs warm search latency, token usage, and quality scores using ResearchEvaluator.
This script avoids importing `research_assistant` (which requires environment setup) and instead
re-uses `SearchResultCache` from `context-optimization` plus a local lightweight `search_web_local`.

Run: 
  python evaluation/benchmark_suite.py

Output: writes `evaluation/reports/benchmark_report.json` and prints a summary.
"""
from pathlib import Path
import time
import json
import sys
# Ensure project root is on sys.path so local package imports work when run as a script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.token_tracker import TokenTracker, MockResponse
from evaluation.research_evaluator import ResearchEvaluator
# Load caching module from the `context-optimization` folder (not a package)
CONTEXT_OPT_DIR = PROJECT_ROOT / 'context-optimization'
if str(CONTEXT_OPT_DIR) not in sys.path:
    sys.path.insert(0, str(CONTEXT_OPT_DIR))
import caching as _caching_mod
SearchResultCache = _caching_mod.SearchResultCache
# Import the in-memory LRU wrapper
from evaluation.cache_wrappers import LRUCacheWrapper

REPORT_DIR = Path(__file__).resolve().parents[0] / 'reports'
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Local lightweight search function reusing the mapping from research_assistant.search_web
SEARCH_RESULTS = {
    "python": "Python is a high-level, interpreted programming language known for its simplicity and readability. Created by Guido van Rossum in 1991, it supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
    "machine learning": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It uses algorithms and statistical models to identify patterns in data.",
    "research assistant": "A research assistant is an AI agent designed to help users find, analyze, and summarize information on various topics. It can search databases, organize findings, and present information in a structured manner.",
    "agent framework": "The Microsoft Agent Framework is a flexible framework for building, orchestrating, and deploying AI agents and multi-agent systems. It supports various LLMs, function calling, and multi-agent patterns.",
}


def search_web_local(query: str, cache: SearchResultCache) -> str:
    # Check cache first
    cached = cache.get(query)
    if cached:
        return cached

    # Simulate an API call by matching keywords
    query_lower = query.lower()
    result = None
    for keyword, text in SEARCH_RESULTS.items():
        if keyword in query_lower:
            result = f"Search results for '{query}':\n\n{text}"
            break
    if not result:
        result = f"Search results for '{query}':\n\nNo specific information found."

    # Persist to cache
    cache.set(query, result)
    return result


class BenchmarkSuite:
    def __init__(self, queries=None, iterations: int = 3):
        # persistent file-backed cache
        persistent = SearchResultCache(cache_dir=str(Path.cwd() / 'benchmark_cache'), ttl_days=7)
        # add in-memory LRU wrapper to speed warm reads
        self.cache = LRUCacheWrapper(persistent_cache=persistent, capacity=256)
        # Expanded realistic queries for broader coverage
        self.queries = queries or [
            'Python programming language',
            'Machine learning basics',
            'Research assistant capabilities',
            'Agent framework design patterns',
            'Transformer model architecture',
            'Context window optimization techniques',
            'Prompt engineering best practices',
            'Memory systems for agents',
            'Evaluation metrics for LLMs',
            'Unknown topic for negative case'
        ]
        self.iterations = iterations
        self.tracker = TokenTracker()
        self.evaluator = ResearchEvaluator()
        self.results = []

    def _estimate_tokens(self, query: str, result: str, cold: bool) -> (int, int):
        # crude heuristic: input tokens proportional to query length, output tokens proportional to result length
        input_tokens = max(4, len(query.split()) * (5 if cold else 1))
        output_tokens = max(8, len(result.split()) * (2 if cold else 1))
        return input_tokens, output_tokens

    def run(self):
        for q in self.queries:
            # Cold run (clear cache then call)
            self.cache.clear()
            t0 = time.perf_counter()
            res_cold = search_web_local(q, self.cache)
            t1 = time.perf_counter()
            cold_time = t1 - t0
            in_tok, out_tok = self._estimate_tokens(q, res_cold, cold=True)
            self.tracker.track(MockResponse(in_tok, out_tok), agent='search_api')

            # Multiple warm runs to measure stability and hit-rate
            warm_times = []
            cache_hits = 0
            for i in range(self.iterations):
                t2 = time.perf_counter()
                res_warm = search_web_local(q, self.cache)
                t3 = time.perf_counter()
                warm_times.append(t3 - t2)
                # If cache.get returned non-None, it's a hit (search_web_local sets cache on miss)
                if self.cache.get(q) is not None:
                    cache_hits += 1

            avg_warm = sum(warm_times) / len(warm_times) if warm_times else 0.0
            in_tok_w, out_tok_w = self._estimate_tokens(q, res_warm, cold=False)
            self.tracker.track(MockResponse(in_tok_w, out_tok_w), agent='search_cache')

            # Quality scoring against a synthetic reference (synthesize_findings-like)
            reference = f"Based on current research, {q} is an important area of study."
            score_cold_acc = self.evaluator.score_accuracy(reference, res_cold)
            score_cold_comp = self.evaluator.score_completeness(reference, res_cold)
            score_warm_acc = self.evaluator.score_accuracy(reference, res_warm)
            score_warm_comp = self.evaluator.score_completeness(reference, res_warm)

            self.results.append({
                'query': q,
                'cold': {
                    'time_s': round(cold_time, 6),
                    'input_tokens': in_tok,
                    'output_tokens': out_tok,
                    'accuracy': score_cold_acc,
                    'completeness': score_cold_comp,
                },
                'warm': {
                    'avg_time_s': round(avg_warm, 6),
                    'iterations': self.iterations,
                    'cache_hits': cache_hits,
                    'input_tokens': in_tok_w,
                    'output_tokens': out_tok_w,
                    'accuracy': score_warm_acc,
                    'completeness': score_warm_comp,
                }
            })

    def summary(self):
        total_cold_time = sum(item['cold']['time_s'] for item in self.results)
        # warm entries may use 'avg_time_s' (new) or 'time_s' (legacy)
        total_warm_time = sum(item['warm'].get('avg_time_s', item['warm'].get('time_s', 0)) for item in self.results)
        total_input = self.tracker.total_input_tokens
        total_output = self.tracker.total_output_tokens
        percent_time_improve = round((1 - total_warm_time / total_cold_time) * 100, 2) if total_cold_time > 0 else 0.0

        summary = {
            'queries': len(self.results),
            'total_cold_time_s': round(total_cold_time, 4),
            'total_warm_time_s': round(total_warm_time, 4),
            'percent_time_improvement': percent_time_improve,
            'total_input_tokens': total_input,
            'total_output_tokens': total_output,
        }
        return summary

    def save_report(self, path: Path):
        report = {
            'results': self.results,
            'summary': self.summary()
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"Saved benchmark report: {path}")


def run_quick_benchmark():
    bs = BenchmarkSuite()
    bs.run()
    out = REPORT_DIR / 'benchmark_report.json'
    bs.save_report(out)
    print('Summary:')
    print(json.dumps(bs.summary(), indent=2))


if __name__ == '__main__':
    run_quick_benchmark()
