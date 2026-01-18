"""Tests for path utilities in agr/cli/paths.py."""

import os
from pathlib import Path

import pytest
import typer

from agr.cli.paths import (
    DEFAULT_REPO_NAME,
    TYPE_TO_SUBDIR,
    console,
    extract_type_from_args,
    find_repo_root,
    get_base_path,
    get_destination,
    get_namespaced_destination,
    is_local_path,
    parse_nested_name,
    parse_resource_ref,
)


class TestFindRepoRoot:
    """Tests for find_repo_root utility."""

    def test_finds_repo_root_in_git_repo(self, tmp_path):
        """Test that find_repo_root finds the .git directory."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        subdir = tmp_path / "subdir" / "nested"
        subdir.mkdir(parents=True)

        original_cwd = os.getcwd()
        try:
            os.chdir(subdir)
            root = find_repo_root()
            assert root == tmp_path
        finally:
            os.chdir(original_cwd)

    def test_returns_cwd_when_not_in_repo(self, tmp_path):
        """Test that find_repo_root returns cwd when not in a git repo."""
        subdir = tmp_path / "not_a_repo" / "subdir"
        subdir.mkdir(parents=True)

        original_cwd = os.getcwd()
        try:
            os.chdir(subdir)
            root = find_repo_root()
            assert root == subdir
        finally:
            os.chdir(original_cwd)


class TestIsLocalPath:
    """Tests for is_local_path utility."""

    def test_recognizes_dot_slash(self):
        """Test that ./path is recognized as local."""
        assert is_local_path("./path/to/file") is True

    def test_recognizes_absolute_path(self):
        """Test that /absolute/path is recognized as local."""
        assert is_local_path("/absolute/path") is True

    def test_recognizes_parent_path(self):
        """Test that ../parent/path is recognized as local."""
        assert is_local_path("../parent/path") is True

    def test_rejects_remote_ref(self):
        """Test that username/name is not recognized as local."""
        assert is_local_path("kasperjunge/commit") is False

    def test_rejects_remote_ref_with_repo(self):
        """Test that username/repo/name is not recognized as local."""
        assert is_local_path("kasperjunge/repo/name") is False

    def test_rejects_simple_name(self):
        """Test that simple name is not recognized as local."""
        assert is_local_path("my-skill") is False


class TestExtractTypeFromArgs:
    """Tests for extract_type_from_args utility."""

    def test_returns_explicit_type_when_provided(self):
        """Test that explicit type takes precedence."""
        args = ["my-skill", "--type", "command"]
        cleaned, resource_type = extract_type_from_args(args, "skill")
        assert resource_type == "skill"
        assert cleaned == args

    def test_extracts_type_from_args(self):
        """Test extraction of --type from args."""
        args = ["my-skill", "--type", "command"]
        cleaned, resource_type = extract_type_from_args(args, None)
        assert resource_type == "command"
        assert cleaned == ["my-skill"]

    def test_extracts_type_short_flag(self):
        """Test extraction of -t from args."""
        args = ["my-skill", "-t", "agent"]
        cleaned, resource_type = extract_type_from_args(args, None)
        assert resource_type == "agent"
        assert cleaned == ["my-skill"]

    def test_returns_none_when_no_type_in_args(self):
        """Test that None is returned when no type in args."""
        args = ["my-skill"]
        cleaned, resource_type = extract_type_from_args(args, None)
        assert resource_type is None
        assert cleaned == ["my-skill"]

    def test_handles_empty_args(self):
        """Test handling of empty args."""
        cleaned, resource_type = extract_type_from_args([], None)
        assert resource_type is None
        assert cleaned == []

    def test_handles_none_args(self):
        """Test handling of None args."""
        cleaned, resource_type = extract_type_from_args(None, None)
        assert resource_type is None
        assert cleaned == []

    def test_type_at_beginning(self):
        """Test extraction when --type is at the beginning."""
        args = ["--type", "skill", "my-skill"]
        cleaned, resource_type = extract_type_from_args(args, None)
        assert resource_type == "skill"
        assert cleaned == ["my-skill"]


class TestParseNestedName:
    """Tests for parse_nested_name utility."""

    def test_parses_simple_name(self):
        """Test parsing a simple name without colons."""
        base_name, segments = parse_nested_name("hello-world")
        assert base_name == "hello-world"
        assert segments == ["hello-world"]

    def test_parses_colon_delimited_name(self):
        """Test parsing a colon-delimited name."""
        base_name, segments = parse_nested_name("dir:hello-world")
        assert base_name == "hello-world"
        assert segments == ["dir", "hello-world"]

    def test_parses_multiple_colons(self):
        """Test parsing multiple colon segments."""
        base_name, segments = parse_nested_name("a:b:c")
        assert base_name == "c"
        assert segments == ["a", "b", "c"]

    def test_raises_on_empty_name(self):
        """Test that empty name raises error."""
        with pytest.raises(typer.BadParameter):
            parse_nested_name("")

    def test_raises_on_leading_colon(self):
        """Test that leading colon raises error."""
        with pytest.raises(typer.BadParameter):
            parse_nested_name(":hello")

    def test_raises_on_trailing_colon(self):
        """Test that trailing colon raises error."""
        with pytest.raises(typer.BadParameter):
            parse_nested_name("hello:")

    def test_raises_on_consecutive_colons(self):
        """Test that consecutive colons raise error."""
        with pytest.raises(typer.BadParameter):
            parse_nested_name("a::b")


class TestParseResourceRef:
    """Tests for parse_resource_ref utility."""

    def test_parses_username_name_format(self):
        """Test parsing username/name format."""
        username, repo, name, segments = parse_resource_ref("kasperjunge/commit")
        assert username == "kasperjunge"
        assert repo == DEFAULT_REPO_NAME
        assert name == "commit"
        assert segments == ["commit"]

    def test_parses_username_repo_name_format(self):
        """Test parsing username/repo/name format."""
        username, repo, name, segments = parse_resource_ref("kasperjunge/custom-repo/commit")
        assert username == "kasperjunge"
        assert repo == "custom-repo"
        assert name == "commit"
        assert segments == ["commit"]

    def test_parses_nested_name(self):
        """Test parsing with nested colon-delimited name."""
        username, repo, name, segments = parse_resource_ref("kasperjunge/dir:hello-world")
        assert username == "kasperjunge"
        assert repo == DEFAULT_REPO_NAME
        assert name == "dir:hello-world"
        assert segments == ["dir", "hello-world"]

    def test_raises_on_single_segment(self):
        """Test that single segment raises error."""
        with pytest.raises(typer.BadParameter):
            parse_resource_ref("onlyname")

    def test_raises_on_too_many_segments(self):
        """Test that too many segments raises error."""
        with pytest.raises(typer.BadParameter):
            parse_resource_ref("a/b/c/d")

    def test_raises_on_empty_username(self):
        """Test that empty username raises error."""
        with pytest.raises(typer.BadParameter):
            parse_resource_ref("/name")


class TestGetBasePath:
    """Tests for get_base_path utility."""

    def test_returns_local_path_when_not_global(self, tmp_path, monkeypatch):
        """Test that local install returns ./.claude/."""
        monkeypatch.chdir(tmp_path)
        result = get_base_path(global_install=False)
        assert result == tmp_path / ".claude"

    def test_returns_home_path_when_global(self):
        """Test that global install returns ~/.claude/."""
        result = get_base_path(global_install=True)
        assert result == Path.home() / ".claude"


class TestGetDestination:
    """Tests for get_destination utility."""

    def test_returns_correct_local_destination(self, tmp_path, monkeypatch):
        """Test that destination includes subdirectory."""
        monkeypatch.chdir(tmp_path)
        result = get_destination("skills", global_install=False)
        assert result == tmp_path / ".claude" / "skills"

    def test_returns_correct_global_destination(self):
        """Test that global destination uses home directory."""
        result = get_destination("commands", global_install=True)
        assert result == Path.home() / ".claude" / "commands"


class TestGetNamespacedDestination:
    """Tests for get_namespaced_destination utility."""

    def test_returns_namespaced_path(self, tmp_path, monkeypatch):
        """Test that namespaced path includes username."""
        monkeypatch.chdir(tmp_path)
        result = get_namespaced_destination(
            username="kasperjunge",
            resource_name="commit",
            resource_subdir="skills",
            global_install=False,
        )
        assert result == tmp_path / ".claude" / "skills" / "kasperjunge" / "commit"


class TestTypeToSubdir:
    """Tests for TYPE_TO_SUBDIR constant."""

    def test_contains_skill(self):
        """Test that skill maps to skills."""
        assert TYPE_TO_SUBDIR["skill"] == "skills"

    def test_contains_command(self):
        """Test that command maps to commands."""
        assert TYPE_TO_SUBDIR["command"] == "commands"

    def test_contains_agent(self):
        """Test that agent maps to agents."""
        assert TYPE_TO_SUBDIR["agent"] == "agents"

    def test_contains_package(self):
        """Test that package maps to packages."""
        assert TYPE_TO_SUBDIR["package"] == "packages"


class TestConsole:
    """Tests for shared console instance."""

    def test_console_is_initialized(self):
        """Test that console is a Console instance."""
        from rich.console import Console

        assert isinstance(console, Console)


class TestDefaultRepoName:
    """Tests for DEFAULT_REPO_NAME constant."""

    def test_default_repo_name(self):
        """Test that default repo name is agent-resources."""
        assert DEFAULT_REPO_NAME == "agent-resources"
