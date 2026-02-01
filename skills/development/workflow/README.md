# Development Workflow Skills

A repeatable workflow for building high-quality changes without rushing decisions or shipping surprises. Each step is a skill you can invoke, so the process is easy to try on a real task end-to-end.

---

## The Workflow

### 1. `/research` — Understand before acting
**Purpose:** Gather facts about the problem and how the codebase relates to it.
**Key principle:** Pure observation, no opinions. You're a neutral reporter.
**Use when:** Starting new work, encountering bugs, or needing to understand existing implementation.
**Output:** Objective findings—files involved, current behavior, patterns observed.

### 2. `/brainstorm-solutions` — Diverge before converging
**Purpose:** Generate 3-5 distinct approaches before evaluating any of them.
**Key principle:** Breadth first. Avoid anchoring on the first idea.
**Use when:** Research is complete and you're ready to explore how to solve the problem.
**Output:** Multiple options across different dimensions (architecture, strategy, tools).

### 3. `/design-solution` — Decide deliberately
**Purpose:** Evaluate trade-offs and converge on a single recommended approach.
**Key principle:** Pick the best fit—not the most novel or the most familiar.
**Use when:** You have multiple options and need to choose one.
**Output:** Pros/cons analysis, effort estimate, codebase fit, and a clear recommendation.

### 4. `/create-plan` — Go deep, then plan
**Purpose:** Create a comprehensive implementation plan with explicit behavior specs.
**Key principle:** Simple over easy. Never cut corners.
**Use when:** Solution is chosen and you're ready to define exactly what to build.
**Output:** Desired/undesired behavior, edge cases, test design, implementation steps.

### 5. `/code-review` — Challenge the work
**Purpose:** Rigorous review for quality, maintainability, and architectural soundness.
**Key principle:** Devil's advocate. Is there a simpler or more correct approach?
**Use when:** After implementing, before committing, or when explicitly asked.
**Output:** Findings by severity (critical/important/minor) with specific recommendations.

### 6. `/commit-work` — Gate the commit
**Purpose:** Ensure quality checks pass and changelog is updated before committing.
**Key principle:** No exceptions. Failing tests = no commit.
**Use when:** Code review passes and work is ready to save.
**Output:** Clean commit with meaningful message and updated CHANGELOG.

### 7. `/make-release` — Ship with confidence
**Purpose:** Publish a new version through the full release pipeline.
**Key principle:** Verify everything. Rushed releases cause incidents.
**Use when:** Feature work is complete, committed, and ready to publish.
**Output:** Version bump, tagged release, PyPI publication, GitHub release.

---

## Why It Works

- **Separate understanding from deciding, and deciding from planning.** Each phase has a clear purpose.
- **Explore multiple options before locking in.** Avoid the trap of the first idea.
- **Commit with quality gates.** Automated checks catch what humans miss.
- **Release only when verifiable.** No shortcuts, no "we can fix it later."

## Quick Start

Pick any task and run `/research <task>`. The skill will guide you to the next step.
