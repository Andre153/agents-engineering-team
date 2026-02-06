"""Main CLI entry point for engineering-team."""

import typer
from rich.console import Console

from . import __version__
from .commands.init import init_command
from .commands.list import list_command
from .commands.status import status_command
from .commands.sync import sync_command


app = typer.Typer(
    name="engineering-team",
    help="Configure Claude Code agents and skills for your projects.",
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"engineering-team version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Engineering Team CLI - Configure Claude Code agents and skills."""
    pass


app.command(name="init")(init_command)
app.command(name="sync")(sync_command)
app.command(name="list")(list_command)
app.command(name="status")(status_command)


if __name__ == "__main__":
    app()
