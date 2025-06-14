# SPDX-License-Identifier: AGPL-3.0-only
"""FlowZo CLI main entry point."""

import asyncio
import json
import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from .session import SessionEngine

app = typer.Typer(
    name="flowzo",
    help="Programmable flow state companion",
    add_completion=False,
)
console = Console()


@app.command()
def start(
    duration: Annotated[int, typer.Option("--duration", "-d", help="Session duration in seconds")] = 5,
    json_output: Annotated[bool, typer.Option("--json", help="Output events as JSON")] = False,
) -> None:
    """Start a focus session using SessionEngine FSM."""
    engine = SessionEngine()
    
    if json_output:
        # Run session and output JSON events
        asyncio.run(_run_session_json(engine, duration))
    else:
        # Run session with rich UI
        asyncio.run(_run_session_ui(engine, duration))


async def _run_session_json(engine: SessionEngine, duration: int) -> None:
    """Run session and output JSON events to stdout."""
    await engine.start_session(duration, priming_duration=1)
    
    # Output all events as JSON
    print(engine.export_events_json())


async def _run_session_ui(engine: SessionEngine, duration: int) -> None:
    """Run session with rich UI progress display."""
    console.print("[bold green]Entering flow...[/bold green]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Focus session", total=duration + 4)  # +4 for priming+cooldown
        
        # Start session in background
        session_task = asyncio.create_task(engine.start_session(duration, priming_duration=1))
        
        # Update progress while session runs
        while not session_task.done():
            status = engine.get_status()
            progress.update(task, description=f"State: {status['state']}")
            progress.advance(task, 0.1)
            await asyncio.sleep(0.1)
        
        await session_task
    
    console.print("[bold blue]Session complete! 🎯[/bold blue]")
    console.print(f"Session ID: {engine.session_id}")
    console.print(f"Total events: {len(engine.events)}")


@app.command()
def next() -> None:
    """Show next task from integrations."""
    console.print("[yellow]Integration not yet implemented[/yellow]")
    console.print("Next: Implement GitHub/Linear integration")


if __name__ == "__main__":
    app() 