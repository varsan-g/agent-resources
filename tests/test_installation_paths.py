"""Tests for resource installation paths (Issue #38).

Tests that resources are installed to the correct paths and that SKILL.md
name fields are updated appropriately.
"""

from pathlib import Path

from typer.testing import CliRunner

from agr.cli.main import app

runner = CliRunner()


class TestSkillInstallationPaths:
    """Tests for skill installation to flattened directories."""

    def test_skill_installs_to_flattened_directory(self, git_project: Path):
        """Skill installs to .claude/skills/<flattened-name>/SKILL.md."""
        skill_dir = git_project / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill")

        result = runner.invoke(app, ["add", "./skills/my-skill"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "skills" / "local:my-skill"
        assert installed.is_dir()
        assert (installed / "SKILL.md").exists()

    def test_skill_name_updated_in_skill_md(self, git_project: Path):
        """SKILL.md name field is updated to flattened name."""
        skill_dir = git_project / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: original-name\n---\n# My Skill")

        result = runner.invoke(app, ["add", "./skills/my-skill"])

        assert result.exit_code == 0
        installed_skill = git_project / ".claude" / "skills" / "local:my-skill" / "SKILL.md"
        content = installed_skill.read_text()
        assert "name: local:my-skill" in content

    def test_skill_preserves_other_frontmatter(self, git_project: Path):
        """SKILL.md preserves other frontmatter fields when updating name."""
        skill_dir = git_project / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: original\ndescription: test skill\ntriggers:\n  - test\n---\n# My Skill"
        )

        result = runner.invoke(app, ["add", "./skills/my-skill"])

        assert result.exit_code == 0
        installed_skill = git_project / ".claude" / "skills" / "local:my-skill" / "SKILL.md"
        content = installed_skill.read_text()
        assert "name: local:my-skill" in content
        assert "description: test skill" in content
        assert "triggers:" in content

    def test_skill_copies_additional_files(self, git_project: Path):
        """Skill directory with additional files copies all files."""
        skill_dir = git_project / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill")
        (skill_dir / "reference.md").write_text("# Reference")
        refs_dir = skill_dir / "references"
        refs_dir.mkdir()
        (refs_dir / "guide.md").write_text("# Guide")

        result = runner.invoke(app, ["add", "./skills/my-skill"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "skills" / "local:my-skill"
        assert (installed / "SKILL.md").exists()
        assert (installed / "reference.md").exists()
        assert (installed / "references" / "guide.md").exists()


class TestCommandInstallationPaths:
    """Tests for command installation to nested directories."""

    def test_command_installs_to_nested_directory(self, git_project: Path):
        """Command installs to .claude/commands/local/<path>/cmd.md."""
        commands_dir = git_project / "commands" / "infra"
        commands_dir.mkdir(parents=True)
        (commands_dir / "deploy.md").write_text("# Deploy")

        result = runner.invoke(app, ["add", "./commands/infra/deploy.md"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "commands" / "local" / "infra" / "deploy.md"
        assert installed.exists()
        assert installed.is_file()

    def test_command_creates_nested_directories(self, git_project: Path):
        """Command installation creates nested directories as needed."""
        commands_dir = git_project / "commands" / "a" / "b" / "c"
        commands_dir.mkdir(parents=True)
        (commands_dir / "deep.md").write_text("# Deep")

        result = runner.invoke(app, ["add", "./commands/a/b/c/deep.md"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "commands" / "local" / "a" / "b" / "c" / "deep.md"
        assert installed.exists()


class TestPackageInstallationPaths:
    """Tests for package explosion to type directories."""

    def test_package_explodes_skills_to_skills_dir(self, git_project: Path):
        """Package skills install to .claude/skills/ with flattened names."""
        pkg_dir = git_project / "my-pkg"
        pkg_dir.mkdir()
        (pkg_dir / "PACKAGE.md").write_text("---\nname: my-pkg\n---\n")
        skill_dir = pkg_dir / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill")

        result = runner.invoke(app, ["add", "./my-pkg"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "skills" / "local:my-pkg:my-skill" / "SKILL.md"
        assert installed.exists()

    def test_package_explodes_commands_to_commands_dir(self, git_project: Path):
        """Package commands install to .claude/commands/ with package namespace."""
        pkg_dir = git_project / "my-pkg"
        pkg_dir.mkdir()
        (pkg_dir / "PACKAGE.md").write_text("---\nname: my-pkg\n---\n")
        commands_dir = pkg_dir / "commands"
        commands_dir.mkdir()
        (commands_dir / "cmd.md").write_text("# Command")
        skill_dir = pkg_dir / "skills" / "helper"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Helper")

        result = runner.invoke(app, ["add", "./my-pkg"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "commands" / "local" / "my-pkg" / "cmd.md"
        assert installed.exists()

    def test_package_explodes_agents_to_agents_dir(self, git_project: Path):
        """Package agents install to .claude/agents/ with package namespace."""
        pkg_dir = git_project / "my-pkg"
        pkg_dir.mkdir()
        (pkg_dir / "PACKAGE.md").write_text("---\nname: my-pkg\n---\n")
        agents_dir = pkg_dir / "agents"
        agents_dir.mkdir()
        (agents_dir / "agent.md").write_text("# Agent")
        skill_dir = pkg_dir / "skills" / "helper"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Helper")

        result = runner.invoke(app, ["add", "./my-pkg"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "agents" / "local" / "my-pkg" / "agent.md"
        assert installed.exists()

    def test_package_not_installed_to_packages_dir(self, git_project: Path):
        """Package does NOT install to .claude/packages/ (old behavior)."""
        pkg_dir = git_project / "my-pkg"
        pkg_dir.mkdir()
        (pkg_dir / "PACKAGE.md").write_text("---\nname: my-pkg\n---\n")
        skill_dir = pkg_dir / "skills" / "helper"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Helper")

        result = runner.invoke(app, ["add", "./my-pkg"])

        assert result.exit_code == 0
        old_packages_dir = git_project / ".claude" / "packages"
        assert not old_packages_dir.exists()
