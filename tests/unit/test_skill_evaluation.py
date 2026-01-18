"""Unit tests for evaluation skill."""

import pytest
from skillforge.skills.evaluation import EvaluationSkill
from skillforge.skills.base import SkillInput


@pytest.mark.asyncio
async def test_evaluation_skill_execution():
    """Test basic evaluation skill execution."""
    skill = EvaluationSkill()

    mock_results = [
        {
            "title": "Test Article 1",
            "url": "https://example.edu/1",
            "snippet": "Test",
            "source": "web",
        },
        {
            "title": "Test Article 2",
            "url": "https://example.com/2",
            "snippet": "Test",
            "source": "arxiv",
        },
    ]

    skill_input = SkillInput(
        query="test",
        context={"results": mock_results},
    )

    result = await skill.execute(skill_input)

    assert result.success is True
    assert "total_sources" in result.data
    assert "source_distribution" in result.data
    assert "average_credibility" in result.data
    assert "credibility_assessment" in result.data
    assert "recommendations" in result.data
    assert "potential_gaps" in result.data


@pytest.mark.asyncio
async def test_evaluation_skill_credibility_scoring():
    """Test that evaluation skill scores academic sources higher."""
    skill = EvaluationSkill()

    # Test with academic sources
    academic_results = [
        {"title": "Test", "url": "https://example.edu", "snippet": "Test", "source": "arxiv"},
        {"title": "Test", "url": "https://example.gov", "snippet": "Test", "source": "pubmed"},
    ]

    academic_input = SkillInput(query="test", context={"results": academic_results})
    academic_result = await skill.execute(academic_input)

    # Test with web sources
    web_results = [
        {"title": "Test", "url": "https://example.com", "snippet": "Test", "source": "web"},
        {"title": "Test", "url": "https://example.net", "snippet": "Test", "source": "web"},
    ]

    web_input = SkillInput(query="test", context={"results": web_results})
    web_result = await skill.execute(web_input)

    # Academic sources should have higher credibility
    assert academic_result.data["average_credibility"] > web_result.data["average_credibility"]


@pytest.mark.asyncio
async def test_evaluation_skill_no_results():
    """Test evaluation skill with no results."""
    skill = EvaluationSkill()
    skill_input = SkillInput(
        query="test",
        context={"results": []},
    )

    result = await skill.execute(skill_input)

    assert result.success is False
    assert result.error is not None


def test_evaluation_skill_properties():
    """Test evaluation skill properties."""
    skill = EvaluationSkill()

    assert skill.name == "evaluation"
    assert skill.description is not None
