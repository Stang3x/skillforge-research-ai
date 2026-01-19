# Performance Metrics & Benchmarking

This document describes the benchmark outputs collected by `evaluation/benchmark_suite.py`.

Location of results: `evaluation/benchmark_results.json`

Primary metrics collected:

- **search.time_s**: elapsed seconds for the `search_web` call
- **synth.time_s**: elapsed seconds for the `synthesize_findings` call
- **preview**: first 400 characters of the returned output for spot-checking

Success criteria (Week 4):

- Average `search.time_s` reduced by 20%+ after caching and optimizations
- Average `synth.time_s` reduced by 20%+ after token/tool optimizations
- Token usage reduction documented in `evaluation/token_usage_report.json` (if `TokenTracker` used)

How to run the benchmark locally:

```bash
python -m evaluation.benchmark_suite
```

Notes:

- The benchmark suite is intentionally simple and focused on end-to-end timings.
- For more detailed profiling, expand `benchmark_suite.py` to capture per-component timings
  and use `evaluation.evaluator.ResearchEvaluator` to score outputs for quality metrics.
# Performance Metrics (Week 4)

This document will record measured improvements from the Week 4 optimization tasks (caching, token tracking, supervisor optimization).

Planned sections:

- Summary: high-level before/after metrics
- Latency: cold vs warm (cached) request times
- Token Usage: input/output tokens per session and per query
- Quality: aggregate `ResearchEvaluator` scores (accuracy, completeness)
- Cost Estimate: token-based cost delta estimation
- Recommendations: next steps to improve caching hit-rate and evaluation fidelity

Run `python evaluation/benchmark_suite.py` to generate a baseline report at `evaluation/reports/benchmark_report.json`.

## Latest Benchmark (generated)

Source report: `evaluation/reports/benchmark_report.json`

- **Queries tested:** 10
- **Total cold time (s):** 0.0063
- **Total warm time (s):** 0.0055
- **Percent time improvement (cold -> warm):** 14.02%
- **Total input tokens (estimated):** 226
- **Total output tokens (estimated):** 639

Key findings:

- The caching layer produces measurable latency improvements for repeated queries (warm runs). In this synthetic microbenchmark the average improvement was ~14%.
- Warm runs observed a 100% hit-rate in the repeated iterations (3 iterations per query) because the cache was filled on the initial cold run.
- Quality scores from the lightweight `ResearchEvaluator` are reported per-query in the JSON report; scores are heuristic and intended for relative comparisons rather than absolute grading.

Next actions:

- Run a larger-scale benchmark (100+ queries) with realistic timing noise and randomized query order to estimate production hit-rate and warm/cold distribution.
- Integrate real token usage from the production LLM client when available to replace the current heuristics.
- Add visualizations (charts) to this document from the JSON report for easier review.

## Large-scale Benchmark (100 queries)

Source report: `evaluation/reports/benchmark_large_report.json`

- **Queries tested:** 100
- **Total cold time (s):** 0.0593
- **Total warm time (s):** 0.1762
- **Percent time improvement (cold -> warm):** -197.16% (warm runs slower)
- **Total input tokens (estimated):** 2,071
- **Total output tokens (estimated):** 4,584

Observation:

- In this synthetic large-scale run warm runs averaged slower than cold runs. This is due to the current cache implementation using JSON files on disk for each entry; reading the cache file (and the per-query JSON payload sizes used in the test) can be slower than the in-memory simulation of the search result generation.

Recommendations:

- Use an in-memory LRU cache (e.g., `functools.lru_cache` or `cachetools`) alongside the persistent JSON store to ensure warm reads are low-latency.
- Compress or store compact summaries in the cache (avoid writing large full-result JSON blobs per query) to reduce IO cost.
- Batch warm-read tests with different cache backends (in-memory, sqlite, Redis) to measure realistic production behavior.
- Replace token heuristics with live LLM `usage` fields when integrating with the real OpenAI/GitHub model client.

Actionable next step: If you want, I can implement an in-memory LRU wrapper around `SearchResultCache` and re-run the large benchmark to show improved warm-run latency.

## LRU Wrapper Benchmark Result

I implemented an in-memory LRU wrapper at `evaluation/cache_wrappers.py` and re-ran the large randomized benchmark using the wrapper.

Key numbers (large benchmark, 100 queries):

- **Total cold time (s):** 0.0622
- **Total warm time (s) with LRU:** 0.0001
- **Percent time improvement (cold -> warm):** 99.81%
- **Total input tokens (estimated):** 2,071
- **Total output tokens (estimated):** 4,584

Notes:

- The LRU in-memory layer dramatically reduces warm-read latency in this synthetic benchmark (from ~0.062s total cold to ~0.0001s total warm across 100 queries). This demonstrates the practical benefit of an in-memory cache for latency-sensitive workloads.
- The persistent JSON store remains as a backing store; the LRU performs write-through so cache durability is preserved while hot entries are served from memory.

Recommendation: adopt the `LRUCacheWrapper` (or a production-grade cache like Redis) for hot-path query caching. I can optionally add an environment flag to switch between backends and re-run benchmarks comparing file-backed, sqlite, redis, and LRU in-memory setups.
 
## Visualizations

Generated charts (see `evaluation/reports/plots`):

- Cold vs Warm Time: [evaluation/reports/plots/cold_vs_warm_time.png](evaluation/reports/plots/cold_vs_warm_time.png)
- Token Usage: [evaluation/reports/plots/tokens_bar.png](evaluation/reports/plots/tokens_bar.png)

Open the PNG files to inspect per-query comparisons (top 20 by metric).
