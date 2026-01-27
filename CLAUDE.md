# Agent Resources

A package manager for AI agents. 

## Commands
...

## Architecture
...

## agr.toml Format

The configuration file uses a flat array of dependencies:

```toml
dependencies = [
    {handle = "username/repo/skill", type = "skill"},
    {handle = "username/skill", type = "skill"},
    {path = "./local/skill", type = "skill"},
]
```

Each dependency has:
- `type`: Always "skill" for now
- `handle`: Remote GitHub reference (username/repo/skill or username/skill)
- `path`: Local path (alternative to handle)

Future: A `tools` section will configure which tools to sync to:
```toml
tools = ["claude", "cursor"]
```

## Code Style
...

## Boundaries

### Always Do
- agr and agrx should always be unified and synced.
- include in the plan to write tests for what is implemented
- Save all skills in `skills/` directory (not `.claude/skills/` which is gitignored)

### Ask First
...

### Never Do
...

## Security
...

# Docs

General
https://agentskills.io/
https://agents.md/

Claude Code:
https://code.claude.com/docs/en/skills
https://code.claude.com/docs/en/slash-commands
https://code.claude.com/docs/en/sub-agents
https://code.claude.com/docs/en/memory

Cursor:
https://cursor.com/docs/context/skills
https://cursor.com/docs/context/commands
https://cursor.com/docs/context/subagents
https://cursor.com/docs/context/rules

GitHub Copilot:
https://docs.github.com/en/copilot/concepts/agents/about-agent-skills

Codex:
https://developers.openai.com/codex/skills
https://developers.openai.com/codex/custom-prompts/

Open Code:
https://opencode.ai/docs/skills
https://opencode.ai/docs/commands/
https://opencode.ai/docs/agents/