"""Tests for init authoring commands."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from agr.cli.main import app


runner = CliRunner()


class TestInitSimplified:
    """Tests for simplified agr init (uv-inspired)."""

    def test_init_creates_agr_toml(self, tmp_path: Path, monkeypatch):
        """Test that agr init creates agr.toml."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        assert (tmp_path / "agr.toml").exists()
        assert "Created agr.toml" in result.output

    def test_init_creates_convention_directories(self, tmp_path: Path, monkeypatch):
        """Test that agr init creates convention directories under resources/."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        assert (tmp_path / "resources").exists()
        assert (tmp_path / "resources" / "skills").exists()
        assert (tmp_path / "resources" / "commands").exists()
        assert (tmp_path / "resources" / "agents").exists()
        assert (tmp_path / "resources" / "packages").exists()

    def test_init_shows_next_steps(self, tmp_path: Path, monkeypatch):
        """Test that agr init shows next steps."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        assert "Next steps" in result.output
        assert "agr init skill" in result.output
        assert "agr add" in result.output

    def test_init_idempotent(self, tmp_path: Path, monkeypatch):
        """Test that agr init is idempotent (can be run multiple times)."""
        monkeypatch.chdir(tmp_path)

        # First run
        result1 = runner.invoke(app, ["init"])
        assert result1.exit_code == 0

        # Second run - should not fail
        result2 = runner.invoke(app, ["init"])
        assert result2.exit_code == 0
        assert "already exists" in result2.output

    def test_init_doesnt_recreate_existing_directories(self, tmp_path: Path, monkeypatch):
        """Test that init doesn't try to recreate existing directories."""
        monkeypatch.chdir(tmp_path)
        # Pre-create a directory
        (tmp_path / "resources" / "skills").mkdir(parents=True)
        (tmp_path / "agr.toml").write_text("dependencies = []")

        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        # Should not show "Created resources/skills/" since it exists
        assert "Created resources/skills/" not in result.output


class TestInitPathInName:
    """Tests for path detection in name argument."""

    def test_init_skill_with_path_in_name(self, tmp_path: Path, monkeypatch):
        """Test that agr init skill resources/skills/my-skill works."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["init", "skill", "resources/skills/my-skill"])

        assert result.exit_code == 0
        assert (tmp_path / "resources" / "skills" / "my-skill" / "SKILL.md").exists()

    def test_init_skill_with_relative_path_in_name(self, tmp_path: Path, monkeypatch):
        """Test that agr init skill ./resources/skills/my-skill works."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["init", "skill", "./resources/skills/my-skill"])

        assert result.exit_code == 0
        assert (tmp_path / "resources" / "skills" / "my-skill" / "SKILL.md").exists()

    def test_init_command_with_path_in_name(self, tmp_path: Path, monkeypatch):
        """Test that agr init command resources/commands/my-cmd works."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["init", "command", "resources/commands/my-cmd"])

        assert result.exit_code == 0
        assert (tmp_path / "resources" / "commands" / "my-cmd.md").exists()

    def test_init_agent_with_path_in_name(self, tmp_path: Path, monkeypatch):
        """Test that agr init agent resources/agents/my-agent works."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["init", "agent", "resources/agents/my-agent"])

        assert result.exit_code == 0
        assert (tmp_path / "resources" / "agents" / "my-agent.md").exists()


class TestInitSkillAuthoring:
    """Tests for agr init skill with authoring paths."""

    def test_init_skill_uses_authoring_path_by_default(self, tmp_path: Path, monkeypatch):
        """Test that skill is created in ./resources/skills/ by default."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["init", "skill", "my-skill"])

        assert result.exit_code == 0
        assert (tmp_path / "resources" / "skills" / "my-skill" / "SKILL.md").exists()

    def test_init_skill_creates_skills_dir(self, tmp_path: Path, monkeypatch):
        """Test that init skill creates resources/skills/ directory if it doesn't exist."""
        monkeypatch.chdir(tmp_path)

        # resources/skills/ doesn't exist yet
        assert not (tmp_path / "resources" / "skills").exists()

        result = runner.invoke(app, ["init", "skill", "my-skill"])

        assert result.exit_code == 0
        assert (tmp_path / "resources" / "skills").is_dir()
        assert (tmp_path / "resources" / "skills" / "my-skill" / "SKILL.md").exists()

    def test_init_skill_legacy_uses_claude_path(self, tmp_path: Path, monkeypatch):
        """Test that --legacy creates in .claude/skills/."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["init", "skill", "my-skill", "--legacy"])

        assert result.exit_code == 0
        assert (tmp_path / ".claude" / "skills" / "my-skill" / "SKILL.md").exists()

    def test_init_skill_custom_path(self, tmp_path: Path, monkeypatch):
        """Test that --path overrides default."""
        monkeypatch.chdir(tmp_path)
        custom_path = tmp_path / "custom"

        result = runner.invoke(app, ["init", "skill", "my-skill", "--path", str(custom_path)])

        assert result.exit_code == 0
        assert (custom_path / "SKILL.md").exists()


class TestInitCommandAuthoring:
    """Tests for agr init command with authoring paths."""

    def test_init_command_uses_authoring_path_by_default(self, tmp_path: Path, monkeypatch):
        """Test that command is created in ./resources/commands/ by default."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["init", "command", "my-cmd"])

        assert result.exit_code == 0
        assert (tmp_path / "resources" / "commands" / "my-cmd.md").exists()

    def test_init_command_creates_commands_dir(self, tmp_path: Path, monkeypatch):
        """Test that init command creates resources/commands/ directory if it doesn't exist."""
        monkeypatch.chdir(tmp_path)

        # resources/commands/ doesn't exist yet
        assert not (tmp_path / "resources" / "commands").exists()

        result = runner.invoke(app, ["init", "command", "my-cmd"])

        assert result.exit_code == 0
        assert (tmp_path / "resources" / "commands").is_dir()
        assert (tmp_path / "resources" / "commands" / "my-cmd.md").exists()

    def test_init_command_legacy_uses_claude_path(self, tmp_path: Path, monkeypatch):
        """Test that --legacy creates in .claude/commands/."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["init", "command", "my-cmd", "--legacy"])

        assert result.exit_code == 0
        assert (tmp_path / ".claude" / "commands" / "my-cmd.md").exists()


class TestInitAgentAuthoring:
    """Tests for agr init agent with authoring paths."""

    def test_init_agent_uses_authoring_path_by_default(self, tmp_path: Path, monkeypatch):
        """Test that agent is created in ./resources/agents/ by default."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["init", "agent", "my-agent"])

        assert result.exit_code == 0
        assert (tmp_path / "resources" / "agents" / "my-agent.md").exists()

    def test_init_agent_creates_agents_dir(self, tmp_path: Path, monkeypatch):
        """Test that init agent creates resources/agents/ directory if it doesn't exist."""
        monkeypatch.chdir(tmp_path)

        # resources/agents/ doesn't exist yet
        assert not (tmp_path / "resources" / "agents").exists()

        result = runner.invoke(app, ["init", "agent", "my-agent"])

        assert result.exit_code == 0
        assert (tmp_path / "resources" / "agents").is_dir()
        assert (tmp_path / "resources" / "agents" / "my-agent.md").exists()

    def test_init_agent_legacy_uses_claude_path(self, tmp_path: Path, monkeypatch):
        """Test that --legacy creates in .claude/agents/."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["init", "agent", "my-agent", "--legacy"])

        assert result.exit_code == 0
        assert (tmp_path / ".claude" / "agents" / "my-agent.md").exists()


class TestInitPackage:
    """Tests for agr init package command."""

    def test_init_package_creates_structure(self, tmp_path: Path, monkeypatch):
        """Test that package creates skills/, commands/, agents/ subdirs."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["init", "package", "my-toolkit"])

        assert result.exit_code == 0
        pkg_path = tmp_path / "resources" / "packages" / "my-toolkit"
        assert pkg_path.is_dir()
        assert (pkg_path / "skills").is_dir()
        assert (pkg_path / "commands").is_dir()
        assert (pkg_path / "agents").is_dir()

    def test_init_package_creates_packages_dir(self, tmp_path: Path, monkeypatch):
        """Test that init package creates resources/packages/ directory if it doesn't exist."""
        monkeypatch.chdir(tmp_path)

        # resources/packages/ doesn't exist yet
        assert not (tmp_path / "resources" / "packages").exists()

        result = runner.invoke(app, ["init", "package", "my-toolkit"])

        assert result.exit_code == 0
        assert (tmp_path / "resources" / "packages").is_dir()

    def test_init_package_custom_path(self, tmp_path: Path, monkeypatch):
        """Test that --path overrides default package location."""
        monkeypatch.chdir(tmp_path)
        custom_path = tmp_path / "libs" / "utils"

        result = runner.invoke(app, ["init", "package", "my-toolkit", "--path", str(custom_path)])

        assert result.exit_code == 0
        assert custom_path.is_dir()
        assert (custom_path / "skills").is_dir()
        assert (custom_path / "commands").is_dir()
        assert (custom_path / "agents").is_dir()

    def test_init_package_errors_if_exists(self, tmp_path: Path, monkeypatch):
        """Test that init package errors if directory exists."""
        monkeypatch.chdir(tmp_path)

        # Create existing package
        (tmp_path / "resources" / "packages" / "my-toolkit").mkdir(parents=True)

        result = runner.invoke(app, ["init", "package", "my-toolkit"])

        assert result.exit_code == 1
        assert "already exists" in result.output
