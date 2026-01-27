"""CLI entry point for agrx - temporary skill runner."""

import shutil
import signal
import subprocess
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from agr.config import AgrConfig, find_config, find_repo_root
from agr.exceptions import AgrError, InvalidHandleError
from agr.fetcher import downloaded_repo, install_skill_from_repo
from agr.handle import ParsedHandle, parse_handle
from agr.tool import DEFAULT_TOOL_NAMES, TOOLS, ToolConfig, get_tool

app = typer.Typer(
    name="agrx",
    help="Run a skill temporarily without adding to agr.toml.",
    no_args_is_help=True,
    add_completion=False,
)

console = Console()

AGRX_PREFIX = "_agrx_"  # Prefix for temporary resources


def _get_default_tool() -> str:
    """Get default tool from agr.toml or fall back to default."""
    config_path = find_config()
    if config_path:
        config = AgrConfig.load(config_path)
        if config.tools:
            return config.tools[0]
    return DEFAULT_TOOL_NAMES[0]


def _check_tool_cli(tool_config: ToolConfig) -> None:
    """Check if tool's CLI is installed.

    Args:
        tool_config: ToolConfig for the tool to check

    Raises:
        typer.Exit: If CLI is not found
    """
    cli_cmd = tool_config.cli_command
    if not cli_cmd:
        console.print(
            f"[red]Error:[/red] {tool_config.name} has no CLI command configured"
        )
        raise typer.Exit(1)
    if shutil.which(cli_cmd) is None:
        console.print(f"[red]Error:[/red] {cli_cmd} CLI not found.")
        if tool_config.install_hint:
            console.print(f"[dim]{tool_config.install_hint}[/dim]")
        raise typer.Exit(1)


def _cleanup_skill(skill_path: Path) -> None:
    """Clean up a temporary skill."""
    if skill_path.exists():
        try:
            shutil.rmtree(skill_path)
        except Exception:
            pass  # Best effort cleanup


@app.command()
def main(
    handle: Annotated[
        str,
        typer.Argument(
            help="Skill handle to run (e.g., kasperjunge/commit).",
        ),
    ],
    tool: Annotated[
        Optional[str],
        typer.Option(
            "--tool",
            "-t",
            help="Tool CLI to use (claude, cursor, copilot).",
        ),
    ] = None,
    interactive: Annotated[
        bool,
        typer.Option(
            "--interactive",
            "-i",
            help="Start interactive session after running the skill.",
        ),
    ] = False,
    prompt: Annotated[
        Optional[str],
        typer.Option(
            "--prompt",
            "-p",
            help="Prompt to pass to the skill.",
        ),
    ] = None,
    global_install: Annotated[
        bool,
        typer.Option(
            "--global",
            "-g",
            help="Install to global skills directory instead of project-local.",
        ),
    ] = False,
) -> None:
    """Run a skill temporarily without adding to agr.toml.

    Downloads and installs the skill to a temporary location, runs it with the
    selected tool's CLI, and cleans up afterwards.

    Examples:
        agrx kasperjunge/commit
        agrx maragudk/skills/collaboration -i
        agrx kasperjunge/commit -p "Review my changes"
        agrx kasperjunge/commit --tool cursor
    """
    # Determine which tool to use
    tool_name = tool or _get_default_tool()

    # Validate tool name
    if tool_name not in TOOLS:
        available = ", ".join(TOOLS.keys())
        console.print(f"[red]Error:[/red] Unknown tool '{tool_name}'")
        console.print(f"[dim]Available tools: {available}[/dim]")
        raise typer.Exit(1)

    tool_config = get_tool(tool_name)

    # Find repo root (or use global dir)
    if global_install:
        skills_dir = tool_config.get_global_skills_dir()
    else:
        repo_root = find_repo_root()
        if repo_root is None:
            console.print("[red]Error:[/red] Not in a git repository")
            console.print(
                f"[dim]Use --global to install to {tool_config.get_global_skills_dir()}[/dim]"
            )
            raise typer.Exit(1)
        skills_dir = tool_config.get_skills_dir(repo_root)

    try:
        # Parse handle
        parsed = parse_handle(handle)

        if parsed.is_local:
            console.print("[red]Error:[/red] agrx only works with remote handles")
            console.print("[dim]Use 'agr add' for local skills[/dim]")
            raise typer.Exit(1)

        # Check tool CLI is available
        _check_tool_cli(tool_config)

        # Get GitHub coordinates
        username, repo_name = parsed.get_github_repo()

        console.print(f"[dim]Downloading {handle}...[/dim]")

        # Create prefixed name for temporary skill
        prefixed_name = f"{AGRX_PREFIX}{parsed.name}"

        # Download and install
        with downloaded_repo(username, repo_name) as repo_dir:
            # Create a modified handle for the prefixed installation
            temp_handle = ParsedHandle(
                username=AGRX_PREFIX.rstrip("_"),
                name=parsed.name,
            )

            install_skill_from_repo(
                repo_dir,
                parsed.name,
                temp_handle,
                skills_dir,
                tool_config,
                overwrite=True,
            )

        # Get the actual installed path based on tool's path structure
        installed_path = skills_dir / temp_handle.to_skill_path(tool_config)
        # For consistency, update temp_skill_path to match
        temp_skill_path = installed_path

        # Set up cleanup handlers
        cleanup_done = False

        def cleanup_handler(signum, frame):
            nonlocal cleanup_done
            if not cleanup_done:
                cleanup_done = True
                _cleanup_skill(temp_skill_path)
            sys.exit(1)

        original_sigint = signal.signal(signal.SIGINT, cleanup_handler)
        original_sigterm = signal.signal(signal.SIGTERM, cleanup_handler)

        try:
            console.print(
                f"[dim]Running skill '{parsed.name}' with {tool_name}...[/dim]"
            )

            # Build the skill prompt
            skill_prompt = f"/{prefixed_name}"
            if prompt:
                skill_prompt += f" {prompt}"

            # Run the appropriate CLI
            cli_cmd = tool_config.cli_command
            if interactive:
                # Run the skill first, then continue in interactive mode
                cmd = [cli_cmd, tool_config.cli_prompt_flag, skill_prompt]
                if tool_config.cli_force_flag:
                    cmd.append(tool_config.cli_force_flag)
                subprocess.run(cmd, check=False)

                console.print("[dim]Continuing in interactive mode...[/dim]")
                subprocess.run([cli_cmd, tool_config.cli_continue_flag], check=False)
            else:
                # Just run the skill
                subprocess.run(
                    [cli_cmd, tool_config.cli_prompt_flag, skill_prompt],
                    check=False,
                )

        finally:
            # Restore signal handlers
            signal.signal(signal.SIGINT, original_sigint)
            signal.signal(signal.SIGTERM, original_sigterm)

            # Clean up
            if not cleanup_done:
                cleanup_done = True
                _cleanup_skill(temp_skill_path)

    except InvalidHandleError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except AgrError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
