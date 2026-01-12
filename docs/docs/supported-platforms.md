# Supported Tools

!!! warning "Coming Soon"
    This functionality is not yet implemented. See the [repository README](https://github.com/kasperjunge/agent-resources) for currently supported features.

Agent Resources can install packages to multiple AI coding tools. It automatically detects which tools you're using.

---

## Automatic Tool Detection

When you run `agr add`, the tool automatically detects your environment by checking:

1. **Existing directories** — looks for `.claude/`, `.cursor/`, `.codex/`, `.github/`, `.opencode/`
2. **Config files** — checks for `CLAUDE.md`, `AGENTS.md`, `.cursorrules`
3. **Running processes** — detects if you're running inside Claude Code, Cursor, etc.

If multiple tools are detected, resources install to all of them. If none are detected, it defaults to Claude Code.

---

## Install Behavior

By default, packages install to all detected tools:

```bash
agr add anthropics/code-reviewer
```

```
Detected tools: Claude Code (primary), Cursor

Installing to:
  Claude Code: .claude/skills/code-reviewer/
  Cursor: .cursor/skills/code-reviewer/

Done
```

---

## Install for Specific Tool

Install to a single tool only:

```bash
agr add anthropics/code-reviewer --tool=claude
agr add anthropics/code-reviewer --tool=cursor
agr add anthropics/code-reviewer --tool=codex
agr add anthropics/code-reviewer --tool=copilot
agr add anthropics/code-reviewer --tool=opencode
```

Install to multiple tools:

```bash
agr add anthropics/code-reviewer --tool=claude,cursor
```

Install to all detected tools:

```bash
agr add anthropics/code-reviewer --tool=all
```

---

## Supported Tools

| Tool | Flag | Directory |
|------|------|-----------|
| Claude Code | `--tool=claude` | `.claude/` |
| Cursor | `--tool=cursor` | `.cursor/` |
| OpenAI Codex | `--tool=codex` | `.codex/` |
| GitHub Copilot | `--tool=copilot` | `.github/` |
| OpenCode | `--tool=opencode` | `.opencode/` |
