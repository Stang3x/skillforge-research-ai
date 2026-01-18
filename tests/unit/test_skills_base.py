"""Unit tests for the skills system."""

import pytest
from skillforge.skills.base import Skill, SkillInput, SkillOutput, SkillRegistry


class MockSkill(Skill):
    """Mock skill for testing."""

    async def execute(self, skill_input: SkillInput) -> SkillOutput:
        return SkillOutput(
            success=True,
            data={"query": skill_input.query},
            metadata={"skill": self.name},
        )


def test_skill_input_creation():
    """Test creating a skill input."""
    skill_input = SkillInput(
        query="test query",
        context={"key": "value"},
        options={"option": "value"},
    )

    assert skill_input.query == "test query"
    assert skill_input.context == {"key": "value"}
    assert skill_input.options == {"option": "value"}


def test_skill_output_creation():
    """Test creating a skill output."""
    skill_output = SkillOutput(
        success=True,
        data={"result": "test"},
        error=None,
        metadata={"info": "test"},
    )

    assert skill_output.success is True
    assert skill_output.data == {"result": "test"}
    assert skill_output.error is None
    assert skill_output.metadata == {"info": "test"}


@pytest.mark.asyncio
async def test_mock_skill_execution():
    """Test executing a mock skill."""
    skill = MockSkill(name="test", description="Test skill")
    skill_input = SkillInput(query="test query")

    result = await skill.execute(skill_input)

    assert result.success is True
    assert result.data["query"] == "test query"
    assert result.metadata["skill"] == "test"


def test_skill_registry_register():
    """Test registering a skill."""
    registry = SkillRegistry()
    skill = MockSkill(name="test", description="Test skill")

    registry.register(skill)

    assert "test" in registry.list_skills()
    assert registry.get("test") == skill


def test_skill_registry_get():
    """Test getting a skill from registry."""
    registry = SkillRegistry()
    skill = MockSkill(name="test", description="Test skill")
    registry.register(skill)

    retrieved_skill = registry.get("test")

    assert retrieved_skill is not None
    assert retrieved_skill.name == "test"


def test_skill_registry_get_nonexistent():
    """Test getting a non-existent skill."""
    registry = SkillRegistry()

    retrieved_skill = registry.get("nonexistent")

    assert retrieved_skill is None


def test_skill_registry_list_skills():
    """Test listing all skills."""
    registry = SkillRegistry()
    skill1 = MockSkill(name="test1", description="Test skill 1")
    skill2 = MockSkill(name="test2", description="Test skill 2")

    registry.register(skill1)
    registry.register(skill2)

    skills = registry.list_skills()

    assert len(skills) == 2
    assert "test1" in skills
    assert "test2" in skills


def test_skill_registry_get_all():
    """Test getting all skills."""
    registry = SkillRegistry()
    skill1 = MockSkill(name="test1", description="Test skill 1")
    skill2 = MockSkill(name="test2", description="Test skill 2")

    registry.register(skill1)
    registry.register(skill2)

    all_skills = registry.get_all()

    assert len(all_skills) == 2
    assert all_skills["test1"] == skill1
    assert all_skills["test2"] == skill2
