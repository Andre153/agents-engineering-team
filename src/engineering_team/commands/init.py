"""Init command for engineering-team CLI."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ..core.config import config_exists, load_config, save_config
from ..core.copier import copy_agents, copy_skills
from ..core.registry import build_registry
from ..core.schema import ProjectConfig
from ..ui.prompts import (
    confirm_installation,
    confirm_reconfigure,
    interactive_skill_selection,
    select_agents,
)
from .. import __version__


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

    # Check for existing configuration
    if config_exists(project_dir):
        if not force:
            if not confirm_reconfigure():
                console.print("[yellow]Aborted.[/yellow]")
                raise typer.Exit(0)
        existing_config = load_config(project_dir)
    else:
        existing_config = None

    # Build registry of available agents and skills
    registry = build_registry()

    if not registry.agents and not registry.categories:
        console.print("[red]Error: No agents or skills found in the package.[/red]")
        raise typer.Exit(1)

    # Interactive agent selection
    preselected_agents = existing_config.agents if existing_config else None
    selected_agents = select_agents(registry.agents, preselected_agents)

    # Interactive skill selection (category-based)
    preselected_skills = existing_config.skills if existing_config else None
    selected_skills = interactive_skill_selection(registry, preselected_skills)

    # Confirm selections
    if not confirm_installation(selected_agents, selected_skills):
        console.print("[yellow]Aborted.[/yellow]")
        raise typer.Exit(0)

    # Create configuration
    config = ProjectConfig(
        version="1.0",
        agents=selected_agents,
        skills=selected_skills,
        installed_at=datetime.now(),
        cli_version=__version__,
    )

    # Save configuration
    config_path = save_config(config, project_dir)
    console.print(f"[green]Created {config_path}[/green]")

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

    console.print("\n[bold green]Done![/bold green]")
    console.print(
        "\nRun [cyan]engineering-team sync[/cyan] to update to the latest versions."
    )
