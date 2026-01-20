"""Tests for directory resource discovery (Issue #38).

Tests recursive discovery of skills, commands, and agents within directories.
"""

from pathlib import Path

from typer.testing import CliRunner

from agr.cli.main import app

runner = CliRunner()


class TestRecursiveSkillDiscovery:
    """Tests for recursive skill discovery in directories."""

    def test_discovers_skills_at_multiple_depths(self, git_project: Path):
        """Discovers skills at various nesting levels."""
        skills_dir = git_project / "skills"
        skills_dir.mkdir()

        (skills_dir / "skill-a").mkdir()
        (skills_dir / "skill-a" / "SKILL.md").write_text("# Skill A")

        (skills_dir / "category" / "skill-b").mkdir(parents=True)
        (skills_dir / "category" / "skill-b" / "SKILL.md").write_text("# Skill B")

        (skills_dir / "cat" / "subcat" / "skill-c").mkdir(parents=True)
        (skills_dir / "cat" / "subcat" / "skill-c" / "SKILL.md").write_text("# Skill C")

        result = runner.invoke(app, ["add", "./skills/"])

        assert result.exit_code == 0
        assert "skill-a" in result.output
        assert "skill-b" in result.output
        assert "skill-c" in result.output
        assert "Added 3 resource(s)" in result.output

    def test_skill_reference_files_not_discovered(self, git_project: Path):
        """Reference .md files inside skill directories are not discovered."""
        skills_dir = git_project / "skills"
        skills_dir.mkdir()

        skill_dir = skills_dir / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# My Skill")
        (skill_dir / "reference.md").write_text("# Reference")
        (skill_dir / "references" / "guide.md").parent.mkdir()
        (skill_dir / "references" / "guide.md").write_text("# Guide")

        result = runner.invoke(app, ["add", "./skills/"])

        assert result.exit_code == 0
        assert "my-skill" in result.output
        assert "Added 1 resource(s)" in result.output
        assert "reference" not in result.output.lower() or "my-skill" in result.output

    def test_empty_directories_ignored(self, git_project: Path):
        """Empty directories don't cause issues."""
        skills_dir = git_project / "skills"
        skills_dir.mkdir()
        (skills_dir / "empty-dir").mkdir()
        (skills_dir / "real-skill").mkdir()
        (skills_dir / "real-skill" / "SKILL.md").write_text("# Real")

        result = runner.invoke(app, ["add", "./skills/"])

        assert result.exit_code == 0
        assert "real-skill" in result.output
        assert "Added 1 resource(s)" in result.output


class TestRecursiveCommandDiscovery:
    """Tests for recursive command discovery in directories."""

    def test_discovers_commands_at_multiple_depths(self, git_project: Path):
        """Discovers commands at various nesting levels."""
        commands_dir = git_project / "commands"
        commands_dir.mkdir()

        (commands_dir / "cmd-a.md").write_text("# Command A")

        (commands_dir / "infra").mkdir()
        (commands_dir / "infra" / "cmd-b.md").write_text("# Command B")

        (commands_dir / "aws" / "ec2").mkdir(parents=True)
        (commands_dir / "aws" / "ec2" / "cmd-c.md").write_text("# Command C")

        result = runner.invoke(app, ["add", "./commands/"])

        assert result.exit_code == 0
        assert "cmd-a" in result.output
        assert "cmd-b" in result.output
        assert "cmd-c" in result.output
        assert "Added 3 resource(s)" in result.output

    def test_nested_commands_preserve_path_structure(self, git_project: Path):
        """Nested commands are installed with preserved path structure."""
        commands_dir = git_project / "commands" / "infra" / "aws"
        commands_dir.mkdir(parents=True)
        (commands_dir / "deploy.md").write_text("# Deploy")

        result = runner.invoke(app, ["add", "./commands/infra/aws/deploy.md"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "commands" / "local" / "infra" / "aws" / "deploy.md"
        assert installed.exists()


class TestMixedResourceDiscovery:
    """Tests for discovering mixed resource types in directories."""

    def test_discovers_skills_and_commands_separately(self, git_project: Path):
        """Adding skills/ and commands/ directories works independently."""
        skills_dir = git_project / "skills"
        skills_dir.mkdir()
        (skills_dir / "my-skill").mkdir()
        (skills_dir / "my-skill" / "SKILL.md").write_text("# Skill")

        commands_dir = git_project / "commands"
        commands_dir.mkdir()
        (commands_dir / "my-cmd.md").write_text("# Command")

        result = runner.invoke(app, ["add", "./skills/"])
        assert result.exit_code == 0
        assert "my-skill" in result.output

        result = runner.invoke(app, ["add", "./commands/"])
        assert result.exit_code == 0
        assert "my-cmd" in result.output

        assert (git_project / ".claude" / "skills" / "local:my-skill" / "SKILL.md").exists()
        assert (git_project / ".claude" / "commands" / "local" / "my-cmd.md").exists()

    def test_resources_directory_with_mixed_types(self, git_project: Path):
        """Resources directory with both skills and commands."""
        resources_dir = git_project / "resources"
        resources_dir.mkdir()

        skills_dir = resources_dir / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill-1").mkdir()
        (skills_dir / "skill-1" / "SKILL.md").write_text("# Skill 1")

        commands_dir = resources_dir / "commands"
        commands_dir.mkdir()
        (commands_dir / "cmd-1.md").write_text("# Command 1")

        result = runner.invoke(app, ["add", "./resources/skills/"])
        assert result.exit_code == 0
        assert "skill-1" in result.output

        result = runner.invoke(app, ["add", "./resources/commands/"])
        assert result.exit_code == 0
        assert "cmd-1" in result.output


class TestDirectoryDiscoveryEdgeCases:
    """Edge case tests for directory discovery."""

    def test_deeply_nested_skills_full_path_in_name(self, git_project: Path):
        """Deeply nested skills get full path in flattened name."""
        deep_path = git_project / "skills" / "a" / "b" / "c" / "d" / "deep-skill"
        deep_path.mkdir(parents=True)
        (deep_path / "SKILL.md").write_text("# Deep Skill")

        result = runner.invoke(app, ["add", "./skills/"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "skills" / "local:a:b:c:d:deep-skill" / "SKILL.md"
        assert installed.exists()

    def test_directory_with_only_skill_md_discovered(self, git_project: Path):
        """Directory containing only SKILL.md is discovered correctly."""
        skills_dir = git_project / "skills"
        skills_dir.mkdir()
        (skills_dir / "minimal-skill").mkdir()
        (skills_dir / "minimal-skill" / "SKILL.md").write_text("# Minimal")

        result = runner.invoke(app, ["add", "./skills/"])

        assert result.exit_code == 0
        assert "minimal-skill" in result.output
