"""Tests for compatibility warnings at add-time."""

from pathlib import Path

import pytest

from agr.adapters.converter import (
    check_compatibility,
    check_compatibility_for_path,
    CompatibilityReport,
)


class TestCheckCompatibility:
    """Tests for check_compatibility function."""

    def test_no_frontmatter_no_issues(self):
        """Test that content without frontmatter has no issues."""
        content = "# My Skill\n\nSome description."
        report = check_compatibility(content, "skill", ["claude", "cursor"])

        assert report.has_issues is False
        assert len(report.issues) == 0

    def test_no_issues_for_common_fields(self):
        """Test that common fields have no issues."""
        content = '''---
name: my-skill
description: A skill
---
# My Skill
'''
        report = check_compatibility(content, "skill", ["claude", "cursor"])

        assert report.has_issues is False

    def test_claude_specific_field_warning(self):
        """Test that Claude-specific fields generate warnings for Cursor."""
        content = '''---
name: my-skill
allowed-tools: Bash, Read
---
# My Skill
'''
        report = check_compatibility(content, "skill", ["claude", "cursor"])

        assert report.has_issues is True
        assert len(report.issues) == 1
        assert report.issues[0].field_name == "allowed-tools"
        assert "claude" in report.issues[0].message.lower()
        assert "cursor" in report.issues[0].affected_tools

    def test_multiple_claude_specific_fields(self):
        """Test multiple Claude-specific fields."""
        content = '''---
name: my-skill
allowed-tools: Bash
model: sonnet
context: true
---
# My Skill
'''
        report = check_compatibility(content, "skill", ["claude", "cursor"])

        assert report.has_issues is True
        # allowed-tools, model, and context are Claude-specific
        field_names = {issue.field_name for issue in report.issues}
        assert "allowed-tools" in field_names
        # model might be mapped, not dropped
        assert "context" in field_names

    def test_single_tool_no_issues(self):
        """Test that single tool target has no compatibility issues."""
        content = '''---
name: my-skill
allowed-tools: Bash
---
# My Skill
'''
        # Only targeting Claude, no compatibility issues
        report = check_compatibility(content, "skill", ["claude"])

        # When only targeting one tool, there shouldn't be cross-tool issues
        # (fields that are specific to the targeted tool are fine)
        assert report.has_issues is False

    def test_cursor_specific_rule_fields(self):
        """Test Cursor-specific rule fields generate warnings for Claude."""
        content = '''---
description: My rule description
alwaysApply: true
---
# My Rule
'''
        report = check_compatibility(content, "rule", ["claude", "cursor"])

        # These are Cursor-specific fields
        field_names = {issue.field_name for issue in report.issues}
        # description and alwaysApply are cursor-specific for rules
        assert "description" in field_names or "alwaysApply" in field_names


class TestCheckCompatibilityForPath:
    """Tests for check_compatibility_for_path function."""

    def test_skill_directory(self, tmp_path: Path):
        """Test compatibility check for a skill directory."""
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text('''---
name: my-skill
allowed-tools: Bash
---
# My Skill
''')

        report = check_compatibility_for_path(
            skill_dir, "skill", ["claude", "cursor"]
        )

        assert report.has_issues is True
        assert any(i.field_name == "allowed-tools" for i in report.issues)

    def test_command_file(self, tmp_path: Path):
        """Test compatibility check for a command file."""
        cmd_file = tmp_path / "deploy.md"
        cmd_file.write_text('''---
name: deploy
---
# Deploy Command
''')

        report = check_compatibility_for_path(
            cmd_file, "command", ["claude", "cursor"]
        )

        # Common fields, no issues
        assert report.has_issues is False

    def test_nonexistent_path(self, tmp_path: Path):
        """Test compatibility check for nonexistent path."""
        nonexistent = tmp_path / "nonexistent"

        report = check_compatibility_for_path(
            nonexistent, "skill", ["claude", "cursor"]
        )

        # Should return empty report
        assert report.has_issues is False

    def test_empty_directory(self, tmp_path: Path):
        """Test compatibility check for directory without SKILL.md."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        report = check_compatibility_for_path(
            empty_dir, "skill", ["claude", "cursor"]
        )

        # Should return empty report
        assert report.has_issues is False


class TestCompatibilityReport:
    """Tests for CompatibilityReport dataclass."""

    def test_has_issues_false_when_empty(self):
        """Test has_issues is False for empty report."""
        report = CompatibilityReport(resource_type="skill")
        assert report.has_issues is False

    def test_has_issues_true_with_issues(self):
        """Test has_issues is True when issues exist."""
        from agr.adapters.converter import CompatibilityIssue

        report = CompatibilityReport(
            resource_type="skill",
            issues=[
                CompatibilityIssue(
                    field_name="test",
                    message="Test message",
                    affected_tools=["cursor"],
                )
            ],
        )
        assert report.has_issues is True
