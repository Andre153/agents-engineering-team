"""Status command for engineering-team CLI."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..core.database import db_exists, get_agents, get_project, get_skills
from ..core.registry import build_registry


console = Console()


def status_command(
    project_dir: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Project directory (defaults to current directory)",
    ),
) -> None:
    """Show currently installed agents and skills for a project."""
    if project_dir is None:
        project_dir = Path.cwd()

    if not db_exists(project_dir):
        console.print("[yellow]No engineering-team configuration found.[/yellow]")
        console.print("Run [cyan]engineering-team init[/cyan] to configure.")
        raise typer.Exit(1)

    project = get_project(project_dir)
    if not project:
        console.print("[red]Error: Could not read project configuration.[/red]")
        raise typer.Exit(1)

    project_id = project["id"]
    agents = get_agents(project_id, project_dir)
    skills = get_skills(project_id, project_dir)

    # Get registry for descriptions
    registry = build_registry()

    console.print(f"\n[bold]Project:[/bold] {project_dir.name}")
    console.print(f"[dim]Path: {project_dir}[/dim]\n")

    # Agents table
    if agents:
        _print_agents_table(agents, registry)
    else:
        console.print("[dim]No agents installed.[/dim]\n")

    # Skills table
    if skills:
        _print_skills_table(skills, registry)
    else:
        console.print("[dim]No skills installed.[/dim]")


def _print_agents_table(agent_names: list[str], registry) -> None:
    """Print installed agents as a table."""
    table = Table(title="Installed Agents", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Description")
    table.add_column("Model", style="yellow")

    for name in sorted(agent_names):
        agent = registry.get_agent(name)
        if agent:
            desc = agent.description
            if len(desc) > 60:
                desc = desc[:57] + "..."
            table.add_row(name, desc, agent.model or "-")
        else:
            table.add_row(name, "[dim]Not found in registry[/dim]", "-")

    console.print(table)
    console.print()


def _print_skills_table(skill_names: list[str], registry) -> None:
    """Print installed skills as a table."""
    table = Table(title="Installed Skills", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Category", style="magenta")
    table.add_column("Description")

    for name in sorted(skill_names):
        skill = registry.get_skill(name)
        if skill:
            desc = skill.description
            if len(desc) > 50:
                desc = desc[:47] + "..."
            table.add_row(name, skill.category, desc)
        else:
            table.add_row(name, "-", "[dim]Not found in registry[/dim]")

    console.print(table)
