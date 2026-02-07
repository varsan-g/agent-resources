"""CLI tests for agr config command group."""

from agr.config import AgrConfig
from tests.cli.assertions import assert_cli


class TestAgrConfigTools:
    """Tests for agr config tools commands."""

    def test_config_tools_default_lists_tools(self, agr, cli_config):
        """agr config tools defaults to list behavior."""
        cli_config('tools = ["claude", "cursor"]\ndependencies = []')

        result = agr("config", "tools")

        assert_cli(result).succeeded().stdout_contains("Configured tools:")
        assert_cli(result).stdout_contains("claude")
        assert_cli(result).stdout_contains("cursor")

    def test_config_tools_set_replaces_tool_list(self, agr, cli_project, cli_config):
        """agr config tools set replaces configured tools."""
        cli_config('tools = ["claude", "cursor"]\ndependencies = []')

        result = agr("config", "tools", "set", "codex", "opencode")

        assert_cli(result).succeeded()
        config = AgrConfig.load(cli_project / "agr.toml")
        assert config.tools == ["codex", "opencode"]

    def test_config_tools_unset_aliases_remove(self, agr, cli_project, cli_config):
        """agr config tools unset behaves like remove."""
        cli_config('tools = ["claude", "codex"]\ndependencies = []')

        result = agr("config", "tools", "unset", "codex")

        assert_cli(result).succeeded().stdout_contains("Removed:")
        config = AgrConfig.load(cli_project / "agr.toml")
        assert config.tools == ["claude"]

    def test_config_tools_remove_updates_default_tool(
        self, agr, cli_project, cli_config
    ):
        """Removing the default tool updates default_tool safely."""
        cli_config(
            'tools = ["claude", "codex"]\ndefault_tool = "codex"\ndependencies = []'
        )

        result = agr("config", "tools", "remove", "codex")

        assert_cli(result).succeeded()
        config = AgrConfig.load(cli_project / "agr.toml")
        assert config.tools == ["claude"]
        assert config.default_tool == "claude"


class TestAgrConfigDefaultTool:
    """Tests for agr config default-tool commands."""

    def test_default_tool_set(self, agr, cli_project, cli_config):
        """agr config default-tool set stores default_tool."""
        cli_config('tools = ["claude", "codex"]\ndependencies = []')

        result = agr("config", "default-tool", "set", "codex")

        assert_cli(result).succeeded().stdout_contains("Default tool set:")
        config = AgrConfig.load(cli_project / "agr.toml")
        assert config.default_tool == "codex"

    def test_default_tool_set_requires_configured_tool(self, agr, cli_config):
        """agr config default-tool set rejects tools not in tools list."""
        cli_config('tools = ["claude"]\ndependencies = []')

        result = agr("config", "default-tool", "set", "codex")

        assert_cli(result).failed().stdout_contains("is not configured")

    def test_default_tool_unset(self, agr, cli_project, cli_config):
        """agr config default-tool unset clears default_tool."""
        cli_config(
            'tools = ["claude", "codex"]\ndefault_tool = "codex"\ndependencies = []'
        )

        result = agr("config", "default-tool", "unset")

        assert_cli(result).succeeded().stdout_contains("Default tool unset:")
        config = AgrConfig.load(cli_project / "agr.toml")
        assert config.default_tool is None


class TestAgrToolsAlias:
    """Tests for deprecated agr tools alias."""

    def test_tools_alias_prints_deprecation_warning(self, agr, cli_config):
        """agr tools warns about deprecation and still works."""
        cli_config('tools = ["claude"]\ndependencies = []')

        result = agr("tools")

        assert_cli(result).succeeded().stdout_contains("deprecated")
        assert_cli(result).stdout_contains("agr config tools")
