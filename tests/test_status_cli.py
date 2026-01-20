"""Tests for agr status CLI command."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from agr.cli.main import app
from agr.config import AgrConfig


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


class TestStatusCommand:
    """Tests for agr status command."""

    def test_status_no_config(self, runner, git_project):
        """Test status when no agr.toml exists."""
        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "No agr.toml found" in result.output

    def test_status_empty_config(self, runner, git_project):
        """Test status with empty config."""
        config_path = git_project / "agr.toml"
        config = AgrConfig()
        config.save(config_path)

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "No resources in agr.toml" in result.output

    def test_status_shows_target_tools(self, runner, git_project):
        """Test that status shows target tools."""
        config_path = git_project / "agr.toml"
        config = AgrConfig()
        config.add_tool_target("claude")
        config.add_tool_target("cursor")
        config.save(config_path)

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "Target tools:" in result.output
        assert "Claude" in result.output or "claude" in result.output

    def test_status_with_local_resource(self, runner, git_project):
        """Test status with a local resource in config."""
        # Create a local skill
        skill_dir = git_project / "resources" / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill")

        # Add to config
        config_path = git_project / "agr.toml"
        config = AgrConfig()
        config.add_local("resources/skills/my-skill", "skill")
        config.save(config_path)

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "resources/skills/my-skill" in result.output

    def test_status_shows_missing_resource(self, runner, git_project):
        """Test status shows missing status for unsynced resource."""
        # Add resource to config but don't install it
        config_path = git_project / "agr.toml"
        config = AgrConfig()
        config.add_remote("testuser/test-skill", "skill")
        config.save(config_path)

        # Create .claude dir but don't install the skill
        (git_project / ".claude").mkdir()

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "testuser/test-skill" in result.output
        # Should show missing status
        assert "missing" in result.output.lower()

    def test_status_verbose_shows_paths(self, runner, git_project):
        """Test that verbose mode shows file paths."""
        # Create a local skill
        skill_dir = git_project / "resources" / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill")

        # Add to config
        config_path = git_project / "agr.toml"
        config = AgrConfig()
        config.add_local("resources/skills/my-skill", "skill")
        config.save(config_path)

        result = runner.invoke(app, ["status", "--verbose"])

        assert result.exit_code == 0
        # Verbose should show path info
        assert "resources/skills/my-skill" in result.output

    def test_status_with_tool_flag(self, runner, git_project):
        """Test status with --tool flag."""
        config_path = git_project / "agr.toml"
        config = AgrConfig()
        config.add_tool_target("claude")
        config.add_tool_target("cursor")
        config.save(config_path)

        result = runner.invoke(app, ["status", "--tool", "claude"])

        assert result.exit_code == 0
        # Should only show Claude
        assert "Claude" in result.output or "claude" in result.output

    def test_status_all_synced_message(self, runner, git_project):
        """Test that all synced shows success message."""
        config_path = git_project / "agr.toml"
        config = AgrConfig()
        # Just have an empty config with no dependencies
        config.save(config_path)

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "All resources synced" in result.output

    def test_status_shows_run_sync_suggestion(self, runner, git_project):
        """Test that missing resources suggest running sync."""
        # Add resource to config but don't install it
        config_path = git_project / "agr.toml"
        config = AgrConfig()
        config.add_remote("testuser/test-skill", "skill")
        config.save(config_path)

        # Create .claude dir but don't install the skill
        (git_project / ".claude").mkdir()

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "agr sync" in result.output or "missing" in result.output.lower()
