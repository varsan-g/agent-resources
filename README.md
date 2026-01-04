# agent-resources

CLI tools to install Claude Code resources (skills, commands, and sub-agents) from GitHub.

## Installation

### Option 1: Install all commands (pip)

```bash
pip install agent-resources
```

This gives you all three commands:
- `skill-add` - Install skills
- `command-add` - Install slash commands
- `agent-add` - Install sub-agents

### Option 2: One-off usage (uvx)

```bash
# Either naming convention works:
uvx skill-add <username>/<skill-name>
uvx add-skill <username>/<skill-name>

uvx command-add <username>/<command-name>
uvx add-command <username>/<command-name>

uvx agent-add <username>/<agent-name>
uvx add-agent <username>/<agent-name>
```

## Usage

```bash
# Install a skill
skill-add kasperjunge/analyze-paper

# Install a slash command
command-add kasperjunge/commit

# Install a sub-agent
agent-add kasperjunge/code-reviewer

# Install globally (to ~/.claude/)
skill-add kasperjunge/analyze-paper --global

# Overwrite existing
skill-add kasperjunge/analyze-paper --overwrite
```

## Creating Your Own Resources

Create a GitHub repository named `agent-resources` with the following structure:

```
agent-resources/
├── .claude/
│   ├── skills/
│   │   └── my-skill/
│   │       └── skill.md
│   ├── commands/
│   │   └── my-command.md
│   └── agents/
│       └── my-agent.md
```

Others can then install your resources:

```bash
skill-add yourusername/my-skill
command-add yourusername/my-command
agent-add yourusername/my-agent
```

## License

MIT
