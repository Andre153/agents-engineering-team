"""Sync command for engineering-team CLI."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ..core.copier import sync_all
from ..core.database import (
    db_exists,
    get_agents,
    get_or_create_project,
    get_skills,
    update_project_timestamp,
)


console = Console()


def sync_command(
    project_dir: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Project directory (defaults to current directory)",
    ),
) -> None:
    """Sync agents and skills to the latest versions from the CLI package."""
    if project_dir is None:
        project_dir = Path.cwd()

    # Check for existing database
    if not db_exists(project_dir):
        console.print(
            "[red]Error: No engineering-team.db found.[/red]\n"
            "Run [cyan]engineering-team init[/cyan] first."
        )
        raise typer.Exit(1)

    # Get project
    project_id = get_or_create_project(project_dir)

    # Load agents and skills from database
    agents = get_agents(project_id, project_dir)
    skills = get_skills(project_id, project_dir)

    if not agents and not skills:
        console.print("[yellow]No agents or skills configured. Nothing to sync.[/yellow]")
        raise typer.Exit(0)

    console.print("[bold]Syncing agents and skills...[/bold]\n")

    # Sync all files
    copied_agents, copied_skills = sync_all(agents, skills, project_dir)

    # Report results
    if copied_agents:
        console.print("[bold]Agents:[/bold]")
        for path in copied_agents:
            console.print(f"  [green]~[/green] {path.relative_to(project_dir)}")

    if copied_skills:
        console.print("\n[bold]Skills:[/bold]")
        for path in copied_skills:
            console.print(f"  [green]~[/green] {path.relative_to(project_dir)}")

    # Update timestamp
    update_project_timestamp(project_id, project_dir)

    console.print("\n[bold green]Sync complete![/bold green]")
