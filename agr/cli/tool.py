"""Tool management commands for agr.

Provides commands to manage which AI coding tools agr syncs resources to.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer

from agr.adapters import AdapterRegistry
from agr.adapters.detector import ToolDetector
from agr.config import AgrConfig, get_or_create_config

app = typer.Typer(
    name="tool",
    help="Manage target AI coding tools.",
)

# Rich console for output
from rich.console import Console
from rich.table import Table

console = Console()


@app.command("add")
def tool_add(
    tool_name: Annotated[
        str,
        typer.Argument(help="Name of the tool to add (e.g., claude, cursor)"),
    ],
) -> None:
    """Add a target tool to sync resources to.

    Validates the tool name, adds it to agr.toml, creates the tool's
    config directory if missing, and triggers a sync.

    Examples:
        agr tool add cursor
        agr tool add claude
    """
    # Validate tool name
    available_tools = AdapterRegistry.all_names()
    if tool_name not in available_tools:
        console.print(
            f"[red]Unknown tool '{tool_name}'. "
            f"Available tools: {', '.join(sorted(available_tools))}[/red]"
        )
        raise typer.Exit(1)

    # Load or create config
    config_path, config = get_or_create_config()

    # Check if already configured
    current_targets = config.tools.targets if config.tools else []
    if tool_name in current_targets:
        console.print(f"[yellow]Tool '{tool_name}' is already configured.[/yellow]")
        return

    # Add to config
    config.add_tool_target(tool_name)
    config.save(config_path)

    # Get adapter to check/create directory
    adapter = AdapterRegistry.get(tool_name)
    tool_dir = Path.cwd() / adapter.format.config_dir

    # Create directory if missing
    created_dir = False
    if not tool_dir.exists():
        tool_dir.mkdir(parents=True)
        created_dir = True

    console.print(f"[green]Added '{tool_name}' to target tools.[/green]")
    if created_dir:
        console.print(f"  Created directory: {adapter.format.config_dir}/")
    console.print(f"  Config updated: agr.toml")

    # Suggest running sync
    console.print()
    console.print("[dim]Run 'agr sync' to sync resources to all target tools.[/dim]")


@app.command("remove")
def tool_remove(
    tool_name: Annotated[
        str,
        typer.Argument(help="Name of the tool to remove"),
    ],
    cleanup: Annotated[
        bool,
        typer.Option(
            "--cleanup",
            help="Also remove the tool's config directory",
        ),
    ] = False,
) -> None:
    """Remove a target tool from agr.toml.

    Optionally removes the tool's config directory with --cleanup.

    Examples:
        agr tool remove cursor
        agr tool remove cursor --cleanup
    """
    # Load config
    config_path, config = get_or_create_config()

    # Check if configured
    current_targets = config.tools.targets if config.tools else []
    if tool_name not in current_targets:
        console.print(f"[yellow]Tool '{tool_name}' is not configured.[/yellow]")
        return

    # Remove from config
    config.remove_tool_target(tool_name)
    config.save(config_path)

    console.print(f"[green]Removed '{tool_name}' from target tools.[/green]")

    # Handle cleanup if requested
    if cleanup:
        try:
            adapter = AdapterRegistry.get(tool_name)
            tool_dir = Path.cwd() / adapter.format.config_dir
            if tool_dir.exists():
                import shutil

                shutil.rmtree(tool_dir)
                console.print(f"  Removed directory: {adapter.format.config_dir}/")
        except Exception as e:
            console.print(f"[yellow]Could not remove directory: {e}[/yellow]")


@app.command("list")
def tool_list(
    format_json: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output in JSON format",
        ),
    ] = False,
) -> None:
    """List available tools and their status.

    Shows all registered tools with indicators for:
    - Configured: Listed in agr.toml [tools].targets
    - Directory: Has local config directory (e.g., .cursor/)
    - CLI: Has CLI command available

    Examples:
        agr tool list
        agr tool list --json
    """
    # Load config
    config_path, config = get_or_create_config()
    configured_targets = config.tools.targets if config.tools else []

    # Detect tools
    detector = ToolDetector()
    detected = detector.detect_all()

    # Get all registered tools
    all_tools = AdapterRegistry.all_names()

    if format_json:
        import json

        tools_data = []
        for tool_name in sorted(all_tools):
            tool_info = next((t for t in detected if t.name == tool_name), None)
            tools_data.append(
                {
                    "name": tool_name,
                    "configured": tool_name in configured_targets,
                    "directory_exists": tool_info.config_dir is not None
                    if tool_info
                    else False,
                    "cli_available": tool_info.cli_available if tool_info else False,
                }
            )
        console.print(json.dumps(tools_data, indent=2))
        return

    # Create table
    table = Table(title="Available Tools")
    table.add_column("Tool", style="cyan")
    table.add_column("Configured", justify="center")
    table.add_column("Directory", justify="center")
    table.add_column("CLI", justify="center")

    for tool_name in sorted(all_tools):
        tool_info = next((t for t in detected if t.name == tool_name), None)

        is_configured = tool_name in configured_targets
        has_directory = tool_info.config_dir is not None if tool_info else False
        has_cli = tool_info.cli_available if tool_info else False

        configured_mark = "[green]\u2713[/green]" if is_configured else "[dim]-[/dim]"
        directory_mark = "[green]\u2713[/green]" if has_directory else "[dim]-[/dim]"
        cli_mark = "[green]\u2713[/green]" if has_cli else "[dim]-[/dim]"

        table.add_row(tool_name, configured_mark, directory_mark, cli_mark)

    console.print(table)

    # Show configured targets summary
    if configured_targets:
        console.print()
        console.print(f"[dim]Configured targets: {', '.join(configured_targets)}[/dim]")
    else:
        console.print()
        console.print("[dim]No tools configured. Use 'agr tool add <tool>' to add one.[/dim]")
