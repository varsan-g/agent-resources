# /agr-feedback

**Submit better feedback with Claude's help.**

Turn vague frustrations into actionable bug reports and feature requests. Claude helps you articulate your feedback, then opens a pre-filled GitHub issue ready to submit.

## Install

```bash
agr add agr-feedback
```

## Usage

```bash
agrx agr-feedback -i "your feedback here"
```

Examples:

```bash
agrx agr-feedback -i "sync command is confusing when there are conflicts"
agrx agr-feedback -i "would be nice to have a dry-run flag"
agrx agr-feedback -i "can't install from private repos"
```

## What You Get

**Before (your initial thought):**
```
sync command is confusing when there are conflicts
```

**After (refined with Claude):**
```markdown
## Type: UX Improvement

## Title: Improve conflict error messages in agr sync

### Description
When `agr sync` detects conflicts, the error message says "conflict detected"
without specifying which file has the conflict or how to resolve it.

### Details
- Current behavior: Generic "conflict detected" message
- Expected: Show which file(s) have conflicts and suggest resolution steps

### Context
- Command: agr sync
```

Then opens GitHub with the issue pre-filled — just click submit.

## How It Works

1. **You provide initial feedback** — a rough idea is fine
2. **Claude asks clarifying questions** — 2-4 focused questions to gather details
3. **Review the formatted feedback** — approve, edit, or cancel
4. **Submit on GitHub** — browser opens with everything pre-filled

## Feedback Types

| Type | When to Use | GitHub Label |
|------|-------------|--------------|
| Bug | Something isn't working | `bug` |
| Feature | New capability or enhancement | `enhancement` |
| UX | Confusing behavior or messaging | `ux` |
| Docs | Documentation missing or unclear | `documentation` |

## Why Use This?

- **Higher quality feedback** — Claude helps you think through the details
- **Structured format** — maintainers can act on it faster
- **No setup required** — browser handles GitHub auth
- **You stay in control** — review before anything is submitted

---

Part of [agent-resources](https://github.com/kasperjunge/agent-resources) — the package manager for Claude Code.
