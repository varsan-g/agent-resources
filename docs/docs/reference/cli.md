---
title: CLI reference
---

# CLI reference

## Global help

```bash
agr --help
```

## agr add

Add resources from GitHub or local paths.

### Syntax

```bash
agr add <username>/<name>
agr add <username>/<repo>/<name>
agr add ./path/to/resource
```

The resource type (skill, command, or agent) is automatically detected.

### Options

- `--type`, `-t`: Explicit resource type (`skill`, `command`, `agent`)
- `--global`, `-g`: Install to `~/.claude/` instead of the current directory
- `--overwrite`: Replace an existing resource

### Examples

```bash
# Auto-detect resource type
agr add kasperjunge/hello-world

# From a custom repository
agr add acme/tools/review --global

# With explicit type (for disambiguation)
agr add kasperjunge/hello --type skill

# Add local path to agr.toml
agr add ./resources/skills/my-skill --type skill

# Add local command
agr add ./resources/commands/deploy.md --type command
```

### Where resources go

Resources install to namespaced paths using a flattened colon format:

```
.claude/
└── skills/
    └── kasperjunge:hello-world/
        └── SKILL.md
```

Commands and agents use nested directories:

```
.claude/
├── commands/
│   └── kasperjunge/
│       └── review.md
└── agents/
    └── kasperjunge/
        └── expert.md
```

### Dependency tracking

When you add a resource, it's automatically recorded in `agr.toml`:

```toml
dependencies = [
    {handle = "kasperjunge/hello-world", type = "skill"},
]
```

### Disambiguation

If the same name exists in multiple resource types, `agr add` will prompt you to use `--type`:

```
Error: Resource 'hello' found in multiple types: skill, command.
Use --type to specify which one to install:
  agr add kasperjunge/hello --type skill
  agr add kasperjunge/hello --type command
```

## agr sync

Synchronize resources from local authoring paths and remote dependencies.

### Syntax

```bash
agr sync
agr sync --prune
agr sync --local
agr sync --remote
agr sync --global
```

### What gets synced

By default, `agr sync` syncs both:

1. **Local authoring resources** — From `resources/skills/`, `resources/commands/`, `resources/agents/`
2. **Remote dependencies** — From `agr.toml`

### Options

- `--global`, `-g`: Sync resources in `~/.claude/` instead of the current directory
- `--prune`: Remove resources that no longer exist in source or `agr.toml`
- `--local`: Only sync local authoring resources
- `--remote`: Only sync remote dependencies from `agr.toml`

### Examples

```bash
# Sync both local and remote resources
agr sync

# Only sync local authoring resources
agr sync --local

# Only sync remote dependencies
agr sync --remote

# Sync and remove deleted resources
agr sync --prune

# Sync global resources
agr sync --global
```

### Local authoring sync

Discovers resources in convention paths and copies them to `.claude/`:

| Source | Destination |
|--------|-------------|
| `resources/skills/<name>/` | `.claude/skills/<username>:<name>/` |
| `resources/commands/<name>.md` | `.claude/commands/<username>/<name>.md` |
| `resources/agents/<name>.md` | `.claude/agents/<username>/<name>.md` |

The username is determined from your git remote. If no remote exists, `local` is used.

### Remote dependency sync

Reads `agr.toml` and installs any missing dependencies:

| Scenario | Action |
|----------|--------|
| Resource in agr.toml, not installed | Installs the resource |
| Resource in agr.toml, already installed | Skips (no action) |
| Resource installed, not in agr.toml | Keeps (unless `--prune`) |

### Output

```
Installed local resource 'my-skill'
Updated local resource 'my-command'
Installed kasperjunge/hello-world (skill)
Sync complete: 2 installed, 1 updated, 0 pruned
```

!!! note
    Pruning only affects resources in namespaced paths (e.g., `.claude/skills/username:skill/`). Resources installed with older versions of agr in flat paths are preserved.

## agr remove

Remove resources from the local installation with auto-detection.

### Syntax

```bash
agr remove <name>
agr remove <username>/<name>
```

Auto-detects the resource type from installed files.

### Options

- `--type`, `-t`: Explicit resource type (`skill`, `command`, `agent`)
- `--global`, `-g`: Remove from `~/.claude/` instead of the current directory

### Examples

```bash
# Auto-detect resource type
agr remove hello-world

# Remove by full reference
agr remove kasperjunge/hello-world

# With explicit type (for disambiguation)
agr remove hello --type skill

# Remove from global installation
agr remove hello-world --global
```

### Dependency tracking

When you remove a resource, it's automatically removed from `agr.toml`.

### Disambiguation

If the same name exists in multiple resource types, `agr remove` will prompt you to use `--type`:

```
Error: Resource 'hello' found in multiple types: skill, command.
Use --type to specify which one to remove:
  agr remove hello --type skill
  agr remove hello --type command
```

!!! warning
    Resources are removed immediately without confirmation.

## agrx

Run skills and commands temporarily without permanent installation.

### Syntax

```bash
agrx <username>/<name>
agrx <username>/<name> "<prompt>"
agrx <username>/<repo>/<name>
```

The resource type (skill or command) is automatically detected. The resource is downloaded, executed, and cleaned up afterwards.

### Options

- `--type`, `-t`: Explicit resource type (`skill` or `command`)
- `--interactive`, `-i`: Start an interactive Claude session
- `--global`, `-g`: Install temporarily to `~/.claude/` instead of `./.claude/`

### Examples

```bash
# Auto-detect and run
agrx kasperjunge/hello-world

# Run with a prompt
agrx kasperjunge/hello-world "analyze this code"

# Interactive mode
agrx kasperjunge/hello-world -i

# With explicit type
agrx kasperjunge/hello --type skill

# From a custom repository
agrx acme/tools/review
```

### Disambiguation

If the same name exists as both a skill and a command, `agrx` will prompt you to use `--type`:

```
Error: Resource 'hello' found in multiple types: skill, command.
Use --type to specify which one to run:
  agrx kasperjunge/hello --type skill
  agrx kasperjunge/hello --type command
```

## agr init

Create scaffolds for resources or set up authoring structure.

### Initialize authoring structure

```bash
agr init
```

Creates `agr.toml` and the convention directories for local resource authoring:

```
./
├── agr.toml
└── resources/
    ├── skills/
    ├── commands/
    ├── agents/
    └── packages/
```

### Create a skill

```bash
agr init skill my-skill
```

Creates `resources/skills/my-skill/SKILL.md` by default.

Options:

- `--path`, `-p`: Custom output path
- `--legacy`: Create in `.claude/skills/` instead of `resources/skills/`

### Create a command

```bash
agr init command my-command
```

Creates `resources/commands/my-command.md` by default.

Options:

- `--path`, `-p`: Custom output path
- `--legacy`: Create in `.claude/commands/` instead of `resources/commands/`

### Create an agent

```bash
agr init agent my-agent
```

Creates `resources/agents/my-agent.md` by default.

Options:

- `--path`, `-p`: Custom output path
- `--legacy`: Create in `.claude/agents/` instead of `resources/agents/`

### Create a package

```bash
agr init package my-toolkit
```

Creates `resources/packages/my-toolkit/` with `skills/`, `commands/`, and `agents/` subdirectories.

Options:

- `--path`, `-p`: Custom output path

## Deprecated syntax

The old subcommand syntax is deprecated but still works:

```bash
# Deprecated (shows warning)
agr add skill <username>/<name>
agr add command <username>/<name>
agr add agent <username>/<name>

agr remove skill <name>
agr remove command <name>
agr remove agent <name>

agrx skill <username>/<name>
agrx command <username>/<name>

# Use instead
agr add <username>/<name>
agr remove <name>
agrx <username>/<name>
```
