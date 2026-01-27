"""Tool configuration for AI coding tools.

All tool-specific paths and configuration are isolated in this module.
Supports Claude Code (flat naming) and Cursor (nested directories).
"""

from dataclasses import dataclass
from pathlib import Path

from agr.exceptions import AgrError


@dataclass(frozen=True)
class ToolConfig:
    """Configuration for an AI coding tool."""

    name: str
    config_dir: str  # e.g., ".claude"
    skills_subdir: str  # e.g., "skills"
    supports_nested: bool = False  # True for nested dir structure (Cursor)

    def get_skills_dir(self, repo_root: Path) -> Path:
        """Get the skills directory for this tool in a repo."""
        return repo_root / self.config_dir / self.skills_subdir

    def get_global_skills_dir(self) -> Path:
        """Get the global skills directory (in user home)."""
        return Path.home() / self.config_dir / self.skills_subdir


# Claude Code tool configuration (flat naming: maragudk--skills--bluesky)
CLAUDE = ToolConfig(
    name="claude",
    config_dir=".claude",
    skills_subdir="skills",
    supports_nested=False,
)

# Cursor tool configuration (nested dirs: maragudk/skills/bluesky/)
CURSOR = ToolConfig(
    name="cursor",
    config_dir=".cursor",
    skills_subdir="skills",
    supports_nested=True,
)

# Registry of all supported tools
TOOLS: dict[str, ToolConfig] = {
    "claude": CLAUDE,
    "cursor": CURSOR,
}

# Default tool names for new configurations
DEFAULT_TOOL_NAMES: list[str] = ["claude"]

# Default tool for all operations
DEFAULT_TOOL = CLAUDE


def get_tool(name: str) -> ToolConfig:
    """Get tool configuration by name.

    Args:
        name: Tool name (e.g., "claude", "cursor")

    Returns:
        ToolConfig for the specified tool

    Raises:
        AgrError: If tool name is not recognized
    """
    if name not in TOOLS:
        available = ", ".join(TOOLS.keys())
        raise AgrError(f"Unknown tool '{name}'. Available tools: {available}")
    return TOOLS[name]
