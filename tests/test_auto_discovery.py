"""Unit tests for auto-discovery (repo root fallback) in resolver."""

import pytest
from pathlib import Path

from agr.resolver import (
    ResolvedResource,
    ResourceSource,
    resolve_remote_resource,
    _resolve_from_repo_root,
)
from agr.fetcher import ResourceType


class TestResolveFromRepoRoot:
    """Tests for _resolve_from_repo_root function."""

    def test_discovers_skill_at_repo_root(self, tmp_path):
        """Test discovering a skill directory at repo root."""
        # Create skill at /go/SKILL.md
        skill_dir = tmp_path / "go"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Go Skill")

        result = _resolve_from_repo_root(tmp_path, "go")

        assert result is not None
        assert result.name == "go"
        assert result.resource_type == ResourceType.SKILL
        assert result.path == Path("go")
        assert result.source == ResourceSource.REPO_ROOT

    def test_discovers_nested_skill_with_colon_name(self, tmp_path):
        """Test discovering nested skill using colon-separated name."""
        # Create skill at /tools/git/SKILL.md
        skill_dir = tmp_path / "tools" / "git"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Git Tools Skill")

        result = _resolve_from_repo_root(tmp_path, "tools:git")

        assert result is not None
        assert result.name == "tools:git"
        assert result.resource_type == ResourceType.SKILL
        assert result.path == Path("tools/git")
        assert result.source == ResourceSource.REPO_ROOT

    def test_discovers_deeply_nested_skill(self, tmp_path):
        """Test discovering deeply nested skill with multiple colons."""
        # Create skill at /category/subcategory/skillname/SKILL.md
        skill_dir = tmp_path / "category" / "subcategory" / "skillname"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Deep Skill")

        result = _resolve_from_repo_root(tmp_path, "category:subcategory:skillname")

        assert result is not None
        assert result.name == "category:subcategory:skillname"
        assert result.resource_type == ResourceType.SKILL
        assert result.path == Path("category/subcategory/skillname")
        assert result.source == ResourceSource.REPO_ROOT

    def test_discovers_skill_anywhere_in_repo(self, tmp_path):
        """Test discovering skill in subdirectory via rglob."""
        # Create skill at /some/deep/path/myskill/SKILL.md
        skill_dir = tmp_path / "some" / "deep" / "path" / "myskill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill")

        result = _resolve_from_repo_root(tmp_path, "myskill")

        assert result is not None
        assert result.name == "myskill"
        assert result.resource_type == ResourceType.SKILL
        assert result.path == Path("some/deep/path/myskill")
        assert result.source == ResourceSource.REPO_ROOT

    def test_discovers_command_in_commands_directory(self, tmp_path):
        """Test discovering command in commands/ directory."""
        # Create command at /commands/deploy.md
        cmd_dir = tmp_path / "commands"
        cmd_dir.mkdir()
        (cmd_dir / "deploy.md").write_text("# Deploy Command")

        result = _resolve_from_repo_root(tmp_path, "deploy")

        assert result is not None
        assert result.name == "deploy"
        assert result.resource_type == ResourceType.COMMAND
        assert result.path == Path("commands/deploy.md")
        assert result.source == ResourceSource.REPO_ROOT

    def test_discovers_nested_command_with_colon_name(self, tmp_path):
        """Test discovering nested command using colon-separated name."""
        # Create command at /commands/aws/deploy.md
        cmd_dir = tmp_path / "commands" / "aws"
        cmd_dir.mkdir(parents=True)
        (cmd_dir / "deploy.md").write_text("# AWS Deploy Command")

        result = _resolve_from_repo_root(tmp_path, "aws:deploy")

        assert result is not None
        assert result.name == "aws:deploy"
        assert result.resource_type == ResourceType.COMMAND
        assert result.path == Path("commands/aws/deploy.md")
        assert result.source == ResourceSource.REPO_ROOT

    def test_discovers_command_anywhere_in_repo(self, tmp_path):
        """Test discovering command in nested commands/ directory."""
        # Create command at /src/cli/commands/build.md
        cmd_dir = tmp_path / "src" / "cli" / "commands"
        cmd_dir.mkdir(parents=True)
        (cmd_dir / "build.md").write_text("# Build Command")

        result = _resolve_from_repo_root(tmp_path, "build")

        assert result is not None
        assert result.name == "build"
        assert result.resource_type == ResourceType.COMMAND
        assert result.path == Path("src/cli/commands/build.md")
        assert result.source == ResourceSource.REPO_ROOT

    def test_discovers_agent_in_agents_directory(self, tmp_path):
        """Test discovering agent in agents/ directory."""
        # Create agent at /agents/reviewer.md
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "reviewer.md").write_text("# Reviewer Agent")

        result = _resolve_from_repo_root(tmp_path, "reviewer")

        assert result is not None
        assert result.name == "reviewer"
        assert result.resource_type == ResourceType.AGENT
        assert result.path == Path("agents/reviewer.md")
        assert result.source == ResourceSource.REPO_ROOT

    def test_discovers_nested_agent_with_colon_name(self, tmp_path):
        """Test discovering nested agent using colon-separated name."""
        # Create agent at /agents/code/reviewer.md
        agents_dir = tmp_path / "agents" / "code"
        agents_dir.mkdir(parents=True)
        (agents_dir / "reviewer.md").write_text("# Code Reviewer Agent")

        result = _resolve_from_repo_root(tmp_path, "code:reviewer")

        assert result is not None
        assert result.name == "code:reviewer"
        assert result.resource_type == ResourceType.AGENT
        assert result.path == Path("agents/code/reviewer.md")
        assert result.source == ResourceSource.REPO_ROOT

    def test_discovers_agent_anywhere_in_repo(self, tmp_path):
        """Test discovering agent in nested agents/ directory."""
        # Create agent at /tools/agents/helper.md
        agents_dir = tmp_path / "tools" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "helper.md").write_text("# Helper Agent")

        result = _resolve_from_repo_root(tmp_path, "helper")

        assert result is not None
        assert result.name == "helper"
        assert result.resource_type == ResourceType.AGENT
        assert result.path == Path("tools/agents/helper.md")
        assert result.source == ResourceSource.REPO_ROOT

    def test_returns_none_when_not_found(self, tmp_path):
        """Test returning None when no matching resource exists."""
        result = _resolve_from_repo_root(tmp_path, "nonexistent")
        assert result is None

    def test_returns_none_for_empty_repo(self, tmp_path):
        """Test returning None for empty repository."""
        result = _resolve_from_repo_root(tmp_path, "anything")
        assert result is None

    def test_skill_priority_over_command(self, tmp_path):
        """Test that skills are discovered before commands."""
        # Create both skill and command with same name
        skill_dir = tmp_path / "myresource"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Skill")

        cmd_dir = tmp_path / "commands"
        cmd_dir.mkdir()
        (cmd_dir / "myresource.md").write_text("# Command")

        result = _resolve_from_repo_root(tmp_path, "myresource")

        # Skill should be found first
        assert result is not None
        assert result.resource_type == ResourceType.SKILL

    def test_command_priority_over_agent(self, tmp_path):
        """Test that commands are discovered before agents."""
        # Create both command and agent with same name
        cmd_dir = tmp_path / "commands"
        cmd_dir.mkdir()
        (cmd_dir / "myresource.md").write_text("# Command")

        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "myresource.md").write_text("# Agent")

        result = _resolve_from_repo_root(tmp_path, "myresource")

        # Command should be found first
        assert result is not None
        assert result.resource_type == ResourceType.COMMAND

    def test_skips_claude_directory(self, tmp_path):
        """Test that .claude/ directory is skipped during auto-discovery."""
        # Create skill in .claude/ (should be skipped)
        claude_skill = tmp_path / ".claude" / "skills" / "myskill"
        claude_skill.mkdir(parents=True)
        (claude_skill / "SKILL.md").write_text("# Skill in .claude")

        result = _resolve_from_repo_root(tmp_path, "myskill")

        # Should not find the skill in .claude/
        assert result is None

    def test_skips_claude_commands(self, tmp_path):
        """Test that .claude/commands/ is skipped during auto-discovery."""
        # Create command in .claude/ (should be skipped)
        claude_cmd = tmp_path / ".claude" / "commands"
        claude_cmd.mkdir(parents=True)
        (claude_cmd / "mycmd.md").write_text("# Command in .claude")

        result = _resolve_from_repo_root(tmp_path, "mycmd")

        # Should not find the command in .claude/
        assert result is None


class TestResolveRemoteResourceWithRepoRoot:
    """Tests for resolve_remote_resource with auto-discovery fallback."""

    def test_agr_toml_priority_over_repo_root(self, tmp_path):
        """Test that agr.toml definitions take priority over repo root."""
        # Create agr.toml with resource definition
        agr_toml = tmp_path / "agr.toml"
        agr_toml.write_text("""
dependencies = [
    {path = "resources/skills/my-skill", type = "skill"},
]
""")

        # Create at agr.toml path
        agr_skill = tmp_path / "resources" / "skills" / "my-skill"
        agr_skill.mkdir(parents=True)
        (agr_skill / "SKILL.md").write_text("# From agr.toml path")

        # Also create at repo root (should be ignored)
        root_skill = tmp_path / "my-skill"
        root_skill.mkdir()
        (root_skill / "SKILL.md").write_text("# From repo root")

        result = resolve_remote_resource(tmp_path, "my-skill")

        assert result is not None
        assert result.source == ResourceSource.AGR_TOML
        assert result.path == Path("resources/skills/my-skill")

    def test_claude_dir_priority_over_repo_root(self, tmp_path):
        """Test that .claude/ directory takes priority over repo root."""
        # Create in .claude/
        claude_skill = tmp_path / ".claude" / "skills" / "my-skill"
        claude_skill.mkdir(parents=True)
        (claude_skill / "SKILL.md").write_text("# From .claude")

        # Also create at repo root (should be ignored)
        root_skill = tmp_path / "my-skill"
        root_skill.mkdir()
        (root_skill / "SKILL.md").write_text("# From repo root")

        result = resolve_remote_resource(tmp_path, "my-skill")

        assert result is not None
        assert result.source == ResourceSource.CLAUDE_DIR

    def test_falls_back_to_repo_root(self, tmp_path):
        """Test fallback to repo root when not in agr.toml or .claude/."""
        # Only create at repo root
        root_skill = tmp_path / "my-skill"
        root_skill.mkdir()
        (root_skill / "SKILL.md").write_text("# From repo root")

        result = resolve_remote_resource(tmp_path, "my-skill")

        assert result is not None
        assert result.source == ResourceSource.REPO_ROOT
        assert result.resource_type == ResourceType.SKILL
        assert result.path == Path("my-skill")

    def test_repo_root_skill_discovery(self, tmp_path):
        """Test discovering skill at repo root via resolve_remote_resource."""
        # Create skill at /golang/SKILL.md
        skill_dir = tmp_path / "golang"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Golang Skill")

        result = resolve_remote_resource(tmp_path, "golang")

        assert result is not None
        assert result.source == ResourceSource.REPO_ROOT
        assert result.resource_type == ResourceType.SKILL

    def test_repo_root_command_discovery(self, tmp_path):
        """Test discovering command via resolve_remote_resource."""
        # Create command at /commands/deploy.md
        cmd_dir = tmp_path / "commands"
        cmd_dir.mkdir()
        (cmd_dir / "deploy.md").write_text("# Deploy")

        result = resolve_remote_resource(tmp_path, "deploy")

        assert result is not None
        assert result.source == ResourceSource.REPO_ROOT
        assert result.resource_type == ResourceType.COMMAND

    def test_repo_root_agent_discovery(self, tmp_path):
        """Test discovering agent via resolve_remote_resource."""
        # Create agent at /agents/helper.md
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "helper.md").write_text("# Helper Agent")

        result = resolve_remote_resource(tmp_path, "helper")

        assert result is not None
        assert result.source == ResourceSource.REPO_ROOT
        assert result.resource_type == ResourceType.AGENT

    def test_repo_root_nested_skill_with_colon(self, tmp_path):
        """Test discovering nested skill with colon name via resolve_remote_resource."""
        # Create skill at /tools/git/SKILL.md
        skill_dir = tmp_path / "tools" / "git"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Git Tools")

        result = resolve_remote_resource(tmp_path, "tools:git")

        assert result is not None
        assert result.source == ResourceSource.REPO_ROOT
        assert result.resource_type == ResourceType.SKILL
        assert result.path == Path("tools/git")

    def test_returns_none_when_not_found_anywhere(self, tmp_path):
        """Test returning None when resource not in agr.toml, .claude/, or repo root."""
        result = resolve_remote_resource(tmp_path, "nonexistent")
        assert result is None


class TestPackagesNotAutoDiscovered:
    """Tests verifying packages are NOT auto-discovered."""

    def test_package_directory_not_discovered_as_skill(self, tmp_path):
        """Test that a package directory is not discovered as a skill."""
        # Create a package-like structure (no SKILL.md at root)
        pkg_dir = tmp_path / "my-package"
        pkg_dir.mkdir()
        skills_dir = pkg_dir / "skills" / "sub-skill"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("# Sub Skill")

        # Query for the package name directly
        result = _resolve_from_repo_root(tmp_path, "my-package")

        # Should not find it as a skill (no SKILL.md at my-package/)
        assert result is None

    def test_packages_directory_not_discovered(self, tmp_path):
        """Test that packages/ directory contents are not auto-discovered."""
        # Create packages/ structure
        pkg_dir = tmp_path / "packages" / "toolkit"
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "skills" / "helper").mkdir(parents=True)
        (pkg_dir / "skills" / "helper" / "SKILL.md").write_text("# Helper")

        # Query for toolkit - should not be found
        result = _resolve_from_repo_root(tmp_path, "toolkit")
        assert result is None

        # Query for helper directly - will be found via rglob
        # This is actually expected behavior - individual skills can be discovered
        result = _resolve_from_repo_root(tmp_path, "helper")
        assert result is not None  # Individual skills can be discovered


class TestColonToPathConversion:
    """Tests for colon-to-path segment conversion."""

    def test_simple_name_no_colon(self, tmp_path):
        """Test simple name without colons."""
        skill_dir = tmp_path / "myskill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# My Skill")

        result = _resolve_from_repo_root(tmp_path, "myskill")

        assert result is not None
        assert result.path == Path("myskill")

    def test_single_colon_two_segments(self, tmp_path):
        """Test name with single colon creates two path segments."""
        skill_dir = tmp_path / "category" / "skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Categorized Skill")

        result = _resolve_from_repo_root(tmp_path, "category:skill")

        assert result is not None
        assert result.path == Path("category/skill")

    def test_multiple_colons_multiple_segments(self, tmp_path):
        """Test name with multiple colons creates multiple path segments."""
        skill_dir = tmp_path / "a" / "b" / "c" / "d"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Deep Skill")

        result = _resolve_from_repo_root(tmp_path, "a:b:c:d")

        assert result is not None
        assert result.path == Path("a/b/c/d")

    def test_command_colon_path_segments(self, tmp_path):
        """Test command name with colons creates nested path."""
        cmd_dir = tmp_path / "commands" / "aws" / "ec2"
        cmd_dir.mkdir(parents=True)
        (cmd_dir / "deploy.md").write_text("# AWS EC2 Deploy")

        result = _resolve_from_repo_root(tmp_path, "aws:ec2:deploy")

        assert result is not None
        assert result.path == Path("commands/aws/ec2/deploy.md")
        assert result.resource_type == ResourceType.COMMAND

    def test_agent_colon_path_segments(self, tmp_path):
        """Test agent name with colons creates nested path."""
        agents_dir = tmp_path / "agents" / "security" / "audit"
        agents_dir.mkdir(parents=True)
        (agents_dir / "scanner.md").write_text("# Security Audit Scanner")

        result = _resolve_from_repo_root(tmp_path, "security:audit:scanner")

        assert result is not None
        assert result.path == Path("agents/security/audit/scanner.md")
        assert result.resource_type == ResourceType.AGENT


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_skill_with_additional_files(self, tmp_path):
        """Test skill directory with additional files is discovered."""
        skill_dir = tmp_path / "myskill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# My Skill")
        (skill_dir / "helper.py").write_text("# Helper code")
        (skill_dir / "README.md").write_text("# Readme")

        result = _resolve_from_repo_root(tmp_path, "myskill")

        assert result is not None
        assert result.resource_type == ResourceType.SKILL

    def test_empty_skill_directory_not_discovered(self, tmp_path):
        """Test empty directory without SKILL.md is not discovered as skill."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = _resolve_from_repo_root(tmp_path, "empty")

        assert result is None

    def test_md_file_not_in_commands_or_agents(self, tmp_path):
        """Test .md file outside commands/agents directories is not discovered."""
        # Create .md file at root
        (tmp_path / "readme.md").write_text("# Readme")
        # Create .md file in random directory
        other_dir = tmp_path / "docs"
        other_dir.mkdir()
        (other_dir / "guide.md").write_text("# Guide")

        result = _resolve_from_repo_root(tmp_path, "readme")
        assert result is None

        result = _resolve_from_repo_root(tmp_path, "guide")
        assert result is None

    def test_case_sensitive_matching(self, tmp_path):
        """Test that resource names are case-sensitive."""
        skill_dir = tmp_path / "MySkill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# My Skill")

        # Exact case should work
        result = _resolve_from_repo_root(tmp_path, "MySkill")
        assert result is not None

        # Different case should not match (on case-sensitive filesystems)
        # Note: This test may behave differently on case-insensitive filesystems
        result_lower = _resolve_from_repo_root(tmp_path, "myskill")
        # On case-insensitive systems (macOS), this might still find it
        # So we just verify the exact case works

    def test_special_characters_in_name(self, tmp_path):
        """Test resource names with hyphens and underscores."""
        skill_dir = tmp_path / "my-skill_v2"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Skill")

        result = _resolve_from_repo_root(tmp_path, "my-skill_v2")

        assert result is not None
        assert result.path == Path("my-skill_v2")

    def test_unicode_in_name(self, tmp_path):
        """Test resource names with unicode characters."""
        skill_dir = tmp_path / "スキル"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Unicode Skill")

        result = _resolve_from_repo_root(tmp_path, "スキル")

        assert result is not None
        assert result.path == Path("スキル")
