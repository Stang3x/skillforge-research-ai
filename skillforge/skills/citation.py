"""Citation skill - formats sources with proper citations."""

from skillforge.skills.base import Skill, SkillInput, SkillOutput
from skillforge.citation import CitationGenerator, CitationStyle, create_source_from_search_result
from typing import List, Dict, Any


class CitationSkill(Skill):
    """Skill for generating citations in various formats."""

    def __init__(self, style: CitationStyle = CitationStyle.APA):
        """
        Initialize the citation skill.

        Args:
            style: The citation style to use (default: APA)
        """
        super().__init__(
            name="citation",
            description=f"Generates citations in {style.value.upper()} format",
        )
        self.citation_generator = CitationGenerator(style=style)

    async def execute(self, skill_input: SkillInput) -> SkillOutput:
        """
        Generate citations for research sources.

        Args:
            skill_input: Input containing sources to cite

        Returns:
            SkillOutput with formatted citations
        """
        try:
            results = skill_input.context.get("results", [])
            style = skill_input.options.get("style", "apa")

            # Update citation style if specified
            if style != self.citation_generator.style.value:
                self.citation_generator.style = CitationStyle(style)

            if not results:
                return SkillOutput(
                    success=False, data=None, error="No sources to cite"
                )

            # Convert search results to sources and generate citations
            citations = []
            for result in results:
                source = create_source_from_search_result(
                    title=result.get("title", "Unknown Title"),
                    url=result.get("url", ""),
                    snippet=result.get("snippet", ""),
                )
                citation = self.citation_generator.generate(source)
                citations.append(citation)

            bibliography = "\n\n".join(citations)

            return SkillOutput(
                success=True,
                data={
                    "style": style,
                    "citations": citations,
                    "bibliography": bibliography,
                    "count": len(citations),
                },
                metadata={"skill": self.name, "style": style},
            )
        except Exception as e:
            return SkillOutput(success=False, data=None, error=str(e))
