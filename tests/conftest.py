"""Test configuration and fixtures."""

import pytest
from pathlib import Path

from agr.config import AgrConfig


@pytest.fixture
def git_project(tmp_path: Path, monkeypatch):
    """Set up a temporary git project directory.

    Returns the tmp_path after changing to the directory and creating a .git folder.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".git").mkdir()
    return tmp_path


@pytest.fixture(autouse=True)
def cleanup_test_entries():
    """Clean up any testuser entries from agr.toml after each test."""
    yield

    agr_toml = Path(__file__).parent.parent / "agr.toml"
    if not agr_toml.exists():
        return

    config = AgrConfig.load(agr_toml)
    original_count = len(config.dependencies)

    config.dependencies = [
        dep for dep in config.dependencies
        if not (
            (dep.handle and dep.handle.startswith("testuser/"))
            or (dep.path and "testuser" in dep.path)
        )
    ]

    if len(config.dependencies) != original_count:
        config.save(agr_toml)
