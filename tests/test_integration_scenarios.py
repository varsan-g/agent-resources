"""Integration tests for various scenarios (Issue #38).

Tests using committed fixtures and new edge case fixtures.
"""

from pathlib import Path

from typer.testing import CliRunner

from agr.cli.main import app
from agr.package import validate_no_nested_packages

PACKAGES_PATH = Path(__file__).parent.parent / "resources" / "packages"
runner = CliRunner()


class TestFixturePackageExplosion:
    """Tests for package explosion using committed fixtures."""

    def test_explode_test_simple_with_package_md(self, git_project: Path):
        """Test _test-simple package uses name from PACKAGE.md."""
        pkg_path = PACKAGES_PATH / "_test-simple"

        result = runner.invoke(app, ["add", str(pkg_path)])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "skills" / "local:test-simple:simple-skill" / "SKILL.md"
        assert installed.exists()

    def test_explode_test_complete_with_package_md(self, git_project: Path):
        """Test _test-complete package explodes all resource types."""
        pkg_path = PACKAGES_PATH / "_test-complete"

        result = runner.invoke(app, ["add", str(pkg_path)])

        assert result.exit_code == 0

        assert (git_project / ".claude" / "skills" / "local:test-complete:alpha" / "SKILL.md").exists()
        assert (git_project / ".claude" / "skills" / "local:test-complete:beta" / "SKILL.md").exists()
        assert (git_project / ".claude" / "commands" / "local" / "test-complete" / "pkg-cmd.md").exists()
        assert (git_project / ".claude" / "agents" / "local" / "test-complete" / "pkg-agent.md").exists()

    def test_explode_test_nested_skills_with_package_md(self, git_project: Path):
        """Test _test-nested-skills package creates proper flattened names."""
        pkg_path = PACKAGES_PATH / "_test-nested-skills"

        result = runner.invoke(app, ["add", str(pkg_path)])

        assert result.exit_code == 0

        assert (
            git_project / ".claude" / "skills" / "local:test-nested-skills:category:cat-skill-one" / "SKILL.md"
        ).exists()
        assert (
            git_project / ".claude" / "skills" / "local:test-nested-skills:category:cat-skill-two" / "SKILL.md"
        ).exists()

    def test_explode_test_commands_only_with_package_md(self, git_project: Path):
        """Test _test-commands-only package explodes commands."""
        pkg_path = PACKAGES_PATH / "_test-commands-only"

        result = runner.invoke(app, ["add", str(pkg_path), "--type", "package"])

        assert result.exit_code == 0 or "contains no resources" in result.output


class TestNewFixtureScenarios:
    """Tests for new edge case fixtures."""

    def test_no_package_md_falls_back_to_directory_name(self, git_project: Path):
        """Test _test-no-package-md uses directory name as fallback."""
        pkg_path = PACKAGES_PATH / "_test-no-package-md"

        result = runner.invoke(app, ["add", str(pkg_path), "--type", "package"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "skills" / "local:_test-no-package-md:standalone-skill" / "SKILL.md"
        assert installed.exists()

    def test_nested_package_md_produces_error(self, git_project: Path):
        """Test _test-nested-package-md produces error for nested PACKAGE.md."""
        pkg_path = PACKAGES_PATH / "_test-nested-package-md"

        result = runner.invoke(app, ["add", str(pkg_path)])

        assert result.exit_code == 1
        assert "nested PACKAGE.md" in result.output

    def test_deep_nesting_produces_full_namespace(self, git_project: Path):
        """Test _test-deep-nesting produces correct full namespace path."""
        pkg_path = PACKAGES_PATH / "_test-deep-nesting"

        result = runner.invoke(app, ["add", str(pkg_path)])

        assert result.exit_code == 0

        deep_installed = (
            git_project / ".claude" / "skills" / "local:test-deep-nesting:level1:level2:level3:deep-skill" / "SKILL.md"
        )
        assert deep_installed.exists()

        shallow_installed = git_project / ".claude" / "skills" / "local:test-deep-nesting:shallow" / "SKILL.md"
        assert shallow_installed.exists()

    def test_all_types_package_explodes_all_types(self, git_project: Path):
        """Test _test-all-types package explodes all 4 resource types."""
        pkg_path = PACKAGES_PATH / "_test-all-types"

        result = runner.invoke(app, ["add", str(pkg_path)])

        assert result.exit_code == 0

        assert (git_project / ".claude" / "skills" / "local:test-all-types:all-types-skill" / "SKILL.md").exists()
        assert (git_project / ".claude" / "commands" / "local" / "test-all-types" / "all-types-cmd.md").exists()
        assert (git_project / ".claude" / "agents" / "local" / "test-all-types" / "all-types-agent.md").exists()


class TestSyncWithPackageMd:
    """Tests for sync command respecting PACKAGE.md."""

    def test_sync_uses_package_md_name(self, git_project: Path):
        """Test that sync respects PACKAGE.md name."""
        pkg_dir = git_project / "my-dir-name"
        pkg_dir.mkdir()
        (pkg_dir / "PACKAGE.md").write_text("---\nname: custom-pkg-name\n---\n")
        skill_dir = pkg_dir / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill")

        (git_project / "agr.toml").write_text(
            '[[dependencies]]\npath = "./my-dir-name"\ntype = "package"\n'
        )

        result = runner.invoke(app, ["sync"])

        assert result.exit_code == 0
        installed = git_project / ".claude" / "skills" / "local:custom-pkg-name:my-skill" / "SKILL.md"
        assert installed.exists()

    def test_sync_updates_when_package_md_changes(self, git_project: Path):
        """Test that sync picks up PACKAGE.md name changes."""
        pkg_dir = git_project / "my-pkg"
        pkg_dir.mkdir()
        (pkg_dir / "PACKAGE.md").write_text("---\nname: old-name\n---\n")
        skill_dir = pkg_dir / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill")

        (git_project / "agr.toml").write_text(
            '[[dependencies]]\npath = "./my-pkg"\ntype = "package"\n'
        )

        result = runner.invoke(app, ["sync"])
        assert result.exit_code == 0
        old_installed = git_project / ".claude" / "skills" / "local:old-name:my-skill" / "SKILL.md"
        assert old_installed.exists()

        (pkg_dir / "PACKAGE.md").write_text("---\nname: new-name\n---\n")

        result = runner.invoke(app, ["sync"])
        assert result.exit_code == 0
        new_installed = git_project / ".claude" / "skills" / "local:new-name:my-skill" / "SKILL.md"
        assert new_installed.exists()


class TestValidateNoNestedPackages:
    """Tests for validate_no_nested_packages function."""

    def test_detects_nested_package_md(self):
        """Test that nested PACKAGE.md is detected in fixture."""
        pkg_path = PACKAGES_PATH / "_test-nested-package-md"
        nested = validate_no_nested_packages(pkg_path)

        assert len(nested) == 1
        assert nested[0].name == "PACKAGE.md"
        assert "nested-pkg" in str(nested[0])

    def test_no_nested_packages_in_valid_fixtures(self):
        """Test that valid fixtures have no nested packages."""
        for pkg_name in ["_test-simple", "_test-complete", "_test-nested-skills"]:
            pkg_path = PACKAGES_PATH / pkg_name
            nested = validate_no_nested_packages(pkg_path)
            assert nested == [], f"Unexpected nested PACKAGE.md in {pkg_name}"
