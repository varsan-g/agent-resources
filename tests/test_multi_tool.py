"""Tests for multi-tool support (Issue #39).

Tests the multi_tool.py helper module and related functionality.
"""

from pathlib import Path

import pytest

from agr.adapters import AdapterRegistry, ClaudeAdapter, CursorAdapter
from agr.cli.multi_tool import (
    InvalidToolError,
    get_target_adapters,
    get_tool_base_path,
    validate_tool_names,
    format_tool_summary,
)
from agr.config import AgrConfig, ToolsConfig


class TestValidateToolNames:
    """Test validate_tool_names function."""

    def test_validate_valid_tools(self):
        """Test validation of valid tool names."""
        result = validate_tool_names(["claude", "cursor"])
        assert result == ["claude", "cursor"]

    def test_validate_single_tool(self):
        """Test validation of a single tool."""
        result = validate_tool_names(["claude"])
        assert result == ["claude"]

    def test_validate_empty_list(self):
        """Test validation of empty list returns empty."""
        result = validate_tool_names([])
        assert result == []

    def test_validate_invalid_tool_raises(self):
        """Test that invalid tool names raise InvalidToolError."""
        with pytest.raises(InvalidToolError, match="Unknown tool"):
            validate_tool_names(["invalid-tool"])

    def test_validate_mixed_valid_invalid_raises(self):
        """Test that mixed valid/invalid raises error."""
        with pytest.raises(InvalidToolError, match="unknown-tool"):
            validate_tool_names(["claude", "unknown-tool"])


class TestGetTargetAdapters:
    """Test get_target_adapters function."""

    def test_cli_flags_take_priority(self):
        """Test that CLI --tool flags take priority over config."""
        config = AgrConfig()
        config.tools = ToolsConfig(targets=["cursor"])

        adapters = get_target_adapters(config=config, tool_flags=["claude"])

        assert len(adapters) == 1
        assert isinstance(adapters[0], ClaudeAdapter)

    def test_config_targets_used_when_no_flags(self):
        """Test that config [tools].targets is used when no CLI flags."""
        config = AgrConfig()
        config.tools = ToolsConfig(targets=["cursor"])

        adapters = get_target_adapters(config=config, tool_flags=None)

        assert len(adapters) == 1
        assert isinstance(adapters[0], CursorAdapter)

    def test_multiple_tools_from_flags(self):
        """Test getting multiple adapters from CLI flags."""
        adapters = get_target_adapters(tool_flags=["claude", "cursor"])

        assert len(adapters) == 2
        adapter_types = {type(a) for a in adapters}
        assert ClaudeAdapter in adapter_types
        assert CursorAdapter in adapter_types

    def test_multiple_tools_from_config(self):
        """Test getting multiple adapters from config."""
        config = AgrConfig()
        config.tools = ToolsConfig(targets=["claude", "cursor"])

        adapters = get_target_adapters(config=config, tool_flags=None)

        assert len(adapters) == 2

    def test_auto_detect_with_config_dir(self, tmp_path):
        """Test auto-detection when tool config directory exists."""
        # Create .claude directory
        (tmp_path / ".claude").mkdir()

        adapters = get_target_adapters(config=None, tool_flags=None, base_path=tmp_path)

        # Should detect claude from .claude directory
        assert len(adapters) >= 1
        claude_adapters = [a for a in adapters if isinstance(a, ClaudeAdapter)]
        assert len(claude_adapters) == 1

    def test_default_to_claude_when_nothing_detected(self, tmp_path):
        """Test default to claude when no tools are detected."""
        # Empty temp path with no tool directories
        adapters = get_target_adapters(config=None, tool_flags=None, base_path=tmp_path)

        assert len(adapters) == 1
        assert isinstance(adapters[0], ClaudeAdapter)

    def test_invalid_tool_flag_raises(self):
        """Test that invalid tool flag raises error."""
        with pytest.raises(InvalidToolError):
            get_target_adapters(tool_flags=["invalid-tool"])

    def test_invalid_config_target_raises(self):
        """Test that invalid config target raises error."""
        config = AgrConfig()
        config.tools = ToolsConfig(targets=["invalid-tool"])

        with pytest.raises(InvalidToolError):
            get_target_adapters(config=config, tool_flags=None)


class TestGetToolBasePath:
    """Test get_tool_base_path function."""

    def test_claude_local_path(self):
        """Test getting local path for Claude adapter."""
        adapter = ClaudeAdapter()
        path = get_tool_base_path(adapter, global_install=False)

        assert path == Path.cwd() / ".claude"

    def test_claude_global_path(self):
        """Test getting global path for Claude adapter."""
        adapter = ClaudeAdapter()
        path = get_tool_base_path(adapter, global_install=True)

        assert path == Path.home() / ".claude"

    def test_cursor_local_path(self):
        """Test getting local path for Cursor adapter."""
        adapter = CursorAdapter()
        path = get_tool_base_path(adapter, global_install=False)

        assert path == Path.cwd() / ".cursor"

    def test_cursor_global_path(self):
        """Test getting global path for Cursor adapter."""
        adapter = CursorAdapter()
        path = get_tool_base_path(adapter, global_install=True)

        assert path == Path.home() / ".cursor"


class TestFormatToolSummary:
    """Test format_tool_summary function."""

    def test_single_tool_with_results(self):
        """Test summary with single tool having results."""
        result = format_tool_summary({"claude": 3})
        assert "1 tool" in result

    def test_multiple_tools_with_results(self):
        """Test summary with multiple tools having results."""
        result = format_tool_summary({"claude": 3, "cursor": 2})
        assert "2 tools" in result

    def test_no_results(self):
        """Test summary with no results."""
        result = format_tool_summary({"claude": 0, "cursor": 0})
        assert "No resources synced" in result

    def test_partial_results(self):
        """Test summary with partial results."""
        result = format_tool_summary({"claude": 2, "cursor": 0})
        assert "1 tool" in result


class TestToolsConfigIntegration:
    """Test ToolsConfig integration with AgrConfig."""

    def test_load_config_with_tools_section(self, tmp_path):
        """Test loading config with [tools] section."""
        config_path = tmp_path / "agr.toml"
        config_path.write_text('''dependencies = []

[tools]
targets = ["claude", "cursor"]
''')

        config = AgrConfig.load(config_path)

        assert config.tools is not None
        assert config.tools.targets == ["claude", "cursor"]

    def test_load_config_without_tools_section(self, tmp_path):
        """Test loading config without [tools] section."""
        config_path = tmp_path / "agr.toml"
        config_path.write_text('''dependencies = []
''')

        config = AgrConfig.load(config_path)

        assert config.tools is None

    def test_save_config_with_tools_section(self, tmp_path):
        """Test saving config with [tools] section."""
        config_path = tmp_path / "agr.toml"

        config = AgrConfig()
        config.tools = ToolsConfig(targets=["claude", "cursor"])
        config.save(config_path)

        content = config_path.read_text()
        assert "[tools]" in content
        assert "targets" in content
        assert "claude" in content
        assert "cursor" in content

    def test_save_config_without_tools(self, tmp_path):
        """Test saving config without tools doesn't add section."""
        config_path = tmp_path / "agr.toml"

        config = AgrConfig()
        config.save(config_path)

        content = config_path.read_text()
        assert "[tools]" not in content

    def test_roundtrip_with_tools(self, tmp_path):
        """Test save and load roundtrip preserves tools config."""
        config_path = tmp_path / "agr.toml"

        # Create and save config
        config = AgrConfig()
        config.tools = ToolsConfig(targets=["claude", "cursor"])
        config.save(config_path)

        # Load and verify
        loaded = AgrConfig.load(config_path)
        assert loaded.tools is not None
        assert loaded.tools.targets == ["claude", "cursor"]


class TestDetectFromConfig:
    """Test ToolDetector.detect_from_config integration."""

    def test_detect_from_config_with_targets(self):
        """Test detect_from_config returns targets from config."""
        from agr.adapters import ToolDetector

        config = AgrConfig()
        config.tools = ToolsConfig(targets=["claude", "cursor"])

        detector = ToolDetector()
        targets = detector.detect_from_config(config)

        assert targets == ["claude", "cursor"]

    def test_detect_from_config_without_tools(self):
        """Test detect_from_config returns empty when no tools section."""
        from agr.adapters import ToolDetector

        config = AgrConfig()

        detector = ToolDetector()
        targets = detector.detect_from_config(config)

        assert targets == []

    def test_detect_from_config_empty_targets(self):
        """Test detect_from_config returns empty for empty targets."""
        from agr.adapters import ToolDetector

        config = AgrConfig()
        config.tools = ToolsConfig(targets=[])

        detector = ToolDetector()
        targets = detector.detect_from_config(config)

        assert targets == []

    def test_get_target_tools_uses_config(self, tmp_path):
        """Test get_target_tools uses config when available."""
        from agr.adapters import ToolDetector

        config = AgrConfig()
        config.tools = ToolsConfig(targets=["cursor"])

        detector = ToolDetector(base_path=tmp_path)
        targets = detector.get_target_tools(config)

        assert targets == ["cursor"]
