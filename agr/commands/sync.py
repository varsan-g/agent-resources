"""agr sync command implementation."""

from pathlib import Path

from rich.console import Console

from agr.config import AgrConfig, find_config, find_repo_root
from agr.exceptions import AgrError
from agr.fetcher import fetch_and_install_to_tools, is_skill_installed
from agr.handle import INSTALLED_NAME_SEPARATOR, LEGACY_SEPARATOR, parse_handle
from agr.skill import SKILL_MARKER
from agr.tool import ToolConfig

console = Console()


def _migrate_legacy_directories(skills_dir: Path, tool: ToolConfig) -> None:
    """Migrate colon-based directory names to the new separator format.

    This ensures backward compatibility with skills installed before
    the Windows-compatible naming scheme was introduced.

    Only applies to flat tools (Claude), not nested tools (Cursor).

    Args:
        skills_dir: The skills directory to scan for legacy directories.
        tool: Tool configuration (migration only for non-nested tools).
    """
    # Only migrate for flat tools
    if tool.supports_nested:
        return

    if not skills_dir.exists():
        return

    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        if LEGACY_SEPARATOR not in skill_dir.name:
            continue
        # Verify it's a skill (has SKILL.md)
        if not (skill_dir / SKILL_MARKER).exists():
            continue

        # Convert legacy separator to new separator
        new_name = skill_dir.name.replace(LEGACY_SEPARATOR, INSTALLED_NAME_SEPARATOR)
        new_path = skills_dir / new_name

        if new_path.exists():
            console.print(f"[yellow]Cannot migrate:[/yellow] {skill_dir.name}")
            console.print(f"  [dim]Target {new_name} already exists[/dim]")
            continue

        try:
            skill_dir.rename(new_path)
            console.print(f"[blue]Migrated:[/blue] {skill_dir.name} -> {new_name}")
        except OSError as e:
            console.print(f"[red]Failed to migrate:[/red] {skill_dir.name}")
            console.print(f"  [dim]{e}[/dim]")


def run_sync() -> None:
    """Run the sync command.

    Installs all dependencies from agr.toml that aren't already installed.
    Also migrates any legacy colon-based directory names to the new
    Windows-compatible double-hyphen format (for flat tools only).
    """
    # Find repo root
    repo_root = find_repo_root()
    if repo_root is None:
        console.print("[red]Error:[/red] Not in a git repository")
        raise SystemExit(1)

    # Find config
    config_path = find_config()
    if config_path is None:
        console.print("[yellow]No agr.toml found.[/yellow] Nothing to sync.")
        return

    config = AgrConfig.load(config_path)

    # Get configured tools
    tools = config.get_tools()

    # Migrate legacy colon-based directories for flat tools
    for tool in tools:
        skills_dir = tool.get_skills_dir(repo_root)
        _migrate_legacy_directories(skills_dir, tool)

    if not config.dependencies:
        console.print("[yellow]No dependencies in agr.toml.[/yellow] Nothing to sync.")
        return

    # Track results per dependency (not per tool)
    results: list[tuple[str, str, str | None]] = []  # (identifier, status, error)

    for dep in config.dependencies:
        identifier = dep.identifier

        try:
            # Parse handle
            if dep.is_local:
                ref = dep.path or ""
            else:
                ref = dep.handle or ""

            handle = parse_handle(ref)

            # Check if already installed in all tools
            all_installed = all(
                is_skill_installed(handle, repo_root, tool) for tool in tools
            )

            if all_installed:
                results.append((identifier, "up-to-date", None))
                continue

            # Get tools that need installation
            tools_needing_install = [
                tool
                for tool in tools
                if not is_skill_installed(handle, repo_root, tool)
            ]

            # Install to all tools that need it (downloads once)
            fetch_and_install_to_tools(
                handle, repo_root, tools_needing_install, overwrite=False
            )

            results.append((identifier, "installed", None))

        except FileExistsError as e:
            results.append((identifier, "error", str(e)))
        except AgrError as e:
            results.append((identifier, "error", str(e)))
        except Exception as e:
            results.append((identifier, "error", f"Unexpected: {e}"))

    # Print results
    installed = 0
    up_to_date = 0
    errors = 0

    for identifier, status, error in results:
        if status == "installed":
            console.print(f"[green]Installed:[/green] {identifier}")
            installed += 1
        elif status == "up-to-date":
            console.print(f"[dim]Up to date:[/dim] {identifier}")
            up_to_date += 1
        else:
            console.print(f"[red]Error:[/red] {identifier}")
            if error:
                console.print(f"  [dim]{error}[/dim]")
            errors += 1

    # Summary
    console.print()
    parts = []
    if installed:
        parts.append(f"{installed} installed")
    if up_to_date:
        parts.append(f"{up_to_date} up to date")
    if errors:
        parts.append(f"{errors} failed")

    console.print(f"[bold]Summary:[/bold] {', '.join(parts)}")

    if errors:
        raise SystemExit(1)
