"""CLI tests for global scope flags (-g/--global)."""

import shutil
from pathlib import Path

from tests.cli.assertions import assert_cli
from tests.cli.runner import run_cli


def _create_skill(skill_dir: Path, name: str) -> Path:
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"""---
name: {name}
---

# {name}
"""
    )
    return skill_dir


class TestGlobalFlags:
    """Tests for global installation flags."""

    def test_add_global_outside_git_repo(self, tmp_path):
        """agr add -g installs globally outside git repos."""
        home = tmp_path / "home"
        home.mkdir()
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        _create_skill(workspace / "skills" / "test-skill", "test-skill")

        result = run_cli(
            ["agr", "add", "-g", "./skills/test-skill"],
            cwd=workspace,
            env={"HOME": str(home)},
        )

        assert_cli(result).succeeded().stdout_contains("Added:")
        installed = home / ".claude" / "skills" / "test-skill"
        assert installed.exists()
        assert (installed / "SKILL.md").exists()
        assert (home / ".agr" / "agr.toml").exists()

    def test_list_global_outside_git_repo(self, tmp_path):
        """agr list -g reads global config outside git repos."""
        home = tmp_path / "home"
        home.mkdir()
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        _create_skill(workspace / "skills" / "test-skill", "test-skill")

        add_result = run_cli(
            ["agr", "add", "-g", "./skills/test-skill"],
            cwd=workspace,
            env={"HOME": str(home)},
        )
        assert_cli(add_result).succeeded()

        result = run_cli(
            ["agr", "list", "-g"],
            cwd=workspace,
            env={"HOME": str(home)},
        )
        assert_cli(result).succeeded().stdout_contains("installed")

    def test_remove_global_outside_git_repo(self, tmp_path):
        """agr remove -g removes globally installed skills."""
        home = tmp_path / "home"
        home.mkdir()
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        _create_skill(workspace / "skills" / "test-skill", "test-skill")

        add_result = run_cli(
            ["agr", "add", "-g", "./skills/test-skill"],
            cwd=workspace,
            env={"HOME": str(home)},
        )
        assert_cli(add_result).succeeded()

        remove_result = run_cli(
            ["agr", "remove", "-g", "./skills/test-skill"],
            cwd=workspace,
            env={"HOME": str(home)},
        )
        assert_cli(remove_result).succeeded().stdout_contains("Removed:")
        assert not (home / ".claude" / "skills" / "test-skill").exists()

    def test_sync_global_outside_git_repo(self, tmp_path):
        """agr sync -g reinstalls missing global dependencies."""
        home = tmp_path / "home"
        home.mkdir()
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        _create_skill(workspace / "skills" / "test-skill", "test-skill")

        add_result = run_cli(
            ["agr", "add", "-g", "./skills/test-skill"],
            cwd=workspace,
            env={"HOME": str(home)},
        )
        assert_cli(add_result).succeeded()

        installed = home / ".claude" / "skills" / "test-skill"
        assert installed.exists()
        shutil.rmtree(installed)
        assert not installed.exists()

        sync_result = run_cli(
            ["agr", "sync", "-g"],
            cwd=workspace,
            env={"HOME": str(home)},
        )
        assert_cli(sync_result).succeeded().stdout_contains("Installed:")
        assert (home / ".claude" / "skills" / "test-skill" / "SKILL.md").exists()

    def test_global_local_dependency_uses_absolute_path(self, tmp_path):
        """agr add -g stores local dependencies as absolute paths."""
        home = tmp_path / "home"
        home.mkdir()
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        _create_skill(workspace / "skills" / "test-skill", "test-skill")

        add_result = run_cli(
            ["agr", "add", "-g", "./skills/test-skill"],
            cwd=workspace,
            env={"HOME": str(home)},
        )
        assert_cli(add_result).succeeded()

        config_path = home / ".agr" / "agr.toml"
        config_content = config_path.read_text()
        assert str((workspace / "skills" / "test-skill").resolve()) in config_content
