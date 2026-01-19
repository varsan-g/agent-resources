---
title: Install locations
---

# Install locations

agr installs resources into either the current project or your global Claude directory, organized by username.

## Namespaced paths

Resources install to namespaced paths that include the GitHub username:

```
.claude/
├── skills/
│   └── kasperjunge:hello-world/
│       └── SKILL.md
├── commands/
│   └── kasperjunge/
│       └── review.md
└── agents/
    └── kasperjunge/
        └── expert.md
```

Skills use a flattened colon format (`username:skill-name`) because Claude Code only discovers top-level directories in `.claude/skills/`. Commands and agents use nested directories.

This organization:

- **Prevents naming conflicts** — Multiple authors can have resources with the same name
- **Shows ownership** — You can see at a glance who created each resource
- **Supports sync** — Makes it easy to track and prune resources
- **Ensures discoverability** — Skills are at top-level where Claude Code finds them

## Project-local installs

Default behavior installs into the current working directory:

```bash
agr add kasperjunge/hello-world
```

This creates:

```
./
└── .claude/
    └── skills/
        └── kasperjunge:hello-world/
            └── SKILL.md
```

## Global installs

Use `--global` (or `-g`) to install into your home directory:

```bash
agr add kasperjunge/hello-world --global
```

This writes to:

```
~/
└── .claude/
    └── skills/
        └── kasperjunge:hello-world/
            └── SKILL.md
```

Global resources are available in all your projects.

## Overwrites

If a resource already exists, you must pass `--overwrite` to replace it:

```bash
agr add kasperjunge/hello-world --overwrite
```

## Backward compatibility

Resources installed with older versions of agr used flat paths without the username:

```
.claude/
└── skills/
    └── hello-world/    # Old flat path (still works)
```

agr continues to recognize these resources:

- `agr remove hello-world` finds resources in both flat and namespaced paths
- `agr sync --prune` only removes namespaced resources, preserving legacy installs

New installations always use the flattened colon format for skills (`username:skill-name`) and nested paths for commands/agents.
