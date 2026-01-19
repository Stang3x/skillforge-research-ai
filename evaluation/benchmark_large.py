"""
Large randomized benchmark (100 queries) that reuses BenchmarkSuite and produces a report.
Run from project root:
  python evaluation/benchmark_large.py
"""
import random
from pathlib import Path
import json
import sys

# Ensure project root on path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.benchmark_suite import BenchmarkSuite, REPORT_DIR

# Build 100 randomized queries by combining topics and modifiers
TOPICS = [
    'Python programming', 'Machine learning', 'Research assistant', 'Agent framework',
    'Transformer model', 'Context window', 'Prompt engineering', 'Memory systems',
    'Evaluation metrics', 'Few-shot learning', 'Reinforcement learning', 'Fine-tuning',
    'Chain of thought', 'Tool use', 'Knowledge retrieval', 'Semantic search',
    'Document retrieval', 'Citation extraction', 'Dataset curation', 'Prompt templates'
]
MODIFIERS = ['basics', 'advanced', 'best practices', 'design patterns', 'overview', 'case study', 'tutorial', 'comparison']

random.seed(42)
queries = []
while len(queries) < 100:
    t = random.choice(TOPICS)
    m = random.choice(MODIFIERS)
    q = f"{t} {m}"
    if q not in queries:
        queries.append(q)

# Shuffle to randomize cold/warm distribution
random.shuffle(queries)

bs = BenchmarkSuite(queries=queries, iterations=5)
bs.run()
out = REPORT_DIR / 'benchmark_large_report.json'
bs.save_report(out)
print('\nLarge benchmark complete. Summary:')
print(json.dumps(bs.summary(), indent=2))
