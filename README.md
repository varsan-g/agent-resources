<div align="center">

# 🧩 agent-resources

**Share and install Claude Code skills, commands, and agents with a single command.**

*A package and project manager for AI agents.*

[![PyPI](https://img.shields.io/pypi/v/agr?color=blue)](https://pypi.org/project/agr/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Try It](#try-it-now) • [Install](#install-any-resource) • [Create Your Own](#create-your-own) • [Community](#community-resources)

</div>

---

## Try It Now

No installation needed. Just run:

```bash
uvx agr add kasperjunge/hello-world
```

**That's it.** The skill is now available in Claude Code. The resource type (skill, command, agent, or bundle) is auto-detected.

Or install permanently:

```bash
pip install agr
agr add kasperjunge/hello-world
```

---

## Install Any Resource

```bash
agr add <username>/<name>                # Auto-detects resource type
agr add <username>/<name> --type skill   # Explicit type (if needed)
```

The resource type (skill, command, agent, or bundle) is auto-detected. Use `--type` to disambiguate if the same name exists in multiple types.

### Default Repository Convention

If you name your repo `agent-resources`, users only need to specify your username and resource name:

```bash
# Installs from github.com/kasperjunge/agent-resources
agr add kasperjunge/hello-world
```

### Install From Any Repository

You can install from any GitHub repository that has the `.claude/` structure. Just use the three-part format:

```bash
# Installs from github.com/username/custom-repo
agr add username/custom-repo/my-skill
```

### Install a Bundle

Install multiple resources at once with bundles:

```bash
agr add kasperjunge/anthropic
```

This installs all skills, commands, and agents from the bundle in one command.

---

## Run Without Installing (agrx)

Try a skill or command without permanent installation:

```bash
agrx kasperjunge/hello-world              # Auto-detects and runs
agrx kasperjunge/hello-world "my prompt"  # Run with a prompt
agrx kasperjunge/hello-world -i           # Interactive mode
```

The resource is downloaded, executed, and cleaned up automatically.

---

## Create Your Own Library

Create your personal agent-resources library:

```bash
agr init repo --github
```

**Done.** You now have a GitHub repo that anyone can install from.

> Requires [GitHub CLI](https://cli.github.com/). Run without `--github` to set up manually.

### What You Get

- A ready-to-use `agent-resources` repo on your GitHub
- Example skill, command, and agent to learn from
- Instant shareability:

```bash
agr add <your-username>/hello-world
```

### Add Your Own Resources

Edit the files in your repo:

```
your-username/agent-resources/
└── .claude/
    ├── skills/          # Skill folders with SKILL.md
    ├── commands/        # Slash command .md files
    └── agents/          # Sub-agent .md files
```

Push to GitHub.

---

## Community Resources

### Go Development Toolkit — [@dsjacobsen](https://github.com/dsjacobsen/agent-resources)

A comprehensive Claude Code toolkit for Go developers.

```bash
agr add dsjacobsen/golang-pro      # Expert Go knowledge
agr add dsjacobsen/go-reviewer     # Code review agent
agr add dsjacobsen/go-check        # Quick code check
```

**Includes**: 1 skill, 9 agents, 11 commands covering scaffolding, testing, API building, refactoring, and more.

### Drupal Development Toolkit — [@madsnorgaard](https://github.com/madsnorgaard/agent-resources)

A comprehensive Claude Code toolkit for Drupal developers.

```bash
agr add madsnorgaard/drupal-expert      # Drupal 10/11 modules, themes, hooks
agr add madsnorgaard/drupal-migration   # D7-to-D10 migrations, CSV imports
agr add madsnorgaard/ddev-expert        # DDEV local development, Xdebug
agr add madsnorgaard/drupal-reviewer    # Code review agent
agr add madsnorgaard/drush-check        # Run health checks
```

**Includes**: 4 skills, 1 agent, 5 commands covering Drupal development, migrations, DDEV, Docker, security audits, and more.

---

**Built something useful?** [Open an issue](https://github.com/kasperjunge/agent-resources-project/issues) with a link to your `agent-resources` repo and we'll add it here.

---

## Legacy Commands

The following syntax is deprecated but still supported for backwards compatibility:

```bash
# Old subcommand syntax (deprecated)
agr add skill <username>/<name>
agr add command <username>/<name>
agr add agent <username>/<name>
agr add bundle <username>/<name>

agr remove skill <name>
agr remove command <name>
agr remove agent <name>

agrx skill <username>/<name>
agrx command <username>/<name>
```

Use the unified syntax instead:

```bash
agr add <username>/<name>
agr remove <name>
agrx <username>/<name>
```

Even older standalone commands are also deprecated:

```bash
uvx add-skill <username>/<skill-name>
uvx add-command <username>/<command-name>
uvx add-agent <username>/<agent-name>
uvx create-agent-resources-repo
```

---

<div align="center">

**MIT License** · Made for the [Claude Code](https://claude.ai/code) community

</div>
