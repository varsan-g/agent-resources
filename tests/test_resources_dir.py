"""Tests for resources directory utilities."""

from pathlib import Path

import pytest

from agr.resources import (
    copy_to_resources,
    get_relative_resources_path,
    get_resource_dest_path,
    get_resources_dir,
    is_in_resources_dir,
    resource_exists_in_resources,
    ensure_resources_structure,
    RESOURCES_DIR_NAME,
)


class TestResourcesDir:
    """Tests for get_resources_dir function."""

    def test_get_resources_dir_default(self, tmp_path: Path, monkeypatch):
        """Test getting resources dir with default path."""
        monkeypatch.chdir(tmp_path)
        result = get_resources_dir()
        assert result == tmp_path / RESOURCES_DIR_NAME

    def test_get_resources_dir_custom_base(self, tmp_path: Path):
        """Test getting resources dir with custom base path."""
        result = get_resources_dir(tmp_path)
        assert result == tmp_path / RESOURCES_DIR_NAME


class TestIsInResourcesDir:
    """Tests for is_in_resources_dir function."""

    def test_path_in_resources_dir(self, tmp_path: Path):
        """Test that path inside resources/ returns True."""
        resources_dir = tmp_path / RESOURCES_DIR_NAME / "skills" / "test-skill"
        resources_dir.mkdir(parents=True)

        assert is_in_resources_dir(resources_dir, tmp_path) is True

    def test_path_outside_resources_dir(self, tmp_path: Path):
        """Test that path outside resources/ returns False."""
        other_dir = tmp_path / "some-other-dir" / "skill"
        other_dir.mkdir(parents=True)

        assert is_in_resources_dir(other_dir, tmp_path) is False

    def test_path_is_resources_dir(self, tmp_path: Path):
        """Test that the resources dir itself returns True."""
        resources_dir = tmp_path / RESOURCES_DIR_NAME
        resources_dir.mkdir()

        assert is_in_resources_dir(resources_dir, tmp_path) is True


class TestGetResourceDestPath:
    """Tests for get_resource_dest_path function."""

    def test_skill_path(self, tmp_path: Path):
        """Test destination path for skills (directories)."""
        result = get_resource_dest_path("skill", "my-skill", tmp_path)
        assert result == tmp_path / "resources" / "skills" / "my-skill"

    def test_command_path(self, tmp_path: Path):
        """Test destination path for commands (.md files)."""
        result = get_resource_dest_path("command", "deploy", tmp_path)
        assert result == tmp_path / "resources" / "commands" / "deploy.md"

    def test_agent_path(self, tmp_path: Path):
        """Test destination path for agents (.md files)."""
        result = get_resource_dest_path("agent", "reviewer", tmp_path)
        assert result == tmp_path / "resources" / "agents" / "reviewer.md"

    def test_rule_path(self, tmp_path: Path):
        """Test destination path for rules (.md files)."""
        result = get_resource_dest_path("rule", "formatting", tmp_path)
        assert result == tmp_path / "resources" / "rules" / "formatting.md"

    def test_package_path(self, tmp_path: Path):
        """Test destination path for packages (directories)."""
        result = get_resource_dest_path("package", "my-package", tmp_path)
        assert result == tmp_path / "resources" / "packages" / "my-package"

    def test_command_with_md_extension(self, tmp_path: Path):
        """Test that .md extension is not duplicated."""
        result = get_resource_dest_path("command", "deploy.md", tmp_path)
        assert result == tmp_path / "resources" / "commands" / "deploy.md"


class TestResourceExistsInResources:
    """Tests for resource_exists_in_resources function."""

    def test_skill_exists(self, tmp_path: Path):
        """Test detecting existing skill directory."""
        skill_dir = tmp_path / "resources" / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)

        assert resource_exists_in_resources("skill", "my-skill", tmp_path) is True

    def test_skill_not_exists(self, tmp_path: Path):
        """Test detecting non-existent skill."""
        assert resource_exists_in_resources("skill", "nonexistent", tmp_path) is False

    def test_command_exists(self, tmp_path: Path):
        """Test detecting existing command file."""
        commands_dir = tmp_path / "resources" / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "deploy.md").write_text("# Deploy")

        assert resource_exists_in_resources("command", "deploy", tmp_path) is True


class TestGetRelativeResourcesPath:
    """Tests for get_relative_resources_path function."""

    def test_skill_relative_path(self):
        """Test relative path for skills."""
        result = get_relative_resources_path("skill", "my-skill")
        assert result == "resources/skills/my-skill"

    def test_command_relative_path(self):
        """Test relative path for commands."""
        result = get_relative_resources_path("command", "deploy")
        assert result == "resources/commands/deploy.md"

    def test_package_relative_path(self):
        """Test relative path for packages."""
        result = get_relative_resources_path("package", "my-package")
        assert result == "resources/packages/my-package"


class TestCopyToResources:
    """Tests for copy_to_resources function."""

    def test_copy_skill_directory(self, tmp_path: Path):
        """Test copying a skill directory to resources/."""
        # Create source skill
        source = tmp_path / "my-skill"
        source.mkdir()
        (source / "SKILL.md").write_text("# My Skill")

        result = copy_to_resources(source, "skill", base_path=tmp_path)

        assert result.success is True
        assert result.dest_path == tmp_path / "resources" / "skills" / "my-skill"
        assert result.dest_path.is_dir()
        assert (result.dest_path / "SKILL.md").exists()

    def test_copy_command_file(self, tmp_path: Path):
        """Test copying a command file to resources/."""
        # Create source command
        source = tmp_path / "deploy.md"
        source.write_text("# Deploy Command")

        result = copy_to_resources(source, "command", base_path=tmp_path)

        assert result.success is True
        assert result.dest_path == tmp_path / "resources" / "commands" / "deploy.md"
        assert result.dest_path.is_file()
        assert result.dest_path.read_text() == "# Deploy Command"

    def test_copy_fails_if_exists(self, tmp_path: Path):
        """Test that copy fails if resource already exists."""
        # Create existing resource
        existing = tmp_path / "resources" / "skills" / "my-skill"
        existing.mkdir(parents=True)
        (existing / "SKILL.md").write_text("# Existing")

        # Try to copy new resource
        source = tmp_path / "my-skill"
        source.mkdir()
        (source / "SKILL.md").write_text("# New")

        result = copy_to_resources(source, "skill", base_path=tmp_path)

        assert result.success is False
        assert "already exists" in result.error

    def test_copy_with_force_overwrites(self, tmp_path: Path):
        """Test that copy with force overwrites existing resource."""
        # Create existing resource
        existing = tmp_path / "resources" / "skills" / "my-skill"
        existing.mkdir(parents=True)
        (existing / "SKILL.md").write_text("# Existing")

        # Try to copy new resource with force
        source = tmp_path / "my-skill"
        source.mkdir()
        (source / "SKILL.md").write_text("# New")

        result = copy_to_resources(source, "skill", base_path=tmp_path, force=True)

        assert result.success is True
        assert (result.dest_path / "SKILL.md").read_text() == "# New"

    def test_copy_custom_name(self, tmp_path: Path):
        """Test copying with a custom name."""
        source = tmp_path / "original-name.md"
        source.write_text("# Content")

        result = copy_to_resources(
            source, "command", name="new-name", base_path=tmp_path
        )

        assert result.success is True
        assert result.dest_path.name == "new-name.md"
        assert result.relative_path == "resources/commands/new-name.md"


class TestEnsureResourcesStructure:
    """Tests for ensure_resources_structure function."""

    def test_creates_all_subdirs(self, tmp_path: Path):
        """Test that all resource subdirectories are created."""
        ensure_resources_structure(tmp_path)

        resources_dir = tmp_path / "resources"
        assert (resources_dir / "skills").is_dir()
        assert (resources_dir / "commands").is_dir()
        assert (resources_dir / "agents").is_dir()
        assert (resources_dir / "rules").is_dir()

    def test_idempotent(self, tmp_path: Path):
        """Test that calling multiple times doesn't error."""
        ensure_resources_structure(tmp_path)
        ensure_resources_structure(tmp_path)  # Should not raise

        assert (tmp_path / "resources" / "skills").is_dir()
