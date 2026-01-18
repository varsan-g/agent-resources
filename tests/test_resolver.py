"""Unit tests for remote resource resolution."""

import pytest
from pathlib import Path

from agr.resolver import (
    ResolvedResource,
    ResourceSource,
    resolve_remote_resource,
    parse_remote_agr_toml,
    _extract_resource_name,
)
from agr.fetcher import ResourceType


class TestResolvedResource:
    """Tests for ResolvedResource dataclass."""

    def test_creates_resolved_resource(self):
        """Test creating a ResolvedResource."""
        resource = ResolvedResource(
            name="my-skill",
            resource_type=ResourceType.SKILL,
            path=Path(".claude/skills/my-skill"),
            source=ResourceSource.CLAUDE_DIR,
        )
        assert resource.name == "my-skill"
        assert resource.resource_type == ResourceType.SKILL
        assert resource.source == ResourceSource.CLAUDE_DIR

    def test_resolved_from_agr_toml(self):
        """Test creating a resource resolved from agr.toml."""
        resource = ResolvedResource(
            name="custom-skill",
            resource_type=ResourceType.SKILL,
            path=Path("skills/custom-skill"),
            source=ResourceSource.AGR_TOML,
        )
        assert resource.source == ResourceSource.AGR_TOML


class TestExtractResourceName:
    """Tests for _extract_resource_name function."""

    def test_extracts_simple_command_name(self):
        """Test extracting name from a command path."""
        name = _extract_resource_name("resources/commands/hello-world.md")
        assert name == "hello-world"

    def test_extracts_simple_skill_name(self):
        """Test extracting name from a skill directory path."""
        name = _extract_resource_name("resources/skills/commit")
        assert name == "commit"

    def test_extracts_simple_package_name(self):
        """Test extracting name from a package path."""
        name = _extract_resource_name("resources/packages/python-dev")
        assert name == "python-dev"

    def test_extracts_nested_skill_name_with_colons(self):
        """Test extracting nested name as colon-delimited string."""
        name = _extract_resource_name("resources/skills/product-strategy/growth-hacker")
        assert name == "product-strategy:growth-hacker"

    def test_extracts_deeply_nested_name(self):
        """Test extracting deeply nested path with multiple colons."""
        name = _extract_resource_name("resources/skills/a/b/c")
        assert name == "a:b:c"

    def test_extracts_name_from_md_file_in_nested_path(self):
        """Test extracting name from .md file in nested directory."""
        name = _extract_resource_name("resources/commands/dir/nested-command.md")
        assert name == "dir:nested-command"


class TestParseRemoteAgrToml:
    """Tests for parse_remote_agr_toml function."""

    def test_parses_dependencies_array_with_path(self, tmp_path):
        """Test parsing dependencies array with path entries."""
        agr_toml = tmp_path / "agr.toml"
        agr_toml.write_text("""
dependencies = [
    {path = "resources/commands/hello-world.md", type = "command"},
    {path = "resources/skills/commit", type = "skill"},
]
""")
        result = parse_remote_agr_toml(tmp_path)

        assert "hello-world" in result
        assert result["hello-world"]["path"] == "resources/commands/hello-world.md"
        assert result["hello-world"]["type"] == "command"
        assert "commit" in result
        assert result["commit"]["path"] == "resources/skills/commit"
        assert result["commit"]["type"] == "skill"

    def test_parses_nested_skill_paths(self, tmp_path):
        """Test parsing nested skill paths into colon-delimited names."""
        agr_toml = tmp_path / "agr.toml"
        agr_toml.write_text("""
dependencies = [
    {path = "resources/skills/product-strategy/growth-hacker", type = "skill"},
    {path = "resources/skills/product-strategy/flywheel", type = "skill"},
]
""")
        result = parse_remote_agr_toml(tmp_path)

        assert "product-strategy:growth-hacker" in result
        assert "product-strategy:flywheel" in result
        assert result["product-strategy:growth-hacker"]["path"] == "resources/skills/product-strategy/growth-hacker"

    def test_parses_package_type(self, tmp_path):
        """Test parsing package type entries."""
        agr_toml = tmp_path / "agr.toml"
        agr_toml.write_text("""
dependencies = [
    {path = "resources/packages/python-dev", type = "package"},
]
""")
        result = parse_remote_agr_toml(tmp_path)

        assert "python-dev" in result
        assert result["python-dev"]["type"] == "package"
        assert result["python-dev"]["package"] is True

    def test_skips_remote_dependencies_with_handle(self, tmp_path):
        """Test that entries with 'handle' (remote deps) are skipped."""
        agr_toml = tmp_path / "agr.toml"
        agr_toml.write_text("""
dependencies = [
    {path = "resources/skills/local-skill", type = "skill"},
    {handle = "dsjacobsen/golang-pro", type = "skill"},
    {handle = "kasperjunge/commit", type = "skill"},
]
""")
        result = parse_remote_agr_toml(tmp_path)

        assert "local-skill" in result
        # Remote dependencies should NOT be in result
        assert "dsjacobsen/golang-pro" not in result
        assert "golang-pro" not in result
        assert "kasperjunge/commit" not in result
        assert "commit" not in result
        assert len(result) == 1

    def test_returns_empty_when_no_agr_toml(self, tmp_path):
        """Test returning empty dict when no agr.toml exists."""
        result = parse_remote_agr_toml(tmp_path)
        assert result == {}

    def test_returns_empty_when_no_dependencies(self, tmp_path):
        """Test returning empty dict when only metadata exists."""
        agr_toml = tmp_path / "agr.toml"
        agr_toml.write_text("""
[project]
name = "my-resources"
""")
        result = parse_remote_agr_toml(tmp_path)
        assert result == {}

    def test_returns_empty_when_dependencies_has_only_remotes(self, tmp_path):
        """Test returning empty dict when dependencies only contain remote handles."""
        agr_toml = tmp_path / "agr.toml"
        agr_toml.write_text("""
dependencies = [
    {handle = "dsjacobsen/golang-pro", type = "skill"},
]
""")
        result = parse_remote_agr_toml(tmp_path)
        assert result == {}


class TestResolveRemoteResource:
    """Tests for resolve_remote_resource function."""

    def test_resolves_from_agr_toml_first(self, tmp_path):
        """Test that agr.toml definitions take priority over .claude/."""
        # Create agr.toml with resource definition using dependencies array
        # Path follows the expected resources/{type}/{name} pattern
        agr_toml = tmp_path / "agr.toml"
        agr_toml.write_text("""
dependencies = [
    {path = "resources/skills/my-skill", type = "skill"},
]
""")

        # Also create in .claude/ (should be ignored since agr.toml has priority)
        claude_skill = tmp_path / ".claude" / "skills" / "my-skill"
        claude_skill.mkdir(parents=True)
        (claude_skill / "SKILL.md").write_text("# Skill from .claude")

        # Also create in the agr.toml specified path
        agr_skill = tmp_path / "resources" / "skills" / "my-skill"
        agr_skill.mkdir(parents=True)
        (agr_skill / "SKILL.md").write_text("# Skill from resources/")

        result = resolve_remote_resource(tmp_path, "my-skill")

        assert result is not None
        assert result.source == ResourceSource.AGR_TOML
        assert result.path == Path("resources/skills/my-skill")

    def test_falls_back_to_claude_dir(self, tmp_path):
        """Test fallback to .claude/ when not in agr.toml."""
        # Only create in .claude/
        claude_skill = tmp_path / ".claude" / "skills" / "my-skill"
        claude_skill.mkdir(parents=True)
        (claude_skill / "SKILL.md").write_text("# Skill from .claude")

        result = resolve_remote_resource(tmp_path, "my-skill")

        assert result is not None
        assert result.source == ResourceSource.CLAUDE_DIR
        assert result.resource_type == ResourceType.SKILL

    def test_returns_none_when_not_found(self, tmp_path):
        """Test returning None when resource doesn't exist."""
        result = resolve_remote_resource(tmp_path, "nonexistent")
        assert result is None

    def test_resolves_command_from_claude_dir(self, tmp_path):
        """Test resolving a command from .claude/ directory."""
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "my-cmd.md").write_text("# My Command")

        result = resolve_remote_resource(tmp_path, "my-cmd")

        assert result is not None
        assert result.resource_type == ResourceType.COMMAND
        assert result.source == ResourceSource.CLAUDE_DIR

    def test_resolves_agent_from_claude_dir(self, tmp_path):
        """Test resolving an agent from .claude/ directory."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "my-agent.md").write_text("# My Agent")

        result = resolve_remote_resource(tmp_path, "my-agent")

        assert result is not None
        assert result.resource_type == ResourceType.AGENT
        assert result.source == ResourceSource.CLAUDE_DIR

    def test_resolves_package_from_agr_toml(self, tmp_path):
        """Test resolving a package from agr.toml."""
        agr_toml = tmp_path / "agr.toml"
        agr_toml.write_text("""
dependencies = [
    {path = "resources/packages/my-toolkit", type = "package"},
]
""")

        # Create package structure
        pkg_dir = tmp_path / "resources" / "packages" / "my-toolkit" / "skills" / "toolkit-skill"
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "SKILL.md").write_text("# Toolkit Skill")

        result = resolve_remote_resource(tmp_path, "my-toolkit")

        assert result is not None
        assert result.source == ResourceSource.AGR_TOML
        assert result.is_package is True

    def test_resolves_package_from_claude_bundle(self, tmp_path):
        """Test resolving a package/bundle from .claude/ directory."""
        # Create bundle structure in .claude/
        bundle_skill = tmp_path / ".claude" / "skills" / "my-bundle" / "bundle-skill"
        bundle_skill.mkdir(parents=True)
        (bundle_skill / "SKILL.md").write_text("# Bundle Skill")

        result = resolve_remote_resource(tmp_path, "my-bundle")

        assert result is not None
        assert result.source == ResourceSource.CLAUDE_DIR
        assert result.is_package is True

    def test_type_override_from_agr_toml(self, tmp_path):
        """Test that type specified in agr.toml is used."""
        agr_toml = tmp_path / "agr.toml"
        agr_toml.write_text("""
dependencies = [
    {path = "resources/skills/helper", type = "skill"},
]
""")

        # Create the skill at the path specified
        skill_dir = tmp_path / "resources" / "skills" / "helper"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Helper")

        result = resolve_remote_resource(tmp_path, "helper")

        assert result is not None
        assert result.resource_type == ResourceType.SKILL
        assert result.source == ResourceSource.AGR_TOML

    def test_resolves_nested_skill_from_agr_toml(self, tmp_path):
        """Test resolving a nested skill with colon-delimited name."""
        agr_toml = tmp_path / "agr.toml"
        agr_toml.write_text("""
dependencies = [
    {path = "resources/skills/product-strategy/growth-hacker", type = "skill"},
]
""")

        # Create the nested skill
        skill_dir = tmp_path / "resources" / "skills" / "product-strategy" / "growth-hacker"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Growth Hacker Skill")

        # Query using colon-delimited name
        result = resolve_remote_resource(tmp_path, "product-strategy:growth-hacker")

        assert result is not None
        assert result.source == ResourceSource.AGR_TOML
        assert result.resource_type == ResourceType.SKILL
        assert result.path == Path("resources/skills/product-strategy/growth-hacker")

    def test_agr_toml_priority_over_claude_dir(self, tmp_path):
        """Test that agr.toml wins when same resource exists in both."""
        # Create agr.toml pointing to custom location
        agr_toml = tmp_path / "agr.toml"
        agr_toml.write_text("""
dependencies = [
    {path = "resources/skills/my-skill", type = "skill"},
]
""")

        # Create in both locations
        agr_skill = tmp_path / "resources" / "skills" / "my-skill"
        agr_skill.mkdir(parents=True)
        (agr_skill / "SKILL.md").write_text("# From agr.toml path")

        claude_skill = tmp_path / ".claude" / "skills" / "my-skill"
        claude_skill.mkdir(parents=True)
        (claude_skill / "SKILL.md").write_text("# From .claude")

        result = resolve_remote_resource(tmp_path, "my-skill")

        assert result is not None
        assert result.source == ResourceSource.AGR_TOML
        assert result.path == Path("resources/skills/my-skill")
