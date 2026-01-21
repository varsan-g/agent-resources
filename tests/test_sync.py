"""Tests for sync command."""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from agr.cli.main import app
from agr.config import AgrConfig


runner = CliRunner()


class TestSyncCommand:
    """Tests for agr sync command."""

    def test_sync_without_agr_toml_shows_message(self, tmp_path: Path, monkeypatch):
        """Test that sync works without agr.toml but shows message."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        result = runner.invoke(app, ["sync"])

        # Now sync succeeds even without agr.toml (can sync local resources)
        assert result.exit_code == 0
        # Should show message about no agr.toml or nothing to sync
        assert "nothing to sync" in result.output.lower() or "skipping remote" in result.output.lower()

    def test_sync_remote_only_errors_without_agr_toml(self, tmp_path: Path, monkeypatch):
        """Test that sync --remote errors when no agr.toml exists."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        result = runner.invoke(app, ["sync", "--remote"])

        # With --remote flag, no agr.toml is not an error, just a message
        assert result.exit_code == 0
        assert "nothing to sync" in result.output.lower() or "skipping remote" in result.output.lower()

    @patch("agr.cli.sync.downloaded_repo")
    @patch("agr.cli.sync.resolve_remote_resource")
    @patch("agr.cli.sync.fetch_resource_from_repo_dir")
    def test_sync_installs_missing_dependencies(
        self, mock_fetch, mock_resolve, mock_downloaded_repo, tmp_path: Path, monkeypatch
    ):
        """Test that sync installs dependencies from agr.toml."""
        from contextlib import contextmanager
        from agr.resolver import ResolvedResource, ResourceSource
        from agr.fetcher import ResourceType

        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Create agr.toml with dependencies
        config = AgrConfig()
        config.add_remote("kasperjunge/commit", "skill")
        config.add_remote("alice/review", "command")
        config.save(tmp_path / "agr.toml")

        # Create .claude directory but no installed resources
        (tmp_path / ".claude" / "skills").mkdir(parents=True)
        (tmp_path / ".claude" / "commands").mkdir(parents=True)

        # Setup mock for downloaded_repo context manager
        @contextmanager
        def mock_context(username, repo_name):
            mock_repo_dir = tmp_path / f"mock_repo_{username}"
            mock_repo_dir.mkdir(exist_ok=True)
            yield mock_repo_dir

        mock_downloaded_repo.side_effect = mock_context

        # Setup mock for resolve_remote_resource
        def resolve_mock(repo_dir, name):
            res_type = ResourceType.SKILL if name == "commit" else ResourceType.COMMAND
            return ResolvedResource(
                name=name,
                resource_type=res_type,
                path=Path(f".claude/skills/{name}"),
                source=ResourceSource.CLAUDE_DIR,
            )

        mock_resolve.side_effect = resolve_mock

        result = runner.invoke(app, ["sync"])

        # Verify fetch was called for both dependencies
        assert mock_fetch.call_count == 2

    @patch("agr.cli.sync.fetch_resource")
    def test_sync_skips_already_installed(
        self, mock_fetch, tmp_path: Path, monkeypatch
    ):
        """Test that sync skips already installed resources."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Create agr.toml with dependency
        config = AgrConfig()
        config.add_remote("kasperjunge/commit", "skill")
        config.save(tmp_path / "agr.toml")

        # Create already installed skill with flattened namespaced path
        skill_dir = tmp_path / ".claude" / "skills" / "kasperjunge:commit"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Commit Skill")

        result = runner.invoke(app, ["sync"])

        # Verify fetch was NOT called (resource already exists)
        mock_fetch.assert_not_called()

    def test_sync_prune_removes_unlisted_resources(
        self, tmp_path: Path, monkeypatch
    ):
        """Test that sync --prune removes resources not in agr.toml."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Create agr.toml with one dependency
        config = AgrConfig()
        config.add_remote("kasperjunge/commit", "skill")
        config.save(tmp_path / "agr.toml")

        # Create installed skill that IS in toml (using flattened name)
        skill_in_toml = tmp_path / ".claude" / "skills" / "kasperjunge:commit"
        skill_in_toml.mkdir(parents=True)
        (skill_in_toml / "SKILL.md").write_text("# Commit Skill")

        # Create installed skill that is NOT in toml (using flattened name)
        skill_not_in_toml = tmp_path / ".claude" / "skills" / "alice:old-skill"
        skill_not_in_toml.mkdir(parents=True)
        (skill_not_in_toml / "SKILL.md").write_text("# Old Skill")

        result = runner.invoke(app, ["sync", "--prune"])

        # Verify skill in toml still exists
        assert skill_in_toml.exists()
        assert (skill_in_toml / "SKILL.md").exists()

        # Verify skill not in toml was removed
        assert not skill_not_in_toml.exists()

    def test_sync_prune_keeps_flat_path_resources(
        self, tmp_path: Path, monkeypatch
    ):
        """Test that sync --prune doesn't remove flat-path (legacy) resources."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Create empty agr.toml
        config = AgrConfig()
        config.save(tmp_path / "agr.toml")

        # Create flat-path skill (legacy)
        flat_skill = tmp_path / ".claude" / "skills" / "legacy-skill"
        flat_skill.mkdir(parents=True)
        (flat_skill / "SKILL.md").write_text("# Legacy Skill")

        result = runner.invoke(app, ["sync", "--prune"])

        # Verify flat-path skill was NOT removed (backward compat)
        assert flat_skill.exists()

    @patch("agr.cli.sync.downloaded_repo")
    @patch("agr.cli.sync.resolve_remote_resource")
    @patch("agr.cli.sync.fetch_resource_from_repo_dir")
    def test_sync_with_custom_repo_dependency(
        self, mock_fetch, mock_resolve, mock_downloaded_repo, tmp_path: Path, monkeypatch
    ):
        """Test that sync handles custom repo dependencies."""
        from contextlib import contextmanager
        from agr.resolver import ResolvedResource, ResourceSource
        from agr.fetcher import ResourceType

        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Create agr.toml with custom repo dependency
        config = AgrConfig()
        config.add_remote("kasperjunge/custom-repo/commit", "skill")
        config.save(tmp_path / "agr.toml")

        # Create .claude directory
        (tmp_path / ".claude" / "skills").mkdir(parents=True)

        # Track repo download calls
        download_calls = []

        @contextmanager
        def mock_context(username, repo_name):
            download_calls.append((username, repo_name))
            mock_repo_dir = tmp_path / "mock_repo"
            mock_repo_dir.mkdir(exist_ok=True)
            yield mock_repo_dir

        mock_downloaded_repo.side_effect = mock_context

        mock_resolve.return_value = ResolvedResource(
            name="commit",
            resource_type=ResourceType.SKILL,
            path=Path(".claude/skills/commit"),
            source=ResourceSource.CLAUDE_DIR,
        )

        result = runner.invoke(app, ["sync"])

        # Verify fetch was called with correct repo
        assert len(download_calls) == 1
        assert download_calls[0][0] == "kasperjunge"
        assert download_calls[0][1] == "custom-repo"

    @patch("agr.cli.sync.downloaded_repo")
    @patch("agr.cli.sync.resolve_remote_resource")
    @patch("agr.cli.sync.fetch_resource_from_repo_dir")
    def test_sync_auto_detects_type(
        self, mock_fetch, mock_resolve, mock_downloaded_repo, tmp_path: Path, monkeypatch
    ):
        """Test that sync auto-detects type when not specified."""
        from contextlib import contextmanager
        from agr.resolver import ResolvedResource, ResourceSource
        from agr.fetcher import ResourceType

        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Create agr.toml without type specified
        config = AgrConfig()
        config.add_remote("kasperjunge/commit", "skill")  # Default type is skill
        config.save(tmp_path / "agr.toml")

        # Create .claude directory
        (tmp_path / ".claude" / "skills").mkdir(parents=True)

        @contextmanager
        def mock_context(username, repo_name):
            mock_repo_dir = tmp_path / "mock_repo"
            mock_repo_dir.mkdir(exist_ok=True)
            yield mock_repo_dir

        mock_downloaded_repo.side_effect = mock_context

        mock_resolve.return_value = ResolvedResource(
            name="commit",
            resource_type=ResourceType.SKILL,
            path=Path(".claude/skills/commit"),
            source=ResourceSource.CLAUDE_DIR,
        )

        result = runner.invoke(app, ["sync"])

        # Verify fetch was called (auto-detection should handle it)
        mock_fetch.assert_called_once()


class TestSyncWithResolver:
    """Tests for Issue #47: Sync using resolve_remote_resource() for consistent resolution."""

    @patch("agr.cli.sync.downloaded_repo")
    @patch("agr.cli.sync.resolve_remote_resource")
    @patch("agr.cli.sync.fetch_resource_from_repo_dir")
    def test_sync_uses_resolver(
        self, mock_fetch, mock_resolve, mock_downloaded_repo, tmp_path: Path, monkeypatch
    ):
        """Test that sync uses resolve_remote_resource() for each dependency."""
        from contextlib import contextmanager
        from agr.resolver import ResolvedResource, ResourceSource
        from agr.fetcher import ResourceType

        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Create agr.toml with dependency
        config = AgrConfig()
        config.add_remote("kasperjunge/commit", "skill")
        config.save(tmp_path / "agr.toml")

        # Create .claude directory
        (tmp_path / ".claude" / "skills").mkdir(parents=True)

        # Setup mock for downloaded_repo context manager
        mock_repo_dir = tmp_path / "mock_repo"
        mock_repo_dir.mkdir()

        @contextmanager
        def mock_context(*args, **kwargs):
            yield mock_repo_dir

        mock_downloaded_repo.side_effect = mock_context

        # Setup mock for resolve_remote_resource
        mock_resolve.return_value = ResolvedResource(
            name="commit",
            resource_type=ResourceType.SKILL,
            path=Path(".claude/skills/commit"),
            source=ResourceSource.CLAUDE_DIR,
        )

        result = runner.invoke(app, ["sync"])

        # Verify resolve_remote_resource was called
        mock_resolve.assert_called_once_with(mock_repo_dir, "commit")

    @patch("agr.cli.sync.downloaded_repo")
    @patch("agr.cli.sync.resolve_remote_resource")
    @patch("agr.cli.sync.fetch_resource_from_repo_dir")
    def test_sync_groups_by_repo(
        self, mock_fetch, mock_resolve, mock_downloaded_repo, tmp_path: Path, monkeypatch
    ):
        """Test that sync groups dependencies by repo to minimize downloads."""
        from contextlib import contextmanager
        from agr.resolver import ResolvedResource, ResourceSource
        from agr.fetcher import ResourceType

        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Create agr.toml with multiple dependencies from same repo
        config = AgrConfig()
        config.add_remote("kasperjunge/commit", "skill")
        config.add_remote("kasperjunge/review", "skill")
        config.add_remote("alice/other-skill", "skill")
        config.save(tmp_path / "agr.toml")

        # Create .claude directory
        (tmp_path / ".claude" / "skills").mkdir(parents=True)

        # Track how many times each repo is downloaded
        download_counts = {}

        @contextmanager
        def mock_context(username, repo_name):
            key = f"{username}/{repo_name}"
            download_counts[key] = download_counts.get(key, 0) + 1
            mock_repo_dir = tmp_path / f"mock_repo_{username}"
            mock_repo_dir.mkdir(exist_ok=True)
            yield mock_repo_dir

        mock_downloaded_repo.side_effect = mock_context

        # Setup mock for resolve_remote_resource
        def resolve_mock(repo_dir, name):
            return ResolvedResource(
                name=name,
                resource_type=ResourceType.SKILL,
                path=Path(f".claude/skills/{name}"),
                source=ResourceSource.CLAUDE_DIR,
            )

        mock_resolve.side_effect = resolve_mock

        result = runner.invoke(app, ["sync"])

        # Verify each repo was only downloaded once (grouped)
        # kasperjunge should be downloaded once (for both commit and review)
        # alice should be downloaded once
        assert download_counts.get("kasperjunge/skills", 0) <= 1
        assert download_counts.get("alice/skills", 0) <= 1

    @patch("agr.cli.sync.downloaded_repo")
    @patch("agr.cli.sync.resolve_remote_resource")
    @patch("agr.cli.sync.fetch_resource_from_repo_dir")
    def test_sync_with_non_standard_path(
        self, mock_fetch, mock_resolve, mock_downloaded_repo, tmp_path: Path, monkeypatch
    ):
        """Test that sync handles resources at non-standard paths (via resolver)."""
        from contextlib import contextmanager
        from agr.resolver import ResolvedResource, ResourceSource
        from agr.fetcher import ResourceType

        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Create agr.toml with dependency
        config = AgrConfig()
        config.add_remote("kasperjunge/custom-skill", "skill")
        config.save(tmp_path / "agr.toml")

        # Create .claude directory
        (tmp_path / ".claude" / "skills").mkdir(parents=True)

        # Setup mock for downloaded_repo context manager
        mock_repo_dir = tmp_path / "mock_repo"
        mock_repo_dir.mkdir()

        @contextmanager
        def mock_context(*args, **kwargs):
            yield mock_repo_dir

        mock_downloaded_repo.side_effect = mock_context

        # Setup mock for resolve_remote_resource - return non-standard path
        custom_path = Path("resources/custom/skills/custom-skill")
        mock_resolve.return_value = ResolvedResource(
            name="custom-skill",
            resource_type=ResourceType.SKILL,
            path=custom_path,
            source=ResourceSource.AGR_TOML,
            package_name="my-package",
        )

        result = runner.invoke(app, ["sync"])

        # Verify fetch_resource_from_repo_dir was called with the custom path
        mock_fetch.assert_called_once()
        call_kwargs = mock_fetch.call_args[1]
        assert call_kwargs.get("source_path") == custom_path
        assert call_kwargs.get("package_name") == "my-package"
