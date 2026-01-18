"""Unit tests for research skill."""

import pytest
from skillforge.skills.research import ResearchSkill
from skillforge.skills.base import SkillInput


@pytest.mark.asyncio
async def test_research_skill_execution():
    """Test basic research skill execution."""
    skill = ResearchSkill(use_mock=True)
    skill_input = SkillInput(query="machine learning")

    result = await skill.execute(skill_input)

    assert result.success is True
    assert "results" in result.data
    assert result.data["query"] == "machine learning"
    assert result.data["count"] > 0


@pytest.mark.asyncio
async def test_research_skill_max_results():
    """Test research skill respects max_results option."""
    skill = ResearchSkill(use_mock=True)
    skill_input = SkillInput(
        query="test query",
        options={"max_results": 5},
    )

    result = await skill.execute(skill_input)

    assert result.success is True
    assert result.data["count"] <= 5


@pytest.mark.asyncio
async def test_research_skill_no_academic():
    """Test research skill without academic sources."""
    skill = ResearchSkill(use_mock=True)
    skill_input = SkillInput(
        query="test query",
        options={"include_academic": False},
    )

    result = await skill.execute(skill_input)

    assert result.success is True
    # Should still have some results from web search
    assert result.data["count"] > 0


def test_research_skill_properties():
    """Test research skill properties."""
    skill = ResearchSkill(use_mock=True)

    assert skill.name == "research"
    assert skill.description is not None
    assert skill.use_mock is True
