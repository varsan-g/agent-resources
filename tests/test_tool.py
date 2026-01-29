"""Tests for agr.tool module."""

from agr.tool import CLAUDE, CODEX, COPILOT, CURSOR, TOOLS, get_tool


class TestToolConfig:
    """Tests for ToolConfig dataclass."""

    def test_tool_config_has_cli_command(self):
        """ToolConfig includes cli_command field."""
        assert CLAUDE.cli_command == "claude"
        assert CURSOR.cli_command == "agent"
        assert CODEX.cli_command == "codex"
        assert COPILOT.cli_command == "copilot"

    def test_tool_config_has_cli_flags(self):
        """ToolConfig includes CLI flag fields."""
        # All tools have prompt flag
        assert CLAUDE.cli_prompt_flag == "-p"
        assert CURSOR.cli_prompt_flag == "-p"
        assert CODEX.cli_prompt_flag is None
        assert COPILOT.cli_prompt_flag == "-p"

        # Each tool has its own force flag
        assert CLAUDE.cli_force_flag == "--dangerously-skip-permissions"
        assert CURSOR.cli_force_flag == "--force"
        assert CODEX.cli_force_flag is None
        assert COPILOT.cli_force_flag == "--allow-all-tools"

        # All tools have continue flag
        assert CLAUDE.cli_continue_flag == "--continue"
        assert CURSOR.cli_continue_flag == "--continue"
        assert CODEX.cli_continue_flag is None
        assert COPILOT.cli_continue_flag == "--continue"

    def test_tool_config_has_install_hint(self):
        """ToolConfig includes install_hint field."""
        assert CLAUDE.install_hint is not None
        assert CURSOR.install_hint is not None
        assert CODEX.install_hint is not None
        assert COPILOT.install_hint is not None

    def test_all_tools_have_cli_config(self):
        """All registered tools have CLI configuration."""
        for name, tool_config in TOOLS.items():
            assert tool_config.cli_command is not None, f"{name} missing cli_command"
            if tool_config.cli_prompt_flag is not None:
                assert tool_config.cli_prompt_flag, f"{name} missing cli_prompt_flag"
            if tool_config.cli_force_flag is not None:
                assert tool_config.cli_force_flag, f"{name} missing cli_force_flag"
            if tool_config.cli_continue_flag is not None:
                assert tool_config.cli_continue_flag, (
                    f"{name} missing cli_continue_flag"
                )
            assert tool_config.install_hint is not None, f"{name} missing install_hint"


class TestGetTool:
    """Tests for get_tool function."""

    def test_get_tool_returns_correct_config(self):
        """get_tool returns the correct ToolConfig."""
        assert get_tool("claude") == CLAUDE
        assert get_tool("cursor") == CURSOR
        assert get_tool("codex") == CODEX
        assert get_tool("copilot") == COPILOT

    def test_get_tool_unknown_raises(self):
        """get_tool raises AgrError for unknown tool."""
        import pytest

        from agr.exceptions import AgrError

        with pytest.raises(AgrError, match="Unknown tool"):
            get_tool("unknown-tool")
