---
title: First steps
---

# First steps

This page gets you from zero to a working resource.

## Install a resource

```bash
agr add kasperjunge/hello-world
```

The resource type (skill, command, agent, or bundle) is auto-detected. This installs the resource into the appropriate directory:

```
./
└── .claude/
    ├── skills/
    │   └── hello-world/       # if it's a skill
    ├── commands/
    │   └── hello-world.md     # if it's a command
    └── agents/
        └── hello-world.md     # if it's an agent
```

## Use your resource

Once installed, your agent can use the new skill automatically and you can run slash commands
inside Claude Code. No additional configuration is required.

## Common options

```bash
# Install globally instead of in the current repo
agr add kasperjunge/hello-world --global

# Overwrite an existing resource
agr add kasperjunge/hello-world --overwrite

# Specify type explicitly (if a name exists in multiple types)
agr add kasperjunge/hello-world --type skill
```

## Run without installing (agrx)

Try a resource without permanent installation:

```bash
agrx kasperjunge/hello-world              # Auto-detects and runs
agrx kasperjunge/hello-world "my prompt"  # Run with a prompt
```

The resource is downloaded, executed, and cleaned up automatically.

## Remove a resource

```bash
agr remove hello-world
```

Auto-detects the resource type. Use `--type` to disambiguate if needed.

## Next steps

- Learn more in [Installing resources](../guides/installing-resources.md)
- Understand layouts in [Repository structure](../concepts/repository-structure.md)
