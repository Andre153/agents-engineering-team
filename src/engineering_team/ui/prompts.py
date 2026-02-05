"""Interactive prompts for engineering-team using questionary."""

from __future__ import annotations

from typing import List, Optional, Set

import questionary
from questionary import Style

from ..core.schema import AgentInfo, Registry, SkillCategory, SkillInfo, StackItem


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


# =============================================================================
# Project Stack Prompts
# =============================================================================

COMMON_LANGUAGES = [
    "Python",
    "TypeScript",
    "JavaScript",
    "Go",
    "Rust",
    "Java",
    "Kotlin",
    "Swift",
    "C#",
    "Ruby",
    "PHP",
    "Dart",
]

COMMON_FRAMEWORKS = [
    "React",
    "Next.js",
    "Vue",
    "Angular",
    "Svelte",
    "Django",
    "FastAPI",
    "Flask",
    "Express",
    "NestJS",
    "Spring Boot",
    "Rails",
    "Laravel",
    "Flutter",
    ".NET",
]

COMMON_DATABASES = [
    "PostgreSQL",
    "MySQL",
    "SQLite",
    "MongoDB",
    "Redis",
    "Firestore",
    "DynamoDB",
    "Supabase",
]

COMMON_CLOUD = [
    "AWS",
    "GCP",
    "Azure",
    "Vercel",
    "Netlify",
    "Cloudflare",
    "DigitalOcean",
    "Firebase",
]


def select_stack_items(
    stack_type: str,
    options: List[str],
    preselected: Optional[List[str]] = None
) -> List[str]:
    """Select stack items from a list of common options."""
    choices = [
        questionary.Choice(title=opt, value=opt, checked=preselected and opt in preselected)
        for opt in options
    ]
    choices.append(questionary.Choice(title="(Other - add custom)", value="__OTHER__"))

    selected = questionary.checkbox(
        f"Select {stack_type}:",
        choices=choices,
        style=CUSTOM_STYLE,
        instruction="(Use arrow keys, <space> to select, <enter> to confirm)",
    ).ask()

    if selected is None:
        return []

    # Handle custom entry
    if "__OTHER__" in selected:
        selected.remove("__OTHER__")
        custom = questionary.text(
            f"Enter custom {stack_type} (comma-separated):",
            style=CUSTOM_STYLE,
        ).ask()
        if custom:
            selected.extend([c.strip() for c in custom.split(",") if c.strip()])

    return selected


def prompt_version(item_name: str) -> Optional[str]:
    """Prompt for a version number (optional)."""
    version = questionary.text(
        f"Version for {item_name} (press Enter to skip):",
        style=CUSTOM_STYLE,
    ).ask()
    return version if version else None


def select_project_stack(preselected: Optional[List[StackItem]] = None) -> List[StackItem]:
    """Interactive selection of project tech stack."""
    stack_items: List[StackItem] = []

    # Build preselected lookup
    preselected_by_type: dict[str, List[str]] = {
        "language": [],
        "framework": [],
        "database": [],
        "cloud": [],
    }
    if preselected:
        for item in preselected:
            preselected_by_type[item.stack_type].append(item.name)

    questionary.print("\n[Project Stack Configuration]", style="bold")
    questionary.print("Select the technologies used in your project.\n", style="fg:gray")

    # Languages
    languages = select_stack_items("languages", COMMON_LANGUAGES, preselected_by_type["language"])
    for lang in languages:
        version = prompt_version(lang)
        stack_items.append(StackItem(stack_type="language", name=lang, version=version))

    # Frameworks
    frameworks = select_stack_items("frameworks", COMMON_FRAMEWORKS, preselected_by_type["framework"])
    for fw in frameworks:
        version = prompt_version(fw)
        stack_items.append(StackItem(stack_type="framework", name=fw, version=version))

    # Databases
    databases = select_stack_items("databases", COMMON_DATABASES, preselected_by_type["database"])
    for db in databases:
        version = prompt_version(db)
        stack_items.append(StackItem(stack_type="database", name=db, version=version))

    # Cloud providers
    cloud = select_stack_items("cloud providers", COMMON_CLOUD, preselected_by_type["cloud"])
    for provider in cloud:
        stack_items.append(StackItem(stack_type="cloud", name=provider))

    return stack_items


def display_stack_summary(stack_items: List[StackItem]) -> None:
    """Display a summary of selected stack items."""
    if not stack_items:
        questionary.print("  Stack: (none configured)", style="fg:gray")
        return

    by_type: dict[str, List[str]] = {
        "language": [],
        "framework": [],
        "database": [],
        "cloud": [],
    }

    for item in stack_items:
        display = item.name
        if item.version:
            display += f" ({item.version})"
        by_type[item.stack_type].append(display)

    labels = {
        "language": "Languages",
        "framework": "Frameworks",
        "database": "Databases",
        "cloud": "Cloud",
    }

    for stack_type, items in by_type.items():
        if items:
            questionary.print(f"  {labels[stack_type]}: {', '.join(items)}", style="fg:cyan")


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


def confirm_installation(
    agents: List[str],
    skills: List[str],
    stack_items: Optional[List[StackItem]] = None
) -> bool:
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

    if stack_items is not None:
        display_stack_summary(stack_items)

    questionary.print("")

    return questionary.confirm(
        "Proceed with installation?",
        default=True,
        style=CUSTOM_STYLE,
    ).ask()
