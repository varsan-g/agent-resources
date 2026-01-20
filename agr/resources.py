"""Resources directory utilities for agr.

Provides utilities for managing the resources/ directory as the source of truth
for local resources in a project.

Architecture:
    resources/              <- Source (git tracked, for local resources)
      skills/
      rules/
      commands/
      agents/

    .claude/                <- Derived (gitignored)
    .cursor/                <- Derived (gitignored)

    agr.toml                <- Declares dependencies + target tools
"""

import shutil
from dataclasses import dataclass
from pathlib import Path

# Standard subdirectory names in resources/
RESOURCE_SUBDIRS = {
    "skill": "skills",
    "command": "commands",
    "agent": "agents",
    "rule": "rules",
    "package": "packages",
}

# Default resources directory name
RESOURCES_DIR_NAME = "resources"


def get_resources_dir(base_path: Path | None = None) -> Path:
    """Get the path to the resources directory.

    Args:
        base_path: Base path (defaults to cwd)

    Returns:
        Path to the resources/ directory
    """
    return (base_path or Path.cwd()) / RESOURCES_DIR_NAME


def is_in_resources_dir(path: Path, base_path: Path | None = None) -> bool:
    """Check if a path is inside the resources/ directory.

    Args:
        path: Path to check
        base_path: Base path for resources dir (defaults to cwd)

    Returns:
        True if path is inside resources/
    """
    resources_dir = get_resources_dir(base_path)
    try:
        resolved_path = path.resolve()
        resolved_resources = resources_dir.resolve()
        return resolved_path.is_relative_to(resolved_resources)
    except ValueError:
        return False


def _is_directory_resource(resource_type: str) -> bool:
    """Return True if the resource type is stored as a directory."""
    return resource_type in ("skill", "package")


def _normalize_resource_name(resource_type: str, name: str) -> str:
    """Normalize resource name, adding .md extension for file-based resources."""
    if _is_directory_resource(resource_type):
        return name
    if not name.endswith(".md"):
        return f"{name}.md"
    return name


def get_resource_dest_path(
    resource_type: str,
    name: str,
    base_path: Path | None = None,
) -> Path:
    """Build the destination path for a resource in resources/.

    Args:
        resource_type: Type of resource (skill, command, agent, rule, package)
        name: Name of the resource
        base_path: Base path for resources dir (defaults to cwd)

    Returns:
        Path where the resource should be stored

    Examples:
        get_resource_dest_path("skill", "commit") -> resources/skills/commit/
        get_resource_dest_path("command", "deploy") -> resources/commands/deploy.md
    """
    resources_dir = get_resources_dir(base_path)
    subdir = RESOURCE_SUBDIRS.get(resource_type, f"{resource_type}s")
    normalized_name = _normalize_resource_name(resource_type, name)
    return resources_dir / subdir / normalized_name


def resource_exists_in_resources(
    resource_type: str,
    name: str,
    base_path: Path | None = None,
) -> bool:
    """Check if a resource already exists in the resources/ directory.

    Args:
        resource_type: Type of resource (skill, command, agent, rule, package)
        name: Name of the resource
        base_path: Base path for resources dir (defaults to cwd)

    Returns:
        True if the resource already exists
    """
    return get_resource_dest_path(resource_type, name, base_path).exists()


def get_relative_resources_path(
    resource_type: str,
    name: str,
) -> str:
    """Get the relative path string for agr.toml.

    Args:
        resource_type: Type of resource
        name: Name of the resource

    Returns:
        Relative path string like "resources/skills/commit"
    """
    subdir = RESOURCE_SUBDIRS.get(resource_type, f"{resource_type}s")
    normalized_name = _normalize_resource_name(resource_type, name)
    return f"{RESOURCES_DIR_NAME}/{subdir}/{normalized_name}"


@dataclass
class CopyResult:
    """Result of copying a resource to resources/."""

    success: bool
    dest_path: Path
    relative_path: str
    error: str | None = None


def copy_to_resources(
    source_path: Path,
    resource_type: str,
    name: str | None = None,
    base_path: Path | None = None,
    force: bool = False,
) -> CopyResult:
    """Copy a resource to the resources/ directory.

    Args:
        source_path: Path to the source resource
        resource_type: Type of resource (skill, command, agent, rule, package)
        name: Name for the resource (defaults to source name)
        base_path: Base path for resources dir (defaults to cwd)
        force: Overwrite existing resource if True

    Returns:
        CopyResult with success status and paths
    """
    if name is None:
        name = source_path.stem if source_path.is_file() else source_path.name

    dest_path = get_resource_dest_path(resource_type, name, base_path)
    relative_path = get_relative_resources_path(resource_type, name)

    # Check if already exists
    if dest_path.exists() and not force:
        return CopyResult(
            success=False,
            dest_path=dest_path,
            relative_path=relative_path,
            error=f"Resource already exists at {relative_path}. Use --force to overwrite.",
        )

    try:
        # Create parent directories
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Remove existing if force
        if dest_path.exists():
            if dest_path.is_dir():
                shutil.rmtree(dest_path)
            else:
                dest_path.unlink()

        # Copy source to destination
        if source_path.is_dir():
            shutil.copytree(source_path, dest_path)
        else:
            shutil.copy2(source_path, dest_path)

        return CopyResult(
            success=True,
            dest_path=dest_path,
            relative_path=relative_path,
        )

    except Exception as e:
        return CopyResult(
            success=False,
            dest_path=dest_path,
            relative_path=relative_path,
            error=str(e),
        )


def ensure_resources_structure(base_path: Path | None = None) -> None:
    """Ensure the resources/ directory structure exists.

    Creates:
        resources/
            skills/
            commands/
            agents/
            rules/

    Args:
        base_path: Base path for resources dir (defaults to cwd)
    """
    resources_dir = get_resources_dir(base_path)

    for subdir in RESOURCE_SUBDIRS.values():
        (resources_dir / subdir).mkdir(parents=True, exist_ok=True)
