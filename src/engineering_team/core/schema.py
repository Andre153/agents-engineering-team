"""Pydantic models for engineering-team configuration."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class AgentInfo(BaseModel):
    """Information about an agent parsed from its markdown file."""

    name: str
    description: str
    file_path: str
    tools: Optional[str] = None
    model: Optional[str] = None
    skills: List[str] = Field(default_factory=list)


class SkillInfo(BaseModel):
    """Information about a skill parsed from its SKILL.md file."""

    name: str
    description: str
    category: str
    dir_path: str
    has_references: bool = False
    has_assets: bool = False


class SkillCategory(BaseModel):
    """A category of skills."""

    name: str
    display_name: str
    skills: List[SkillInfo] = Field(default_factory=list)


class Registry(BaseModel):
    """Registry of all available agents and skills."""

    agents: List[AgentInfo] = Field(default_factory=list)
    categories: List[SkillCategory] = Field(default_factory=list)

    def get_agent(self, name: str) -> Optional[AgentInfo]:
        """Get an agent by name."""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None

    def get_skill(self, name: str) -> Optional[SkillInfo]:
        """Get a skill by name."""
        for category in self.categories:
            for skill in category.skills:
                if skill.name == name:
                    return skill
        return None

    def get_all_skills(self) -> List[SkillInfo]:
        """Get all skills across all categories."""
        skills = []
        for category in self.categories:
            skills.extend(category.skills)
        return skills
