"""Shared exception classes for agr."""


class AgrError(Exception):
    """Base exception for agr errors."""

    pass


class RepoNotFoundError(AgrError):
    """Raised when the GitHub repo doesn't exist."""

    pass


class ResourceNotFoundError(AgrError):
    """Raised when the skill/command/agent doesn't exist in the repo."""

    pass


class ResourceExistsError(AgrError):
    """Raised when the resource already exists locally."""

    pass


class BundleNotFoundError(AgrError):
    """Raised when no bundle directory exists in any resource type."""

    pass
