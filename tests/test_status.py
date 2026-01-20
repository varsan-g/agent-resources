"""Tests for status models and computation."""

from pathlib import Path

import pytest

from agr.config import AgrConfig, Dependency
from agr.status import (
    SyncStatus,
    ToolResourceStatus,
    ResourceStatus,
    UntrackedResource,
    StatusReport,
)


class TestSyncStatus:
    """Tests for SyncStatus enum."""

    def test_status_values(self):
        """Test that all status values are defined."""
        assert SyncStatus.SYNCED.value == "synced"
        assert SyncStatus.OUTDATED.value == "outdated"
        assert SyncStatus.MISSING.value == "missing"
        assert SyncStatus.UNTRACKED.value == "untracked"


class TestToolResourceStatus:
    """Tests for ToolResourceStatus dataclass."""

    def test_create_synced_status(self, tmp_path: Path):
        """Test creating a synced status."""
        status = ToolResourceStatus(
            tool_name="Claude",
            status=SyncStatus.SYNCED,
            path=tmp_path / "skills" / "test",
        )

        assert status.tool_name == "Claude"
        assert status.status == SyncStatus.SYNCED
        assert status.path is not None

    def test_create_missing_status_with_message(self):
        """Test creating a missing status with message."""
        status = ToolResourceStatus(
            tool_name="Cursor",
            status=SyncStatus.MISSING,
            message="Source path not found",
        )

        assert status.status == SyncStatus.MISSING
        assert status.message == "Source path not found"


class TestResourceStatus:
    """Tests for ResourceStatus dataclass."""

    def test_is_synced_all_true(self):
        """Test is_synced_all when all tools are synced."""
        resource = ResourceStatus(
            identifier="kasperjunge/commit",
            resource_type="skill",
            is_local=False,
            tool_statuses=[
                ToolResourceStatus(tool_name="Claude", status=SyncStatus.SYNCED),
                ToolResourceStatus(tool_name="Cursor", status=SyncStatus.SYNCED),
            ],
        )

        assert resource.is_synced_all is True
        assert resource.has_issues is False

    def test_is_synced_all_false(self):
        """Test is_synced_all when some tools are missing."""
        resource = ResourceStatus(
            identifier="kasperjunge/commit",
            resource_type="skill",
            is_local=False,
            tool_statuses=[
                ToolResourceStatus(tool_name="Claude", status=SyncStatus.SYNCED),
                ToolResourceStatus(tool_name="Cursor", status=SyncStatus.MISSING),
            ],
        )

        assert resource.is_synced_all is False
        assert resource.has_issues is True

    def test_has_issues_outdated(self):
        """Test has_issues detects outdated status."""
        resource = ResourceStatus(
            identifier="./commands/docs.md",
            resource_type="command",
            is_local=True,
            tool_statuses=[
                ToolResourceStatus(tool_name="Claude", status=SyncStatus.OUTDATED),
            ],
        )

        assert resource.has_issues is True


class TestUntrackedResource:
    """Tests for UntrackedResource dataclass."""

    def test_create_untracked(self, tmp_path: Path):
        """Test creating an untracked resource."""
        untracked = UntrackedResource(
            tool_name="Claude",
            name="old-skill",
            resource_type="skill",
            path=tmp_path / "skills" / "old-skill",
        )

        assert untracked.tool_name == "Claude"
        assert untracked.name == "old-skill"


class TestStatusReport:
    """Tests for StatusReport dataclass."""

    def test_all_synced_true(self):
        """Test all_synced when everything is synced."""
        report = StatusReport(
            target_tools=["Claude", "Cursor"],
            resources=[
                ResourceStatus(
                    identifier="test/skill",
                    resource_type="skill",
                    is_local=False,
                    tool_statuses=[
                        ToolResourceStatus(tool_name="Claude", status=SyncStatus.SYNCED),
                        ToolResourceStatus(tool_name="Cursor", status=SyncStatus.SYNCED),
                    ],
                ),
            ],
            untracked=[],
        )

        assert report.all_synced is True
        assert report.has_drift is False

    def test_has_drift_with_missing(self):
        """Test has_drift with missing resources."""
        report = StatusReport(
            target_tools=["Claude"],
            resources=[
                ResourceStatus(
                    identifier="test/skill",
                    resource_type="skill",
                    is_local=False,
                    tool_statuses=[
                        ToolResourceStatus(tool_name="Claude", status=SyncStatus.MISSING),
                    ],
                ),
            ],
        )

        assert report.has_drift is True
        assert report.missing_count == 1

    def test_has_drift_with_untracked(self, tmp_path: Path):
        """Test has_drift with untracked resources."""
        report = StatusReport(
            target_tools=["Claude"],
            resources=[],
            untracked=[
                UntrackedResource(
                    tool_name="Claude",
                    name="orphan",
                    resource_type="skill",
                    path=tmp_path / "skills" / "orphan",
                ),
            ],
        )

        assert report.has_drift is True
        assert report.all_synced is False

    def test_synced_count(self):
        """Test synced_count calculation."""
        report = StatusReport(
            target_tools=["Claude", "Cursor"],
            resources=[
                ResourceStatus(
                    identifier="skill1",
                    resource_type="skill",
                    is_local=False,
                    tool_statuses=[
                        ToolResourceStatus(tool_name="Claude", status=SyncStatus.SYNCED),
                        ToolResourceStatus(tool_name="Cursor", status=SyncStatus.SYNCED),
                    ],
                ),
                ResourceStatus(
                    identifier="skill2",
                    resource_type="skill",
                    is_local=False,
                    tool_statuses=[
                        ToolResourceStatus(tool_name="Claude", status=SyncStatus.SYNCED),
                        ToolResourceStatus(tool_name="Cursor", status=SyncStatus.MISSING),
                    ],
                ),
            ],
        )

        assert report.synced_count == 3
        assert report.missing_count == 1

    def test_empty_report(self):
        """Test empty status report."""
        report = StatusReport(target_tools=["Claude"])

        assert report.all_synced is True
        assert report.has_drift is False
        assert report.synced_count == 0
        assert report.missing_count == 0
