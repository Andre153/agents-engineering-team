"""Sync command for engineering-team CLI."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ..core.config import config_exists, load_config, save_config
from ..core.copier import sync_all
from .. import __version__


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

    # Check for existing configuration
    if not config_exists(project_dir):
        console.print(
            "[red]Error: No engineering-team.json found.[/red]\n"
            "Run [cyan]engineering-team init[/cyan] first."
        )
        raise typer.Exit(1)

    # Load configuration
    config = load_config(project_dir)
    if config is None:
        console.print("[red]Error: Could not load configuration.[/red]")
        raise typer.Exit(1)

    if not config.agents and not config.skills:
        console.print("[yellow]No agents or skills configured. Nothing to sync.[/yellow]")
        raise typer.Exit(0)

    console.print("[bold]Syncing agents and skills...[/bold]\n")

    # Sync all files
    copied_agents, copied_skills = sync_all(
        config.agents, config.skills, project_dir
    )

    # Report results
    if copied_agents:
        console.print("[bold]Agents:[/bold]")
        for path in copied_agents:
            console.print(f"  [green]~[/green] {path.relative_to(project_dir)}")

    if copied_skills:
        console.print("\n[bold]Skills:[/bold]")
        for path in copied_skills:
            console.print(f"  [green]~[/green] {path.relative_to(project_dir)}")

    # Update timestamp and CLI version
    config.installed_at = datetime.now()
    config.cli_version = __version__
    save_config(config, project_dir)

    console.print("\n[bold green]Sync complete![/bold green]")
