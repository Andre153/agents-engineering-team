"""Init command for engineering-team CLI."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ..core.copier import copy_agents, copy_skills
from ..core.database import (
    db_exists,
    get_agents,
    get_or_create_project,
    get_project,
    get_skills,
    init_database,
    set_agents,
    set_skills,
    update_project_timestamp,
)
from ..core.registry import build_registry, resolve_skill_dependencies
from ..ui.prompts import (
    confirm_reconfigure,
    select_agents,
    select_skills_flat,
)


console = Console()


def init_command(
    project_dir: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Project directory (defaults to current directory)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force reconfiguration without prompting",
    ),
) -> None:
    """Initialize engineering-team configuration for a project."""
    if project_dir is None:
        project_dir = Path.cwd()

    # Check for existing database
    existing_project = None
    if db_exists(project_dir):
        if not force:
            if not confirm_reconfigure():
                console.print("[yellow]Aborted.[/yellow]")
                raise typer.Exit(0)
        existing_project = get_project(project_dir)

    # Build registry of available agents and skills
    registry = build_registry()

    if not registry.agents and not registry.categories:
        console.print("[red]Error: No agents or skills found in the package.[/red]")
        raise typer.Exit(1)

    # Get preselected values from existing config
    preselected_agents = None
    preselected_skills = None

    if existing_project:
        project_id = existing_project["id"]
        preselected_agents = get_agents(project_id, project_dir)
        preselected_skills = get_skills(project_id, project_dir)

    # 1. Agent selection
    selected_agents = select_agents(registry.agents, preselected_agents)

    # 2. Resolve skill dependencies
    required_map = resolve_skill_dependencies(registry, selected_agents)
    if required_map:
        console.print("\n[bold]Auto-resolved skill dependencies:[/bold]")
        for skill, agents in required_map.items():
            console.print(
                f"  [green]+[/green] {skill} [dim](required by {', '.join(agents)})[/dim]"
            )
        console.print()

    # 3. Flat skill selection with required skills pre-checked
    selected_skills = select_skills_flat(registry, required_map, preselected_skills)

    # 4. Warn if user unchecked a required skill
    missing = set(required_map.keys()) - set(selected_skills)
    if missing:
        console.print(
            f"[yellow]Warning:[/yellow] {', '.join(sorted(missing))} "
            f"removed but required by selected agents"
        )

    # Initialize database if needed
    if not db_exists(project_dir):
        db_path = init_database(project_dir)
        console.print(f"[green]Created {db_path}[/green]")
    else:
        console.print(f"[green]Updated {project_dir / 'engineering-team.db'}[/green]")

    # Get or create project record
    project_id = get_or_create_project(project_dir)

    # Save selections to database
    set_agents(project_id, selected_agents, project_dir)
    set_skills(project_id, selected_skills, project_dir)
    update_project_timestamp(project_id, project_dir)

    # Copy files
    if selected_agents:
        console.print("\n[bold]Installing agents...[/bold]")
        copied_agents = copy_agents(selected_agents, project_dir)
        for path in copied_agents:
            console.print(f"  [green]+[/green] {path.relative_to(project_dir)}")

    if selected_skills:
        console.print("\n[bold]Installing skills...[/bold]")
        copied_skills = copy_skills(selected_skills, project_dir)
        for path in copied_skills:
            console.print(f"  [green]+[/green] {path.relative_to(project_dir)}")

    agent_count = len(selected_agents)
    skill_count = len(selected_skills)
    console.print(
        f"\n[bold green]Done![/bold green] "
        f"{agent_count} agent{'s' if agent_count != 1 else ''} "
        f"and {skill_count} skill{'s' if skill_count != 1 else ''} installed."
    )
