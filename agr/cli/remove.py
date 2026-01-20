"""Remove subcommand for agr - delete local resources."""

import shutil
from pathlib import Path
from typing import Annotated, List, Optional

import typer

from agr.cli.common import (
    TYPE_TO_SUBDIR,
    console,
    error_exit,
    extract_type_from_args,
    find_repo_root,
    get_base_path,
    handle_remove_bundle,
    handle_remove_resource,
    handle_remove_unified,
    is_local_path,
)
from agr.cli.multi_tool import get_target_adapters, get_tool_base_path, InvalidToolError
from agr.config import find_config, AgrConfig
from agr.fetcher import ResourceType
from agr.github import get_username_from_git_remote

# Deprecated subcommand names
DEPRECATED_SUBCOMMANDS = {"skill", "command", "agent", "bundle"}




def handle_remove_local(
    local_path: str,
    global_install: bool = False,
    tool_flags: list[str] | None = None,
) -> None:
    """Handle removing a local resource by path.

    Removes from both agr.toml and target tool directories.

    Args:
        local_path: The local path to remove (e.g., "./commands/docs.md")
        global_install: If True, remove from global config directory
        tool_flags: Optional list of tool names from CLI --tool flags
    """
    # Find and load config
    config_path = find_config()
    if not config_path:
        error_exit("No agr.toml found")

    config = AgrConfig.load(config_path)

    # Check if path is in config
    dep = config.get_by_path(local_path)
    if not dep:
        error_exit(f"Path '{local_path}' not found in agr.toml")

    # Get username for finding installed resource
    repo_root = find_repo_root()
    username = get_username_from_git_remote(repo_root)
    if not username:
        username = "local"

    # Determine installed path
    source_path = Path(local_path)
    name = source_path.stem if source_path.is_file() else source_path.name

    subdir = TYPE_TO_SUBDIR.get(dep.type, "skills")

    # Get target adapters
    try:
        adapters = get_target_adapters(config=config, tool_flags=tool_flags)
    except InvalidToolError as e:
        error_exit(str(e))

    # Remove from all target tools
    for adapter in adapters:
        base_path = get_tool_base_path(adapter, global_install)
        config_dir = adapter.format.config_dir

        if dep.type in ("skill", "package"):
            installed_path = base_path / subdir / username / name
        else:
            installed_path = base_path / subdir / username / f"{name}.md"

        # Remove from tool directory
        if installed_path.exists():
            if installed_path.is_dir():
                shutil.rmtree(installed_path)
            else:
                installed_path.unlink()

            rel_path = installed_path.relative_to(base_path)
            console.print(f"[green]Removed from {config_dir}/: {rel_path}[/green]")

            # Clean up empty parent directories
            parent = installed_path.parent
            if parent.exists() and not any(parent.iterdir()):
                parent.rmdir()

    # Remove from config
    config.remove_by_path(local_path)
    config.save(config_path)

    console.print(f"[green]Removed '{local_path}' from agr.toml[/green]")


app = typer.Typer(
    help="Remove skills, commands, or agents.",
)


def _extract_remove_options(
    args: list[str] | None,
    explicit_type: str | None,
    explicit_tools: list[str] | None = None,
) -> tuple[list[str], str | None, list[str] | None]:
    """Extract --type/-t and --tool options from args list."""
    if not args:
        return [], explicit_type, explicit_tools

    cleaned_args: list[str] = []
    resource_type = explicit_type
    tools = list(explicit_tools) if explicit_tools else None

    i = 0
    while i < len(args):
        arg = args[i]
        has_next = i + 1 < len(args)

        if arg in ("--type", "-t") and has_next and resource_type is None:
            resource_type = args[i + 1]
            i += 2
        elif arg == "--tool" and has_next:
            if tools is None:
                tools = []
            tools.append(args[i + 1])
            i += 2
        else:
            cleaned_args.append(arg)
            i += 1

    return cleaned_args, resource_type, tools


@app.callback(invoke_without_command=True)
def remove_unified(
    ctx: typer.Context,
    args: Annotated[
        Optional[List[str]],
        typer.Argument(help="Name or path of the resource to remove"),
    ] = None,
    resource_type: Annotated[
        Optional[str],
        typer.Option(
            "--type",
            "-t",
            help="Explicit resource type: skill, command, agent, or bundle",
        ),
    ] = None,
    global_install: Annotated[
        bool,
        typer.Option(
            "--global",
            "-g",
            help="Remove from global config directory",
        ),
    ] = False,
    tool: Annotated[
        Optional[List[str]],
        typer.Option(
            "--tool",
            help="Target tool(s) to remove from (e.g., --tool claude --tool cursor)",
        ),
    ] = None,
) -> None:
    """Remove a resource from the local installation with auto-detection.

    Auto-detects the resource type (skill, command, agent) from local files.
    Use --type to explicitly specify when a name exists in multiple types.
    Use --tool to specify target tools (defaults to config or auto-detect).

    Supports both resource names and local paths:
      agr remove hello-world          # Remove by name
      agr remove ./commands/docs.md   # Remove by path

    Examples:
      agr remove hello-world
      agr remove hello-world --type skill
      agr remove hello-world --global
      agr remove ./commands/docs.md
      agr remove ./commands/docs.md --tool claude --tool cursor
    """
    # Extract options from args if they were captured there
    cleaned_args, resource_type, tool = _extract_remove_options(args, resource_type, tool)

    if not cleaned_args:
        console.print(ctx.get_help())
        raise typer.Exit(0)

    first_arg = cleaned_args[0]

    # Handle local paths
    if is_local_path(first_arg):
        handle_remove_local(first_arg, global_install, tool)
        return

    # Handle deprecated subcommand syntax: agr remove skill <name>
    if first_arg in DEPRECATED_SUBCOMMANDS:
        if len(cleaned_args) < 2:
            error_exit(f"Missing resource name after '{first_arg}'.")

        name = cleaned_args[1]
        if first_arg == "bundle":
            console.print(
                f"[yellow]Warning: 'agr remove bundle' is deprecated. "
                f"Use 'agr remove {name} --type bundle' instead.[/yellow]"
            )
            handle_remove_bundle(name, global_install)
        else:
            console.print(
                f"[yellow]Warning: 'agr remove {first_arg}' is deprecated. "
                f"Use 'agr remove {name}' instead.[/yellow]"
            )
            if first_arg == "skill":
                handle_remove_resource(name, ResourceType.SKILL, "skills", global_install)
            elif first_arg == "command":
                handle_remove_resource(name, ResourceType.COMMAND, "commands", global_install)
            elif first_arg == "agent":
                handle_remove_resource(name, ResourceType.AGENT, "agents", global_install)
        return

    # Normal unified remove: agr remove <name>
    # Note: Remote resources currently only support single tool (Claude)
    name = first_arg
    handle_remove_unified(name, resource_type, global_install)
