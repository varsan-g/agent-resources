"""Utility functions for agr."""

import re
from pathlib import Path


def compute_flattened_skill_name(username: str, path_segments: list[str]) -> str:
    """Compute the flattened skill name with colons.

    Claude Code's .claude/skills/ directory only discovers top-level directories.
    To support nested skill organization, we flatten the path using colons.

    Args:
        username: The GitHub username or "local" for local resources
        path_segments: Path segments from skills/ root to the skill
                       e.g., ["commit"] or ["product-strategy", "growth-hacker"]

    Returns:
        Flattened name with colons, e.g.:
        - ("kasperjunge", ["commit"]) -> "kasperjunge:commit"
        - ("kasperjunge", ["product-strategy", "growth-hacker"]) -> "kasperjunge:product-strategy:growth-hacker"

    Examples:
        >>> compute_flattened_skill_name("kasperjunge", ["commit"])
        'kasperjunge:commit'
        >>> compute_flattened_skill_name("kasperjunge", ["product-strategy", "growth-hacker"])
        'kasperjunge:product-strategy:growth-hacker'
        >>> compute_flattened_skill_name("dsjacobsen", ["golang-pro"])
        'dsjacobsen:golang-pro'
    """
    if not path_segments:
        raise ValueError("path_segments cannot be empty")

    parts = [username] + path_segments
    return ":".join(parts)


def compute_path_segments_from_skill_path(skill_path: Path, skills_root: Path | None = None) -> list[str]:
    """Compute namespace path segments from a skill source path.

    Extracts the relative path from the skills/ root to the skill directory.

    Args:
        skill_path: Full path to the skill directory
        skills_root: Optional explicit skills root. If not provided, attempts
                     to find "skills" in the path.

    Returns:
        List of path segments from skills root to skill.

    Examples:
        >>> compute_path_segments_from_skill_path(Path("./resources/skills/commit"))
        ['commit']
        >>> compute_path_segments_from_skill_path(Path("./resources/skills/product-strategy/growth-hacker"))
        ['product-strategy', 'growth-hacker']
        >>> compute_path_segments_from_skill_path(Path("./skills/my-skill"))
        ['my-skill']
    """
    parts = skill_path.parts

    # If explicit skills_root provided, compute relative path
    if skills_root is not None:
        try:
            rel_path = skill_path.relative_to(skills_root)
            return list(rel_path.parts)
        except ValueError:
            # skill_path is not relative to skills_root, fall back to name only
            return [skill_path.name]

    # Find "skills" in path and take everything after
    try:
        skills_idx = parts.index("skills")
        segments = list(parts[skills_idx + 1 :])
        if segments:
            return segments
    except ValueError:
        pass

    # No "skills" in path, use just the name
    return [skill_path.name]


def update_skill_md_name(skill_dir: Path, new_name: str) -> None:
    """Update the name field in SKILL.md after installation.

    Parses the YAML frontmatter and updates the 'name' field to match
    the flattened directory name for discoverability.

    Args:
        skill_dir: Path to the skill directory containing SKILL.md
        new_name: The new name to set in the frontmatter

    Raises:
        FileNotFoundError: If SKILL.md doesn't exist in skill_dir
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

    content = skill_md.read_text()

    # Check if file has YAML frontmatter (starts with ---)
    if not content.startswith("---"):
        # No frontmatter, add it with name
        new_content = f"---\nname: {new_name}\n---\n\n{content}"
        skill_md.write_text(new_content)
        return

    # Split by frontmatter delimiter
    parts = content.split("---", 2)
    if len(parts) < 3:
        # Malformed frontmatter, prepend new frontmatter
        new_content = f"---\nname: {new_name}\n---\n\n{content}"
        skill_md.write_text(new_content)
        return

    frontmatter = parts[1]
    body = parts[2]

    # Update or add name in frontmatter
    lines = frontmatter.strip().split("\n")
    new_lines = []
    name_found = False

    for line in lines:
        # Match name field (handles 'name: value' or 'name:value')
        if re.match(r"^\s*name\s*:", line):
            new_lines.append(f"name: {new_name}")
            name_found = True
        else:
            new_lines.append(line)

    if not name_found:
        # Insert name at the beginning of frontmatter
        new_lines.insert(0, f"name: {new_name}")

    new_frontmatter = "\n".join(new_lines)
    new_content = f"---\n{new_frontmatter}\n---{body}"
    skill_md.write_text(new_content)
