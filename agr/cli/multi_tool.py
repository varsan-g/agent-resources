"""Multi-tool support utilities for agr CLI commands.

Provides helpers for resolving target adapters based on CLI flags,
config settings, and auto-detection.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from agr.adapters import AdapterRegistry, AdapterNotFoundError, ToolDetector
from agr.adapters.base import ToolAdapter

if TYPE_CHECKING:
    from agr.config import AgrConfig


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
