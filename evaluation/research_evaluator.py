"""
ResearchEvaluator - lightweight LLM-as-Judge evaluator.
Provides numeric scores (1.0-5.0) for accuracy, completeness and a pairwise comparator.
This is a deterministic, local evaluator intended for automated benchmarking.
"""
from typing import List, Tuple
import re

class ResearchEvaluator:
    """Simple evaluator using token/keyword overlap heuristics.

    Methods:
    - score_accuracy(ref: str, candidate: str) -> float
    - score_completeness(ref: str, candidate: str) -> float
    - pairwise_compare(a: str, b: str, reference: str) -> Tuple[float,float]
    - aggregate_score(scores: List[float]) -> float
    """

    def __init__(self, min_score: float = 1.0, max_score: float = 5.0):
        self.min_score = min_score
        self.max_score = max_score

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"\w+", text.lower())
        return tokens

    def score_accuracy(self, reference: str, candidate: str) -> float:
        """Estimate accuracy by overlap of named entities / keywords between reference and candidate."""
        if not reference or not candidate:
            return self.min_score
        rset = set(self._tokenize(reference))
        cset = set(self._tokenize(candidate))
        if not rset:
            return self.min_score
        overlap = len(rset & cset) / len(rset)
        score = self.min_score + overlap * (self.max_score - self.min_score)
        return round(score, 2)

    def score_completeness(self, reference: str, candidate: str) -> float:
        """Estimate completeness by coverage of reference tokens present in candidate and length ratio."""
        if not reference or not candidate:
            return self.min_score
        r_tokens = self._tokenize(reference)
        c_tokens = self._tokenize(candidate)
        if not r_tokens:
            return self.min_score
        covered = sum(1 for t in set(r_tokens) if t in c_tokens)
        coverage_ratio = covered / len(set(r_tokens))
        length_ratio = min(1.0, len(c_tokens) / max(1, len(r_tokens)))
        score = self.min_score + 0.7 * coverage_ratio * (self.max_score - self.min_score) + 0.3 * length_ratio * (self.max_score - self.min_score)
        return round(score, 2)

    def pairwise_compare(self, a: str, b: str, reference: str) -> Tuple[float, float]:
        """Score two candidates against a reference. Returns (score_a, score_b)."""
        sa = self.score_accuracy(reference, a)
        ca = self.score_completeness(reference, a)
        sb = self.score_accuracy(reference, b)
        cb = self.score_completeness(reference, b)
        # Aggregate (weighted)
        score_a = round((0.6 * sa + 0.4 * ca), 2)
        score_b = round((0.6 * sb + 0.4 * cb), 2)
        return score_a, score_b

    def aggregate_score(self, scores: List[float]) -> float:
        if not scores:
            return self.min_score
        return round(sum(scores) / len(scores), 2)


if __name__ == '__main__':
    # quick self-test
    ref = "Multi-agent systems coordinate multiple specialized agents to solve complex tasks."
    cand_good = "A multi-agent system uses specialized agents (coordinator, researcher, analyst) to coordinate and solve complex tasks."
    cand_bad = "Agents talk to each other."
    ev = ResearchEvaluator()
    print('accuracy good:', ev.score_accuracy(ref, cand_good))
    print('completeness good:', ev.score_completeness(ref, cand_good))
    print('accuracy bad:', ev.score_accuracy(ref, cand_bad))
    print('completeness bad:', ev.score_completeness(ref, cand_bad))
    print('pairwise:', ev.pairwise_compare(cand_good, cand_bad, ref))
