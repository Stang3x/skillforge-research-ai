"""LLM-as-Judge evaluator (lightweight, pluggable).

This module provides a `ResearchEvaluator` class that scores responses
on accuracy, completeness, and relevance on a 1.0-5.0 scale. It is
heuristic-first but designed to be replaced or extended with an LLM
scoring backend if available.
"""
from __future__ import annotations
from typing import Optional, Tuple, Dict
import math
import re


def _tokenize(text: str):
    # simple word tokenizer, lowercased
    return re.findall(r"\w+", text.lower())


def _score_frac(shared: int, total: int) -> float:
    if total <= 0:
        return 0.0
    frac = shared / total
    # map [0..1] to [1..5]
    return 1.0 + 4.0 * frac


class ResearchEvaluator:
    """Evaluate responses using lightweight heuristics.

    Methods:
    - `evaluate_accuracy(response, reference)` -> float
    - `evaluate_completeness(response, reference)` -> float
    - `evaluate_relevance(response, query)` -> float
    - `pairwise_compare(a, b, reference=None, query=None)` -> Dict
    - `aggregate(scores)` -> float
    """

    def __init__(self, llm_client: Optional[object] = None):
        # llm_client is optional; if provided, can be used to get LLM judgments
        self.llm_client = llm_client

    def evaluate_accuracy(self, response: str, reference: str) -> float:
        """Heuristic accuracy: token overlap with a reference answer.

        Returns a score in [1.0, 5.0].
        """
        resp_tokens = set(_tokenize(response))
        ref_tokens = set(_tokenize(reference))
        if not ref_tokens:
            return 1.0
        shared = len(resp_tokens & ref_tokens)
        return round(min(5.0, _score_frac(shared, len(ref_tokens))), 2)

    def evaluate_completeness(self, response: str, reference: str) -> float:
        """Completeness heuristic: fraction of reference concepts covered.

        If the response is longer and contains more of the reference tokens,
        it scores higher.
        """
        return self.evaluate_accuracy(response, reference)

    def evaluate_relevance(self, response: str, query: str) -> float:
        """Relevance: measures presence of query terms in the response."""
        resp_tokens = set(_tokenize(response))
        query_tokens = set(_tokenize(query))
        if not query_tokens:
            return 1.0
        shared = len(resp_tokens & query_tokens)
        return round(min(5.0, _score_frac(shared, len(query_tokens))), 2)

    def pairwise_compare(self, a: str, b: str, reference: Optional[str] = None, query: Optional[str] = None) -> Dict[str, float]:
        """Compare two responses `a` and `b`.

        Returns a dict with individual component scores and an `overall` score
        for each response.
        """
        results = {}
        for name, text in (('a', a), ('b', b)):
            acc = self.evaluate_accuracy(text, reference) if reference else 3.0
            comp = self.evaluate_completeness(text, reference) if reference else 3.0
            rel = self.evaluate_relevance(text, query) if query else 3.0
            overall = round((acc + comp + rel) / 3.0, 2)
            results[name] = {'accuracy': acc, 'completeness': comp, 'relevance': rel, 'overall': overall}
        return results

    def aggregate(self, scores: Tuple[float, ...]) -> float:
        """Aggregate multiple numeric scores into a single rating."""
        if not scores:
            return 0.0
        avg = float(sum(scores)) / len(scores)
        return round(avg, 2)


if __name__ == '__main__':
    # simple smoke test
    ev = ResearchEvaluator()
    a = "Python is a programming language created by Guido van Rossum in 1991."
    ref = "Python was created by Guido van Rossum in 1991 and is a high-level language."
    print('Accuracy:', ev.evaluate_accuracy(a, ref))
    print('Relevance:', ev.evaluate_relevance(a, 'what is python'))
