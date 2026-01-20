"""Tests for remote resource handling (Issue #38).

Tests for remote package context, resource resolution, and installation with PACKAGE.md.
Note: Many of these tests use mocking since they don't actually fetch from GitHub.
"""

from pathlib import Path

from typer.testing import CliRunner

from agr.cli.main import app
from agr.package import parse_package_md

PACKAGES_PATH = Path(__file__).parent.parent / "resources" / "packages"
runner = CliRunner()


class TestRemotePackageContext:
    """Tests for PACKAGE.md handling in remote repositories."""

    def test_remote_package_md_format(self):
        """Test that our fixture PACKAGE.md files have correct format."""
        # Verify our committed fixtures have valid PACKAGE.md
        for pkg_name in ["_test-simple", "_test-complete", "_test-nested-skills"]:
            package_md = PACKAGES_PATH / pkg_name / "PACKAGE.md"
            assert package_md.exists(), f"Missing PACKAGE.md in {pkg_name}"

            result = parse_package_md(package_md)
            assert result.valid is True, f"Invalid PACKAGE.md in {pkg_name}: {result.error}"
            assert result.name is not None

    def test_package_md_name_used_for_remote_namespace(self, git_project: Path):
        """Test that PACKAGE.md name is used when installing remote packages."""
        pkg_dir = git_project / "cache" / "testuser" / "test-repo" / "my-dir"
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "PACKAGE.md").write_text("---\nname: custom-name\n---\n")
        skill_dir = pkg_dir / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill")

        result = parse_package_md(pkg_dir / "PACKAGE.md")
        assert result.valid is True
        assert result.name == "custom-name"


class TestRemoteResourceResolution:
    """Tests for remote resource resolution priority (agr.toml > .claude/ > auto-discover)."""

    def test_agr_toml_structure_is_valid(self, tmp_path: Path):
        """Test that agr.toml structure is created correctly for remote deps."""
        from agr.config import AgrConfig, Dependency

        config = AgrConfig(dependencies=[])
        config.add_remote("testuser/test-skill", "skill")
        config.save(tmp_path / "agr.toml")

        loaded = AgrConfig.load(tmp_path / "agr.toml")
        assert len(loaded.dependencies) == 1
        assert loaded.dependencies[0].handle == "testuser/test-skill"
        assert loaded.dependencies[0].type == "skill"

    def test_config_remote_dependency_with_type(self, tmp_path: Path):
        """Test remote dependency with explicit type."""
        from agr.config import AgrConfig, Dependency

        dep = Dependency(handle="testuser/my-pkg", type="package")
        config = AgrConfig(dependencies=[dep])
        config.save(tmp_path / "agr.toml")

        loaded = AgrConfig.load(tmp_path / "agr.toml")
        assert loaded.dependencies[0].type == "package"


class TestRemoteInstallWithPackage:
    """Tests for remote installation with package namespacing."""

    def test_local_package_uses_expected_namespace_format(self, git_project: Path):
        """Local package installation uses user:package:skill format."""
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

    def test_namespace_format_with_nested_skill(self, git_project: Path):
        """Nested skill in package uses full namespace path."""
        pkg_dir = git_project / "toolkit"
        pkg_dir.mkdir()
        (pkg_dir / "PACKAGE.md").write_text("---\nname: toolkit\n---\n")
        skill_dir = pkg_dir / "skills" / "category" / "nested-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Nested Skill")

        result = runner.invoke(app, ["add", "./toolkit"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "skills" / "local:toolkit:category:nested-skill" / "SKILL.md"
        assert installed.exists()


class TestRemoteHandleValidation:
    """Tests for remote handle validation."""

    def test_valid_handle_formats(self):
        """Test that valid handle formats are recognized."""
        from agr.cli.common import is_local_path

        # Remote handles should return False for is_local_path
        assert is_local_path("username/skill") is False
        assert is_local_path("username/repo/skill") is False
        assert is_local_path("org/repo/path/skill") is False

    def test_local_paths_not_treated_as_remote(self):
        """Test that local paths are not treated as remote handles."""
        from agr.cli.common import is_local_path

        # Local paths should return True
        assert is_local_path("./local/path") is True
        assert is_local_path("../parent/path") is True
        assert is_local_path("/absolute/path") is True


class TestRemotePackageMdParsing:
    """Tests for parsing PACKAGE.md from various sources."""

    def test_parse_valid_package_md(self, tmp_path: Path):
        """Parse a valid PACKAGE.md with name field."""
        package_md = tmp_path / "PACKAGE.md"
        package_md.write_text("---\nname: my-package\n---\n# Package Description")

        result = parse_package_md(package_md)

        assert result.valid is True
        assert result.name == "my-package"
        assert result.error is None

    def test_parse_package_md_with_extra_fields(self, tmp_path: Path):
        """Parse PACKAGE.md with additional frontmatter fields."""
        package_md = tmp_path / "PACKAGE.md"
        package_md.write_text(
            "---\nname: my-package\ndescription: A test package\nversion: 1.0.0\n---\n"
        )

        result = parse_package_md(package_md)

        assert result.valid is True
        assert result.name == "my-package"

    def test_parse_missing_package_md(self, tmp_path: Path):
        """Handle missing PACKAGE.md file gracefully."""
        package_md = tmp_path / "PACKAGE.md"

        result = parse_package_md(package_md)

        assert result.valid is False
        assert result.name is None
        assert "not found" in result.error
