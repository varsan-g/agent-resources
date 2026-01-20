"""Comprehensive tests for path namespacing functionality (Issue #38).

Tests the full namespacing logic for all resource types: skills, commands, agents, and rules.
"""

from pathlib import Path

from typer.testing import CliRunner

from agr.cli.main import app
from agr.utils import compute_flattened_resource_name, compute_path_segments

runner = CliRunner()


class TestSkillPathNamespacing:
    """Tests for skill path namespace generation."""

    def test_standalone_skill_namespace(self, git_project: Path):
        """Standalone skill uses local:skill format."""
        skill_dir = git_project / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill")

        result = runner.invoke(app, ["add", "./skills/my-skill"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "skills" / "local:my-skill" / "SKILL.md"
        assert installed.exists()

    def test_nested_skill_namespace(self, git_project: Path):
        """Nested skill uses local:parent:child format."""
        skill_dir = git_project / "skills" / "category" / "nested-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Nested Skill")

        result = runner.invoke(app, ["add", "./skills/category/nested-skill"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "skills" / "local:category:nested-skill" / "SKILL.md"
        assert installed.exists()

    def test_packaged_skill_namespace(self, git_project: Path):
        """Skill in package uses local:pkg:skill format."""
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

    def test_deeply_nested_packaged_skill_namespace(self, git_project: Path):
        """Deeply nested skill in package uses full path segments."""
        pkg_dir = git_project / "deep-pkg"
        pkg_dir.mkdir()
        (pkg_dir / "PACKAGE.md").write_text("---\nname: deep-pkg\n---\n")
        skill_dir = pkg_dir / "skills" / "a" / "b" / "c" / "skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Deep Skill")

        result = runner.invoke(app, ["add", "./deep-pkg"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "skills" / "local:deep-pkg:a:b:c:skill" / "SKILL.md"
        assert installed.exists()


class TestCommandPathNamespacing:
    """Tests for command path namespace generation."""

    def test_command_in_commands_dir(self, git_project: Path):
        """Command in commands/ installs to .claude/commands/local/cmd.md."""
        commands_dir = git_project / "commands"
        commands_dir.mkdir()
        (commands_dir / "deploy.md").write_text("# Deploy")

        result = runner.invoke(app, ["add", "./commands/deploy.md"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "commands" / "local" / "deploy.md"
        assert installed.exists()

    def test_nested_command_preserves_path(self, git_project: Path):
        """Nested command preserves directory structure."""
        nested_dir = git_project / "commands" / "infra" / "aws"
        nested_dir.mkdir(parents=True)
        (nested_dir / "deploy.md").write_text("# Deploy")

        result = runner.invoke(app, ["add", "./commands/infra/aws/deploy.md"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "commands" / "local" / "infra" / "aws" / "deploy.md"
        assert installed.exists()

    def test_package_command_namespacing(self, git_project: Path):
        """Command in package uses local/pkg/cmd.md path."""
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


class TestAgentPathNamespacing:
    """Tests for agent path namespace generation."""

    def test_agent_in_agents_dir(self, git_project: Path):
        """Agent in agents/ installs to .claude/agents/local/agent.md."""
        agents_dir = git_project / "agents"
        agents_dir.mkdir()
        (agents_dir / "reviewer.md").write_text("# Reviewer")

        result = runner.invoke(app, ["add", "./agents/reviewer.md"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "agents" / "local" / "reviewer.md"
        assert installed.exists()

    def test_nested_agent_preserves_path(self, git_project: Path):
        """Nested agent preserves directory structure."""
        nested_dir = git_project / "agents" / "code" / "review"
        nested_dir.mkdir(parents=True)
        (nested_dir / "linter.md").write_text("# Linter")

        result = runner.invoke(app, ["add", "./agents/code/review/linter.md"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "agents" / "local" / "code" / "review" / "linter.md"
        assert installed.exists()


class TestRulePathNamespacing:
    """Tests for rule path namespace generation."""

    def test_rule_in_rules_dir(self, git_project: Path):
        """Rule in rules/ installs to .claude/rules/local/rule.md."""
        rules_dir = git_project / "rules"
        rules_dir.mkdir()
        (rules_dir / "style.md").write_text("# Style Guide")

        result = runner.invoke(app, ["add", "./rules/style.md"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "rules" / "local" / "style.md"
        assert installed.exists()

    def test_nested_rule_preserves_path(self, git_project: Path):
        """Nested rule preserves directory structure."""
        nested_dir = git_project / "rules" / "security"
        nested_dir.mkdir(parents=True)
        (nested_dir / "auth.md").write_text("# Auth Rules")

        result = runner.invoke(app, ["add", "./rules/security/auth.md"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "rules" / "local" / "security" / "auth.md"
        assert installed.exists()


class TestComputePathSegmentsUnit:
    """Unit tests for compute_path_segments function."""

    def test_single_segment_skill(self):
        """skills/commit -> ["commit"]"""
        result = compute_path_segments(Path("skills/commit"))
        assert result == ["commit"]

    def test_multi_segment_skill(self):
        """skills/git/status -> ["git", "status"]"""
        result = compute_path_segments(Path("skills/git/status"))
        assert result == ["git", "status"]

    def test_command_file(self):
        """commands/deploy.md -> ["deploy"]"""
        result = compute_path_segments(Path("commands/deploy.md"))
        assert result == ["deploy"]

    def test_nested_command(self):
        """commands/infra/deploy.md -> ["infra", "deploy"]"""
        result = compute_path_segments(Path("commands/infra/deploy.md"))
        assert result == ["infra", "deploy"]


class TestComputeFlattenedResourceNameUnit:
    """Unit tests for compute_flattened_resource_name function."""

    def test_standalone_resource(self):
        """("local", ["skill"]) -> "local:skill" """
        result = compute_flattened_resource_name("local", ["skill"])
        assert result == "local:skill"

    def test_nested_resource(self):
        """("local", ["git", "status"]) -> "local:git:status" """
        result = compute_flattened_resource_name("local", ["git", "status"])
        assert result == "local:git:status"

    def test_packaged_resource(self):
        """("local", ["skill"], "pkg") -> "local:pkg:skill" """
        result = compute_flattened_resource_name("local", ["skill"], "pkg")
        assert result == "local:pkg:skill"

    def test_nested_packaged_resource(self):
        """("local", ["a", "b"], "pkg") -> "local:pkg:a:b" """
        result = compute_flattened_resource_name("local", ["a", "b"], "pkg")
        assert result == "local:pkg:a:b"
