"""Multi-tool support utilities for agr CLI commands.

Provides helpers for resolving target adapters based on CLI flags,
config settings, and auto-detection.
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from rich.console import Console

from agr.adapters import AdapterRegistry, AdapterNotFoundError, ToolDetector
from agr.adapters.base import ToolAdapter

if TYPE_CHECKING:
    from agr.config import AgrConfig

console = Console()


class InvalidToolError(Exception):
    """Raised when a tool name is not valid/registered."""


def validate_tool_names(tool_names: list[str]) -> list[str]:
    """Validate that all tool names are registered adapters.

    Raises:
        InvalidToolError: If any tool name is not registered
    """
    if not tool_names:
        return tool_names

    available = AdapterRegistry.all_names()
    invalid = [name for name in tool_names if name not in available]

    if invalid:
        raise InvalidToolError(
            f"Unknown tool(s): {', '.join(sorted(invalid))}. "
            f"Available tools: {', '.join(sorted(available))}"
        )

    return tool_names


def _resolve_tool_names(
    config: "AgrConfig | None",
    tool_flags: list[str] | None,
    base_path: Path | None,
) -> list[str]:
    """Resolve tool names from flags, config, or auto-detection.

    Priority:
    1. CLI --tool flags
    2. Config [tools].targets
    3. Auto-detect or default to Claude
    """
    if tool_flags:
        return validate_tool_names(tool_flags)

    if config and config.tools and config.tools.targets:
        return validate_tool_names(config.tools.targets)

    detector = ToolDetector(base_path=base_path)
    return detector.get_target_tools(config)


def get_target_adapters(
    config: "AgrConfig | None" = None,
    tool_flags: list[str] | None = None,
    base_path: Path | None = None,
) -> list[ToolAdapter]:
    """Get the list of target adapters for operations.

    Resolution priority:
    1. CLI --tool flags (if provided)
    2. Config [tools].targets (if config provided and has targets)
    3. Auto-detect from environment (tools with local config dirs)
    4. Default to Claude

    Raises:
        InvalidToolError: If any specified tool name is invalid
    """
    tool_names = _resolve_tool_names(config, tool_flags, base_path)

    adapters = []
    for name in tool_names:
        try:
            adapters.append(AdapterRegistry.get(name))
        except AdapterNotFoundError as e:
            raise InvalidToolError(str(e)) from e

    return adapters


def get_tool_base_path(
    adapter: ToolAdapter,
    global_install: bool,
) -> Path:
    """Get the base path for a specific tool.

    Args:
        adapter: The tool adapter
        global_install: If True, return global config dir (~/.claude/)

    Returns:
        Path to the tool's base directory
    """
    if global_install:
        return adapter.format.global_config_dir
    return Path.cwd() / adapter.format.config_dir


def format_tool_summary(results: dict[str, int]) -> str:
    """Format a summary of multi-tool sync results.

    Example:
        >>> format_tool_summary({"claude": 3, "cursor": 2})
        "Summary: Synced to 2 tools"
    """
    tool_count = sum(1 for count in results.values() if count > 0)

    if tool_count == 0:
        return "No resources synced"
    if tool_count == 1:
        return "Synced to 1 tool"
    return f"Summary: Synced to {tool_count} tools"


def needs_interactive_selection(
    config: "AgrConfig | None",
    tool_flags: list[str] | None,
) -> bool:
    """Check if interactive tool selection is needed.

    Returns True only when all conditions are met:
    - No --tool flags provided
    - No tools configured in agr.toml
    - No tools detected via directories
    - Running in an interactive TTY
    """
    if tool_flags:
        return False

    if config and config.tools and config.tools.targets:
        return False

    if not sys.stdin.isatty():
        return False

    detector = ToolDetector()
    detected = detector.detect_all()
    return not any(t.config_dir is not None for t in detected)


def interactive_tool_selection(
    config: "AgrConfig",
    config_path: Path,
) -> list[str]:
    """Prompt user to select target tools interactively.

    Called when no tools are configured and none are detected via directories.

    Args:
        config: Current agr config
        config_path: Path to save updated config

    Returns:
        List of selected tool names
    """
    # Get all available tools
    available_tools = AdapterRegistry.all_names()
    detector = ToolDetector()
    detected = detector.detect_all()

    console.print()
    console.print("[yellow]No target tools configured.[/yellow]")
    console.print("Which tools would you like to sync resources to?")
    console.print()

    # Display options with detected status
    tool_info = []
    for i, tool_name in enumerate(sorted(available_tools), 1):
        tool_detection = next((t for t in detected if t.name == tool_name), None)
        has_dir = tool_detection.config_dir is not None if tool_detection else False
        has_cli = tool_detection.cli_available if tool_detection else False

        status_parts = []
        if has_dir:
            status_parts.append("directory exists")
        if has_cli:
            status_parts.append("CLI available")
        status = f" ({', '.join(status_parts)})" if status_parts else ""

        console.print(f"  {i}. {tool_name}{status}")
        tool_info.append(tool_name)

    console.print()

    # Get user input
    while True:
        try:
            selection = typer.prompt(
                "Enter selection (comma-separated numbers, e.g., 1,2)",
                default="1"
            )

            # Parse selection
            selected_indices = [int(s.strip()) for s in selection.split(",")]
            selected_tools = []

            for idx in selected_indices:
                if idx < 1 or idx > len(tool_info):
                    console.print(f"[red]Invalid selection: {idx}[/red]")
                    continue
                selected_tools.append(tool_info[idx - 1])

            if not selected_tools:
                console.print("[red]No valid tools selected. Please try again.[/red]")
                continue

            break

        except ValueError:
            console.print("[red]Invalid input. Please enter numbers separated by commas.[/red]")

    # Save selection to config
    for tool_name in selected_tools:
        config.add_tool_target(tool_name)
    config.save(config_path)

    console.print()
    console.print(f"[green]Saved to agr.toml: {', '.join(selected_tools)}[/green]")
    console.print()

    # Create directories for selected tools if they don't exist
    for tool_name in selected_tools:
        adapter = AdapterRegistry.get(tool_name)
        tool_dir = Path.cwd() / adapter.format.config_dir
        if not tool_dir.exists():
            tool_dir.mkdir(parents=True)
            console.print(f"[dim]Created directory: {adapter.format.config_dir}/[/dim]")

    return selected_tools


def get_target_adapters_with_persistence(
    config: "AgrConfig | None",
    config_path: Path | None,
    tool_flags: list[str] | None = None,
    base_path: Path | None = None,
    persist_auto_detected: bool = True,
) -> list[ToolAdapter]:
    """Get target adapters with optional persistence of auto-detected tools.

    This wraps get_target_adapters() with persistence logic:
    - tool_flags provided: NO persistence (intentional one-off)
    - config.tools.targets exists: NO persistence (already configured)
    - Tools auto-detected: YES, persist to agr.toml (if persist_auto_detected=True)

    Args:
        config: Current agr config (may be None)
        config_path: Path to agr.toml for saving (required if persist_auto_detected=True)
        tool_flags: Tool flags from CLI --tool options
        base_path: Base path for tool detection
        persist_auto_detected: Whether to persist auto-detected tools to config

    Returns:
        List of target tool adapters

    Raises:
        InvalidToolError: If any specified tool name is invalid
    """
    # Determine if we should persist
    should_persist = (
        persist_auto_detected
        and config_path is not None
        and not tool_flags  # Not an intentional one-off
        and not (config and config.tools and config.tools.targets)  # Not already configured
    )

    adapters = get_target_adapters(config=config, tool_flags=tool_flags, base_path=base_path)

    # Persist auto-detected tools if conditions are met
    if should_persist and adapters:
        from agr.config import AgrConfig

        # Create or load config
        if config is None:
            config = AgrConfig()

        # Add detected tools to config
        for adapter in adapters:
            config.add_tool_target(adapter.format.name)

        # Save config
        config.save(config_path)
        console.print(f"[dim]Saved target tools to agr.toml: {', '.join(a.format.name for a in adapters)}[/dim]")

    return adapters
