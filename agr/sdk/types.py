"""Type definitions for the SDK."""

from dataclasses import dataclass


@dataclass
class SkillInfo:
    """Metadata about a skill without downloading it."""

    name: str
    handle: str
    description: str | None
    repo: str
    owner: str
