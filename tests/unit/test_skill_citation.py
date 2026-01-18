"""Unit tests for citation skill."""

import pytest
from skillforge.skills.citation import CitationSkill
from skillforge.skills.base import SkillInput
from skillforge.citation import CitationStyle


@pytest.mark.asyncio
async def test_citation_skill_execution():
    """Test basic citation skill execution."""
    skill = CitationSkill(style=CitationStyle.APA)

    mock_results = [
        {
            "title": "Test Article 1",
            "url": "https://example.com/1",
            "snippet": "Test snippet",
        },
        {
            "title": "Test Article 2",
            "url": "https://example.com/2",
            "snippet": "Test snippet",
        },
    ]

    skill_input = SkillInput(
        query="test",
        context={"results": mock_results},
    )

    result = await skill.execute(skill_input)

    assert result.success is True
    assert "citations" in result.data
    assert "bibliography" in result.data
    assert result.data["count"] == 2


@pytest.mark.asyncio
async def test_citation_skill_different_styles():
    """Test citation skill with different citation styles."""
    for style in [CitationStyle.APA, CitationStyle.MLA, CitationStyle.CHICAGO]:
        skill = CitationSkill(style=style)

        mock_results = [
            {
                "title": "Test Article",
                "url": "https://example.com",
                "snippet": "Test",
            }
        ]

        skill_input = SkillInput(
            query="test",
            context={"results": mock_results},
            options={"style": style.value},
        )

        result = await skill.execute(skill_input)

        assert result.success is True
        assert result.data["style"] == style.value


@pytest.mark.asyncio
async def test_citation_skill_no_sources():
    """Test citation skill with no sources."""
    skill = CitationSkill()
    skill_input = SkillInput(
        query="test",
        context={"results": []},
    )

    result = await skill.execute(skill_input)

    assert result.success is False
    assert result.error is not None


def test_citation_skill_properties():
    """Test citation skill properties."""
    skill = CitationSkill(style=CitationStyle.APA)

    assert skill.name == "citation"
    assert skill.description is not None
