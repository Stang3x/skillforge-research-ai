"""Research skill - performs web searches and gathers information."""

from skillforge.skills.base import Skill, SkillInput, SkillOutput
from skillforge.search import search_all, SearchResult
from typing import List


class ResearchSkill(Skill):
    """Skill for performing research through web and academic searches."""

    def __init__(self, use_mock: bool = False):
        """
        Initialize the research skill.

        Args:
            use_mock: Use mock data for offline/testing
        """
        super().__init__(
            name="research",
            description="Performs web and academic searches to gather research information",
        )
        self.use_mock = use_mock

    async def execute(self, skill_input: SkillInput) -> SkillOutput:
        """
        Execute research by searching the web and academic sources.

        Args:
            skill_input: Input containing the research query

        Returns:
            SkillOutput with search results
        """
        try:
            query = skill_input.query
            max_results = skill_input.options.get("max_results", 10)
            include_academic = skill_input.options.get("include_academic", True)

            results = await search_all(
                query, web=True, academic=include_academic, use_mock=self.use_mock
            )

            return SkillOutput(
                success=True,
                data={
                    "query": query,
                    "results": [r.model_dump() for r in results[:max_results]],
                    "count": len(results[:max_results]),
                },
                metadata={"skill": self.name, "use_mock": self.use_mock},
            )
        except Exception as e:
            return SkillOutput(success=False, data=None, error=str(e))
