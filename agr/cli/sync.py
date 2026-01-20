"""Sync command for agr."""

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, List, Optional

import typer

from agr.config import AgrConfig, Dependency, find_config, get_or_create_config
from agr.exceptions import AgrError, RepoNotFoundError, ResourceNotFoundError, ResourceExistsError
from agr.fetcher import RESOURCE_CONFIGS, ResourceType, fetch_resource, downloaded_repo, fetch_resource_from_repo_dir
from agr.github import get_username_from_git_remote
from agr.resolver import discover_all_repo_resources, ResolvedResource
from agr.cli.common import (
    DEFAULT_REPO_NAME,
    TYPE_TO_SUBDIR,
    console,
    fetch_spinner,
    find_repo_root,
)
from agr.cli.paths import remove_path
from agr.adapters import AdapterRegistry
from agr.adapters.detector import ToolDetector
from agr.cli.multi_tool import get_target_adapters, get_tool_base_path, InvalidToolError
from agr.utils import (
    compute_flattened_resource_name,
    compute_path_segments,
    find_package_context,
    update_skill_md_name,
)

app = typer.Typer()


def _interactive_tool_selection(
    config: AgrConfig,
    config_path: Path,
) -> list[str]:
    """Prompt user to select target tools interactively.

    Called when no tools are configured and none are detected via directories.

    Args:
        config: Current agr config
        config_path: Path to save updated config

    Returns:
        List of selected tool names
    """
    # Get all available tools
    available_tools = AdapterRegistry.all_names()
    detector = ToolDetector()
    detected = detector.detect_all()

    console.print()
    console.print("[yellow]No target tools configured.[/yellow]")
    console.print("Which tools would you like to sync resources to?")
    console.print()

    # Display options with detected status
    tool_info = []
    for i, tool_name in enumerate(sorted(available_tools), 1):
        tool_detection = next((t for t in detected if t.name == tool_name), None)
        has_dir = tool_detection.config_dir is not None if tool_detection else False
        has_cli = tool_detection.cli_available if tool_detection else False

        status_parts = []
        if has_dir:
            status_parts.append("directory exists")
        if has_cli:
            status_parts.append("CLI available")
        status = f" ({', '.join(status_parts)})" if status_parts else ""

        console.print(f"  {i}. {tool_name}{status}")
        tool_info.append(tool_name)

    console.print()

    # Get user input
    while True:
        try:
            selection = typer.prompt(
                "Enter selection (comma-separated numbers, e.g., 1,2)",
                default="1"
            )

            # Parse selection
            selected_indices = [int(s.strip()) for s in selection.split(",")]
            selected_tools = []

            for idx in selected_indices:
                if idx < 1 or idx > len(tool_info):
                    console.print(f"[red]Invalid selection: {idx}[/red]")
                    continue
                selected_tools.append(tool_info[idx - 1])

            if not selected_tools:
                console.print("[red]No valid tools selected. Please try again.[/red]")
                continue

            break

        except ValueError:
            console.print("[red]Invalid input. Please enter numbers separated by commas.[/red]")

    # Save selection to config
    for tool_name in selected_tools:
        config.add_tool_target(tool_name)
    config.save(config_path)

    console.print()
    console.print(f"[green]Saved to agr.toml: {', '.join(selected_tools)}[/green]")
    console.print()

    # Create directories for selected tools if they don't exist
    for tool_name in selected_tools:
        adapter = AdapterRegistry.get(tool_name)
        tool_dir = Path.cwd() / adapter.format.config_dir
        if not tool_dir.exists():
            tool_dir.mkdir(parents=True)
            console.print(f"[dim]Created directory: {adapter.format.config_dir}/[/dim]")

    return selected_tools


def _needs_interactive_selection(
    config: AgrConfig | None,
    tool_flags: list[str] | None,
) -> bool:
    """Check if interactive tool selection is needed.

    Returns True if:
    - No --tool flags provided (not CI mode)
    - No tools configured in agr.toml
    - No tools detected via directories
    - Running in an interactive TTY

    Args:
        config: Current agr config (may be None)
        tool_flags: Tool flags from CLI

    Returns:
        True if interactive selection is needed
    """
    import sys

    # If tool flags provided, no need for interactive selection
    if tool_flags:
        return False

    # If tools configured in agr.toml, no need for interactive selection
    if config and config.tools and config.tools.targets:
        return False

    # Check if any tools are detected via directories
    detector = ToolDetector()
    detected = detector.detect_all()
    tools_with_dirs = [t for t in detected if t.config_dir is not None]

    if tools_with_dirs:
        return False

    # Only prompt if running interactively (has a TTY)
    if not sys.stdin.isatty():
        return False

    return True


@dataclass
class RepoSyncResult:
    """Result of syncing all resources from a repository."""

    installed_skills: list[str] = field(default_factory=list)
    installed_commands: list[str] = field(default_factory=list)
    installed_agents: list[str] = field(default_factory=list)
    installed_rules: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[tuple[str, str]] = field(default_factory=list)

    @property
    def total_installed(self) -> int:
        """Total number of resources installed."""
        return (
            len(self.installed_skills)
            + len(self.installed_commands)
            + len(self.installed_agents)
            + len(self.installed_rules)
        )

    @property
    def total_skipped(self) -> int:
        """Total number of resources skipped."""
        return len(self.skipped)

    @property
    def total_errors(self) -> int:
        """Total number of errors."""
        return len(self.errors)


# Mapping from type string to ResourceType enum
TYPE_STRING_TO_ENUM = {
    "skill": ResourceType.SKILL,
    "command": ResourceType.COMMAND,
    "agent": ResourceType.AGENT,
}


def _parse_dependency_ref(ref: str) -> tuple[str, str, str]:
    """Parse a dependency reference from agr.toml.

    Supports:
    - "username/name" -> username, DEFAULT_REPO_NAME, name
    - "username/repo/name" -> username, repo, name
    """
    parts = ref.split("/")
    if len(parts) == 2:
        return parts[0], DEFAULT_REPO_NAME, parts[1]
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    raise ValueError(f"Invalid dependency reference: {ref}")


def _is_resource_installed(
    username: str,
    name: str,
    resource_type: ResourceType,
    base_path: Path,
) -> bool:
    """Check if a resource is installed at the namespaced path."""
    from agr.handle import ParsedHandle

    config = RESOURCE_CONFIGS[resource_type]
    handle = ParsedHandle.from_components(username, name)

    if config.is_directory:
        # Skills: .claude/skills/<flattened_name>/SKILL.md
        resource_path = handle.to_skill_path(base_path)
        return resource_path.is_dir() and (resource_path / "SKILL.md").exists()
    else:
        # Commands/Agents: .claude/commands/username/name.md
        resource_path = handle.to_resource_path(base_path, resource_type.value)
        return resource_path.is_file()


def _type_string_to_enum(type_str: str) -> ResourceType | None:
    """Convert type string to ResourceType enum, or None if unknown."""
    return TYPE_STRING_TO_ENUM.get(type_str.lower())


def _discover_installed_namespaced_resources(
    base_path: Path,
) -> set[str]:
    """
    Discover all installed namespaced resources.

    Returns set of dependency refs in agr.toml format (slash-separated).
    For skills with flattened names like "kasperjunge:commit",
    returns "kasperjunge/commit".

    Uses centralized handle module for consistent conversion.
    """
    from agr.handle import skill_dirname_to_toml_handle

    installed = set()

    # Check skills - stored with flattened colon names like "kasperjunge:commit"
    skills_dir = base_path / "skills"
    if skills_dir.is_dir():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                if ":" in skill_dir.name:
                    # Use centralized conversion
                    toml_handle = skill_dirname_to_toml_handle(skill_dir.name)
                    installed.add(toml_handle)

    # Check commands and agents (nested format: username/[path/]name.md)
    for type_dir in ["commands", "agents"]:
        type_path = base_path / type_dir
        if not type_path.is_dir():
            continue
        for username_dir in type_path.iterdir():
            if not username_dir.is_dir():
                continue
            for md_file in username_dir.rglob("*.md"):
                # Build relative path from username dir
                # e.g., pkg/infra/deploy.md -> pkg/infra/deploy
                rel_path = md_file.relative_to(username_dir)
                parts = list(rel_path.parts)
                parts[-1] = rel_path.stem  # Remove .md extension
                handle_path = "/".join(parts)
                installed.add(f"{username_dir.name}/{handle_path}")

    return installed


def _remove_namespaced_resource(username: str, name: str, base_path: Path) -> None:
    """Remove a namespaced resource from disk.

    Uses ParsedHandle for consistent path building across resource types.
    For example, username="kasperjunge", name="commit"
    will remove ".claude/skills/kasperjunge:commit/".

    Args:
        username: GitHub username
        name: Resource name (may contain "/" for nested paths)
        base_path: Base .claude directory path
    """
    from agr.handle import ParsedHandle

    handle = ParsedHandle.from_components(username, name)
    paths_to_try = [
        handle.to_skill_path(base_path),
        handle.to_command_path(base_path),
        handle.to_agent_path(base_path),
    ]

    for path in paths_to_try:
        if path.exists():
            remove_path(path)
            return




def _sync_local_dependency(
    dep: Dependency,
    username: str,
    base_path: Path,
    repo_root: Path,
) -> tuple[str | None, str | None, tuple[str, str] | None]:
    """Sync a single local dependency to .claude directory.

    Returns:
        Tuple of (installed_name, updated_name, error_tuple).
        Only one will be non-None based on the action taken.
    """
    if not dep.path:
        return (None, None, None)

    source_path = repo_root / dep.path
    if not source_path.exists():
        return (None, None, (dep.path, f"Source path does not exist: {source_path}"))

    # Determine destination path based on type
    subdir = TYPE_TO_SUBDIR.get(dep.type, "skills")

    # Handle package explosion
    if dep.type == "package":
        name = source_path.name
        try:
            from agr.cli.add import _explode_package
            # Check if any exploded skills exist (using flattened names)
            skills_dir = base_path / "skills"
            pkg_prefix = f"{username}:{name}:"
            has_existing_skills = skills_dir.is_dir() and any(
                d.name.startswith(pkg_prefix) for d in skills_dir.iterdir() if d.is_dir()
            )
            is_update = has_existing_skills or any([
                (base_path / "commands" / username / name).exists(),
                (base_path / "agents" / username / name).exists(),
            ])
            _explode_package(source_path, username, name, base_path)
            if is_update:
                return (None, name, None)
            return (name, None, None)
        except Exception as e:
            return (None, None, (name, str(e)))

    # Check if source is inside a package
    package_name, _ = find_package_context(source_path)

    # Build destination path
    if dep.type == "skill":
        # Skills use flattened colon-namespaced directory names
        path_segments = compute_path_segments(source_path)
        flattened_name = compute_flattened_resource_name(username, path_segments, package_name)
        dest_path = base_path / subdir / flattened_name
        name = flattened_name
    else:
        # Commands/agents are files - include nested path structure
        path_segments = compute_path_segments(source_path)
        name = source_path.stem
        if package_name:
            all_segments = [package_name] + path_segments
        else:
            all_segments = path_segments
        nested_dirs = all_segments[:-1]
        if nested_dirs:
            dest_path = base_path / subdir / username / Path(*nested_dirs) / f"{name}.md"
        else:
            dest_path = base_path / subdir / username / f"{name}.md"

    try:
        is_update = dest_path.exists()

        # Check if source is newer than destination
        if is_update:
            if source_path.is_dir():
                source_marker = source_path / "SKILL.md"
                dest_marker = dest_path / "SKILL.md"
                if source_marker.exists() and dest_marker.exists():
                    if source_marker.stat().st_mtime <= dest_marker.stat().st_mtime:
                        return (None, None, None)  # Up to date
            elif source_path.stat().st_mtime <= dest_path.stat().st_mtime:
                return (None, None, None)  # Up to date

            # Remove existing before updating
            if dest_path.is_dir():
                shutil.rmtree(dest_path)
            else:
                dest_path.unlink()

        # Create parent directories
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy source to destination
        if source_path.is_dir():
            shutil.copytree(source_path, dest_path)
            # Update SKILL.md name field for skills
            if dep.type == "skill":
                update_skill_md_name(dest_path, flattened_name)
        else:
            shutil.copy2(source_path, dest_path)

        if is_update:
            return (None, name, None)
        return (name, None, None)

    except Exception as e:
        return (None, None, (name, str(e)))


def _sync_local_dependencies(
    config: AgrConfig,
    base_path: Path,
    prune: bool,
) -> tuple[int, int, int, int]:
    """Sync local dependencies from agr.toml to .claude directory.

    Only syncs dependencies explicitly listed in the config.

    Returns:
        Tuple of (installed, updated, pruned, failed) counts
    """
    repo_root = find_repo_root() or Path.cwd()

    username = get_username_from_git_remote(repo_root)
    if not username:
        console.print("[yellow]Warning: Could not determine username from git remote.[/yellow]")
        console.print("[yellow]Using 'local' as namespace. Configure git remote for proper namespacing.[/yellow]")
        username = "local"

    local_deps = config.get_local_dependencies()
    if not local_deps:
        return (0, 0, 0, 0)

    installed_count, updated_count, failed_count = 0, 0, 0
    synced_names: set[str] = set()

    for dep in local_deps:
        installed, updated, error = _sync_local_dependency(
            dep, username, base_path, repo_root
        )
        if installed:
            console.print(f"[green]Installed local resource '{installed}'[/green]")
            synced_names.add(installed)
            installed_count += 1
        if updated:
            console.print(f"[blue]Updated local resource '{updated}'[/blue]")
            synced_names.add(updated)
            updated_count += 1
        if error:
            name, msg = error
            console.print(f"[red]Failed to sync '{name}': {msg}[/red]")
            failed_count += 1

    # Pruning for local resources (if requested)
    pruned_count = 0
    if prune:
        pruned_count = _prune_unlisted_local_resources(
            config, base_path, username, synced_names
        )

    return (installed_count, updated_count, pruned_count, failed_count)


def _parse_repo_ref(repo_ref: str) -> tuple[str, str]:
    """Parse a repository reference into owner and repo name.

    Args:
        repo_ref: Repository reference like "owner/repo"

    Returns:
        Tuple of (owner, repo_name)

    Raises:
        typer.BadParameter: If the format is invalid
    """
    parts = repo_ref.split("/")
    if len(parts) != 2:
        raise typer.BadParameter(
            f"Invalid repository reference '{repo_ref}'. Expected format: owner/repo"
        )
    return parts[0], parts[1]


def _print_discovered_resources(resources: list[ResolvedResource]) -> None:
    """Print discovered resources grouped by type."""
    skills = [r for r in resources if r.resource_type == ResourceType.SKILL]
    commands = [r for r in resources if r.resource_type == ResourceType.COMMAND]
    agents = [r for r in resources if r.resource_type == ResourceType.AGENT]

    console.print(f"[bold]Discovered {len(resources)} resources:[/bold]")

    if skills:
        skill_names = ", ".join(sorted(r.name for r in skills))
        console.print(f"  [cyan]Skills ({len(skills)}):[/cyan] {skill_names}")
    if commands:
        command_names = ", ".join(sorted(r.name for r in commands))
        console.print(f"  [cyan]Commands ({len(commands)}):[/cyan] {command_names}")
    if agents:
        agent_names = ", ".join(sorted(r.name for r in agents))
        console.print(f"  [cyan]Agents ({len(agents)}):[/cyan] {agent_names}")


def _install_all_resources(
    repo_dir: Path,
    resources: list[ResolvedResource],
    owner: str,
    repo: str,
    base_path: Path,
    overwrite: bool,
) -> RepoSyncResult:
    """Install all discovered resources from a repository.

    Args:
        repo_dir: Path to the extracted repository
        resources: List of resources to install
        owner: GitHub owner/username
        repo: Repository name
        base_path: Base .claude directory path
        overwrite: Whether to overwrite existing resources

    Returns:
        RepoSyncResult with counts of installed, skipped, and errored resources
    """
    result = RepoSyncResult()

    for resource in resources:
        if resource.resource_type is None:
            result.errors.append((resource.name, "Unknown resource type"))
            continue

        try:
            res_config = RESOURCE_CONFIGS[resource.resource_type]
            dest = base_path / res_config.dest_subdir

            # Build path segments from the resource path
            path_segments = list(resource.path.parts)
            if path_segments and path_segments[-1] == "SKILL.md":
                path_segments = path_segments[:-1]

            # Use the last segment as the simple name
            simple_name = resource.name

            fetch_resource_from_repo_dir(
                repo_dir,
                simple_name,
                [simple_name],  # path_segments for destination
                dest,
                resource.resource_type,
                overwrite,
                username=owner,
                source_path=resource.path,
                package_name=resource.package_name,
            )

            # Track by type
            if resource.resource_type == ResourceType.SKILL:
                result.installed_skills.append(resource.name)
            elif resource.resource_type == ResourceType.COMMAND:
                result.installed_commands.append(resource.name)
            elif resource.resource_type == ResourceType.AGENT:
                result.installed_agents.append(resource.name)
            elif resource.resource_type == ResourceType.RULE:
                result.installed_rules.append(resource.name)

            console.print(f"  [green]+ {resource.resource_type.value} '{resource.name}'[/green]")

        except ResourceExistsError:
            result.skipped.append(resource.name)
            console.print(f"  [dim]= {resource.resource_type.value} '{resource.name}' (exists)[/dim]")

        except (ResourceNotFoundError, AgrError) as e:
            result.errors.append((resource.name, str(e)))
            console.print(f"  [red]! {resource.resource_type.value} '{resource.name}': {e}[/red]")

    return result


def _add_resources_to_toml(
    resources: list[ResolvedResource],
    owner: str,
    repo: str,
    installed_names: set[str],
    global_install: bool,
) -> None:
    """Add installed resources to agr.toml.

    Args:
        resources: List of all discovered resources
        owner: GitHub owner/username
        repo: Repository name
        installed_names: Names of resources that were actually installed
        global_install: Whether this is a global installation
    """
    if global_install:
        return

    try:
        config_path, config = get_or_create_config()

        for resource in resources:
            if resource.name not in installed_names:
                continue

            if resource.resource_type is None:
                continue

            # Build the handle: owner/repo/name or owner/name for default repo
            if repo == DEFAULT_REPO_NAME:
                handle = f"{owner}/{resource.name}"
            else:
                handle = f"{owner}/{repo}/{resource.name}"

            config.add_remote(handle, resource.resource_type.value)

        config.save(config_path)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not update agr.toml: {e}[/yellow]")


def _print_sync_repo_result(result: RepoSyncResult, owner: str, repo: str) -> None:
    """Print summary of repository sync results."""
    console.print()  # Empty line before summary

    if result.total_installed > 0:
        console.print(f"[green]Installed {result.total_installed} resources[/green]")

    if result.total_skipped > 0:
        console.print(
            f"[yellow]Skipped {result.total_skipped} existing resources. "
            f"Use --overwrite to replace.[/yellow]"
        )

    if result.total_errors > 0:
        console.print(f"[red]Failed to install {result.total_errors} resources[/red]")

    if result.total_installed > 0:
        console.print("[dim]Added to agr.toml[/dim]")


def _handle_sync_repo(
    owner: str,
    repo: str,
    global_install: bool,
    overwrite: bool,
    skip_confirm: bool,
    tool_flags: list[str] | None = None,
) -> None:
    """Sync all resources from a GitHub repository.

    Args:
        owner: GitHub owner/username
        repo: Repository name
        global_install: Whether to install globally
        overwrite: Whether to overwrite existing resources
        skip_confirm: Whether to skip confirmation prompt
        tool_flags: Optional list of tool names from CLI --tool flags
    """
    console.print(f"Fetching {owner}/{repo}...")

    try:
        with downloaded_repo(owner, repo) as repo_dir:
            # Discover all resources
            resources = discover_all_repo_resources(repo_dir)

            if not resources:
                console.print(f"[yellow]No resources found in {owner}/{repo}[/yellow]")
                return

            # Show discovered resources
            _print_discovered_resources(resources)
            console.print()

            # Load config for interactive selection check
            config_path_for_repo = find_config()
            config_for_repo = None
            if config_path_for_repo:
                config_for_repo = AgrConfig.load(config_path_for_repo)
            else:
                # Create a config path for potential tool selection
                config_path_for_repo = Path.cwd() / "agr.toml"
                config_for_repo = AgrConfig()

            # Check if interactive tool selection is needed
            if _needs_interactive_selection(config_for_repo, tool_flags):
                _interactive_tool_selection(config_for_repo, config_path_for_repo)
                # Reload config after selection
                config_for_repo = AgrConfig.load(config_path_for_repo)

            # Get target adapters
            try:
                adapters = get_target_adapters(config=config_for_repo, tool_flags=tool_flags)
            except InvalidToolError as e:
                console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1)

            # Show target tools
            if len(adapters) > 1:
                tool_names = [a.format.display_name for a in adapters]
                console.print(f"[dim]Target tools: {', '.join(tool_names)}[/dim]")
                console.print()

            # Confirm installation
            if not skip_confirm:
                if not typer.confirm(f"Install {len(resources)} resources?", default=True):
                    console.print("[dim]Cancelled[/dim]")
                    return

            # Install to each target tool
            any_errors = False
            for adapter in adapters:
                tool_name = adapter.format.display_name
                base_path = get_tool_base_path(adapter, global_install)

                if len(adapters) > 1:
                    console.print()
                    console.print(f"[bold]Installing to {tool_name}...[/bold]")
                else:
                    console.print()
                    console.print("[bold]Installing:[/bold]")

                # Install all resources
                result = _install_all_resources(
                    repo_dir, resources, owner, repo, base_path, overwrite
                )

                # Add to agr.toml (only once, for the first tool)
                if adapter == adapters[0]:
                    installed_names = set(
                        result.installed_skills
                        + result.installed_commands
                        + result.installed_agents
                        + result.installed_rules
                    )
                    _add_resources_to_toml(resources, owner, repo, installed_names, global_install)

                # Print summary for this tool
                if len(adapters) > 1:
                    console.print(f"  [{tool_name}] {result.total_installed} installed")
                else:
                    _print_sync_repo_result(result, owner, repo)

                if result.total_errors > 0:
                    any_errors = True

            if len(adapters) > 1:
                console.print()
                console.print(f"[dim]Summary: Synced to {len(adapters)} tool(s)[/dim]")

            if any_errors:
                raise typer.Exit(1)

    except RepoNotFoundError:
        console.print(f"[red]Repository '{owner}/{repo}' not found on GitHub.[/red]")
        raise typer.Exit(1)


def _prune_unlisted_local_resources(
    config: AgrConfig,
    base_path: Path,
    username: str,
    synced_names: set[str],
) -> int:
    """Remove local resources that are not in the config.

    For skills, checks for flattened names like "kasperjunge:commit"
    that start with the username prefix.
    """
    # Build set of expected local resources
    expected_paths = {dep.path for dep in config.get_local_dependencies()}

    pruned_count = 0

    # Check skills - now stored with flattened names at top level
    skills_dir = base_path / "skills"
    if skills_dir.is_dir():
        prefix = f"{username}:"
        for item in skills_dir.iterdir():
            if item.is_dir() and item.name.startswith(prefix):
                # This is a local skill (starts with our username)
                if item.name in synced_names:
                    continue
                # This resource is not in our expected set - it may be from old auto-discovery
                # Only prune if it looks like a local resource (not a remote one)
                # We can't easily tell, so we'll skip pruning here for safety
                # The user should manually remove unwanted resources

    # Check commands, agents, packages - still use nested structure
    for subdir in ["commands", "agents", "packages"]:
        user_dir = base_path / subdir / username
        if not user_dir.is_dir():
            continue

        for item in user_dir.iterdir():
            # Skip if this was just synced
            name = item.stem if item.is_file() else item.name
            if name in synced_names:
                continue

            # This resource is not in our expected set - it may be from old auto-discovery
            # Only prune if it looks like a local resource (not a remote one)
            # We can't easily tell, so we'll skip pruning here for safety
            # The user should manually remove unwanted resources

    return pruned_count


@app.command()
def sync(
    repo_ref: Annotated[
        Optional[str],
        typer.Argument(
            help="GitHub repository reference (owner/repo) to sync all resources from"
        ),
    ] = None,
    global_install: bool = typer.Option(
        False, "--global", "-g",
        help="Sync to global config directory",
    ),
    prune: bool = typer.Option(
        False, "--prune",
        help="Remove resources not listed in agr.toml",
    ),
    local_only: bool = typer.Option(
        False, "--local",
        help="Only sync local dependencies from agr.toml",
    ),
    remote_only: bool = typer.Option(
        False, "--remote",
        help="Only sync remote dependencies from agr.toml",
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", "-o",
        help="Overwrite existing resources (for repo sync)",
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y",
        help="Skip confirmation prompt (for repo sync)",
    ),
    tool: Annotated[
        Optional[List[str]],
        typer.Option(
            "--tool",
            help="Target tool(s) to sync to (e.g., --tool claude --tool cursor). Can be repeated.",
        ),
    ] = None,
) -> None:
    """Synchronize installed resources with agr.toml dependencies.

    Without arguments: syncs resources from agr.toml.
    With owner/repo argument: installs all resources from that GitHub repository.

    Examples:
        agr sync                              # Sync from agr.toml to configured tools
        agr sync --tool claude --tool cursor  # Sync to specific tools
        agr sync maragudk/skills              # Install all from maragudk/skills
        agr sync owner/repo --yes             # Skip confirmation

    Use --local to only sync local path dependencies.
    Use --remote to only sync remote GitHub dependencies.
    Use --tool to specify target tools (defaults to config or auto-detect).
    """
    # If repo_ref is provided, sync all resources from that repo
    if repo_ref:
        try:
            owner, repo = _parse_repo_ref(repo_ref)
        except typer.BadParameter as e:
            console.print(f"[red]{e}[/red]")
            raise typer.Exit(1)

        _handle_sync_repo(owner, repo, global_install, overwrite, yes, tool)
        return

    # Otherwise, sync from agr.toml
    config_path = find_config()
    if not config_path:
        console.print("[dim]No agr.toml found. Nothing to sync.[/dim]")
        console.print("[dim]Use 'agr add' to add dependencies first.[/dim]")
        return

    config = AgrConfig.load(config_path)

    # Save config if it was migrated from old format
    if config._migrated:
        config.save(config_path)
        console.print("[blue]Migrated agr.toml to new format[/blue]")

    # Check if interactive tool selection is needed
    if _needs_interactive_selection(config, tool):
        _interactive_tool_selection(config, config_path)
        # Reload config after selection
        config = AgrConfig.load(config_path)

    # Get target adapters
    try:
        adapters = get_target_adapters(config=config, tool_flags=tool)
    except InvalidToolError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    # Track overall results across all tools
    any_failed = False
    tool_results: dict[str, dict[str, int]] = {}

    for adapter in adapters:
        tool_name = adapter.format.display_name
        base_path = get_tool_base_path(adapter, global_install)

        if len(adapters) > 1:
            console.print(f"\n[bold]Syncing to {tool_name}...[/bold]")

        total_installed, total_updated, total_pruned, total_failed = 0, 0, 0, 0

        # Sync local dependencies
        if not remote_only:
            installed, updated, pruned, failed = _sync_local_dependencies(config, base_path, prune)
            total_installed += installed
            total_updated += updated
            total_pruned += pruned
            total_failed += failed

        # Sync remote dependencies
        if not local_only:
            installed, _skipped, failed, pruned = _sync_remote_dependencies(config, base_path, prune)
            total_installed += installed
            total_pruned += pruned
            total_failed += failed

        # Store results for this tool
        tool_results[tool_name] = {
            "installed": total_installed,
            "updated": total_updated,
            "pruned": total_pruned,
            "failed": total_failed,
        }

        if len(adapters) > 1:
            _print_tool_sync_summary(tool_name, total_installed, total_updated, total_pruned, total_failed)

        if total_failed > 0:
            any_failed = True

    # Print overall summary
    if len(adapters) == 1:
        results = list(tool_results.values())[0]
        _print_sync_summary(results["installed"], results["updated"], results["pruned"], results["failed"])
    else:
        _print_multi_tool_summary(tool_results)

    if any_failed:
        raise typer.Exit(1)


def _build_sync_parts(installed: int, updated: int, pruned: int, failed: int) -> list[str]:
    """Build list of sync result parts for display."""
    parts = []
    if installed:
        parts.append(f"{installed} installed")
    if updated:
        parts.append(f"{updated} updated")
    if pruned:
        parts.append(f"{pruned} pruned")
    if failed:
        parts.append(f"[red]{failed} failed[/red]")
    return parts


def _print_tool_sync_summary(tool_name: str, installed: int, updated: int, pruned: int, failed: int) -> None:
    """Print a summary of sync results for a single tool."""
    parts = _build_sync_parts(installed, updated, pruned, failed)
    summary = ", ".join(parts) if parts else "Nothing to sync"
    console.print(f"  [{tool_name}] {summary}")


def _format_count(value: int, color: str) -> str:
    """Format a count with color if non-zero, dim otherwise."""
    return f"[{color}]{value}[/{color}]" if value > 0 else "[dim]0[/dim]"


def _print_multi_tool_summary(tool_results: dict[str, dict[str, int]]) -> None:
    """Print overall summary for multi-tool sync."""
    from rich.table import Table

    total_installed = sum(r["installed"] for r in tool_results.values())
    total_updated = sum(r["updated"] for r in tool_results.values())
    total_failed = sum(r["failed"] for r in tool_results.values())

    console.print()

    if total_installed == 0 and total_updated == 0 and total_failed == 0:
        console.print("[dim]Nothing to sync across all tools.[/dim]")
        return

    table = Table(title="Sync Summary", show_header=True, header_style="bold")
    table.add_column("Tool", style="cyan")
    table.add_column("Installed", justify="right")
    table.add_column("Updated", justify="right")
    table.add_column("Failed", justify="right")

    for tool_name, results in tool_results.items():
        table.add_row(
            tool_name,
            _format_count(results["installed"], "green"),
            _format_count(results["updated"], "blue"),
            _format_count(results["failed"], "red"),
        )

    console.print(table)
    console.print()

    parts = []
    if total_installed > 0:
        parts.append(f"[green]{total_installed} installed[/green]")
    if total_updated > 0:
        parts.append(f"[blue]{total_updated} updated[/blue]")
    if total_failed > 0:
        parts.append(f"[red]{total_failed} failed[/red]")

    if parts:
        console.print(f"Total: {', '.join(parts)}")


def _print_sync_summary(installed: int, updated: int, pruned: int, failed: int) -> None:
    """Print a summary of sync results."""
    parts = _build_sync_parts(installed, updated, pruned, failed)
    if not parts:
        console.print("[dim]Nothing to sync.[/dim]")
        return
    console.print(f"[dim]Sync complete: {', '.join(parts)}[/dim]")


def _sync_remote_dependencies(
    config: AgrConfig,
    base_path: Path,
    prune: bool,
) -> tuple[int, int, int, int]:
    """Sync remote dependencies from agr.toml.

    Returns:
        Tuple of (installed, skipped, failed, pruned) counts
    """
    installed_count, skipped_count, failed_count, pruned_count = 0, 0, 0, 0

    for dep in config.get_remote_dependencies():
        if not dep.handle:
            continue

        try:
            username, repo_name, name = _parse_dependency_ref(dep.handle)
        except ValueError as e:
            console.print(f"[yellow]Skipping invalid dependency '{dep.handle}': {e}[/yellow]")
            continue

        resource_type = _type_string_to_enum(dep.type) if dep.type else ResourceType.SKILL

        if _is_resource_installed(username, name, resource_type, base_path):
            skipped_count += 1
            continue

        try:
            res_config = RESOURCE_CONFIGS[resource_type]
            dest = base_path / res_config.dest_subdir

            with fetch_spinner():
                fetch_resource(
                    username, repo_name, name, [name], dest, resource_type,
                    overwrite=False, username=username,
                )
            console.print(f"[green]Installed {resource_type.value} '{name}'[/green]")
            installed_count += 1
        except (RepoNotFoundError, ResourceNotFoundError, AgrError) as e:
            console.print(f"[red]Failed to install '{dep.handle}': {e}[/red]")
            failed_count += 1

    if prune:
        pruned_count = _prune_unlisted_remote_resources(config, base_path)

    return (installed_count, skipped_count, failed_count, pruned_count)


def _prune_unlisted_remote_resources(config: AgrConfig, base_path: Path) -> int:
    """Remove installed resources that are not in the config."""
    expected_refs = set()
    for dep in config.get_remote_dependencies():
        if not dep.handle:
            continue
        try:
            username, _, name = _parse_dependency_ref(dep.handle)
            expected_refs.add(f"{username}/{name}")
        except ValueError:
            continue

    installed_refs = _discover_installed_namespaced_resources(base_path)
    pruned_count = 0

    for ref in installed_refs:
        if ref not in expected_refs:
            parts = ref.split("/")
            if len(parts) == 2:
                username, name = parts
                _remove_namespaced_resource(username, name, base_path)
                console.print(f"[yellow]Pruned '{ref}'[/yellow]")
                pruned_count += 1

    return pruned_count
