#!/usr/bin/env bash
set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not inside a git repository." >&2
  exit 1
fi

branch=$(git branch --show-current)

echo "Current branch: $branch"

if [[ "$branch" == "main" ]]; then
  echo
  echo "=== Staged changes (stat) ==="
  git diff --stat --staged
  echo
  echo "=== Staged files ==="
  git diff --name-only --staged
else
  echo
  echo "=== Changes vs main (stat) ==="
  git diff --stat main...HEAD
  echo
  echo "=== Changed files vs main ==="
  git diff --name-only main...HEAD
  echo
  echo "=== Uncommitted changes (stat) ==="
  git diff --stat
  echo
  echo "=== Uncommitted files ==="
  git diff --name-only
fi
