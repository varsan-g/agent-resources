# Skills Ecosystem Analysis: Jobs To Be Done & Market Opportunities

*Analysis Date: 2026-01-26*

## Executive Summary

After analyzing 60+ skills across 5 major repositories, I've identified **10 core jobs to be done** that people are solving with skills today, and **12 categories of unmet needs** that represent significant market opportunities.

---

## Part 1: What Skills Exist Today — Taxonomy

### Category Distribution

| Category | Count | % | Examples |
|----------|-------|---|----------|
| Domain Expertise | 15 | 25% | go, drupal-expert, sql, python-development |
| Document Generation | 5 | 8% | pdf, docx, xlsx, pptx |
| Frontend/Creative | 8 | 13% | frontend-design, algorithmic-art, canvas-design |
| Development Workflows | 12 | 20% | code-review, worktrees, decisions, brainstorm |
| Tool Integration | 6 | 10% | mcp-builder, datastar, observable-plot |
| Business/Sales | 5 | 8% | lead-research, competitive-ads, brand-guidelines |
| Self-Improvement | 3 | 5% | meeting-insights, developer-growth, journal |
| Scaffolding/Generation | 4 | 7% | go-scaffold, module-scaffold, skill-creator |
| Collaboration/Social | 2 | 3% | bluesky, collaboration |

---

## Part 2: The 10 Core Jobs To Be Done

These are the fundamental human needs that skills are solving:

### 1. "Make me an expert instantly"
*Skills: go, drupal-expert, sql, gomponents, datastar*

**The job**: People need domain expertise they don't have time to acquire. A Drupal migration could take months to learn; a skill compresses that into immediate availability.

**Key insight**: Skills act as **compressed expertise packages**. The best ones don't just give instructions—they encode years of hard-won conventions, gotchas, and best practices.

**Pattern**: These skills are structured as "knowledge dumps" with decision trees for common scenarios.

---

### 2. "Eliminate tedious format work"
*Skills: pdf, docx, xlsx, pptx*

**The job**: Format conversion and document creation is pure friction. People don't want to fight with Word's layout engine or Excel's formulas.

**Key insight**: Document skills are among the most universally needed. Every knowledge worker creates documents. These skills have **massive horizontal appeal**.

**Pattern**: Imperative + declarative. "Create a proposal" (high-level intent) that handles all formatting details.

---

### 3. "Help me think through problems systematically"
*Skills: brainstorm, research-issue, decisions*

**The job**: People need structured thinking support. Brainstorming alone is hard. Weighing tradeoffs is cognitively taxing.

**Key insight**: These skills transform the AI from a tool into a **thinking partner**. The `brainstorm` skill's genius is forcing single questions to prevent overwhelm. The `decisions` skill creates institutional memory.

**Pattern**: Socratic method—questions before answers. Structured output formats that force completeness.

---

### 4. "Catch mistakes I'd miss"
*Skills: code-review, drupal-security, go-reviewer*

**The job**: Quality assurance without human cost or social friction. Getting code reviewed by humans is slow and can be awkward.

**Key insight**: The `code-review` skill uses **competing agents** to find issues—gamifying QA. Security skills that auto-activate on risky patterns (like the drupal-security skill) are particularly powerful.

**Pattern**: Proactive triggering. Multi-perspective analysis. Specific, actionable feedback with examples.

---

### 5. "Remember what I did and why"
*Skills: journal, decisions*

**The job**: AI-assisted work happens fast. Context gets lost. Why did we choose SQLite? What did we learn last week?

**Key insight**: This is **meta-cognition for AI work**. The journal skill creates a persistent SQLite database of learnings. The decisions skill creates a permanent ADR (Architecture Decision Record) file.

**Pattern**: Append-only logs. Full-text search. Triggered on significant events.

---

### 6. "Work faster in parallel"
*Skills: worktrees*

**The job**: Maximize throughput by enabling multiple agents to work simultaneously without conflicts.

**Key insight**: This is infrastructure for **multi-agent orchestration**. As agents become more capable, coordination becomes the bottleneck. Worktrees solve git conflicts elegantly.

**Pattern**: Isolation mechanisms. Clear handoff protocols. Cleanup procedures.

---

### 7. "Create things I couldn't before"
*Skills: frontend-design, algorithmic-art, canvas-design, nanobanana*

**The job**: Democratize creative work. Non-designers want beautiful UIs. Non-artists want generative art.

**Key insight**: The `frontend-design` skill explicitly fights "AI slop" with bold aesthetic direction. It's not about automation—it's about **capability expansion**.

**Pattern**: Strong opinions. Detailed aesthetic guidance. Anti-patterns explicitly listed.

---

### 8. "Understand my own patterns"
*Skills: meeting-insights-analyzer, developer-growth-analysis*

**The job**: Self-awareness through AI analysis. People want feedback on their communication, coding patterns, and growth areas.

**Key insight**: These skills turn **personal data into insights**. The meeting analyzer finds conflict avoidance patterns. The growth analyzer reads your Claude Code history and identifies skill gaps.

**Pattern**: Data ingestion → Pattern recognition → Actionable feedback → Resource curation.

---

### 9. "Find opportunities I'd miss"
*Skills: lead-research-assistant, competitive-ads-extractor*

**The job**: Business intelligence. Finding leads. Understanding competitor strategies.

**Key insight**: These are **proactive intelligence skills**. They don't wait for questions—they surface opportunities and patterns from external data.

**Pattern**: Define criteria → Search broadly → Score/prioritize → Deliver actionable output.

---

### 10. "Build tools for my tools"
*Skills: mcp-builder, skill-creator*

**The job**: Extensibility. People want to customize their AI assistant with new capabilities.

**Key insight**: This is the **meta-layer**. Skills that build skills. Tools that build tools. These have compounding value as the ecosystem grows.

**Pattern**: Best practices documentation. Templates. Quality checklists. Evaluation frameworks.

---

## Part 3: The Unmet Needs — Where To Build Next

These are jobs people have but likely don't know skills can solve. This is where market opportunity lies.

### Tier 1: High Impact, Clear Demand

#### A. Communication Crafting
*Gap*: No skills for drafting difficult emails, negotiation prep, performance review writing, or stakeholder communication.

**Opportunity skills**:
- `difficult-conversation` — Prepare scripts for hard talks with evidence-based communication frameworks
- `stakeholder-update` — Transform technical work into executive-friendly summaries
- `negotiation-prep` — Research counterparty, generate BATNA analysis, prepare talking points

**Why it matters**: Communication is 40%+ of knowledge work. Every professional needs this daily.

---

#### B. Legacy System Archaeology
*Gap*: No skills for understanding undocumented codebases, reverse-engineering intent, or creating documentation from existing code.

**Opportunity skills**:
- `codebase-archaeologist` — Understand large legacy systems, map dependencies, identify patterns
- `doc-from-code` — Generate documentation by analyzing existing implementation
- `dependency-explainer` — Explain why each dependency exists and what would break without it

**Why it matters**: Most code is legacy code. Understanding it is often harder than writing new code.

---

#### C. Error Investigation
*Gap*: No skills for systematically investigating production errors, interpreting stack traces, or connecting symptoms to root causes.

**Opportunity skills**:
- `error-detective` — Given an error log/stack trace, investigate root cause systematically
- `incident-postmortem` — Generate blameless postmortems from incident data
- `log-interpreter` — Find patterns in application logs that indicate problems

**Why it matters**: Debugging is ~50% of development time. Better tools here have massive leverage.

---

### Tier 2: High Impact, Emerging Demand

#### D. Technical Estimation
*Gap*: No skills for estimating effort, breaking down vague requirements into concrete tasks, or quantifying technical debt.

**Opportunity skills**:
- `estimate-this` — Break down requirements into tasks with effort estimates and confidence intervals
- `tech-debt-quantifier` — Analyze codebase and produce prioritized debt inventory with cost estimates
- `scope-analyzer` — Given a feature request, identify hidden complexity and edge cases

**Why it matters**: Bad estimates derail projects. AI can analyze codebases to give better-grounded estimates.

---

#### E. Compliance & Legal
*Gap*: No skills for license compatibility checking, privacy compliance (GDPR), accessibility audits, or security standard alignment.

**Opportunity skills**:
- `license-checker` — Analyze dependencies for license conflicts
- `privacy-auditor` — Find potential GDPR/CCPA issues in code
- `a11y-reviewer` — Audit frontend code for accessibility violations
- `security-standards` — Check alignment with SOC2, HIPAA, etc.

**Why it matters**: Compliance failures are expensive. Proactive checking prevents costly remediation.

---

#### F. Team Knowledge Management
*Gap*: No skills for onboarding documentation generation, knowledge transfer, or "why did we do this" institutional memory.

**Opportunity skills**:
- `onboarding-generator` — Create onboarding guides from codebase analysis
- `tribal-knowledge-capture` — Interview developers and create searchable documentation
- `context-handoff` — Generate handoff docs when someone leaves a project

**Why it matters**: Knowledge loss is one of the biggest costs in software teams.

---

### Tier 3: Emerging Patterns, Future Demand

#### G. Multi-Agent Coordination
*Gap*: Beyond worktrees, there are no skills for coordinating multiple agents on complex tasks, resolving conflicts, or merging parallel work.

**Opportunity skills**:
- `agent-coordinator` — Break down large tasks and assign to parallel agents
- `merge-resolver` — Intelligently merge conflicting changes from multiple agents
- `work-partitioner` — Analyze a task and determine optimal parallelization strategy

**Why it matters**: As agents get more capable, coordination becomes the bottleneck.

---

#### H. Financial/Business Analysis
*Gap*: No skills for technical cost estimation, feature ROI analysis, or build-vs-buy decisions.

**Opportunity skills**:
- `cost-estimator` — Estimate infrastructure costs for a proposed architecture
- `feature-roi` — Analyze potential value vs. effort for feature prioritization
- `build-vs-buy` — Comprehensive analysis of building internally vs. using third-party

**Why it matters**: Engineering increasingly needs to justify decisions in business terms.

---

#### I. Learning & Growth
*Gap*: Beyond developer-growth, no skills for creating personalized learning paths, generating tutorials from code, or testing understanding.

**Opportunity skills**:
- `learning-path` — Analyze skill gaps and create personalized study plans
- `tutorial-generator` — Create step-by-step tutorials from working code
- `concept-checker` — Quiz on technical concepts to identify knowledge gaps

**Why it matters**: Continuous learning is required but poorly supported by tools.

---

#### J. Meeting & Calendar Intelligence
*Gap*: Beyond meeting-insights, no skills for meeting preparation, agenda generation, or action item tracking.

**Opportunity skills**:
- `meeting-prep` — Research attendees, summarize relevant context, generate questions
- `agenda-builder` — Create structured agendas based on goals and attendees
- `action-tracker` — Extract and track commitments from meeting notes

**Why it matters**: Meetings consume huge time. Better prep = better outcomes.

---

#### K. API & Integration Design
*Gap*: No skills for designing APIs, versioning strategies, or integration patterns between systems.

**Opportunity skills**:
- `api-designer` — Design RESTful/GraphQL APIs with best practices
- `version-strategist` — Plan API versioning and migration paths
- `integration-architect` — Design patterns for connecting multiple systems

**Why it matters**: Integration is where most complexity lives in modern systems.

---

#### L. Personal Productivity
*Gap*: No skills for task prioritization, context switching optimization, or workload management.

**Opportunity skills**:
- `priority-matrix` — Analyze tasks and generate Eisenhower matrix
- `context-bundler` — Group related tasks to minimize context switching
- `workload-analyzer` — Identify overcommitment and suggest rebalancing

**Why it matters**: Personal productivity gains compound massively over time.

---

## Part 4: Strategic Recommendations

### Insight 1: Skills That Self-Activate Are More Valuable

The drupal-security skill auto-activates when you're writing risky code. The decisions skill suggests recording significant architectural choices. **Proactive skills > reactive skills**.

**Recommendation**: Build skills with trigger conditions, not just manual invocation.

---

### Insight 2: The Meta-Layer Has Compounding Returns

`skill-creator` and `mcp-builder` enable more skills. The journal enables better memory. **Infrastructure skills multiply everything else**.

**Recommendation**: Invest in meta-skills that improve the skill ecosystem itself.

---

### Insight 3: Structured Output Enables Downstream Automation

The `research-issue` skill produces a specific markdown format. The `decisions` skill appends to a standard file. **Predictable output enables chaining**.

**Recommendation**: Define clear output schemas so skills can compose.

---

### Insight 4: Anti-Patterns Are As Valuable As Patterns

The `frontend-design` skill explicitly lists what NOT to do (generic fonts, purple gradients). **Constraints enable creativity**.

**Recommendation**: Include "never do this" sections in skills.

---

### Insight 5: Personal Data Analysis Is Underexploited

`meeting-insights` and `developer-growth` analyze YOUR data to give YOU feedback. This is a **deeply personal value proposition** that's hard to replicate.

**Recommendation**: Build skills that analyze personal/local data (git history, browser history, calendar, email) for insights.

---

## Part 5: The 5 Skills To Build First

Based on impact × feasibility × market gap:

| Priority | Skill | JTBD | Why Now |
|----------|-------|------|---------|
| 1 | `error-detective` | Catch mistakes | Every developer debugs daily |
| 2 | `stakeholder-update` | Communication | Universal need, clear format |
| 3 | `codebase-archaeologist` | Expert instantly | Legacy code is everywhere |
| 4 | `estimate-this` | Think systematically | Chronic pain point |
| 5 | `license-checker` | Compliance | Legal risk is expensive |

---

## Conclusion

The skills ecosystem reveals that people want AI to:

1. **Compress expertise** (make me expert instantly)
2. **Eliminate friction** (tedious format work)
3. **Augment cognition** (think through problems)
4. **Ensure quality** (catch mistakes)
5. **Preserve knowledge** (remember decisions)
6. **Enable parallelism** (work faster)
7. **Expand capability** (create what I couldn't)
8. **Generate self-insight** (understand my patterns)
9. **Surface opportunities** (find what I'd miss)
10. **Build more tools** (meta-layer extensibility)

The biggest gaps are in **communication**, **legacy system understanding**, **error investigation**, **technical estimation**, and **compliance checking**. These represent the next wave of high-value skills.

---

## Appendix: Data Sources

Skills analyzed from:
- `skill-repos/skills-maragudk/` (19 skills)
- `skill-repos/skills-anthropics/` (16 skills)
- `skill-repos/agent-resources-madsnorgaard/` (5 skills + agents)
- `skill-repos/agent-resources-dsjacobsen/` (8 agents + 10 commands)
- `skill-repos/Ai-Agent-Skills/` (40+ skills)
