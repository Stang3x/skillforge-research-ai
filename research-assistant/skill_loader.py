"""
Skill Loader Module

Loads and manages SKILL.md files from the skills/ directory.
Parses skill metadata (frontmatter) and content.
Provides skill composition and invocation utilities.
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional
import yaml


@dataclass
class Skill:
    """Represents a single skill loaded from SKILL.md file."""
    
    name: str
    description: str
    content: str
    filepath: str
    
    def __repr__(self) -> str:
        return f"Skill(name='{self.name}', description='{self.description[:50]}...')"


class SkillLoader:
    """Loads and manages skills from SKILL.md files."""
    
    def __init__(self, skills_dir: str = "skills"):
        """
        Initialize skill loader.
        
        Args:
            skills_dir: Directory containing SKILL.md files
        """
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Skill] = {}
        self._load_skills()
    
    def _load_skills(self) -> None:
        """Load all SKILL.md files from skills directory."""
        if not self.skills_dir.exists():
            print(f"Warning: Skills directory '{self.skills_dir}' not found")
            return
        
        # Find all .md files in skills directory
        skill_files = list(self.skills_dir.glob("*.md"))
        
        for skill_file in skill_files:
            try:
                skill = self._parse_skill_file(skill_file)
                if skill:
                    self.skills[skill.name] = skill
                    print(f"[OK] Loaded skill: {skill.name}")
            except Exception as e:
                print(f"[ERROR] Loading {skill_file.name}: {e}")
    
    def _parse_skill_file(self, filepath: Path) -> Optional[Skill]:
        """
        Parse a SKILL.md file.
        
        Format:
        ---
        name: skill-name
        description: One-line description
        ---
        
        # Content below frontmatter
        """
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract frontmatter (YAML between --- markers)
        frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        
        if not frontmatter_match:
            raise ValueError(f"No frontmatter found in {filepath}")
        
        # Parse YAML frontmatter
        frontmatter_text = frontmatter_match.group(1)
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML frontmatter in {filepath}: {e}")
        
        # Extract metadata
        name = frontmatter.get("name")
        description = frontmatter.get("description")
        
        if not name:
            raise ValueError(f"Missing 'name' in frontmatter of {filepath}")
        if not description:
            raise ValueError(f"Missing 'description' in frontmatter of {filepath}")
        
        # Extract content (everything after frontmatter)
        content_start = frontmatter_match.end()
        skill_content = content[content_start:].strip()
        
        return Skill(
            name=name,
            description=description,
            content=skill_content,
            filepath=str(filepath)
        )
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name."""
        return self.skills.get(name)
    
    def get_all_skills(self) -> Dict[str, Skill]:
        """Get all loaded skills."""
        return self.skills
    
    def list_skills(self) -> List[str]:
        """Get list of all skill names."""
        return list(self.skills.keys())
    
    def get_skill_summary(self) -> str:
        """Get formatted summary of all loaded skills."""
        if not self.skills:
            return "No skills loaded"
        
        summary = "## Available Skills\n\n"
        for name, skill in self.skills.items():
            summary += f"- **{name}**: {skill.description}\n"
        
        return summary
    
    def build_skill_context(self, skill_names: Optional[List[str]] = None) -> str:
        """
        Build a context string for agent system prompt.
        
        Args:
            skill_names: List of specific skills to include (default: all)
        
        Returns:
            Formatted string with skill instructions for system prompt
        """
        if skill_names is None:
            skill_names = self.list_skills()
        
        context = "## Available Skills\n\n"
        context += "You have access to the following skills to enhance your research assistance:\n\n"
        
        for name in skill_names:
            skill = self.get_skill(name)
            if not skill:
                continue
            
            context += f"### {name.replace('-', ' ').title()}\n"
            context += f"{skill.description}\n\n"
        
        return context
    
    def build_full_skill_documentation(self, skill_names: Optional[List[str]] = None) -> str:
        """
        Build complete skill documentation for detailed instructions.
        
        Args:
            skill_names: List of specific skills to include (default: all)
        
        Returns:
            Full formatted documentation with skill content
        """
        if skill_names is None:
            skill_names = self.list_skills()
        
        docs = "# Integrated Skills Documentation\n\n"
        docs += f"This agent has access to {len(skill_names)} specialized skills:\n\n"
        
        for name in skill_names:
            skill = self.get_skill(name)
            if not skill:
                continue
            
            docs += f"## Skill: {name.replace('-', ' ').title()}\n"
            docs += f"{skill.content}\n\n"
            docs += "---\n\n"
        
        return docs
    
    def get_skill_composition_guide(self) -> str:
        """
        Get guide for composing skills together.
        
        Returns:
            Documentation on skill composition patterns
        """
        guide = """# Skill Composition Guide

## How Skills Work Together

Your research assistant integrates multiple skills to provide comprehensive research support:

### Skill Invocation Patterns

**Pattern 1: Sequential Composition**
When research flows through multiple skills:
1. User asks research question
2. Research Methodology skill guides planning and quality assessment
3. Source Evaluation skill assesses source credibility and bias
4. Citation Standards skill formats references
5. Agent provides complete research guidance

Example: Help me research AI ethics
  | Plan research scope (Methodology) 
  | Evaluate sources (Source Evaluation) 
  | Format citations (Citation Standards)

**Pattern 2: Parallel Composition**
Use multiple skills independently for different aspects:
- Question about research methodology -> Use Research Methodology skill
- Question about citations -> Use Citation Standards skill  
- Question about source quality -> Use Source Evaluation skill

**Pattern 3: Iterative Refinement**
Apply skills repeatedly for increasingly refined output:
1. Initial research plan (Methodology)
2. Source assessment (Source Evaluation)
3. Refinement of plan based on available sources
4. Final citation formatting (Citation Standards)

## When to Use Each Skill

### Research Methodology Skill
Use when user asks about:
- How to plan a research project
- What methodology to use
- How to assess research quality
- How to identify and mitigate bias
- How to follow academic standards (PRISMA, CONSORT, etc.)

### Citation Standards Skill
Use when user asks about:
- How to format citations (APA, MLA, Chicago, IEEE)
- How to build bibliographies
- How to manage sources
- How to avoid plagiarism
- Citation tool recommendations

### Source Evaluation Skill
Use when user asks about:
- Whether a source is credible
- How to detect bias in sources
- Whether a source is relevant
- How to rank sources by quality
- How to identify red flags in sources

## Best Practices

1. Combine skills for comprehensive answers - Don't just use one skill; chain them together
2. Reference specific skill sections - Point users to relevant examples and guidelines
3. Adapt to user expertise level - Use simpler guidance for novices, detailed frameworks for experts
4. Provide concrete examples - Every skill has examples; use them to illustrate guidance
5. Flag important guidelines - Highlight critical best practices from each skill
"""
        return guide


def initialize_skills(skills_dir: str = "skills") -> SkillLoader:
    """
    Initialize skill loader for use in agent.
    
    Args:
        skills_dir: Directory containing SKILL.md files
    
    Returns:
        Initialized SkillLoader instance
    """
    return SkillLoader(skills_dir=skills_dir)


if __name__ == "__main__":
    # Test skill loading
    loader = initialize_skills()
    
    print("=" * 60)
    print("Skill Loader Test")
    print("=" * 60)
    print(f"\nLoaded {len(loader.list_skills())} skills:")
    for skill_name in loader.list_skills():
        skill = loader.get_skill(skill_name)
        print(f"  - {skill.name}: {skill.description}")
    
    print("\n" + loader.get_skill_composition_guide())