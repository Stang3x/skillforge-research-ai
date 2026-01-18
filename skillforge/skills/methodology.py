"""Methodology skill - provides research methodology guidance."""

from skillforge.skills.base import Skill, SkillInput, SkillOutput


class MethodologySkill(Skill):
    """Skill for generating research methodology recommendations."""

    def __init__(self):
        """Initialize the methodology skill."""
        super().__init__(
            name="methodology",
            description="Provides research methodology recommendations and best practices",
        )

    async def execute(self, skill_input: SkillInput) -> SkillOutput:
        """
        Generate methodology recommendations.

        Args:
            skill_input: Input containing the research topic

        Returns:
            SkillOutput with methodology guidance
        """
        try:
            query = skill_input.query
            research_type = skill_input.options.get("research_type", "general")

            methodology = self._generate_methodology(query, research_type)

            return SkillOutput(
                success=True,
                data=methodology,
                metadata={"skill": self.name, "research_type": research_type},
            )
        except Exception as e:
            return SkillOutput(success=False, data=None, error=str(e))

    def _generate_methodology(self, query: str, research_type: str) -> dict:
        """Generate methodology recommendations."""
        base_steps = [
            "Define clear research questions",
            "Conduct comprehensive literature review",
            "Identify appropriate data sources",
            "Select suitable research methods",
            "Establish criteria for evaluation",
            "Plan data collection and analysis",
            "Consider ethical implications",
        ]

        if research_type == "quantitative":
            specific_methods = [
                "Design surveys or experiments",
                "Define sample size and selection criteria",
                "Choose statistical analysis methods",
                "Plan data visualization strategies",
            ]
        elif research_type == "qualitative":
            specific_methods = [
                "Design interview or observation protocols",
                "Select appropriate sampling strategy",
                "Choose qualitative analysis framework",
                "Plan for data triangulation",
            ]
        else:
            specific_methods = [
                "Determine if quantitative, qualitative, or mixed methods is appropriate",
                "Consider available resources and constraints",
                "Review similar studies for methodological guidance",
            ]

        return {
            "research_topic": query,
            "research_type": research_type,
            "core_steps": base_steps,
            "specific_methods": specific_methods,
            "best_practices": [
                "Document all methodological decisions",
                "Ensure reproducibility of research",
                "Address potential biases and limitations",
                "Plan for peer review and validation",
            ],
        }
