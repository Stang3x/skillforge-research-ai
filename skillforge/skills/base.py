"""Base classes for the modular skills system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SkillInput(BaseModel):
    """Input data for a skill."""

    query: str = Field(..., description="The research query or task")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    options: Dict[str, Any] = Field(default_factory=dict, description="Skill-specific options")


class SkillOutput(BaseModel):
    """Output data from a skill."""

    success: bool = Field(..., description="Whether the skill executed successfully")
    data: Any = Field(None, description="The output data")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Skill(ABC):
    """Base class for all skills in the system."""

    def __init__(self, name: str, description: str):
        """
        Initialize a skill.

        Args:
            name: The unique name of the skill
            description: A human-readable description of what the skill does
        """
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, skill_input: SkillInput) -> SkillOutput:
        """
        Execute the skill with the given input.

        Args:
            skill_input: The input data for the skill

        Returns:
            SkillOutput: The result of executing the skill
        """
        pass

    def __repr__(self) -> str:
        return f"<Skill: {self.name}>"


class SkillRegistry:
    """Registry for managing available skills."""

    def __init__(self):
        """Initialize an empty skill registry."""
        self._skills: Dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        """
        Register a skill in the registry.

        Args:
            skill: The skill to register
        """
        self._skills[skill.name] = skill

    def get(self, name: str) -> Optional[Skill]:
        """
        Get a skill by name.

        Args:
            name: The name of the skill

        Returns:
            The skill if found, None otherwise
        """
        return self._skills.get(name)

    def list_skills(self) -> List[str]:
        """
        List all registered skill names.

        Returns:
            List of skill names
        """
        return list(self._skills.keys())

    def get_all(self) -> Dict[str, Skill]:
        """
        Get all registered skills.

        Returns:
            Dictionary mapping skill names to skill instances
        """
        return self._skills.copy()


# Global skill registry instance
skill_registry = SkillRegistry()
