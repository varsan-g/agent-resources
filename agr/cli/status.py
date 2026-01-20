"""Status command for agr.

Provides a command to show the sync status of resources across target tools.
"""

from pathlib import Path
from typing import Annotated, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from agr.config import AgrConfig, find_config
from agr.cli.common import find_repo_root
from agr.cli.multi_tool import get_target_adapters, InvalidToolError
from agr.status import SyncStatus, compute_status_report

app = typer.Typer(
    name="status",
    help="Show sync status of resources.",
)

console = Console()


# Status indicators
STATUS_ICONS = {
    SyncStatus.SYNCED: "[green]\u2713[/green]",  # ✓
    SyncStatus.OUTDATED: "[yellow]~[/yellow]",  # ~
    SyncStatus.MISSING: "[red]\u2717[/red]",  # ✗
    SyncStatus.UNTRACKED: "[dim]?[/dim]",  # ?
}

STATUS_TEXT = {
    SyncStatus.SYNCED: "[green]synced[/green]",
    SyncStatus.OUTDATED: "[yellow]outdated[/yellow]",
    SyncStatus.MISSING: "[red]missing[/red]",
    SyncStatus.UNTRACKED: "[dim]untracked[/dim]",
}


@app.callback(invoke_without_command=True)
def status(
    ctx: typer.Context,
    tool: Annotated[
        Optional[List[str]],
        typer.Option(
            "--tool",
            help="Target tool(s) to check status for (e.g., --tool claude --tool cursor)",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Show detailed status including file paths",
        ),
    ] = False,
) -> None:
    """Show sync status of resources across target tools.

    Displays which resources from agr.toml are synced to each target tool,
    and identifies any untracked resources in tool directories.

    Examples:
        agr status
        agr status --tool claude
        agr status --verbose
    """
    # Find config
    config_path = find_config()
    if not config_path:
        console.print("[dim]No agr.toml found. Nothing to check.[/dim]")
        console.print("[dim]Use 'agr add' to add dependencies first.[/dim]")
        raise typer.Exit(0)

    config = AgrConfig.load(config_path)

    # Get target adapters
    try:
        adapters = get_target_adapters(config=config, tool_flags=tool)
    except InvalidToolError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    # Compute status
    repo_root = find_repo_root()
    report = compute_status_report(config, adapters, repo_root)

    # Print header
    tool_names = ", ".join(report.target_tools)
    console.print(f"[bold]Target tools:[/bold] {tool_names}")
    console.print()

    # Print resources section
    if report.resources:
        console.print("[bold]Resources:[/bold]")

        for resource in report.resources:
            # Resource identifier
            console.print(f"  [cyan]{resource.identifier}[/cyan]")

            # Status for each tool
            for ts in resource.tool_statuses:
                icon = STATUS_ICONS.get(ts.status, "?")
                status_text = STATUS_TEXT.get(ts.status, str(ts.status.value))

                if verbose and ts.path:
                    console.print(f"    {ts.tool_name:<10} {icon} {status_text} ({ts.path})")
                else:
                    console.print(f"    {ts.tool_name:<10} {icon} {status_text}")

                if ts.message and verbose:
                    console.print(f"               [dim]{ts.message}[/dim]")

            console.print()
    else:
        console.print("[dim]No resources in agr.toml[/dim]")
        console.print()

    # Print untracked resources section
    if report.untracked:
        console.print("[bold]Untracked resources (not in agr.toml):[/bold]")

        # Group by tool
        by_tool: dict[str, list] = {}
        for resource in report.untracked:
            by_tool.setdefault(resource.tool_name, []).append(resource)

        for tool_name, resources in sorted(by_tool.items()):
            names = ", ".join(r.name for r in resources)
            console.print(f"  {tool_name}: [dim]{names}[/dim]")

        console.print()
        console.print("[dim]Use 'agr add <path>' to manage, or remove manually.[/dim]")
        console.print()

    # Print summary
    if report.all_synced:
        console.print("[green]\u2713 All resources synced[/green]")
    else:
        if report.missing_count > 0:
            console.print(f"[yellow]{report.missing_count} resource(s) missing. Run 'agr sync' to install.[/yellow]")
        if report.untracked:
            console.print(f"[dim]{len(report.untracked)} untracked resource(s)[/dim]")
