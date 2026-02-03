"""Interactive prompts for engineering-team using questionary."""

from __future__ import annotations

from typing import List, Optional, Set

import questionary
from questionary import Style

from ..core.schema import AgentInfo, Registry, SkillCategory, SkillInfo


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
        "engineering-team.json already exists. Do you want to reconfigure?",
        default=False,
        style=CUSTOM_STYLE,
    ).ask()


def select_agents(agents: List[AgentInfo], preselected: Optional[List[str]] = None) -> List[str]:
    """Display multi-select prompt for agents."""
    if not agents:
        return []

    choices = []
    for agent in agents:
        # Truncate description if too long
        desc = agent.description
        if len(desc) > 80:
            desc = desc[:77] + "..."

        choice = questionary.Choice(
            title=f"{agent.name} - {desc}",
            value=agent.name,
            checked=preselected and agent.name in preselected,
        )
        choices.append(choice)

    selected = questionary.checkbox(
        "Select agents to install:",
        choices=choices,
        style=CUSTOM_STYLE,
        instruction="(Use arrow keys to move, <space> to select, <enter> to confirm)",
    ).ask()

    return selected or []


DONE_SELECTING = "__DONE__"


def select_skill_category(categories: List[SkillCategory]) -> Optional[str]:
    """Display menu to select a skill category."""
    if not categories:
        return None

    choices = [
        questionary.Choice(
            title=f"{cat.display_name} ({len(cat.skills)} skills)",
            value=cat.name,
        )
        for cat in categories
    ]
    choices.append(questionary.Choice(title="Done selecting skills", value=DONE_SELECTING))

    return questionary.select(
        "Select a skill category:",
        choices=choices,
        style=CUSTOM_STYLE,
    ).ask()


def select_skills_in_category(
    category: SkillCategory, preselected: Optional[List[str]] = None
) -> List[str]:
    """Display multi-select prompt for skills in a category."""
    if not category.skills:
        return []

    choices = []
    for skill in category.skills:
        # Truncate description if too long
        desc = skill.description
        if len(desc) > 70:
            desc = desc[:67] + "..."

        choice = questionary.Choice(
            title=f"{skill.name} - {desc}",
            value=skill.name,
            checked=preselected and skill.name in preselected,
        )
        choices.append(choice)

    selected = questionary.checkbox(
        f"Select skills from {category.display_name}:",
        choices=choices,
        style=CUSTOM_STYLE,
        instruction="(Use arrow keys to move, <space> to select, <enter> to confirm)",
    ).ask()

    return selected or []


def interactive_skill_selection(
    registry: Registry, preselected: Optional[List[str]] = None
) -> List[str]:
    """Interactive category-based skill selection."""
    selected_skills: Set[str] = set(preselected or [])
    categories = registry.categories

    if not categories:
        return []

    while True:
        # Show current selection count
        if selected_skills:
            questionary.print(
                f"\nCurrently selected: {', '.join(sorted(selected_skills))}",
                style="fg:green",
            )

        category_name = select_skill_category(categories)

        if category_name is None or category_name == DONE_SELECTING:
            # User chose "Done" or cancelled
            break

        # Find the selected category
        category = next((c for c in categories if c.name == category_name), None)
        if category is None:
            continue

        # Let user select skills in this category
        new_selections = select_skills_in_category(
            category, preselected=list(selected_skills)
        )

        # Update selected skills (add newly selected, remove deselected from this category)
        category_skill_names = {s.name for s in category.skills}
        selected_skills -= category_skill_names  # Remove all from this category
        selected_skills.update(new_selections)  # Add back selected ones

    return list(selected_skills)


def confirm_installation(agents: List[str], skills: List[str]) -> bool:
    """Confirm the installation selections."""
    questionary.print("\nYou have selected:", style="bold")

    if agents:
        questionary.print(f"  Agents: {', '.join(agents)}", style="fg:cyan")
    else:
        questionary.print("  Agents: (none)", style="fg:gray")

    if skills:
        questionary.print(f"  Skills: {', '.join(skills)}", style="fg:cyan")
    else:
        questionary.print("  Skills: (none)", style="fg:gray")

    questionary.print("")

    return questionary.confirm(
        "Proceed with installation?",
        default=True,
        style=CUSTOM_STYLE,
    ).ask()
