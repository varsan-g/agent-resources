"""Status models and computation for agr.

Provides data models and utilities for tracking sync status of resources
across multiple AI coding tools.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agr.adapters.base import ToolAdapter
    from agr.config import AgrConfig, Dependency


class SyncStatus(Enum):
    """Status of a resource relative to its expected state."""

    SYNCED = "synced"  # Resource exists and matches source
    OUTDATED = "outdated"  # Resource exists but may need update
    MISSING = "missing"  # Resource should exist but doesn't
    UNTRACKED = "untracked"  # Resource exists but not in agr.toml


@dataclass
class ToolResourceStatus:
    """Status of a resource in a specific tool."""

    tool_name: str
    status: SyncStatus
    path: Path | None = None
    message: str | None = None


@dataclass
class ResourceStatus:
    """Status of a resource across all target tools."""

    identifier: str  # Handle or path from agr.toml
    resource_type: str
    is_local: bool
    source_path: Path | None = None
    tool_statuses: list[ToolResourceStatus] = field(default_factory=list)

    @property
    def is_synced_all(self) -> bool:
        """Return True if resource is synced to all tools."""
        return all(ts.status == SyncStatus.SYNCED for ts in self.tool_statuses)

    @property
    def has_issues(self) -> bool:
        """Return True if any tool has missing or outdated status."""
        return any(
            ts.status in (SyncStatus.MISSING, SyncStatus.OUTDATED)
            for ts in self.tool_statuses
        )


@dataclass
class UntrackedResource:
    """A resource found in a tool directory but not in agr.toml."""

    tool_name: str
    name: str
    resource_type: str
    path: Path


@dataclass
class StatusReport:
    """Complete status report for a project."""

    target_tools: list[str]
    resources: list[ResourceStatus] = field(default_factory=list)
    untracked: list[UntrackedResource] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        """Return True if there's any drift between config and installed."""
        return any(r.has_issues for r in self.resources) or bool(self.untracked)

    @property
    def all_synced(self) -> bool:
        """Return True if all resources are fully synced."""
        return all(r.is_synced_all for r in self.resources) and not self.untracked

    @property
    def missing_count(self) -> int:
        """Count of missing resources across all tools."""
        return sum(
            1 for r in self.resources for ts in r.tool_statuses
            if ts.status == SyncStatus.MISSING
        )

    @property
    def synced_count(self) -> int:
        """Count of synced resources across all tools."""
        return sum(
            1 for r in self.resources for ts in r.tool_statuses
            if ts.status == SyncStatus.SYNCED
        )


def _check_skill_installed(installed_path: Path) -> bool:
    """Check if a skill is installed at the given path."""
    return installed_path.is_dir() and (installed_path / "SKILL.md").exists()


def _make_status(
    tool_name: str, installed_path: Path, is_installed: bool
) -> ToolResourceStatus:
    """Create a ToolResourceStatus based on installation status."""
    status = SyncStatus.SYNCED if is_installed else SyncStatus.MISSING
    return ToolResourceStatus(tool_name=tool_name, status=status, path=installed_path)


def check_resource_in_tool(
    dep: "Dependency",
    adapter: "ToolAdapter",
    base_path: Path,
    repo_root: Path | None = None,
) -> ToolResourceStatus:
    """Check the sync status of a dependency in a specific tool.

    Args:
        dep: The dependency to check
        adapter: Tool adapter to check against
        base_path: Base path for the tool (e.g., .claude/)
        repo_root: Repository root for local paths

    Returns:
        ToolResourceStatus with the check result
    """
    tool_name = adapter.format.display_name

    if dep.is_local and dep.path:
        source_path = (repo_root or Path.cwd()) / dep.path
        if not source_path.exists():
            return ToolResourceStatus(
                tool_name=tool_name,
                status=SyncStatus.MISSING,
                message=f"Source path not found: {dep.path}",
            )

        from agr.github import get_username_from_git_remote

        username = get_username_from_git_remote(repo_root) or "local"

        if dep.type == "skill":
            from agr.utils import compute_flattened_resource_name, compute_path_segments

            path_segments = compute_path_segments(source_path)
            flattened_name = compute_flattened_resource_name(username, path_segments, None)
            installed_path = base_path / "skills" / flattened_name
            return _make_status(tool_name, installed_path, _check_skill_installed(installed_path))

        name = source_path.stem
        installed_path = base_path / f"{dep.type}s" / username / f"{name}.md"
        return _make_status(tool_name, installed_path, installed_path.exists())

    if dep.is_remote and dep.handle:
        from agr.handle import ParsedHandle

        try:
            handle = ParsedHandle.from_handle(dep.handle)
        except Exception:
            return ToolResourceStatus(
                tool_name=tool_name,
                status=SyncStatus.MISSING,
                message=f"Invalid handle: {dep.handle}",
            )

        if dep.type == "skill":
            installed_path = handle.to_skill_path(base_path)
            return _make_status(tool_name, installed_path, _check_skill_installed(installed_path))

        installed_path = handle.to_resource_path(base_path, dep.type)
        return _make_status(tool_name, installed_path, installed_path.exists())

    return ToolResourceStatus(
        tool_name=tool_name,
        status=SyncStatus.MISSING,
        message="Unknown dependency type",
    )


def discover_untracked_resources(
    adapter: "ToolAdapter",
    base_path: Path,
    config: "AgrConfig",
) -> list[UntrackedResource]:
    """Discover resources installed in a tool but not in agr.toml.

    Args:
        adapter: Tool adapter
        base_path: Base path for the tool
        config: Current configuration

    Returns:
        List of untracked resources
    """
    tool_name = adapter.format.display_name
    untracked = []

    # Get all installed resources
    installed = adapter.discover_installed(base_path)

    # Build set of expected identifiers from config
    expected_handles = {dep.handle for dep in config.dependencies if dep.handle}
    expected_paths = {dep.path for dep in config.dependencies if dep.path}

    for resource in installed:
        # Check if this resource is tracked
        # For skills with namespaced names like "kasperjunge:commit"
        # The handle in config is "kasperjunge/commit"
        if resource.username:
            # Remote resource - check handle
            possible_handle = f"{resource.username}/{resource.name}"
            if possible_handle in expected_handles:
                continue
            # Also check 3-part handles
            for handle in expected_handles:
                parts = handle.split("/") if handle else []
                if len(parts) == 3 and parts[2] == resource.name:
                    continue

        # Check if it's a local resource by checking paths
        # This is approximate - local resources may have different names
        is_tracked = False
        for path in expected_paths:
            if path and resource.name in path:
                is_tracked = True
                break

        if not is_tracked:
            untracked.append(
                UntrackedResource(
                    tool_name=tool_name,
                    name=resource.name,
                    resource_type=resource.resource_type,
                    path=resource.path,
                )
            )

    return untracked


def compute_status_report(
    config: "AgrConfig",
    adapters: list["ToolAdapter"],
    repo_root: Path | None = None,
) -> StatusReport:
    """Compute the full status report for a project.

    Args:
        config: Current configuration
        adapters: List of target tool adapters
        repo_root: Repository root path

    Returns:
        StatusReport with all resource statuses
    """
    from agr.cli.multi_tool import get_tool_base_path

    tool_names = [a.format.display_name for a in adapters]
    report = StatusReport(target_tools=tool_names)

    # Check each dependency
    for dep in config.dependencies:
        source_path = None
        if dep.is_local and dep.path:
            source_path = (repo_root or Path.cwd()) / dep.path

        resource_status = ResourceStatus(
            identifier=dep.identifier,
            resource_type=dep.type,
            is_local=dep.is_local,
            source_path=source_path,
        )

        for adapter in adapters:
            base_path = get_tool_base_path(adapter, global_install=False)
            tool_status = check_resource_in_tool(dep, adapter, base_path, repo_root)
            resource_status.tool_statuses.append(tool_status)

        report.resources.append(resource_status)

    # Discover untracked resources
    for adapter in adapters:
        base_path = get_tool_base_path(adapter, global_install=False)
        if base_path.exists():
            untracked = discover_untracked_resources(adapter, base_path, config)
            report.untracked.extend(untracked)

    return report
