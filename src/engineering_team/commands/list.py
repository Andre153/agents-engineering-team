"""List command for engineering-team CLI."""

import json
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..core.registry import build_registry


console = Console()


def list_command(
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output in JSON format",
    ),
    agents_only: bool = typer.Option(
        False,
        "--agents",
        "-a",
        help="Show only agents",
    ),
    skills_only: bool = typer.Option(
        False,
        "--skills",
        "-s",
        help="Show only skills",
    ),
) -> None:
    """List available agents and skills."""
    registry = build_registry()

    if json_output:
        _output_json(registry, agents_only, skills_only)
    else:
        _output_tables(registry, agents_only, skills_only)


def _output_json(registry, agents_only: bool, skills_only: bool) -> None:
    """Output registry as JSON."""
    data = {}

    if not skills_only:
        data["agents"] = [
            {
                "name": agent.name,
                "description": agent.description,
                "model": agent.model,
                "tools": agent.tools,
                "skills": agent.skills,
            }
            for agent in registry.agents
        ]

    if not agents_only:
        data["skills"] = {}
        for category in registry.categories:
            data["skills"][category.name] = [
                {
                    "name": skill.name,
                    "description": skill.description,
                    "hasReferences": skill.has_references,
                    "hasAssets": skill.has_assets,
                }
                for skill in category.skills
            ]

    console.print(json.dumps(data, indent=2))


def _output_tables(registry, agents_only: bool, skills_only: bool) -> None:
    """Output registry as formatted tables."""
    if not skills_only and registry.agents:
        _print_agents_table(registry.agents)

    if not agents_only and registry.categories:
        if not skills_only and registry.agents:
            console.print()  # Spacing between tables
        _print_skills_tables(registry.categories)


def _print_agents_table(agents) -> None:
    """Print agents as a table."""
    table = Table(title="Available Agents", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Description")
    table.add_column("Model", style="yellow")

    for agent in agents:
        # Truncate description
        desc = agent.description
        if len(desc) > 60:
            desc = desc[:57] + "..."

        table.add_row(
            agent.name,
            desc,
            agent.model or "-",
        )

    console.print(table)


def _print_skills_tables(categories) -> None:
    """Print skills organized by category."""
    for category in categories:
        table = Table(
            title=f"Skills: {category.display_name}",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Name", style="green")
        table.add_column("Description")
        table.add_column("Refs", justify="center")
        table.add_column("Assets", justify="center")

        for skill in category.skills:
            # Truncate description
            desc = skill.description
            if len(desc) > 50:
                desc = desc[:47] + "..."

            table.add_row(
                skill.name,
                desc,
                "[green]Yes[/green]" if skill.has_references else "-",
                "[green]Yes[/green]" if skill.has_assets else "-",
            )

        console.print(table)
        console.print()  # Spacing between category tables
