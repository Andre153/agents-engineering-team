"""File copying logic for engineering-team."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from .registry import build_registry
from .schema import AgentInfo, SkillInfo


def get_claude_dir(project_dir: Optional[Path] = None) -> Path:
    """Get the .claude directory path."""
    if project_dir is None:
        project_dir = Path.cwd()
    return project_dir / ".claude"


def ensure_claude_dirs(project_dir: Optional[Path] = None) -> Tuple[Path, Path]:
    """Ensure .claude/agents and .claude/skills directories exist."""
    claude_dir = get_claude_dir(project_dir)
    agents_dir = claude_dir / "agents"
    skills_dir = claude_dir / "skills"

    agents_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)

    return agents_dir, skills_dir


def copy_agent(agent: AgentInfo, project_dir: Optional[Path] = None) -> Path:
    """Copy an agent file to the project's .claude/agents directory."""
    agents_dir, _ = ensure_claude_dirs(project_dir)

    src_path = Path(agent.file_path)
    dest_path = agents_dir / src_path.name

    shutil.copy2(src_path, dest_path)
    return dest_path


def copy_skill(skill: SkillInfo, project_dir: Optional[Path] = None) -> Path:
    """Copy a skill directory to the project's .claude/skills directory."""
    _, skills_dir = ensure_claude_dirs(project_dir)

    src_dir = Path(skill.dir_path)
    dest_dir = skills_dir / skill.name

    # Remove existing skill directory if it exists
    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    # Copy SKILL.md
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_dir / "SKILL.md", dest_dir / "SKILL.md")

    # Copy references directory if it exists
    if skill.has_references:
        refs_src = src_dir / "references"
        refs_dest = dest_dir / "references"
        shutil.copytree(refs_src, refs_dest)

    # Copy assets directory if it exists
    if skill.has_assets:
        assets_src = src_dir / "assets"
        assets_dest = dest_dir / "assets"
        shutil.copytree(assets_src, assets_dest)

    return dest_dir


def copy_agents(agent_names: List[str], project_dir: Optional[Path] = None) -> List[Path]:
    """Copy multiple agents to the project."""
    registry = build_registry()
    copied = []

    for name in agent_names:
        agent = registry.get_agent(name)
        if agent:
            path = copy_agent(agent, project_dir)
            copied.append(path)

    return copied


def copy_skills(skill_names: List[str], project_dir: Optional[Path] = None) -> List[Path]:
    """Copy multiple skills to the project."""
    registry = build_registry()
    copied = []

    for name in skill_names:
        skill = registry.get_skill(name)
        if skill:
            path = copy_skill(skill, project_dir)
            copied.append(path)

    return copied


def sync_all(
    agent_names: List[str], skill_names: List[str], project_dir: Optional[Path] = None
) -> Tuple[List[Path], List[Path]]:
    """Sync all agents and skills to the project (re-copy everything)."""
    agents = copy_agents(agent_names, project_dir)
    skills = copy_skills(skill_names, project_dir)
    return agents, skills
