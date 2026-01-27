---
name: release
description: Use when ready to publish a new version. Triggers on "release", "publish", "ship it", or version bump requests. Runs quality checks, bumps version, tags, and creates GitHub release.
---

# Release

Release workflow for publishing a new version to PyPI via GitHub Actions.

## When to Use

- After feature work is complete and committed
- When asked to release, publish, or ship a new version
- When bumping to a new version number

## Prerequisites

Before releasing:
- All work committed (clean working tree)
- On `main` branch
- `/code-review` passed
- `/commit` completed (CHANGELOG updated)

## Workflow

```
┌─────────────────────────┐
│ 1. Verify clean state   │
│    git status           │
└───────────┬─────────────┘
            │
            ▼
      ┌───────────┐
      │ Clean?    │───No──→ STOP. Commit or stash first.
      └─────┬─────┘
            │Yes
            ▼
┌─────────────────────────┐
│ 2. Run quality checks   │
│    ty → ruff → pytest   │
└───────────┬─────────────┘
            │
            ▼
      ┌───────────┐
      │ All pass? │───No──→ STOP. Fix issues first.
      └─────┬─────┘
            │Yes
            ▼
┌─────────────────────────┐
│ 3. Bump version         │
│    agr/__init__.py      │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 4. Update CHANGELOG     │
│    [Unreleased] → [X.Y.Z]
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 5. Commit version bump  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 6. Tag + Push           │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 7. Create GitHub release│
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 8. Verify release       │
└─────────────────────────┘
```

## Step 1: Verify Clean State

```bash
git status
git branch --show-current
```

**Requirements:**
- Working tree must be clean (no uncommitted changes)
- Must be on `main` branch

If not clean: Run `/commit` first or stash changes.

## Step 2: Run Quality Checks

```bash
ty                    # Type checking
ruff check .          # Linting
ruff format --check . # Format check
pytest                # Tests
```

**All must pass.** No exceptions - releases with failing tests are forbidden.

## Step 3: Bump Version

Edit `agr/__init__.py`:

```python
__version__ = "X.Y.Z"  # New version
```

**Version format:** Follow [SemVer](https://semver.org/)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

## Step 4: Update CHANGELOG

In `CHANGELOG.md`, convert the Unreleased section to a versioned release:

**Before:**
```markdown
## [Unreleased]

### Added
- New feature
```

**After:**
```markdown
## [Unreleased]

## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature
```

Keep an empty `[Unreleased]` section at the top for future changes.

## Step 5: Commit Version Bump

```bash
git add agr/__init__.py CHANGELOG.md
git commit -m "$(cat <<'EOF'
Release vX.Y.Z

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## Step 6: Tag and Push

```bash
git tag vX.Y.Z
git push origin main
git push origin vX.Y.Z
```

**Order matters:** Push commit first, then tag. This ensures the commit exists on remote before the tag references it.

## Step 7: Create GitHub Release

Create a GitHub Release at `https://github.com/<owner>/<repo>/releases`.

This is where release notes live - they're published to GitHub Releases, visible to users browsing the repo. Extract content from CHANGELOG and transform into user-friendly release notes.

### Writing Good Release Notes

**Structure:**
```markdown
## What's New in vX.Y.Z

[1-2 sentence summary of the most important change]

### Highlights
- **Feature Name**: Brief user-facing description (not implementation details)

### Added
- New capability or feature (from CHANGELOG)

### Changed
- Modified behavior (from CHANGELOG)

### Fixed
- Bug fix (from CHANGELOG)

### Breaking Changes
- Any breaking changes with migration instructions
```

**Guidelines:**
- Lead with impact, not implementation
- Write for users, not developers
- Include migration steps for breaking changes
- Link to docs/issues where helpful

**Example:**
```markdown
## What's New in v0.7.0

Windows users can now install and manage skills without path issues.

### Highlights
- **Windows Support**: Skill directories now use `--` separator instead of `:` for full Windows compatibility

### Changed
- Installed skill directories use `username--skill` format instead of `username:skill`
- Existing installations are automatically migrated on `agr sync`

### Added
- Development workflow skills: `/research`, `/discover-solution-space`, `/make-plan`, `/code-review`, `/commit`
```

### Create the Release

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z" \
  --notes "$(cat <<'EOF'
## What's New in vX.Y.Z

[Summary]

### Highlights
- **Key Feature**: Description

### Added
- ...

### Changed
- ...

### Fixed
- ...
EOF
)"
```

**Source of truth:** Release notes come from CHANGELOG. Don't write them fresh - transform CHANGELOG entries into user-friendly language.

## Step 8: Verify Release

```bash
gh release view vX.Y.Z        # Verify release exists
git ls-remote --tags origin   # Verify tag pushed
gh run list --limit 3         # Check GitHub Actions status
```

### Verify GitHub Actions Pipeline

The tag push triggers `.github/workflows/publish.yml` which:
1. **Quality checks**: Runs ruff + pytest
2. **Build**: Creates wheel and sdist with hatch
3. **Publish**: Uploads to PyPI via trusted publishing (OIDC)

```bash
# Watch the workflow run
gh run watch

# Or check status
gh run list --workflow=publish.yml --limit 1
```

### Verify PyPI Publication

```bash
# Check package is available (may take a few minutes)
pip index versions agr

# Or visit https://pypi.org/project/agr/
```

## Red Flags - STOP

- Uncommitted changes → Commit first
- Tests failing → Fix before release
- Not on main branch → Switch to main
- CHANGELOG not updated → Update it
- Skipping quality checks → Never skip

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Releasing with dirty working tree | Commit or stash first |
| Skipping tests "we tested earlier" | Run tests immediately before release |
| Writing release notes from scratch | Extract from CHANGELOG |
| Forgetting to push the tag | Push tag separately after commit |
| Not verifying GitHub Actions | Check that PyPI publish triggered |

## No Exceptions

- "We already tested it" → Run tests again now
- "It's just a patch" → Full quality checks required
- "Nobody reads release notes" → CHANGELOG is documentation. Use it.
- "We're in a hurry" → Rushed releases cause incidents
