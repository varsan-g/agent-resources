---
title: Installing resources
---

# Installing resources

Install skills, commands, and agents directly from GitHub.

## Install from the default repo name

If a user has a repo named `agent-resources`, you only need the username:

```bash
agr add username/my-resource
```

The resource type (skill, command, agent, or bundle) is auto-detected.

## Install from a custom repo name

If the repo name is not `agent-resources`, include it:

```bash
agr add username/custom-repo/my-resource
```

## Install nested resources

You can organize resources into nested folders and reference them with `:`.
For example, this installs from:

```bash
agr add username/backend:hello-world
```

```
./
└── .claude/
    └── skills/
        └── backend/
            └── hello-world/
```

The same pattern works for commands and agents.

## Install globally

Global installs go to `~/.claude/` instead of the current project:

```bash
agr add username/my-resource --global
```

## Overwrite an existing resource

```bash
agr add username/my-resource --overwrite
```

## Disambiguate resource types

If the same name exists in multiple types (e.g., both a skill and a command named `hello`), use the `--type` flag:

```bash
agr add username/hello --type skill
agr add username/hello --type command
```

Valid types: `skill`, `command`, `agent`, `bundle`

## Verify the install

Check that files exist in `.claude/` or `~/.claude/`, then run your command or let your
agent use the skill automatically.
