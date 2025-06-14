# SPDX-License-Identifier: AGPL-3.0-only
"""FlowZo CLI main entry point."""

import time
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(
    name="flowzo",
    help="Programmable flow state companion",
    add_completion=False,
)
console = Console()


@app.command()
def start(
    duration: Annotated[int, typer.Option("--duration", "-d", help="Session duration in seconds")] = 5,
) -> None:
    """Start a focus session."""
    console.print("[bold green]Entering flow...[/bold green]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Focus session active", total=duration)
        
        for _ in range(duration):
            time.sleep(1)
            progress.advance(task)
    
    console.print("[bold blue]Session complete! 🎯[/bold blue]")


@app.command()
def next() -> None:
    """Show next task from integrations."""
    console.print("[yellow]Integration not yet implemented[/yellow]")
    console.print("Next: Implement GitHub/Linear integration")


if __name__ == "__main__":
    app() 