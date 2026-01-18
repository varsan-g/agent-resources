"""Unit tests for the list command functionality."""

import pytest
from pathlib import Path

from agr.config import Dependency
from agr.cli.list import _is_installed


class TestIsInstalled:
    """Tests for _is_installed helper function."""

    def test_local_skill_uses_flattened_name(self, tmp_path):
        """Test that local skill check uses flattened colon-namespaced path."""
        # Create installed skill at flattened path: .claude/skills/kasperjunge:commit/
        skill_dir = tmp_path / "skills" / "kasperjunge:commit"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Commit skill")

        dep = Dependency(type="skill", path="resources/skills/commit")

        # Should find it at the flattened path
        assert _is_installed(dep, tmp_path, "kasperjunge") is True

    def test_local_skill_not_found_at_nested_path(self, tmp_path):
        """Test that local skill is NOT found at old nested path structure."""
        # Create skill at old nested path: .claude/skills/kasperjunge/commit/
        # This is the WRONG path - should not be detected
        skill_dir = tmp_path / "skills" / "kasperjunge" / "commit"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Commit skill")

        dep = Dependency(type="skill", path="resources/skills/commit")

        # Should NOT find it at the nested path (that's the old buggy behavior)
        assert _is_installed(dep, tmp_path, "kasperjunge") is False

    def test_local_nested_skill_uses_flattened_name(self, tmp_path):
        """Test that nested local skill uses flattened path with colons."""
        # Create nested skill at: .claude/skills/kasperjunge:product-strategy:growth-hacker/
        skill_dir = tmp_path / "skills" / "kasperjunge:product-strategy:growth-hacker"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Growth hacker skill")

        dep = Dependency(type="skill", path="resources/skills/product-strategy/growth-hacker")

        assert _is_installed(dep, tmp_path, "kasperjunge") is True

    def test_local_command_uses_nested_path(self, tmp_path):
        """Test that local command uses nested username/name.md path."""
        # Create the source file so path.is_file() works correctly
        source_dir = tmp_path / "resources" / "commands"
        source_dir.mkdir(parents=True)
        (source_dir / "hello-world.md").write_text("# Source Hello World")

        # Create command at: .claude/commands/kasperjunge/hello-world.md
        claude_dir = tmp_path / ".claude"
        cmd_dir = claude_dir / "commands" / "kasperjunge"
        cmd_dir.mkdir(parents=True)
        (cmd_dir / "hello-world.md").write_text("# Hello World")

        # Use absolute path so is_file() check works
        dep = Dependency(type="command", path=str(source_dir / "hello-world.md"))

        assert _is_installed(dep, claude_dir, "kasperjunge") is True

    def test_local_agent_uses_nested_path(self, tmp_path):
        """Test that local agent uses nested username/name.md path."""
        # Create the source file so path.is_file() works correctly
        source_dir = tmp_path / "resources" / "agents"
        source_dir.mkdir(parents=True)
        (source_dir / "reviewer.md").write_text("# Source Reviewer")

        # Create agent at: .claude/agents/kasperjunge/reviewer.md
        claude_dir = tmp_path / ".claude"
        agent_dir = claude_dir / "agents" / "kasperjunge"
        agent_dir.mkdir(parents=True)
        (agent_dir / "reviewer.md").write_text("# Reviewer")

        # Use absolute path so is_file() check works
        dep = Dependency(type="agent", path=str(source_dir / "reviewer.md"))

        assert _is_installed(dep, claude_dir, "kasperjunge") is True

    def test_remote_skill_uses_flattened_name(self, tmp_path):
        """Test that remote skill check uses flattened colon-namespaced path."""
        # Create installed skill at: .claude/skills/dsjacobsen:golang-pro/
        skill_dir = tmp_path / "skills" / "dsjacobsen:golang-pro"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Golang Pro skill")

        dep = Dependency(type="skill", handle="dsjacobsen/golang-pro")

        assert _is_installed(dep, tmp_path, "local") is True

    def test_remote_skill_not_found_at_nested_path(self, tmp_path):
        """Test that remote skill is NOT found at old nested path structure."""
        # Create skill at old nested path: .claude/skills/dsjacobsen/golang-pro/
        skill_dir = tmp_path / "skills" / "dsjacobsen" / "golang-pro"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Golang Pro skill")

        dep = Dependency(type="skill", handle="dsjacobsen/golang-pro")

        # Should NOT find it at the nested path
        assert _is_installed(dep, tmp_path, "local") is False

    def test_remote_skill_requires_skill_md(self, tmp_path):
        """Test that remote skill requires SKILL.md to exist."""
        # Create directory but no SKILL.md
        skill_dir = tmp_path / "skills" / "dsjacobsen:golang-pro"
        skill_dir.mkdir(parents=True)

        dep = Dependency(type="skill", handle="dsjacobsen/golang-pro")

        assert _is_installed(dep, tmp_path, "local") is False

    def test_remote_agent_uses_nested_path(self, tmp_path):
        """Test that remote agent uses nested username/name.md path."""
        # Create agent at: .claude/agents/dsjacobsen/go-reviewer.md
        agent_dir = tmp_path / "agents" / "dsjacobsen"
        agent_dir.mkdir(parents=True)
        (agent_dir / "go-reviewer.md").write_text("# Go Reviewer")

        dep = Dependency(type="agent", handle="dsjacobsen/go-reviewer")

        assert _is_installed(dep, tmp_path, "local") is True

    def test_local_package_uses_flattened_name(self, tmp_path):
        """Test that local package check uses flattened path like skills."""
        # Packages use the same flattened naming as skills
        pkg_dir = tmp_path / "packages" / "kasperjunge:my-toolkit"
        pkg_dir.mkdir(parents=True)

        dep = Dependency(type="package", path="resources/packages/my-toolkit")

        assert _is_installed(dep, tmp_path, "kasperjunge") is True
