---
title: References and paths
---

# References and paths

Resources are referenced by GitHub owner and name.

## Reference formats

Short form (default repo name `agent-resources`):

```
<username>/<resource-name>
```

Full form (custom repo name):

```
<username>/<repo>/<resource-name>
```

Examples:

```bash
agr add kasperjunge/hello-world
agr add acme/tools/review
```

## Nested resources with colons

A resource name may include `:` to represent nested folders in the source repository:

```bash
agr add username/backend:hello-world
```

This maps to a resource at `resources/skills/backend/hello-world/` (or `.claude/skills/backend/hello-world/`) in the source repository.

## How references become paths

When you install a resource, the reference determines where it goes:

| Reference | Resource Type | Installed path |
|-----------|--------------|----------------|
| `kasperjunge/hello-world` | skill | `.claude/skills/kasperjunge:hello-world/` |
| `acme/tools/review` | command | `.claude/commands/acme/review.md` |
| `kasperjunge/expert` | agent | `.claude/agents/kasperjunge/expert.md` |

Skills use a flattened colon format (`username:skill-name`) because Claude Code only discovers top-level directories. Commands and agents use nested username directories.

## Using references with commands

All agr commands accept references in the same format:

```bash
# Add
agr add kasperjunge/hello-world

# Remove (can use just the name or full reference)
agr remove hello-world
agr remove kasperjunge/hello-world

# Run temporarily
agrx kasperjunge/hello-world
```
