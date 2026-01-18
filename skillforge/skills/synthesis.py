"""Synthesis skill - synthesizes research findings into a coherent summary."""

from skillforge.skills.base import Skill, SkillInput, SkillOutput
from typing import List, Dict, Any


class SynthesisSkill(Skill):
    """Skill for synthesizing research findings."""

    def __init__(self):
        """Initialize the synthesis skill."""
        super().__init__(
            name="synthesis",
            description="Synthesizes research findings into a coherent summary with key insights",
        )

    async def execute(self, skill_input: SkillInput) -> SkillOutput:
        """
        Synthesize research findings.

        Args:
            skill_input: Input containing research results to synthesize

        Returns:
            SkillOutput with synthesized summary
        """
        try:
            results = skill_input.context.get("results", [])
            query = skill_input.query

            if not results:
                return SkillOutput(
                    success=False, data=None, error="No research results to synthesize"
                )

            # Create a structured synthesis
            summary = self._create_summary(query, results)
            key_findings = self._extract_key_findings(results)
            themes = self._identify_themes(results)

            synthesis = {
                "summary": summary,
                "key_findings": key_findings,
                "themes": themes,
                "sources_analyzed": len(results),
            }

            return SkillOutput(
                success=True, data=synthesis, metadata={"skill": self.name, "query": query}
            )
        except Exception as e:
            return SkillOutput(success=False, data=None, error=str(e))

    def _create_summary(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Create a summary paragraph from research results."""
        summary_parts = [
            f"Research on '{query}' reveals several important insights.",
            f"Analysis of {len(results)} sources indicates:",
        ]

        # Extract key information from top results
        for i, result in enumerate(results[:3], 1):
            title = result.get("title", "Unknown")
            snippet = result.get("snippet", "")
            if snippet:
                summary_parts.append(f"{i}. {title}: {snippet[:100]}...")

        return " ".join(summary_parts)

    def _extract_key_findings(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extract key findings from results."""
        findings = []

        for result in results[:5]:
            snippet = result.get("snippet", "")
            if snippet and len(snippet) > 20:
                # Extract meaningful phrases (simplified)
                finding = snippet.split(".")[0] if "." in snippet else snippet[:100]
                findings.append(finding)

        return findings

    def _identify_themes(self, results: List[Dict[str, Any]]) -> List[str]:
        """Identify common themes across results."""
        # Simple theme identification based on source types
        themes = set()

        for result in results:
            source = result.get("source", "web")
            if source == "arxiv":
                themes.add("Academic Research")
            elif source == "pubmed":
                themes.add("Medical/Biological Studies")
            else:
                themes.add("General Information")

        return list(themes)
