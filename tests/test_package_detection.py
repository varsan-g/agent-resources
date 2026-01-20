"""Tests for PACKAGE.md detection and validation (Issue #38).

Tests the behavior when PACKAGE.md is present, missing, or invalid.
"""

from pathlib import Path

from typer.testing import CliRunner

from agr.cli.main import app
from agr.cli.add import _detect_local_type
from agr.package import parse_package_md

PACKAGES_PATH = Path(__file__).parent.parent / "resources" / "packages"
runner = CliRunner()


class TestPackageMdDetection:
    """Tests for directory detection as package when PACKAGE.md present."""

    def test_directory_with_package_md_detected_as_package(self, tmp_path: Path):
        """Directory with PACKAGE.md is detected as package type."""
        pkg_dir = tmp_path / "my-pkg"
        pkg_dir.mkdir()
        (pkg_dir / "PACKAGE.md").write_text("---\nname: my-pkg\n---\n")

        result = _detect_local_type(pkg_dir)
        assert result == "package"

    def test_directory_without_package_md_not_detected_as_package(self, tmp_path: Path):
        """Directory without PACKAGE.md is NOT auto-detected as package."""
        pkg_dir = tmp_path / "my-dir"
        pkg_dir.mkdir()
        skills_dir = pkg_dir / "skills" / "my-skill"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("# Skill")

        result = _detect_local_type(pkg_dir)
        assert result is None  # Not "package"

    def test_package_md_takes_priority_over_skill_md(self, tmp_path: Path):
        """PACKAGE.md detection takes priority over SKILL.md in same directory."""
        pkg_dir = tmp_path / "dual-markers"
        pkg_dir.mkdir()
        (pkg_dir / "PACKAGE.md").write_text("---\nname: my-pkg\n---\n")
        (pkg_dir / "SKILL.md").write_text("# Skill")

        result = _detect_local_type(pkg_dir)
        assert result == "package"


class TestPackageMdNameExtraction:
    """Tests for extracting package name from PACKAGE.md frontmatter."""

    def test_uses_name_from_package_md(self, git_project: Path):
        """Package uses name from PACKAGE.md, not directory name."""
        pkg_dir = git_project / "directory-name"
        pkg_dir.mkdir()
        (pkg_dir / "PACKAGE.md").write_text("---\nname: package-name\n---\n")
        skill_dir = pkg_dir / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill")

        result = runner.invoke(app, ["add", "./directory-name"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "skills" / "local:package-name:my-skill" / "SKILL.md"
        assert installed.exists()
        wrong = git_project / ".claude" / "skills" / "local:directory-name:my-skill"
        assert not wrong.exists()

    def test_name_with_hyphen_extracted_correctly(self, tmp_path: Path):
        """Package names with hyphens are extracted correctly."""
        package_md = tmp_path / "PACKAGE.md"
        package_md.write_text("---\nname: my-cool-package\n---\n")

        result = parse_package_md(package_md)
        assert result.valid is True
        assert result.name == "my-cool-package"

    def test_name_with_underscore_extracted_correctly(self, tmp_path: Path):
        """Package names with underscores are extracted correctly."""
        package_md = tmp_path / "PACKAGE.md"
        package_md.write_text("---\nname: my_cool_package\n---\n")

        result = parse_package_md(package_md)
        assert result.valid is True
        assert result.name == "my_cool_package"


class TestPackageMdValidation:
    """Tests for PACKAGE.md validation errors."""

    def test_missing_frontmatter_errors(self, git_project: Path):
        """PACKAGE.md without frontmatter produces error."""
        pkg_dir = git_project / "bad-pkg"
        pkg_dir.mkdir()
        (pkg_dir / "PACKAGE.md").write_text("# Just content, no frontmatter")
        skill_dir = pkg_dir / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Skill")

        result = runner.invoke(app, ["add", "./bad-pkg"])

        assert result.exit_code == 1
        assert "Invalid PACKAGE.md" in result.output

    def test_missing_name_field_errors(self, git_project: Path):
        """PACKAGE.md without name field produces error."""
        pkg_dir = git_project / "bad-pkg"
        pkg_dir.mkdir()
        (pkg_dir / "PACKAGE.md").write_text("---\ndescription: missing name\n---\n")
        skill_dir = pkg_dir / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Skill")

        result = runner.invoke(app, ["add", "./bad-pkg"])

        assert result.exit_code == 1
        assert "Invalid PACKAGE.md" in result.output

    def test_empty_name_field_errors(self, git_project: Path):
        """PACKAGE.md with empty name field produces error."""
        pkg_dir = git_project / "bad-pkg"
        pkg_dir.mkdir()
        (pkg_dir / "PACKAGE.md").write_text("---\nname:\n---\n")
        skill_dir = pkg_dir / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Skill")

        result = runner.invoke(app, ["add", "./bad-pkg"])

        assert result.exit_code == 1
        assert "Invalid PACKAGE.md" in result.output


class TestCommittedFixturesWithPackageMd:
    """Tests using committed fixtures that have PACKAGE.md."""

    def test_test_simple_has_package_md(self):
        """_test-simple fixture has valid PACKAGE.md."""
        package_md = PACKAGES_PATH / "_test-simple" / "PACKAGE.md"
        assert package_md.exists()

        result = parse_package_md(package_md)
        assert result.valid is True
        assert result.name == "test-simple"

    def test_test_complete_has_package_md(self):
        """_test-complete fixture has valid PACKAGE.md."""
        package_md = PACKAGES_PATH / "_test-complete" / "PACKAGE.md"
        assert package_md.exists()

        result = parse_package_md(package_md)
        assert result.valid is True
        assert result.name == "test-complete"

    def test_test_nested_skills_has_package_md(self):
        """_test-nested-skills fixture has valid PACKAGE.md."""
        package_md = PACKAGES_PATH / "_test-nested-skills" / "PACKAGE.md"
        assert package_md.exists()

        result = parse_package_md(package_md)
        assert result.valid is True
        assert result.name == "test-nested-skills"

    def test_test_commands_only_has_package_md(self):
        """_test-commands-only fixture has valid PACKAGE.md."""
        package_md = PACKAGES_PATH / "_test-commands-only" / "PACKAGE.md"
        assert package_md.exists()

        result = parse_package_md(package_md)
        assert result.valid is True
        assert result.name == "test-commands-only"
