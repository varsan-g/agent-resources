---
title: Resource types
---

# Resource types

agr manages three resource types for Claude Code.

## Skills

A skill is a directory with a `SKILL.md` file that defines behavior and instructions.

```
./
└── .claude/
    └── skills/
        └── username:code-reviewer/
            └── SKILL.md
```

Skills use a flattened colon format (`username:skill-name`) because Claude Code only discovers top-level directories.

## Commands

A command is a markdown file that defines what happens when a user runs a slash command.

```
./
└── .claude/
    └── commands/
        └── username/
            └── review.md
```

## Agents

An agent is a markdown file that defines a sub-agent that your main agent can delegate to.

```
./
└── .claude/
    └── agents/
        └── username/
            └── test-writer.md
```
