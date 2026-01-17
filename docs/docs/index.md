---
title: Introduction
---

# Introduction

Agent Resources (agr) is a CLI for installing and creating Claude Code resources from GitHub.
It lets you pull skills, slash commands, and subagents into your local `.claude/` folder with a
single command.

## Highlights

- Install a skill, command, or sub-agent from GitHub in seconds
- Share skills, slash commands, and subagents with a simple handle like `username/skillname`
- Create a personal library of skills, subagents, and slash commands you can install anywhere with one command
- Skip the configuration overhead of Anthropics plugin marketplaces

## Quick start

No install required:

```bash
uvx agr add kasperjunge/hello-world
```

Install permanently:

```bash
pip install agr
agr add kasperjunge/hello-world
```

The resource type (skill, command, agent, or bundle) is auto-detected.

## What agr installs

agr installs files into one of these locations:

```
./
└── .claude/
    ├── skills/
    ├── commands/
    └── agents/
```

Or globally:

```
~/
└── .claude/
    ├── skills/
    ├── commands/
    └── agents/
```

## How it works

Resources are fetched from GitHub repositories that follow a simple layout:

```
agent-resources/
└── .claude/
    ├── skills/
    ├── commands/
    └── agents/
```

By default, `agr add` looks in a repository named `agent-resources` on the user's GitHub account.
If a repo has a different name, include it in the reference.

## Next steps

- Start with [Installation](getting-started/installation.md)
- Learn common workflows in [Installing resources](guides/installing-resources.md)
- Understand the model in [Resource types](concepts/resource-types.md)
- Browse full CLI details in [CLI reference](reference/cli.md)
