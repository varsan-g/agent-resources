---
name: agent-feedback
description: Report undesired agent behavior from the current chat session as a GitHub issue. Use when the user invokes /agent-feedback to report mistakes, missed codebase patterns, bad solutions, or other undesired behavior.
argument-hint: "[description of undesired vs desired behavior]"
disable-model-invocation: true
allowed-tools: Bash(gh *)
---

# Agent Feedback

Create a GitHub issue documenting undesired agent behavior from the current chat session.

## Workflow

1. **Get feedback description**
   - If `$ARGUMENTS` provided: use as the feedback description
   - If empty: ask user to describe undesired behavior and what they expected

2. **Analyze current chat session** to extract:
   - User's job to be done
   - What the agent did (undesired behavior)
   - What was expected (desired behavior)
   - Files involved with paths
   - Patterns the agent missed
   - Context for prevention

3. **Create issue**:

```bash
gh issue create \
  --repo DineroRegnskab/dinero-web-2.0 \
  --label "agent-feedback" \
  --title "[Agent Feedback] <brief description>" \
  --body "$(cat <<'EOF'
## Summary

<1-2 sentence summary>

## Job to Be Done

<What user was trying to accomplish>

## Undesired Behavior

<What the agent did wrong>

## Desired Behavior

<What was expected>

## Files Involved

- `path/to/file.ts`

## Context for Prevention

<Patterns/conventions to add to skills or CLAUDE.md>

## Chat Session Summary

<Brief summary of conversation>
EOF
)"
```

## Example

`/agent-feedback "Agent used useState instead of our useAppState hook"`

Creates issue titled: `[Agent Feedback] Used useState instead of useAppState hook`
