"""Unit tests for methodology skill."""

import pytest
from skillforge.skills.methodology import MethodologySkill
from skillforge.skills.base import SkillInput


@pytest.mark.asyncio
async def test_methodology_skill_execution():
    """Test basic methodology skill execution."""
    skill = MethodologySkill()
    skill_input = SkillInput(query="machine learning research")

    result = await skill.execute(skill_input)

    assert result.success is True
    assert "core_steps" in result.data
    assert "specific_methods" in result.data
    assert "best_practices" in result.data


@pytest.mark.asyncio
async def test_methodology_skill_quantitative():
    """Test methodology skill for quantitative research."""
    skill = MethodologySkill()
    skill_input = SkillInput(
        query="test research",
        options={"research_type": "quantitative"},
    )

    result = await skill.execute(skill_input)

    assert result.success is True
    assert result.data["research_type"] == "quantitative"
    # Check for quantitative-specific methods
    methods_text = " ".join(result.data["specific_methods"])
    assert "survey" in methods_text.lower() or "statistical" in methods_text.lower()


@pytest.mark.asyncio
async def test_methodology_skill_qualitative():
    """Test methodology skill for qualitative research."""
    skill = MethodologySkill()
    skill_input = SkillInput(
        query="test research",
        options={"research_type": "qualitative"},
    )

    result = await skill.execute(skill_input)

    assert result.success is True
    assert result.data["research_type"] == "qualitative"
    # Check for qualitative-specific methods
    methods_text = " ".join(result.data["specific_methods"])
    assert "interview" in methods_text.lower() or "qualitative" in methods_text.lower()


def test_methodology_skill_properties():
    """Test methodology skill properties."""
    skill = MethodologySkill()

    assert skill.name == "methodology"
    assert skill.description is not None
