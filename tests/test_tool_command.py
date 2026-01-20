"""Tests for agr tool management commands."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from agr.cli.main import app
from agr.config import AgrConfig, ToolsConfig


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def git_project(tmp_path: Path, monkeypatch):
    """Set up a temporary git project directory."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".git").mkdir()
    return tmp_path


class TestToolAdd:
    """Tests for agr tool add command."""

    def test_add_valid_tool(self, runner, git_project):
        """Test adding a valid tool."""
        result = runner.invoke(app, ["tool", "add", "cursor"])

        assert result.exit_code == 0
        assert "Added 'cursor' to target tools" in result.output

        # Verify config was updated
        config = AgrConfig.load(git_project / "agr.toml")
        assert "cursor" in config.get_tool_targets()

        # Verify directory was created
        assert (git_project / ".cursor").is_dir()

    def test_add_tool_creates_directory(self, runner, git_project):
        """Test that adding a tool creates its directory."""
        # Directory shouldn't exist yet
        assert not (git_project / ".cursor").exists()

        result = runner.invoke(app, ["tool", "add", "cursor"])

        assert result.exit_code == 0
        assert "Created directory" in result.output
        assert (git_project / ".cursor").is_dir()

    def test_add_tool_directory_exists(self, runner, git_project):
        """Test adding a tool when directory already exists."""
        # Create directory first
        (git_project / ".cursor").mkdir()

        result = runner.invoke(app, ["tool", "add", "cursor"])

        assert result.exit_code == 0
        assert "Created directory" not in result.output

    def test_add_already_configured_tool(self, runner, git_project):
        """Test adding an already configured tool."""
        # First add
        runner.invoke(app, ["tool", "add", "cursor"])

        # Second add should warn
        result = runner.invoke(app, ["tool", "add", "cursor"])

        assert result.exit_code == 0
        assert "already configured" in result.output

    def test_add_invalid_tool(self, runner, git_project):
        """Test adding an invalid tool name."""
        result = runner.invoke(app, ["tool", "add", "invalid-tool"])

        assert result.exit_code == 1
        assert "Unknown tool" in result.output
        assert "Available tools" in result.output


class TestToolRemove:
    """Tests for agr tool remove command."""

    def test_remove_configured_tool(self, runner, git_project):
        """Test removing a configured tool."""
        # First add the tool
        runner.invoke(app, ["tool", "add", "cursor"])

        # Then remove it
        result = runner.invoke(app, ["tool", "remove", "cursor"])

        assert result.exit_code == 0
        assert "Removed 'cursor' from target tools" in result.output

        # Verify config was updated
        config = AgrConfig.load(git_project / "agr.toml")
        assert "cursor" not in config.get_tool_targets()

    def test_remove_unconfigured_tool(self, runner, git_project):
        """Test removing a tool that's not configured."""
        result = runner.invoke(app, ["tool", "remove", "cursor"])

        assert result.exit_code == 0
        assert "is not configured" in result.output

    def test_remove_with_cleanup(self, runner, git_project):
        """Test removing a tool with --cleanup flag."""
        # First add the tool
        runner.invoke(app, ["tool", "add", "cursor"])
        assert (git_project / ".cursor").is_dir()

        # Remove with cleanup
        result = runner.invoke(app, ["tool", "remove", "cursor", "--cleanup"])

        assert result.exit_code == 0
        assert "Removed directory" in result.output
        assert not (git_project / ".cursor").exists()

    def test_remove_without_cleanup(self, runner, git_project):
        """Test removing a tool without --cleanup preserves directory."""
        # First add the tool
        runner.invoke(app, ["tool", "add", "cursor"])

        # Remove without cleanup
        result = runner.invoke(app, ["tool", "remove", "cursor"])

        assert result.exit_code == 0
        # Directory should still exist
        assert (git_project / ".cursor").is_dir()


class TestToolList:
    """Tests for agr tool list command."""

    def test_list_tools(self, runner, git_project):
        """Test listing available tools."""
        result = runner.invoke(app, ["tool", "list"])

        assert result.exit_code == 0
        assert "claude" in result.output
        assert "cursor" in result.output

    def test_list_with_configured_tool(self, runner, git_project):
        """Test listing shows configured status."""
        # Add a tool
        runner.invoke(app, ["tool", "add", "cursor"])

        result = runner.invoke(app, ["tool", "list"])

        assert result.exit_code == 0
        assert "Configured targets: cursor" in result.output

    def test_list_json_format(self, runner, git_project):
        """Test listing in JSON format."""
        runner.invoke(app, ["tool", "add", "cursor"])

        result = runner.invoke(app, ["tool", "list", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)

        assert isinstance(data, list)
        assert len(data) >= 2  # At least claude and cursor

        # Find cursor in the list
        cursor_tool = next((t for t in data if t["name"] == "cursor"), None)
        assert cursor_tool is not None
        assert cursor_tool["configured"] is True
        assert cursor_tool["directory_exists"] is True

    def test_list_no_tools_configured(self, runner, git_project):
        """Test listing when no tools are configured."""
        result = runner.invoke(app, ["tool", "list"])

        assert result.exit_code == 0
        assert "No tools configured" in result.output


class TestConfigToolMethods:
    """Tests for AgrConfig tool target methods."""

    def test_add_tool_target_creates_tools_config(self):
        """Test that add_tool_target creates ToolsConfig if needed."""
        config = AgrConfig()
        assert config.tools is None

        config.add_tool_target("cursor")

        assert config.tools is not None
        assert "cursor" in config.tools.targets

    def test_add_tool_target_appends_to_existing(self):
        """Test adding to existing tool targets."""
        config = AgrConfig()
        config.tools = ToolsConfig(targets=["claude"])

        config.add_tool_target("cursor")

        assert "claude" in config.tools.targets
        assert "cursor" in config.tools.targets
        assert len(config.tools.targets) == 2

    def test_add_tool_target_no_duplicates(self):
        """Test that adding same tool twice doesn't duplicate."""
        config = AgrConfig()
        config.add_tool_target("cursor")
        config.add_tool_target("cursor")

        assert config.tools.targets.count("cursor") == 1

    def test_remove_tool_target(self):
        """Test removing a tool target."""
        config = AgrConfig()
        config.tools = ToolsConfig(targets=["claude", "cursor"])

        removed = config.remove_tool_target("cursor")

        assert removed is True
        assert "cursor" not in config.tools.targets
        assert "claude" in config.tools.targets

    def test_remove_tool_target_not_found(self):
        """Test removing a tool that's not configured."""
        config = AgrConfig()
        config.tools = ToolsConfig(targets=["claude"])

        removed = config.remove_tool_target("cursor")

        assert removed is False

    def test_remove_tool_target_no_tools_config(self):
        """Test removing when no tools config exists."""
        config = AgrConfig()

        removed = config.remove_tool_target("cursor")

        assert removed is False

    def test_get_tool_targets(self):
        """Test getting tool targets list."""
        config = AgrConfig()
        config.tools = ToolsConfig(targets=["claude", "cursor"])

        targets = config.get_tool_targets()

        assert targets == ["claude", "cursor"]

    def test_get_tool_targets_empty(self):
        """Test getting tool targets when not configured."""
        config = AgrConfig()

        targets = config.get_tool_targets()

        assert targets == []

    def test_save_and_load_preserves_tools(self, tmp_path: Path):
        """Test that save/load roundtrip preserves tools config."""
        config_path = tmp_path / "agr.toml"

        # Create config with tools
        config = AgrConfig()
        config.add_tool_target("claude")
        config.add_tool_target("cursor")
        config.save(config_path)

        # Load and verify
        loaded = AgrConfig.load(config_path)
        assert loaded.get_tool_targets() == ["claude", "cursor"]
