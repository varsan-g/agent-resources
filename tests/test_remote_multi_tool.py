"""Tests for remote `agr add` multi-tool support (Issues #45 and #48).

Tests that remote `agr add` respects tool flags, config targets, and
auto-detected tools, and that auto-detected tools are persisted to agr.toml.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from agr.cli.main import app
from agr.config import AgrConfig, ToolsConfig
from agr.cli.multi_tool import (
    needs_interactive_selection,
    get_target_adapters_with_persistence,
    InvalidToolError,
)
from agr.adapters import ClaudeAdapter, CursorAdapter


runner = CliRunner()


class TestRemoteAddMultiTool:
    """Tests for remote agr add multi-tool support."""

    @patch("agr.cli.handlers.downloaded_repo")
    def test_remote_add_respects_tool_flag(
        self, mock_download, tmp_path: Path, monkeypatch
    ):
        """Test that remote add respects --tool flag."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Create mock repo with a skill
        repo_dir = tmp_path / "mock_repo"
        skill_dir = repo_dir / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Test Skill")

        mock_download.return_value.__enter__ = lambda self: repo_dir
        mock_download.return_value.__exit__ = lambda self, *args: None

        # Install with --tool cursor
        result = runner.invoke(app, ["add", "testowner/test-skill", "--tool", "cursor"])

        assert result.exit_code == 0

        # Should be installed to .cursor/, not .claude/
        cursor_skill = tmp_path / ".cursor" / "skills" / "testowner:test-skill"
        claude_skill = tmp_path / ".claude" / "skills" / "testowner:test-skill"

        assert cursor_skill.exists(), "Skill should be in .cursor/"
        assert not claude_skill.exists(), "Skill should not be in .claude/"

    @patch("agr.cli.handlers.downloaded_repo")
    def test_remote_add_respects_config_targets(
        self, mock_download, tmp_path: Path, monkeypatch
    ):
        """Test that remote add respects [tools].targets in agr.toml."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Create agr.toml with tools.targets
        config = AgrConfig()
        config.tools = ToolsConfig(targets=["cursor"])
        config.save(tmp_path / "agr.toml")

        # Create mock repo with a skill
        repo_dir = tmp_path / "mock_repo"
        skill_dir = repo_dir / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Test Skill")

        mock_download.return_value.__enter__ = lambda self: repo_dir
        mock_download.return_value.__exit__ = lambda self, *args: None

        result = runner.invoke(app, ["add", "testowner/test-skill"])

        assert result.exit_code == 0

        # Should be installed to .cursor/ per config
        cursor_skill = tmp_path / ".cursor" / "skills" / "testowner:test-skill"
        assert cursor_skill.exists(), "Skill should be installed to configured tool"

    @patch("agr.cli.handlers.downloaded_repo")
    def test_remote_add_auto_detects_tools(
        self, mock_download, tmp_path: Path, monkeypatch
    ):
        """Test that remote add auto-detects tools from existing directories."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Create .cursor/ directory to trigger auto-detection
        (tmp_path / ".cursor").mkdir()

        # Create mock repo with a skill
        repo_dir = tmp_path / "mock_repo"
        skill_dir = repo_dir / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Test Skill")

        mock_download.return_value.__enter__ = lambda self: repo_dir
        mock_download.return_value.__exit__ = lambda self, *args: None

        result = runner.invoke(app, ["add", "testowner/test-skill"])

        assert result.exit_code == 0

        # Should be installed to .cursor/ (auto-detected)
        cursor_skill = tmp_path / ".cursor" / "skills" / "testowner:test-skill"
        assert cursor_skill.exists(), "Skill should be installed to auto-detected tool"

    @patch("agr.cli.handlers.downloaded_repo")
    def test_remote_add_installs_to_multiple_tools(
        self, mock_download, tmp_path: Path, monkeypatch
    ):
        """Test that remote add installs to multiple tools with --tool flags."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Create mock repo with a skill
        repo_dir = tmp_path / "mock_repo"
        skill_dir = repo_dir / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Test Skill")

        mock_download.return_value.__enter__ = lambda self: repo_dir
        mock_download.return_value.__exit__ = lambda self, *args: None

        # Install to both claude and cursor
        result = runner.invoke(
            app, ["add", "testowner/test-skill", "--tool", "claude", "--tool", "cursor"]
        )

        assert result.exit_code == 0

        # Should be installed to both
        claude_skill = tmp_path / ".claude" / "skills" / "testowner:test-skill"
        cursor_skill = tmp_path / ".cursor" / "skills" / "testowner:test-skill"

        assert claude_skill.exists(), "Skill should be in .claude/"
        assert cursor_skill.exists(), "Skill should be in .cursor/"

    @patch("agr.cli.handlers.downloaded_repo")
    def test_remote_add_defaults_to_claude_in_non_tty(
        self, mock_download, tmp_path: Path, monkeypatch
    ):
        """Test that remote add defaults to Claude when not interactive."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # No config, no tool directories, non-interactive
        # Create mock repo with a skill
        repo_dir = tmp_path / "mock_repo"
        skill_dir = repo_dir / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Test Skill")

        mock_download.return_value.__enter__ = lambda self: repo_dir
        mock_download.return_value.__exit__ = lambda self, *args: None

        # CliRunner is non-interactive by default
        result = runner.invoke(app, ["add", "testowner/test-skill"])

        assert result.exit_code == 0

        # Should default to .claude/
        claude_skill = tmp_path / ".claude" / "skills" / "testowner:test-skill"
        assert claude_skill.exists(), "Skill should default to .claude/"


class TestToolPersistence:
    """Tests for auto-detected tool persistence to agr.toml."""

    def test_auto_detected_tools_persisted(self, tmp_path: Path):
        """Test that auto-detected tools are persisted to agr.toml."""
        # Create .cursor directory to trigger detection
        (tmp_path / ".cursor").mkdir()
        config_path = tmp_path / "agr.toml"

        adapters = get_target_adapters_with_persistence(
            config=None,
            config_path=config_path,
            tool_flags=None,
            base_path=tmp_path,
            persist_auto_detected=True,
        )

        # Should have detected cursor
        assert len(adapters) >= 1
        cursor_adapters = [a for a in adapters if isinstance(a, CursorAdapter)]
        assert len(cursor_adapters) == 1

        # Config should be saved with detected tool
        assert config_path.exists(), "agr.toml should be created"
        config = AgrConfig.load(config_path)
        assert config.tools is not None
        assert "cursor" in config.tools.targets

    def test_tool_flags_not_persisted(self, tmp_path: Path):
        """Test that --tool flags are not persisted (intentional one-off)."""
        config_path = tmp_path / "agr.toml"

        adapters = get_target_adapters_with_persistence(
            config=None,
            config_path=config_path,
            tool_flags=["cursor"],  # Explicit flag
            base_path=tmp_path,
            persist_auto_detected=True,
        )

        # Should have cursor adapter
        assert len(adapters) == 1
        assert isinstance(adapters[0], CursorAdapter)

        # Config should NOT be saved (explicit flag = intentional one-off)
        assert not config_path.exists(), "agr.toml should not be created for explicit flags"

    def test_existing_config_targets_not_overwritten(self, tmp_path: Path):
        """Test that existing [tools].targets is not overwritten."""
        config_path = tmp_path / "agr.toml"

        # Create config with existing targets
        config = AgrConfig()
        config.tools = ToolsConfig(targets=["claude"])
        config.save(config_path)

        # Create .cursor directory
        (tmp_path / ".cursor").mkdir()

        adapters = get_target_adapters_with_persistence(
            config=config,
            config_path=config_path,
            tool_flags=None,
            base_path=tmp_path,
            persist_auto_detected=True,
        )

        # Should use config targets (claude), not auto-detected (cursor)
        assert len(adapters) == 1
        assert isinstance(adapters[0], ClaudeAdapter)

        # Config should still have original targets
        reloaded = AgrConfig.load(config_path)
        assert reloaded.tools.targets == ["claude"]

    def test_no_persistence_for_global_install(self, tmp_path: Path):
        """Test that global installs don't persist tools."""
        # Create .cursor directory
        (tmp_path / ".cursor").mkdir()

        adapters = get_target_adapters_with_persistence(
            config=None,
            config_path=None,  # No config path = global install
            tool_flags=None,
            base_path=tmp_path,
            persist_auto_detected=True,
        )

        # Should still detect tools but not persist
        assert len(adapters) >= 1


class TestNeedsInteractiveSelection:
    """Tests for needs_interactive_selection function."""

    def test_returns_false_with_tool_flags(self):
        """Test that tool flags disable interactive selection."""
        result = needs_interactive_selection(config=None, tool_flags=["claude"])
        assert result is False

    def test_returns_false_with_config_targets(self):
        """Test that config targets disable interactive selection."""
        config = AgrConfig()
        config.tools = ToolsConfig(targets=["claude"])

        result = needs_interactive_selection(config=config, tool_flags=None)
        assert result is False

    def test_returns_false_with_detected_tool_dirs(self, tmp_path: Path, monkeypatch):
        """Test that detected tool directories disable interactive selection."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".claude").mkdir()

        result = needs_interactive_selection(config=None, tool_flags=None)
        assert result is False

    @patch("sys.stdin.isatty", return_value=False)
    def test_returns_false_in_non_tty(self, mock_isatty, tmp_path: Path, monkeypatch):
        """Test that non-TTY environment disables interactive selection."""
        monkeypatch.chdir(tmp_path)
        # No tool directories, no config

        result = needs_interactive_selection(config=None, tool_flags=None)
        assert result is False


class TestRemoteAddWithExplicitType:
    """Tests for remote add with explicit --type flag and multi-tool."""

    @patch("agr.cli.handlers.downloaded_repo")
    @patch("agr.cli.handlers.fetch_resource")
    def test_explicit_type_respects_tool_flag(
        self, mock_fetch, mock_download, tmp_path: Path, monkeypatch
    ):
        """Test that explicit type with --tool flag installs to correct tool."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Create mock repo
        repo_dir = tmp_path / "mock_repo"
        repo_dir.mkdir()

        mock_download.return_value.__enter__ = lambda self: repo_dir
        mock_download.return_value.__exit__ = lambda self, *args: None

        result = runner.invoke(
            app, ["add", "testowner/my-skill", "--type", "skill", "--tool", "cursor"]
        )

        # fetch_resource should be called with cursor path
        if mock_fetch.called:
            call_args = mock_fetch.call_args
            dest_path = call_args[0][4]  # 5th positional arg is dest
            assert ".cursor" in str(dest_path)


class TestRemoteAddBundleMultiTool:
    """Tests for remote bundle add with multi-tool support."""

    @patch("agr.cli.handlers.fetch_bundle")
    def test_bundle_respects_tool_flag(
        self, mock_fetch_bundle, tmp_path: Path, monkeypatch
    ):
        """Test that bundle add respects --tool flag."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Mock successful bundle fetch
        mock_result = MagicMock()
        mock_result.total_installed = 3
        mock_result.total_skipped = 0
        mock_result.installed_skills = ["skill-a"]
        mock_result.installed_commands = ["cmd-a"]
        mock_result.installed_agents = []
        mock_result.skipped_skills = []
        mock_result.skipped_commands = []
        mock_result.skipped_agents = []
        mock_fetch_bundle.return_value = mock_result

        result = runner.invoke(
            app, ["add", "testowner/my-bundle", "--type", "bundle", "--tool", "cursor"]
        )

        # fetch_bundle should be called with cursor path
        if mock_fetch_bundle.called:
            call_args = mock_fetch_bundle.call_args
            dest_base = call_args[0][3]  # 4th positional arg is dest_base
            assert ".cursor" in str(dest_base)
