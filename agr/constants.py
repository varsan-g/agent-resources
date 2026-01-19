"""Centralized constants for the agr package - derived from ClaudeAdapter."""

from agr.adapters import AdapterRegistry

_adapter = AdapterRegistry.get_default()
_fmt = _adapter.format

# Tool directory name - derived from Claude adapter
TOOL_DIR_NAME = _fmt.config_dir  # ".claude"

# Subdirectory names - derived from adapter
SKILLS_SUBDIR = _fmt.skill_dir     # "skills"
COMMANDS_SUBDIR = _fmt.command_dir # "commands"
AGENTS_SUBDIR = _fmt.agent_dir     # "agents"
RULES_SUBDIR = _fmt.rule_dir       # "rules"
PACKAGES_SUBDIR = "packages"       # Not yet in adapter
