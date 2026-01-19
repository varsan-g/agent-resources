---
title: Local resource authoring
---

# Local resource authoring

Author resources in convention paths and sync them to `.claude/` for use with Claude Code.

## Overview

Local authoring separates your source files from the installed `.claude/` directory:

```
./
├── resources/           # Your source files (edit here)
│   ├── skills/
│   ├── commands/
│   ├── agents/
│   └── packages/
│
└── .claude/             # Installed files (synced automatically)
    ├── skills/
    │   └── your-username:my-skill/
    ├── commands/
    │   └── your-username/
    └── agents/
        └── your-username/
```

Benefits:

- **Clean separation** — Source files stay organized outside `.claude/`
- **Automatic namespacing** — Resources are organized by your GitHub username
- **Incremental updates** — Only changed files are synced
- **Package support** — Group related resources together

## Getting started

### Set up the directory structure

```bash
agr init
```

Creates `agr.toml` and the standard authoring directories:

```
./
├── agr.toml
└── resources/
    ├── skills/
    ├── commands/
    ├── agents/
    └── packages/
```

### Create a resource

```bash
agr init skill my-skill
```

Creates `resources/skills/my-skill/SKILL.md` with a starter template.

### Sync to .claude/

```bash
agr sync
```

Copies resources to `.claude/` where Claude Code can use them. Skills are installed with flattened colon names (e.g., `.claude/skills/username:my-skill/`).

## Convention paths

agr discovers resources in these locations:

| Path | Resource type |
|------|---------------|
| `resources/skills/<name>/SKILL.md` | Skill |
| `resources/commands/<name>.md` | Command |
| `resources/agents/<name>.md` | Agent |
| `resources/packages/<pkg>/skills/<name>/SKILL.md` | Packaged skill |
| `resources/packages/<pkg>/commands/<name>.md` | Packaged command |
| `resources/packages/<pkg>/agents/<name>.md` | Packaged agent |

## Creating resources

### Skills

```bash
agr init skill code-reviewer
```

Creates:

```
resources/
└── skills/
    └── code-reviewer/
        └── SKILL.md
```

### Commands

```bash
agr init command deploy
```

Creates:

```
resources/
└── commands/
    └── deploy.md
```

### Agents

```bash
agr init agent test-writer
```

Creates:

```
resources/
└── agents/
    └── test-writer.md
```

### Packages

Packages group related resources under a single namespace:

```bash
agr init package my-toolkit
```

Creates:

```
resources/
└── packages/
    └── my-toolkit/
        ├── skills/
        ├── commands/
        └── agents/
```

Then add resources to the package:

```bash
agr init skill helper --path resources/packages/my-toolkit/skills/helper
agr init command build --path resources/packages/my-toolkit/commands
```

## Syncing resources

### Basic sync

```bash
agr sync
```

Discovers all resources in convention paths and copies them to `.claude/`. Only files that have changed since the last sync are updated.

### Local-only sync

```bash
agr sync --local
```

Only syncs local authoring resources, skipping remote dependencies from `agr.toml`.

### Pruning deleted resources

```bash
agr sync --prune
```

Removes resources from `.claude/` that no longer exist in your authoring paths.

## Username namespacing

Resources are installed to `.claude/` with username namespacing to prevent naming conflicts.

### How the username is determined

agr extracts the username from your git remote:

```bash
# If your remote is:
git@github.com:kasperjunge/agent-resources.git

# Skills install with flattened colon format:
.claude/skills/kasperjunge:my-skill/

# Commands and agents use nested directories:
.claude/commands/kasperjunge/my-command.md
.claude/agents/kasperjunge/my-agent.md
```

### If no git remote exists

If agr can't determine a username, it uses `local` as the namespace:

```
.claude/skills/local:my-skill/
```

Configure a git remote to get proper namespacing:

```bash
git remote add origin git@github.com:your-username/your-repo.git
```

## Workflow example

### Starting a new project

```bash
# Initialize authoring structure
agr init

# Create some resources
agr init skill code-reviewer
agr init command lint-check

# Edit the files
$EDITOR resources/skills/code-reviewer/SKILL.md
$EDITOR resources/commands/lint-check.md

# Sync to .claude/
agr sync
```

### Making changes

```bash
# Edit your resource
$EDITOR resources/skills/code-reviewer/SKILL.md

# Sync changes
agr sync
# Output: Updated local resource 'code-reviewer'
```

### Cleaning up

```bash
# Delete a resource
rm -rf resources/skills/old-skill/

# Remove from .claude/
agr sync --prune
# Output: Pruned local resource 'old-skill'
```

## Using with remote dependencies

Local authoring works alongside remote dependencies from `agr.toml`:

```bash
# Add a remote dependency
agr add kasperjunge/hello-world

# Sync both local and remote resources
agr sync
```

To sync only one type:

```bash
agr sync --local   # Only local authoring resources
agr sync --remote  # Only remote dependencies from agr.toml
```

## Legacy mode

If you prefer the old behavior of creating resources directly in `.claude/`:

```bash
agr init skill my-skill --legacy
```

Creates `.claude/skills/my-skill/SKILL.md` instead of `resources/skills/my-skill/SKILL.md`.

!!! note
    Legacy resources aren't managed by `agr sync` and must be edited in place.

## agr.toml resource definitions

For publishing, you can define custom resource paths in `agr.toml`:

```toml
dependencies = [
    {path = "resources/skills/my-skill", type = "skill"},
    {path = "resources/packages/my-toolkit", type = "package"},
]
```

This allows consumers to install resources by name even if they're in non-standard locations.
