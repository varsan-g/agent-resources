"""Tests for adapter integration with constants and paths.

Verifies that the constants and path utilities correctly derive
values from the ClaudeAdapter.
"""

from pathlib import Path

import pytest

from agr.adapters import AdapterRegistry
from agr.cli.paths import get_base_path, TYPE_TO_SUBDIR, _build_type_to_subdir
from agr.constants import (
    TOOL_DIR_NAME,
    SKILLS_SUBDIR,
    COMMANDS_SUBDIR,
    AGENTS_SUBDIR,
    RULES_SUBDIR,
    PACKAGES_SUBDIR,
)


@pytest.fixture
def adapter():
    """Provide the default adapter for tests."""
    return AdapterRegistry.get_default()


class TestConstantsMatchAdapter:
    """Tests that constants match adapter values."""

    def test_tool_dir_name(self, adapter):
        """Test that TOOL_DIR_NAME matches adapter config_dir."""
        assert TOOL_DIR_NAME == adapter.format.config_dir

    def test_skills_subdir(self, adapter):
        """Test that SKILLS_SUBDIR matches adapter skill_dir."""
        assert SKILLS_SUBDIR == adapter.format.skill_dir

    def test_commands_subdir(self, adapter):
        """Test that COMMANDS_SUBDIR matches adapter command_dir."""
        assert COMMANDS_SUBDIR == adapter.format.command_dir

    def test_agents_subdir(self, adapter):
        """Test that AGENTS_SUBDIR matches adapter agent_dir."""
        assert AGENTS_SUBDIR == adapter.format.agent_dir

    def test_rules_subdir(self, adapter):
        """Test that RULES_SUBDIR matches adapter rule_dir."""
        assert RULES_SUBDIR == adapter.format.rule_dir


class TestTypeToSubdirMatchesAdapter:
    """Tests that TYPE_TO_SUBDIR matches adapter values."""

    @pytest.mark.parametrize(
        "resource_type,attr_name",
        [
            ("skill", "skill_dir"),
            ("command", "command_dir"),
            ("agent", "agent_dir"),
            ("rule", "rule_dir"),
        ],
    )
    def test_type_to_subdir_mapping(self, adapter, resource_type, attr_name):
        """Test that TYPE_TO_SUBDIR entries match adapter format attributes."""
        assert TYPE_TO_SUBDIR[resource_type] == getattr(adapter.format, attr_name)

    def test_build_type_to_subdir_function(self, adapter):
        """Test that _build_type_to_subdir produces correct mapping."""
        result = _build_type_to_subdir()
        assert result["skill"] == adapter.format.skill_dir
        assert result["command"] == adapter.format.command_dir
        assert result["agent"] == adapter.format.agent_dir
        assert result["rule"] == adapter.format.rule_dir
        assert result["package"] == "packages"


class TestGetBasePath:
    """Tests that get_base_path uses the adapter correctly."""

    def test_local_path(self, tmp_path, monkeypatch, adapter):
        """Test that get_base_path returns correct local path."""
        monkeypatch.chdir(tmp_path)
        result = get_base_path(global_install=False)
        assert result == tmp_path / adapter.format.config_dir

    def test_global_path(self, tmp_path, monkeypatch, adapter):
        """Test that get_base_path returns correct global path."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        result = get_base_path(global_install=True)
        assert result == tmp_path / adapter.format.config_dir

    def test_with_explicit_adapter(self, tmp_path, monkeypatch):
        """Test that get_base_path accepts an explicit adapter."""
        monkeypatch.chdir(tmp_path)
        adapter = AdapterRegistry.get("claude")
        result = get_base_path(global_install=False, adapter=adapter)
        assert result == tmp_path / adapter.format.config_dir

    def test_global_with_explicit_adapter(self, tmp_path, monkeypatch):
        """Test that get_base_path global works with explicit adapter."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        adapter = AdapterRegistry.get("claude")
        result = get_base_path(global_install=True, adapter=adapter)
        assert result == tmp_path / adapter.format.config_dir


class TestAdapterIntegrationConsistency:
    """Tests that the integration is consistent across modules."""

    def test_constants_and_paths_match(self):
        """Test that constants.py and paths.py produce same values."""
        assert SKILLS_SUBDIR == TYPE_TO_SUBDIR["skill"]
        assert COMMANDS_SUBDIR == TYPE_TO_SUBDIR["command"]
        assert AGENTS_SUBDIR == TYPE_TO_SUBDIR["agent"]
        assert RULES_SUBDIR == TYPE_TO_SUBDIR["rule"]
        assert PACKAGES_SUBDIR == TYPE_TO_SUBDIR["package"]

    def test_default_adapter_is_claude(self, adapter):
        """Test that the default adapter is Claude."""
        assert adapter.format.name == "claude"

    def test_get_base_path_uses_config_dir(self, tmp_path, monkeypatch):
        """Test that get_base_path uses config_dir from adapter."""
        monkeypatch.chdir(tmp_path)
        result = get_base_path(global_install=False)
        assert result.name == TOOL_DIR_NAME
