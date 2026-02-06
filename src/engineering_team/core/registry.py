"""Agent and skill discovery for engineering-team."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

from .schema import AgentInfo, Registry, SkillCategory, SkillInfo


# Category display names
CATEGORY_DISPLAY_NAMES = {
    "languages": "Languages",
    "frameworks": "Frameworks",
    "databases": "Databases",
    "design": "Design & Documentation",
    "cloud": "Cloud & Infrastructure",
    "product": "Product",
    "test-tools": "Test Tools",
}


def get_data_dir() -> Path:
    """Get the path to the bundled data directory."""
    return Path(__file__).parent.parent / "data"


def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}, content

    # Find the closing ---
    end_match = re.search(r"\n---\n", content[3:])
    if not end_match:
        return {}, content

    frontmatter_str = content[3 : end_match.start() + 3]
    body = content[end_match.end() + 3 :]

    try:
        frontmatter = yaml.safe_load(frontmatter_str)
        return frontmatter or {}, body
    except yaml.YAMLError:
        return {}, content


def discover_agents(data_dir: Optional[Path] = None) -> List[AgentInfo]:
    """Discover all available agents from the data directory."""
    if data_dir is None:
        data_dir = get_data_dir()

    agents_dir = data_dir / "agents"
    if not agents_dir.exists():
        return []

    agents = []
    for md_file in sorted(agents_dir.glob("*.md")):
        content = md_file.read_text()
        frontmatter, _ = parse_frontmatter(content)

        if "name" not in frontmatter:
            # Use filename as name if not specified
            frontmatter["name"] = md_file.stem

        agent = AgentInfo(
            name=frontmatter.get("name", md_file.stem),
            description=frontmatter.get("description", "No description available"),
            file_path=str(md_file),
            tools=frontmatter.get("tools"),
            model=frontmatter.get("model"),
            skills=frontmatter.get("skills", []),
        )
        agents.append(agent)

    return agents


def discover_skills(data_dir: Optional[Path] = None) -> List[SkillCategory]:
    """Discover all available skills organized by category."""
    if data_dir is None:
        data_dir = get_data_dir()

    skills_dir = data_dir / "skills"
    if not skills_dir.exists():
        return []

    categories = []

    # Iterate through category directories
    for category_dir in sorted(skills_dir.iterdir()):
        if not category_dir.is_dir():
            continue

        category_name = category_dir.name
        category = SkillCategory(
            name=category_name,
            display_name=CATEGORY_DISPLAY_NAMES.get(category_name, category_name.title()),
            skills=[],
        )

        # Find skills in this category
        for skill_dir in sorted(category_dir.iterdir()):
            if not skill_dir.is_dir():
                continue

            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            content = skill_md.read_text()
            frontmatter, _ = parse_frontmatter(content)

            skill = SkillInfo(
                name=frontmatter.get("name", skill_dir.name),
                description=frontmatter.get("description", "No description available"),
                category=category_name,
                dir_path=str(skill_dir),
                has_references=(skill_dir / "references").exists(),
                has_assets=(skill_dir / "assets").exists(),
            )
            category.skills.append(skill)

        if category.skills:
            categories.append(category)

    return categories


def build_registry(data_dir: Optional[Path] = None) -> Registry:
    """Build the complete registry of agents and skills."""
    return Registry(
        agents=discover_agents(data_dir),
        categories=discover_skills(data_dir),
    )


def resolve_skill_dependencies(
    registry: Registry, agent_names: List[str]
) -> Dict[str, List[str]]:
    """Map each required skill to the agents that need it."""
    deps: Dict[str, List[str]] = {}
    for name in agent_names:
        agent = registry.get_agent(name)
        if agent:
            for skill in agent.skills:
                deps.setdefault(skill, []).append(name)
    return deps
