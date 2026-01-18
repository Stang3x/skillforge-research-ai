"""Integration tests for the full research workflow."""

import pytest
from skillforge.skills import skill_registry, SkillInput
from skillforge.skills.research import ResearchSkill
from skillforge.skills.synthesis import SynthesisSkill
from skillforge.skills.citation import CitationSkill
from skillforge.skills.evaluation import EvaluationSkill
from skillforge.citation import CitationStyle


@pytest.mark.asyncio
async def test_full_research_workflow():
    """Test the complete research workflow."""
    # Initialize skills
    research_skill = ResearchSkill(use_mock=True)
    synthesis_skill = SynthesisSkill()
    citation_skill = CitationSkill(style=CitationStyle.APA)
    eval_skill = EvaluationSkill()

    # Step 1: Research
    research_input = SkillInput(
        query="quantum computing",
        options={"max_results": 10},
    )
    research_result = await research_skill.execute(research_input)

    assert research_result.success is True
    results = research_result.data["results"]
    assert len(results) > 0

    # Step 2: Synthesis
    synthesis_input = SkillInput(
        query="quantum computing",
        context={"results": results},
    )
    synthesis_result = await synthesis_skill.execute(synthesis_input)

    assert synthesis_result.success is True
    assert "summary" in synthesis_result.data
    assert "key_findings" in synthesis_result.data

    # Step 3: Evaluation
    eval_input = SkillInput(
        query="quantum computing",
        context={"results": results},
    )
    eval_result = await eval_skill.execute(eval_input)

    assert eval_result.success is True
    assert "average_credibility" in eval_result.data
    assert "recommendations" in eval_result.data

    # Step 4: Citation
    citation_input = SkillInput(
        query="quantum computing",
        context={"results": results},
        options={"style": "apa"},
    )
    citation_result = await citation_skill.execute(citation_input)

    assert citation_result.success is True
    assert "citations" in citation_result.data
    assert "bibliography" in citation_result.data


@pytest.mark.asyncio
async def test_skill_registry_workflow():
    """Test using the skill registry for the workflow."""
    # Register skills
    skill_registry.register(ResearchSkill(use_mock=True))
    skill_registry.register(SynthesisSkill())
    skill_registry.register(CitationSkill())

    # Get skills from registry
    research_skill = skill_registry.get("research")
    synthesis_skill = skill_registry.get("synthesis")

    assert research_skill is not None
    assert synthesis_skill is not None

    # Execute workflow
    research_input = SkillInput(query="artificial intelligence")
    research_result = await research_skill.execute(research_input)

    assert research_result.success is True

    synthesis_input = SkillInput(
        query="artificial intelligence",
        context={"results": research_result.data["results"]},
    )
    synthesis_result = await synthesis_skill.execute(synthesis_input)

    assert synthesis_result.success is True


@pytest.mark.asyncio
async def test_different_citation_styles():
    """Test workflow with different citation styles."""
    research_skill = ResearchSkill(use_mock=True)
    research_input = SkillInput(query="machine learning")
    research_result = await research_skill.execute(research_input)

    results = research_result.data["results"]

    # Test each citation style
    for style in ["apa", "mla", "chicago"]:
        citation_skill = CitationSkill(style=CitationStyle(style))
        citation_input = SkillInput(
            query="machine learning",
            context={"results": results},
            options={"style": style},
        )
        citation_result = await citation_skill.execute(citation_input)

        assert citation_result.success is True
        assert citation_result.data["style"] == style


@pytest.mark.asyncio
async def test_error_handling_workflow():
    """Test workflow error handling."""
    synthesis_skill = SynthesisSkill()

    # Try to synthesize with no results
    synthesis_input = SkillInput(
        query="test",
        context={"results": []},
    )
    synthesis_result = await synthesis_skill.execute(synthesis_input)

    assert synthesis_result.success is False
    assert synthesis_result.error is not None
