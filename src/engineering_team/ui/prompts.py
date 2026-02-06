"""Interactive prompts for engineering-team using questionary."""

from __future__ import annotations

from typing import Dict, List, Optional

import questionary
from questionary import Choice, Separator, Style

from ..core.schema import AgentInfo, Registry


# Custom style for prompts
CUSTOM_STYLE = Style(
    [
        ("qmark", "fg:cyan bold"),
        ("question", "bold"),
        ("answer", "fg:cyan"),
        ("pointer", "fg:cyan bold"),
        ("highlighted", "fg:cyan bold"),
        ("selected", "fg:green"),
        ("separator", "fg:gray"),
        ("instruction", "fg:gray"),
    ]
)


def confirm_reconfigure() -> bool:
    """Ask user if they want to reconfigure existing installation."""
    return questionary.confirm(
        "engineering-team.db already exists. Do you want to reconfigure?",
        default=False,
        style=CUSTOM_STYLE,
    ).ask()


def _group_agents(agents: List[AgentInfo]) -> Dict[str, List[AgentInfo]]:
    """Group agents into Backend / Mobile / General buckets."""
    groups: Dict[str, List[AgentInfo]] = {
        "Backend": [],
        "Mobile": [],
        "General": [],
    }
    for agent in agents:
        name_lower = agent.name.lower()
        if "backend" in name_lower:
            groups["Backend"].append(agent)
        elif "mobile" in name_lower:
            groups["Mobile"].append(agent)
        else:
            groups["General"].append(agent)
    return groups


def select_agents(
    agents: List[AgentInfo], preselected: Optional[List[str]] = None
) -> List[str]:
    """Display grouped multi-select prompt for agents with skill dependency hints."""
    if not agents:
        return []

    groups = _group_agents(agents)
    choices: list = []

    for group_name, group_agents in groups.items():
        if not group_agents:
            continue
        choices.append(Separator(f"── {group_name} ──"))
        for agent in group_agents:
            desc = agent.description
            if len(desc) > 50:
                desc = desc[:47] + "..."
            label = f"{agent.name:<28} {desc}"
            if agent.skills:
                label += f"   needs: {', '.join(agent.skills)}"
            choices.append(
                Choice(
                    title=label,
                    value=agent.name,
                    checked=preselected and agent.name in preselected,
                )
            )

    selected = questionary.checkbox(
        "Select agents to install:",
        choices=choices,
        style=CUSTOM_STYLE,
        instruction="(Use arrow keys to move, <space> to select, <enter> to confirm)",
    ).ask()

    return selected or []


def select_skills_flat(
    registry: Registry,
    required_map: Dict[str, List[str]],
    preselected: Optional[List[str]] = None,
) -> List[str]:
    """Display a single flat skill list with required skills pre-checked."""
    all_skills = registry.get_all_skills()
    if not all_skills:
        return []

    preselected_set = set(preselected or [])
    required_names = set(required_map.keys())

    # Split into required vs additional
    required_skills = [s for s in all_skills if s.name in required_names]
    additional_skills = [s for s in all_skills if s.name not in required_names]

    choices: list = []

    if required_skills:
        choices.append(Separator("── Required by selected agents ──"))
        for skill in required_skills:
            desc = skill.description
            if len(desc) > 45:
                desc = desc[:42] + "..."
            category_tag = _category_tag(skill.category)
            choices.append(
                Choice(
                    title=f"{skill.name:<24} {desc}   {category_tag}",
                    value=skill.name,
                    checked=True,
                )
            )

    if additional_skills:
        choices.append(Separator("── Additional skills ──"))
        for skill in additional_skills:
            desc = skill.description
            if len(desc) > 45:
                desc = desc[:42] + "..."
            category_tag = _category_tag(skill.category)
            choices.append(
                Choice(
                    title=f"{skill.name:<24} {desc}   {category_tag}",
                    value=skill.name,
                    checked=skill.name in preselected_set and skill.name not in required_names,
                )
            )

    selected = questionary.checkbox(
        "Select additional skills:",
        choices=choices,
        style=CUSTOM_STYLE,
        instruction="(Required skills are pre-selected. Press <enter> to confirm)",
    ).ask()

    return selected or []


def _category_tag(category: str) -> str:
    """Return a display tag for a skill category."""
    tags = {
        "languages": "[Languages]",
        "frameworks": "[Frameworks]",
        "databases": "[Databases]",
        "design": "[Design]",
        "cloud": "[Cloud]",
        "product": "[Product]",
        "test-tools": "[Test Tools]",
    }
    return tags.get(category, f"[{category.title()}]")
