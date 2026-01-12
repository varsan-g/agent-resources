# Install Agent Resources

!!! warning "Coming Soon"
    This functionality is not yet implemented. See the [repository README](https://github.com/kasperjunge/agent-resources) for currently supported features.

There are several ways to install resources depending on what you need.

---

## Install All From packages/

If your project has a `packages/` directory with installed packages, you can install all of them:

```bash
agr add
```

This works like `npm install` — it reads from the packages directory and ensures all resources are installed.

---

## Install a Package

Packages bundle skills, commands, and subagents together:

```bash
agr add username/packagename
```

---

## Install Individual Resources

You can also install skills, commands, and subagents individually:

```bash
# Install a skill
agr add skill username/skillname

# Install a command
agr add command username/commandname

# Install a subagent
agr add agent username/agentname
```

---

## Using uvx

All commands work with `uvx` if you don't want to install `agr` globally:

```bash
uvx agr add username/packagename
```

---

## Installation Options

Install to a specific tool:

```bash
agr add username/packagename --tool=cursor
```

Install to multiple tools:

```bash
agr add username/packagename --tool=claude,cursor
```

Install globally (available in all projects):

```bash
agr add username/packagename --global
```

Overwrite an existing resource:

```bash
agr add username/packagename --overwrite
```
