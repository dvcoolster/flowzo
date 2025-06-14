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
from flowzo_ledger.database import FlowLedger
from flowzo_integrations.github import GitHubIntegration
from flowzo_integrations.linear import LinearIntegration

app = typer.Typer(
    name="flowzo",
    help="Programmable flow state companion",
    add_completion=False,
)
console = Console()

# Auth subcommand
auth_app = typer.Typer(name="auth", help="Manage integration authentication")
app.add_typer(auth_app)


@app.command()
def start(
    duration: Annotated[int, typer.Option("--duration", "-d", help="Session duration in seconds")] = 5,
    json_output: Annotated[bool, typer.Option("--json", help="Output events as JSON")] = False,
    no_ledger: Annotated[bool, typer.Option("--no-ledger", help="Skip ledger storage")] = False,
) -> None:
    """Start a focus session using SessionEngine FSM."""
    # Initialize ledger unless disabled
    ledger = None if no_ledger else FlowLedger()
    engine = SessionEngine(ledger=ledger)
    
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
def next(
    source: Annotated[str, typer.Option("--source", "-s", help="Integration source (github/linear)")] = "github",
) -> None:
    """Show next task from integrations."""
    asyncio.run(_get_next_task(source))


async def _get_next_task(source: str) -> None:
    """Get next task from specified integration."""
    try:
        if source == "github":
            github = GitHubIntegration()
            issue = await github.get_next_issue()
            if issue:
                console.print(f"[bold green]Next GitHub Issue:[/bold green]")
                console.print(f"[bold]{issue.repository}#{issue.number}[/bold]: {issue.title}")
                console.print(f"URL: {issue.html_url}")
                if issue.labels:
                    console.print(f"Labels: {', '.join(issue.labels)}")
            else:
                console.print("[yellow]No assigned GitHub issues found[/yellow]")
        
        elif source == "linear":
            linear = LinearIntegration()
            issue = await linear.get_next_issue()
            if issue:
                console.print(f"[bold green]Next Linear Issue:[/bold green]")
                console.print(f"[bold]{issue.identifier}[/bold]: {issue.title}")
                console.print(f"Team: {issue.team} | State: {issue.state}")
                console.print(f"URL: {issue.url}")
                if issue.labels:
                    console.print(f"Labels: {', '.join(issue.labels)}")
            else:
                console.print("[yellow]No assigned Linear issues found[/yellow]")
        
        else:
            console.print(f"[red]Unknown source: {source}[/red]")
            console.print("Available sources: github, linear")
    
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Integration error: {e}[/red]")


@auth_app.command("github")
def auth_github(
    token: Annotated[str, typer.Option("--token", "-t", help="GitHub personal access token")],
    username: Annotated[str, typer.Option("--username", "-u", help="GitHub username")],
) -> None:
    """Store GitHub authentication token."""
    github = GitHubIntegration()
    github.store_token(token, username)
    console.print(f"[green]GitHub token stored for user: {username}[/green]")


@auth_app.command("linear")
def auth_linear(
    api_key: Annotated[str, typer.Option("--api-key", "-k", help="Linear API key")],
) -> None:
    """Store Linear authentication API key."""
    linear = LinearIntegration()
    linear.store_api_key(api_key)
    console.print("[green]Linear API key stored[/green]")


@auth_app.command("test")
def auth_test(
    source: Annotated[str, typer.Option("--source", "-s", help="Integration to test (github/linear)")] = "github",
) -> None:
    """Test integration authentication."""
    asyncio.run(_test_auth(source))


async def _test_auth(source: str) -> None:
    """Test authentication for specified integration."""
    try:
        if source == "github":
            github = GitHubIntegration()
            user_info = await github.test_connection()
            console.print(f"[green]GitHub connection successful![/green]")
            console.print(f"User: {user_info['login']} ({user_info['name']})")
        
        elif source == "linear":
            linear = LinearIntegration()
            user_info = await linear.test_connection()
            console.print(f"[green]Linear connection successful![/green]")
            console.print(f"User: {user_info['viewer']['name']} ({user_info['viewer']['email']})")
        
        else:
            console.print(f"[red]Unknown source: {source}[/red]")
    
    except Exception as e:
        console.print(f"[red]Authentication test failed: {e}[/red]")


if __name__ == "__main__":
    app() 