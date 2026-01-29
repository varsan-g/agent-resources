"""GitHub download and skill installation."""

import logging
import os
import shutil
import tarfile
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import httpx

from agr.exceptions import (
    AgrError,
    AuthenticationError,
    RepoNotFoundError,
    SkillNotFoundError,
)
from agr.handle import INSTALLED_NAME_SEPARATOR, ParsedHandle
from agr.metadata import build_handle_id, read_skill_metadata, write_skill_metadata
from agr.skill import (
    SKILL_MARKER,
    find_skill_in_repo,
    is_valid_skill_dir,
    update_skill_md_name,
)
from agr.tool import DEFAULT_TOOL, ToolConfig

logger = logging.getLogger(__name__)


def _skill_dir_matches_handle(skill_dir: Path, handle_id: str | None) -> bool:
    """Check whether a skill directory matches a handle via metadata."""
    if not handle_id:
        return False
    meta = read_skill_metadata(skill_dir)
    if not meta:
        return False
    return meta.get("id") == handle_id


def _find_local_name_conflicts(
    handle: ParsedHandle,
    skills_dir: Path,
    tool: ToolConfig,
    repo_root: Path | None,
    default_dest: Path,
) -> tuple[list[Path], bool]:
    """Find conflicting local installs with the same skill name.

    Returns a tuple of (conflict_paths, has_unknown_metadata).
    """
    handle_id = build_handle_id(handle, repo_root)
    conflicts: list[Path] = []
    has_unknown = False

    if tool.supports_nested:
        candidates = [skills_dir / "local" / handle.name]
    else:
        candidates = [skills_dir / handle.name, skills_dir / handle.to_installed_name()]

    for path in candidates:
        if tool.supports_nested and path == default_dest:
            continue
        if not is_valid_skill_dir(path):
            continue
        meta = read_skill_metadata(path)
        if meta:
            if meta.get("type") != "local":
                continue
            if meta.get("id") == handle_id:
                continue
            conflicts.append(path)
            continue
        has_unknown = True
        conflicts.append(path)

    return conflicts, has_unknown


def _find_existing_skill_dir(
    handle: ParsedHandle,
    skills_dir: Path,
    tool: ToolConfig,
    repo_root: Path | None,
) -> Path | None:
    """Find an existing installed skill directory for this handle."""
    if tool.supports_nested:
        skill_path = skills_dir / handle.to_skill_path(tool)
        return skill_path if is_valid_skill_dir(skill_path) else None

    handle_id = build_handle_id(handle, repo_root)
    name_path = skills_dir / handle.name
    full_path = skills_dir / handle.to_installed_name()

    if is_valid_skill_dir(name_path) and _skill_dir_matches_handle(
        name_path, handle_id
    ):
        return name_path
    if is_valid_skill_dir(full_path) and _skill_dir_matches_handle(
        full_path, handle_id
    ):
        return full_path

    # Legacy fallback: flat installs used full path names
    if is_valid_skill_dir(full_path):
        return full_path

    return None


def _resolve_skill_destination(
    handle: ParsedHandle,
    skills_dir: Path,
    tool: ToolConfig,
    repo_root: Path | None,
) -> Path:
    """Resolve the destination path for installing a skill."""
    if tool.supports_nested:
        return skills_dir / handle.to_skill_path(tool)

    existing = _find_existing_skill_dir(handle, skills_dir, tool, repo_root)
    if existing:
        return existing

    name_path = skills_dir / handle.name
    if is_valid_skill_dir(name_path):
        return skills_dir / handle.to_installed_name()

    return name_path


def _get_github_token() -> str | None:
    """Get GitHub token from environment.

    Checks GITHUB_TOKEN first, then falls back to GH_TOKEN (used by gh CLI).

    Returns:
        Token string if set and non-empty, None otherwise.
    """
    for env_var in ("GITHUB_TOKEN", "GH_TOKEN"):
        token = os.environ.get(env_var, "")
        if token.strip():
            return token.strip()
    return None


@contextmanager
def downloaded_repo(username: str, repo_name: str) -> Generator[Path, None, None]:
    """Download a GitHub repo tarball and yield the extracted directory.

    Args:
        username: GitHub username
        repo_name: Repository name

    Yields:
        Path to extracted repository directory

    Raises:
        RepoNotFoundError: If the repository doesn't exist
        AuthenticationError: If authentication fails (private repo without valid token)
        AgrError: If download or extraction fails
    """
    tarball_url = (
        f"https://github.com/{username}/{repo_name}/archive/refs/heads/main.tar.gz"
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        tarball_path = tmp_path / "repo.tar.gz"

        # Download tarball
        try:
            # Build headers with optional auth
            headers = {}
            token = _get_github_token()
            if token:
                headers["Authorization"] = f"token {token}"

            with httpx.Client(follow_redirects=True, timeout=30.0) as client:
                response = client.get(tarball_url, headers=headers)
                if response.status_code == 401:
                    if token:
                        raise AuthenticationError(
                            "Authentication failed. Check that GITHUB_TOKEN is valid."
                        )
                    else:
                        raise AuthenticationError(
                            "Authentication required. Set GITHUB_TOKEN to access this repository."
                        )
                if response.status_code == 403:
                    if token:
                        raise AuthenticationError(
                            "Access denied. Check that GITHUB_TOKEN has 'repo' scope "
                            "for private repositories."
                        )
                    else:
                        raise AuthenticationError(
                            "Access denied. Set GITHUB_TOKEN to access private repositories."
                        )
                if response.status_code == 404:
                    raise RepoNotFoundError(
                        f"Repository '{username}/{repo_name}' not found on GitHub"
                    )
                if response.status_code == 429:
                    raise AgrError(
                        "GitHub rate limit exceeded. Set GITHUB_TOKEN for higher limits "
                        "or wait before retrying."
                    )
                response.raise_for_status()
                tarball_path.write_bytes(response.content)
        except httpx.HTTPStatusError:
            # Don't include the original exception - it may contain auth headers
            raise AgrError(
                f"Failed to download repository '{username}/{repo_name}': "
                f"HTTP {response.status_code}"
            ) from None
        except httpx.RequestError as e:
            raise AgrError(f"Network error: {type(e).__name__}") from None

        # Extract tarball
        extract_path = tmp_path / "extracted"
        with tarfile.open(tarball_path, "r:gz") as tar:
            tar.extractall(extract_path, filter="data")

        # GitHub tarballs extract to {repo}-{branch}/
        repo_dir = extract_path / f"{repo_name}-main"
        if not repo_dir.exists():
            # Try finding the extracted directory
            dirs = list(extract_path.iterdir())
            if dirs:
                repo_dir = dirs[0]
            else:
                raise AgrError("Failed to extract repository")

        yield repo_dir


def _copy_skill_to_destination(
    source: Path,
    dest: Path,
    handle: ParsedHandle,
    tool: ToolConfig,
    overwrite: bool,
    repo_root: Path | None,
) -> Path:
    """Copy skill source to destination with overwrite handling.

    Args:
        source: Source skill directory
        dest: Destination path
        handle: Parsed handle for naming
        tool: Tool configuration
        overwrite: Whether to overwrite existing
        repo_root: Repository root for metadata resolution (optional)

    Returns:
        Path to installed skill

    Raises:
        FileExistsError: If skill exists and not overwriting
    """
    if dest.exists() and not overwrite:
        raise FileExistsError(
            f"Skill already exists at {dest}. Use --overwrite to replace."
        )

    if dest.exists():
        shutil.rmtree(dest)

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, dest)

    update_skill_md_name(dest, dest.name)
    write_skill_metadata(dest, handle, repo_root, tool.name, dest.name)

    return dest


def install_skill_from_repo(
    repo_dir: Path,
    skill_name: str,
    handle: ParsedHandle,
    dest_dir: Path,
    tool: ToolConfig,
    repo_root: Path | None,
    overwrite: bool = False,
) -> Path:
    """Install a skill from a downloaded repository.

    Args:
        repo_dir: Path to extracted repository
        skill_name: Name of the skill to install
        handle: Parsed handle for naming
        dest_dir: Destination skills directory
        tool: Tool configuration for path structure
        repo_root: Repository root for metadata resolution (optional)
        overwrite: Whether to overwrite existing

    Returns:
        Path to installed skill

    Raises:
        SkillNotFoundError: If skill not found in repo
        FileExistsError: If skill exists and not overwriting
    """
    # Find the skill in the repo
    skill_source = find_skill_in_repo(repo_dir, skill_name)
    if skill_source is None:
        raise SkillNotFoundError(
            f"Skill '{skill_name}' not found in repository.\n"
            f"No directory named '{skill_name}' containing SKILL.md was found.\n"
            f"Hint: Create a skill at 'skills/{skill_name}/SKILL.md' or '{skill_name}/SKILL.md'"
        )

    skill_dest = _resolve_skill_destination(handle, dest_dir, tool, repo_root)

    return _copy_skill_to_destination(
        skill_source, skill_dest, handle, tool, overwrite, repo_root
    )


def install_local_skill(
    source_path: Path,
    dest_dir: Path,
    tool: ToolConfig,
    overwrite: bool = False,
    repo_root: Path | None = None,
    handle: ParsedHandle | None = None,
) -> Path:
    """Install a local skill.

    Args:
        source_path: Path to local skill directory
        dest_dir: Destination skills directory
        tool: Tool configuration for path structure
        overwrite: Whether to overwrite existing
        repo_root: Repository root for metadata resolution (optional)
        handle: Optional pre-parsed handle for metadata and naming

    Returns:
        Path to installed skill

    Raises:
        SkillNotFoundError: If source is not a valid skill
        FileExistsError: If skill exists and not overwriting
        AgrError: If skill name contains reserved separator
    """
    # Validate source
    if not is_valid_skill_dir(source_path):
        raise SkillNotFoundError(
            f"'{source_path}' is not a valid skill (missing {SKILL_MARKER})"
        )

    # Validate skill name doesn't contain reserved separator (for flat tools)
    if not tool.supports_nested and INSTALLED_NAME_SEPARATOR in source_path.name:
        raise AgrError(
            f"Skill name '{source_path.name}' contains reserved sequence '{INSTALLED_NAME_SEPARATOR}'"
        )

    # Determine installed path using ParsedHandle for consistency
    handle = handle or ParsedHandle(
        is_local=True, name=source_path.name, local_path=source_path
    )
    if repo_root is None:
        # dest_dir is typically <repo>/.tool/skills
        repo_root = dest_dir.parent.parent

    default_dest = dest_dir / handle.to_skill_path(tool)
    conflicts, has_unknown = _find_local_name_conflicts(
        handle, dest_dir, tool, repo_root, default_dest
    )
    if conflicts:
        locations = ", ".join(str(path) for path in conflicts)
        hint = ""
        if has_unknown:
            hint = " If this is a remote skill, run `agr sync` or reinstall it to add metadata."
        raise AgrError(
            f"Local skill name '{handle.name}' is already installed at {locations}. "
            "agr allows only one local skill with a given name. "
            "Rename the skill or remove the existing one."
            f"{hint}"
        )

    skill_dest = _resolve_skill_destination(handle, dest_dir, tool, repo_root)

    return _copy_skill_to_destination(
        source_path, skill_dest, handle, tool, overwrite, repo_root
    )


def fetch_and_install(
    handle: ParsedHandle,
    repo_root: Path,
    tool: ToolConfig = DEFAULT_TOOL,
    overwrite: bool = False,
) -> Path:
    """Fetch and install a skill.

    Args:
        handle: Parsed handle (remote or local)
        repo_root: Repository root path
        tool: Tool configuration for path structure
        overwrite: Whether to overwrite existing

    Returns:
        Path to installed skill

    Raises:
        Various exceptions on failure
    """
    skills_dir = tool.get_skills_dir(repo_root)

    if handle.is_local:
        # Local skill installation
        if handle.local_path is None:
            raise ValueError("Local handle missing path")

        source_path = handle.local_path
        if not source_path.is_absolute():
            source_path = (repo_root / source_path).resolve()

        return install_local_skill(
            source_path, skills_dir, tool, overwrite, repo_root, handle
        )

    # Remote skill installation
    username, repo_name = handle.get_github_repo()

    with downloaded_repo(username, repo_name) as repo_dir:
        return install_skill_from_repo(
            repo_dir, handle.name, handle, skills_dir, tool, repo_root, overwrite
        )


def fetch_and_install_to_tools(
    handle: ParsedHandle,
    repo_root: Path,
    tools: list[ToolConfig],
    overwrite: bool = False,
) -> dict[str, Path]:
    """Fetch skill once and install to multiple tools.

    This optimizes the common case of installing to multiple tools by
    downloading the repository only once.

    Args:
        handle: Parsed handle (remote or local)
        repo_root: Repository root path
        tools: List of tool configurations to install to
        overwrite: Whether to overwrite existing installations

    Returns:
        Dict mapping tool name to installed path

    Raises:
        Various exceptions on failure. On partial failure, already installed
        tools are rolled back (removed).
    """
    if not tools:
        raise ValueError("No tools provided for installation")

    installed: dict[str, Path] = {}

    def _rollback():
        """Remove all successfully installed skills."""
        for tool_name, rollback_path in installed.items():
            try:
                shutil.rmtree(rollback_path)
            except OSError as e:
                logger.warning(
                    f"Failed to rollback {tool_name} at {rollback_path}: {e}"
                )

    if handle.is_local:
        # Local: no download needed, just iterate with rollback
        for tool in tools:
            try:
                installed[tool.name] = fetch_and_install(
                    handle, repo_root, tool, overwrite
                )
            except Exception:
                _rollback()
                raise
        return installed

    # Remote: download once, install to all
    username, repo_name = handle.get_github_repo()

    with downloaded_repo(username, repo_name) as repo_dir:
        for tool in tools:
            try:
                skills_dir = tool.get_skills_dir(repo_root)
                path = install_skill_from_repo(
                    repo_dir,
                    handle.name,
                    handle,
                    skills_dir,
                    tool,
                    repo_root,
                    overwrite,
                )
                installed[tool.name] = path
            except Exception:
                _rollback()
                raise

    return installed


def uninstall_skill(
    handle: ParsedHandle, repo_root: Path, tool: ToolConfig = DEFAULT_TOOL
) -> bool:
    """Uninstall a skill.

    Args:
        handle: Parsed handle identifying the skill
        repo_root: Repository root path
        tool: Tool configuration for path structure

    Returns:
        True if removed, False if not found
    """
    skills_dir = tool.get_skills_dir(repo_root)
    skill_path = _find_existing_skill_dir(handle, skills_dir, tool, repo_root)

    if not skill_path:
        return False

    shutil.rmtree(skill_path)

    # Clean up empty parent directories for nested structures
    if tool.supports_nested:
        _cleanup_empty_parents(skill_path.parent, skills_dir)

    return True


def _cleanup_empty_parents(path: Path, stop_at: Path) -> None:
    """Remove empty parent directories up to stop_at.

    Args:
        path: Starting path to clean
        stop_at: Directory to stop at (not removed)
    """
    # Resolve symlinks to ensure proper path comparison
    path = path.resolve()
    stop_at = stop_at.resolve()
    current = path

    while current != stop_at and current.exists():
        # Safety: ensure we're still within stop_at
        try:
            current.relative_to(stop_at)
        except ValueError:
            break  # Escaped the directory

        if current.is_dir() and not any(current.iterdir()):
            try:
                current.rmdir()
            except OSError:
                break  # Permission error or other issue
            current = current.parent
        else:
            break


def get_installed_skills(repo_root: Path, tool: ToolConfig = DEFAULT_TOOL) -> list[str]:
    """Get list of installed skill names.

    Args:
        repo_root: Repository root path
        tool: Tool configuration for path structure

    Returns:
        List of installed skill directory names (flat) or paths (nested)
    """
    skills_dir = tool.get_skills_dir(repo_root)

    if not skills_dir.exists():
        return []

    if tool.supports_nested:
        # For nested tools, recursively find all SKILL.md files
        skills = []
        for skill_md in skills_dir.rglob(SKILL_MARKER):
            skill_path = skill_md.parent.relative_to(skills_dir)
            skills.append(str(skill_path))
        return skills
    else:
        # For flat tools, just list top-level directories
        return [
            d.name
            for d in skills_dir.iterdir()
            if d.is_dir() and (d / SKILL_MARKER).exists()
        ]


def is_skill_installed(
    handle: ParsedHandle, repo_root: Path, tool: ToolConfig = DEFAULT_TOOL
) -> bool:
    """Check if a skill is installed.

    Args:
        handle: Parsed handle identifying the skill
        repo_root: Repository root path
        tool: Tool configuration for path structure

    Returns:
        True if installed
    """
    skills_dir = tool.get_skills_dir(repo_root)
    skill_path = _find_existing_skill_dir(handle, skills_dir, tool, repo_root)
    return bool(skill_path and is_valid_skill_dir(skill_path))
