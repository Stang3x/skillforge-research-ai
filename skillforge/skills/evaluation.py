"""Evaluation skill - evaluates research quality and credibility."""

from skillforge.skills.base import Skill, SkillInput, SkillOutput
from typing import List, Dict, Any


class EvaluationSkill(Skill):
    """Skill for evaluating research quality and source credibility."""

    def __init__(self):
        """Initialize the evaluation skill."""
        super().__init__(
            name="evaluation",
            description="Evaluates research quality, source credibility, and identifies gaps",
        )

    async def execute(self, skill_input: SkillInput) -> SkillOutput:
        """
        Evaluate research quality and sources.

        Args:
            skill_input: Input containing research results to evaluate

        Returns:
            SkillOutput with evaluation metrics
        """
        try:
            results = skill_input.context.get("results", [])

            if not results:
                return SkillOutput(
                    success=False, data=None, error="No research results to evaluate"
                )

            evaluation = self._evaluate_sources(results)

            return SkillOutput(
                success=True, data=evaluation, metadata={"skill": self.name}
            )
        except Exception as e:
            return SkillOutput(success=False, data=None, error=str(e))

    def _evaluate_sources(self, results: List[Dict[str, Any]]) -> dict:
        """Evaluate the quality and credibility of sources."""
        source_types = {}
        credibility_scores = []

        for result in results:
            source = result.get("source", "web")
            source_types[source] = source_types.get(source, 0) + 1

            # Simple credibility scoring
            score = self._calculate_credibility_score(result)
            credibility_scores.append(score)

        avg_credibility = (
            sum(credibility_scores) / len(credibility_scores) if credibility_scores else 0
        )

        return {
            "total_sources": len(results),
            "source_distribution": source_types,
            "average_credibility": round(avg_credibility, 2),
            "credibility_assessment": self._get_credibility_assessment(avg_credibility),
            "recommendations": self._generate_recommendations(source_types, avg_credibility),
            "potential_gaps": self._identify_gaps(source_types),
        }

    def _calculate_credibility_score(self, result: Dict[str, Any]) -> float:
        """Calculate credibility score for a source."""
        score = 50.0  # Base score

        source = result.get("source", "web")

        # Academic sources get higher scores
        if source == "arxiv":
            score += 30
        elif source == "pubmed":
            score += 35
        elif source == "web":
            score += 10

        # Check for URL indicators
        url = result.get("url", "")
        if ".edu" in url:
            score += 10
        elif ".gov" in url:
            score += 15
        elif ".org" in url:
            score += 5

        return min(score, 100.0)

    def _get_credibility_assessment(self, score: float) -> str:
        """Get textual assessment of credibility."""
        if score >= 80:
            return "High credibility - primarily academic and authoritative sources"
        elif score >= 60:
            return "Good credibility - mix of academic and reputable sources"
        elif score >= 40:
            return "Moderate credibility - consider seeking more authoritative sources"
        else:
            return "Low credibility - recommend additional verification"

    def _generate_recommendations(
        self, source_types: Dict[str, int], avg_credibility: float
    ) -> List[str]:
        """Generate recommendations for improving research quality."""
        recommendations = []

        if avg_credibility < 60:
            recommendations.append("Seek more peer-reviewed and academic sources")

        if "arxiv" not in source_types and "pubmed" not in source_types:
            recommendations.append("Include academic databases in your search")

        if source_types.get("web", 0) > source_types.get("arxiv", 0) + source_types.get(
            "pubmed", 0
        ):
            recommendations.append("Balance web sources with academic literature")

        if len(source_types) == 1:
            recommendations.append("Diversify sources across multiple platforms")

        if not recommendations:
            recommendations.append("Good source diversity - continue with current approach")

        return recommendations

    def _identify_gaps(self, source_types: Dict[str, int]) -> List[str]:
        """Identify potential gaps in research coverage."""
        gaps = []

        if "arxiv" not in source_types:
            gaps.append("No arXiv papers found - consider technical/scientific literature")

        if "pubmed" not in source_types:
            gaps.append("No PubMed papers found - consider medical/biological literature")

        if len(source_types) < 2:
            gaps.append("Limited source diversity - expand search to multiple databases")

        return gaps if gaps else ["No significant gaps identified"]
