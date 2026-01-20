"""Tests for single file type detection (Issue #38).

Tests ancestor-based type detection and ambiguous file error handling.
"""

from pathlib import Path

from typer.testing import CliRunner

from agr.cli.main import app
from agr.cli.add import detect_resource_type_from_ancestors, _detect_local_type

runner = CliRunner()


class TestAncestorBasedTypeDetection:
    """Tests for detecting resource type from parent directories."""

    def test_file_in_commands_dir_detected_as_command(self, tmp_path: Path):
        """File under commands/ is detected as command."""
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        file_path = commands_dir / "deploy.md"
        file_path.write_text("# Deploy")

        result = detect_resource_type_from_ancestors(file_path)
        assert result == "command"

    def test_file_in_nested_commands_dir_detected_as_command(self, tmp_path: Path):
        """File deep under commands/ is still detected as command."""
        nested_dir = tmp_path / "commands" / "infra" / "aws"
        nested_dir.mkdir(parents=True)
        file_path = nested_dir / "deploy.md"
        file_path.write_text("# Deploy")

        result = detect_resource_type_from_ancestors(file_path)
        assert result == "command"

    def test_file_in_agents_dir_detected_as_agent(self, tmp_path: Path):
        """File under agents/ is detected as agent."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        file_path = agents_dir / "reviewer.md"
        file_path.write_text("# Reviewer")

        result = detect_resource_type_from_ancestors(file_path)
        assert result == "agent"

    def test_file_in_rules_dir_detected_as_rule(self, tmp_path: Path):
        """File under rules/ is detected as rule."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        file_path = rules_dir / "style.md"
        file_path.write_text("# Style")

        result = detect_resource_type_from_ancestors(file_path)
        assert result == "rule"

    def test_file_not_in_type_dir_returns_none(self, tmp_path: Path):
        """File not under type directory returns None."""
        file_path = tmp_path / "random.md"
        file_path.write_text("# Random")

        result = detect_resource_type_from_ancestors(file_path)
        assert result is None

    def test_closest_type_dir_wins(self, tmp_path: Path):
        """When multiple type dirs in path, closest one wins."""
        # Create path like agents/commands/x.md
        nested_dir = tmp_path / "agents" / "commands"
        nested_dir.mkdir(parents=True)
        file_path = nested_dir / "test.md"
        file_path.write_text("# Test")

        result = detect_resource_type_from_ancestors(file_path)
        # "commands" is closer than "agents"
        assert result == "command"


class TestAmbiguousFileHandling:
    """Tests for error handling when file type cannot be determined."""

    def test_root_md_file_produces_clear_error(self, git_project: Path):
        """Adding .md file not under type directory produces clear error."""
        (git_project / "random.md").write_text("# Random")

        result = runner.invoke(app, ["add", "./random.md"])

        assert result.exit_code == 1
        assert "Cannot determine resource type" in result.output
        assert "--type" in result.output

    def test_error_message_suggests_type_flag(self, git_project: Path):
        """Error message suggests using --type flag."""
        (git_project / "ambiguous.md").write_text("# Ambiguous")

        result = runner.invoke(app, ["add", "./ambiguous.md"])

        assert result.exit_code == 1
        assert "--type" in result.output
        assert "command" in result.output or "agent" in result.output

    def test_type_flag_overrides_detection(self, git_project: Path):
        """--type flag allows adding ambiguous files."""
        (git_project / "random.md").write_text("# Random Command")

        result = runner.invoke(app, ["add", "./random.md", "--type", "command"])

        assert result.exit_code == 0
        assert "Added local command 'random'" in result.output

    def test_type_flag_overrides_auto_detection(self, git_project: Path):
        """--type takes precedence over auto-detection."""
        commands_dir = git_project / "commands"
        commands_dir.mkdir()
        (commands_dir / "deploy.md").write_text("# Deploy Agent")

        result = runner.invoke(app, ["add", "./commands/deploy.md", "--type", "agent"])

        assert result.exit_code == 0
        assert "Added local agent 'deploy'" in result.output
        installed = git_project / ".claude" / "agents" / "local" / "deploy.md"
        assert installed.exists()


class TestDetectLocalTypeFunction:
    """Unit tests for _detect_local_type function."""

    def test_directory_with_skill_md_detected_as_skill(self, tmp_path: Path):
        """Directory containing SKILL.md is detected as skill."""
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Skill")

        result = _detect_local_type(skill_dir)
        assert result == "skill"

    def test_directory_with_package_md_detected_as_package(self, tmp_path: Path):
        """Directory containing PACKAGE.md is detected as package."""
        pkg_dir = tmp_path / "my-pkg"
        pkg_dir.mkdir()
        (pkg_dir / "PACKAGE.md").write_text("---\nname: my-pkg\n---\n")

        result = _detect_local_type(pkg_dir)
        assert result == "package"

    def test_empty_directory_returns_none(self, tmp_path: Path):
        """Empty directory returns None."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = _detect_local_type(empty_dir)
        assert result is None

    def test_file_without_md_extension_returns_none(self, tmp_path: Path):
        """Non-.md file returns None."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("text content")

        result = _detect_local_type(txt_file)
        assert result is None
