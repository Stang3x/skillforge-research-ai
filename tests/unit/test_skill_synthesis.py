"""Unit tests for synthesis skill."""

import pytest
from skillforge.skills.synthesis import SynthesisSkill
from skillforge.skills.base import SkillInput


@pytest.mark.asyncio
async def test_synthesis_skill_execution():
    """Test basic synthesis skill execution."""
    skill = SynthesisSkill()

    mock_results = [
        {
            "title": "Test Article 1",
            "url": "https://example.com/1",
            "snippet": "This is a test article about machine learning.",
            "source": "web",
        },
        {
            "title": "Test Article 2",
            "url": "https://example.com/2",
            "snippet": "Another article discussing deep learning concepts.",
            "source": "arxiv",
        },
    ]

    skill_input = SkillInput(
        query="machine learning",
        context={"results": mock_results},
    )

    result = await skill.execute(skill_input)

    assert result.success is True
    assert "summary" in result.data
    assert "key_findings" in result.data
    assert "themes" in result.data
    assert result.data["sources_analyzed"] == 2


@pytest.mark.asyncio
async def test_synthesis_skill_no_results():
    """Test synthesis skill with no results."""
    skill = SynthesisSkill()
    skill_input = SkillInput(
        query="test query",
        context={"results": []},
    )

    result = await skill.execute(skill_input)

    assert result.success is False
    assert result.error is not None


@pytest.mark.asyncio
async def test_synthesis_skill_themes():
    """Test that synthesis identifies themes correctly."""
    skill = SynthesisSkill()

    mock_results = [
        {"title": "Test 1", "snippet": "Text", "source": "web"},
        {"title": "Test 2", "snippet": "Text", "source": "arxiv"},
        {"title": "Test 3", "snippet": "Text", "source": "pubmed"},
    ]

    skill_input = SkillInput(
        query="test",
        context={"results": mock_results},
    )

    result = await skill.execute(skill_input)

    assert result.success is True
    assert len(result.data["themes"]) > 0


def test_synthesis_skill_properties():
    """Test synthesis skill properties."""
    skill = SynthesisSkill()

    assert skill.name == "synthesis"
    assert skill.description is not None
