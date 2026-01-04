# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

This is a Python monorepo containing CLI tools for installing Claude Code resources (skills, commands, and sub-agents) from GitHub repositories.

## Repository Structure

```
packages/
├── agent-resources/     # Core library with shared fetching logic, exposes all three CLIs
├── skill-add/           # Thin wrapper for `uvx skill-add`
├── command-add/         # Thin wrapper for `uvx command-add`
├── agent-add/           # Thin wrapper for `uvx agent-add`
├── add-skill/           # Thin wrapper for `uvx add-skill` (alternative naming)
├── add-command/         # Thin wrapper for `uvx add-command` (alternative naming)
└── add-agent/           # Thin wrapper for `uvx add-agent` (alternative naming)
```

**Primary usage pattern** is via uvx for one-off execution:
```bash
# Either naming convention works:
uvx skill-add <username>/<skill-name>
uvx add-skill <username>/<skill-name>

uvx command-add <username>/<command-name>
uvx add-command <username>/<command-name>

uvx agent-add <username>/<agent-name>
uvx add-agent <username>/<agent-name>
```

The individual packages exist to enable this clean uvx UX. They are thin wrappers that depend on `agent-resources`, which contains the shared core logic.


## Architecture

**Core Components** (in `packages/agent-resources/src/agent_resources/`):
- `fetcher.py` - Generic resource fetcher that downloads from GitHub tarballs and extracts resources
- `cli/common.py` - Shared CLI utilities (argument parsing, destination resolution)
- `cli/skill.py`, `cli/command.py`, `cli/agent.py` - Typer CLI apps for each resource type
- `exceptions.py` - Custom exception hierarchy

**Resource Types**:
- Skills: Directories copied to `.claude/skills/<name>/`
- Commands: Single `.md` files copied to `.claude/commands/<name>.md`
- Agents: Single `.md` files copied to `.claude/agents/<name>.md`

**Fetching Pattern**: Resources are fetched from `https://github.com/<username>/agent-resources/` repositories by downloading the main branch tarball and extracting the specific resource.

## Dependencies

- `httpx` - HTTP client for downloading from GitHub
- `typer` - CLI framework
