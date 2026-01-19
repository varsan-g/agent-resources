---
title: Creating a shareable repo
---

# Creating a shareable repo

Create a repository that others can install resources from using `agr add`.

## Initialize your project

```bash
mkdir agent-resources
cd agent-resources
git init
agr init
```

This creates the standard authoring structure:

```
./
├── agr.toml
└── resources/
    ├── skills/
    ├── commands/
    ├── agents/
    └── packages/
```

## Create your resources

Add skills, commands, and agents:

```bash
agr init skill code-reviewer
agr init command deploy
agr init agent test-writer
```

Edit the generated files to add your content.

## Sync to .claude/

Before publishing, sync your resources:

```bash
agr sync
```

This copies resources to `.claude/` where they can be discovered by consumers.

## Push to GitHub

```bash
git add .
git commit -m "Initial resources"
gh repo create agent-resources --public --source=. --push
```

Or create the repo on GitHub first and push manually.

## Recommended repo name

If your repository is named `agent-resources`, users can install with the short form:

```bash
agr add username/my-skill
```

If the repo has a different name, users must include it:

```bash
agr add username/custom-repo/my-skill
```

## Share with others

Once published, share your resources:

```bash
# Others can install your resources
agr add your-username/code-reviewer
agr add your-username/deploy
```

## Next steps

- Edit resources in `resources/` and run `agr sync` to update
- Push changes to GitHub to share updates
- See [Local resource authoring](local-authoring.md) for the full workflow
