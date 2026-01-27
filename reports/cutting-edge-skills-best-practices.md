# Cutting-Edge Best Practices for Building AI Agent Skills

*Research compiled: 2026-01-26*

---

## Executive Summary

The field of AI agent skills has undergone a fundamental paradigm shift. **Prompt engineering is giving way to context engineering**—a systems-level discipline focused on information flow, state management, and context curation. This document synthesizes state-of-the-art thinking from across the industry to provide a comprehensive guide for building world-class skills.

---

## Part 1: The Paradigm Shift — From Prompts to Context Engineering

### The New Mental Model

> "The primary skill for developers will not be to coax a model into working with clever phrasing and prompt engineering. Instead, they will need to focus on **context engineering**, the discipline that focuses on designing the information flow, managing the state, and curating the context that the model 'sees.' It is a move from linguistic trickery to systems engineering."
> — [Machine Learning Mastery](https://machinelearningmastery.com/7-agentic-ai-trends-to-watch-in-2026/)

Andrej Karpathy's framing: **LLMs are like a new kind of operating system**. The LLM is the CPU, and the context window is RAM. Just as an OS curates what fits into RAM, context engineering curates what the model sees at any moment.

### What This Means for Skills

Skills are no longer just "prompt templates." They are **context management systems** that:
- Control what information enters the model's working memory
- Structure how that information is organized and prioritized
- Define when to load and unload context dynamically
- Manage state across interactions

**Sources:**
- [Context Engineering for AI Agents: Lessons from Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
- [Memory for AI Agents: A New Paradigm - The New Stack](https://thenewstack.io/memory-for-ai-agents-a-new-paradigm-of-context-engineering/)
- [Context Engineering - LangChain Blog](https://www.blog.langchain.com/context-engineering-for-agents/)

---

## Part 2: Progressive Disclosure — The Core Architecture

### The Three-Level System

Agent Skills use **progressive disclosure** as their core design principle:

| Level | What Loads | Token Cost | When |
|-------|------------|------------|------|
| **Discovery** | Metadata only (name + description) | ~50 tokens | Always |
| **Activation** | Full SKILL.md body | 2,000-5,000 tokens | When relevant |
| **Execution** | Scripts, references, assets | Unlimited | As needed |

> "Progressive disclosure allows us to build much more sophisticated agents without having to worry about context window bloat. Skills can include entire API documentation, large datasets, entire libraries of references."
> — [Claude Agent Skills Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)

### Why This Matters

Traditional approaches stuff everything into the system prompt. This creates:
- **Cost explosion**: Tool definitions alone can consume ~55k tokens
- **Accuracy degradation**: More options = worse selection performance

Progressive disclosure achieves **85% token reduction** while maintaining capability.

### Skill File Structure

```
skill-name/
├── SKILL.md          # Required - metadata + instructions
├── scripts/          # Optional - executable code
├── references/       # Optional - documentation, specs
└── assets/           # Optional - templates, fonts, images
```

**Best Practice**: When SKILL.md becomes unwieldy, split content into reference files. Keep mutually exclusive contexts separate to minimize token usage.

**Sources:**
- [Anthropic Engineering: Equipping Agents with Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Agent Skills Standard Overview](https://agentskills.io/home)
- [Progressive Disclosure Might Replace MCP - MCPJam](https://www.mcpjam.com/blog/claude-agent-skills)

---

## Part 3: Memory & State Management

### The Memory Hierarchy

Research identifies three types of long-term memory that enable agent improvement:

| Type | Purpose | Example |
|------|---------|---------|
| **Episodic** | Past interactions and experiences | "Last time we tried X, it failed because Y" |
| **Semantic** | Factual knowledge and beliefs | User preferences, project context |
| **Procedural** | How to perform tasks | Learned workflows, optimized patterns |

### State-Based vs. Retrieval-Based Memory

> "Retrieval-based memory treats past interactions as loosely related documents, making it brittle to phrasing, prone to missing overrides, and unable to reconcile conflicts. **State-based memory** encodes user knowledge as structured, authoritative fields with clear precedence, supports belief updates instead of fact accumulation, and enables deterministic decision-making."
> — [OpenAI Agents SDK Cookbook](https://cookbook.openai.com/examples/agents_sdk/context_personalization)

**Key insight**: State-based memory makes agents behave like **persistent concierges** rather than search engines.

### The Manus Approach: File System as Context

Manus treats the filesystem as unlimited, persistent memory:

1. **Offload old tool results to files** (not just summarization)
2. **Use todo.md for attention management** — pushes global plan into recent attention span
3. **Implement recoverable compression** — drop content if URL/path is preserved

> "When Manus handles complex tasks, it tends to create a todo.md file—and update it step-by-step as the task progresses. That's not just cute behavior—it's a deliberate mechanism to manipulate attention."

### Practical Memory Strategies

| Strategy | When to Use | Trade-off |
|----------|-------------|-----------|
| **Context trimming** | Short tasks, recent info critical | Loses long-range context |
| **Context summarization** | Long tasks, need history | Loses detail |
| **File offloading** | Complex multi-step work | Requires filesystem access |
| **Hybrid** | Production systems | Most complex to implement |

**Sources:**
- [Memory in the Age of AI Agents - arXiv](https://arxiv.org/abs/2512.13564)
- [Why Multi-Agent Systems Need Memory Engineering - MongoDB](https://www.mongodb.com/company/blog/technical/why-multi-agent-systems-need-memory-engineering)
- [Context Engineering for Manus](https://rlancemartin.github.io/2025/10/15/manus/)

---

## Part 4: Tool Design Principles

### The Token Problem

> "Loading definitions for 50+ tools into the system prompt creates two problems: cost (58 tools can consume ~55k tokens) and **accuracy degradation** (as options increase, selection ability decreases)."
> — [Composio Tool Calling Guide](https://composio.dev/blog/ai-agent-tool-calling-guide)

### Modern Tool Architecture (2026)

Production systems now use **dynamic tool discovery**:

```
Step 0: Tool Discovery (query registry based on intent)
Step 1: Tool Selection (from dynamically loaded subset)
Step 2: Parameter Extraction
Step 3: Execution
Step 4: Result Processing
Step 5: Response Generation
```

This achieves **85% token reduction** compared to static loading.

### Tool Definition Best Practices

**Naming & Documentation:**
- Clear, descriptive names reflecting function
- Consistent prefixes (e.g., `github_create_issue`, `github_list_repos`)
- Concise but complete descriptions
- Include examples in parameter descriptions

**Schema Design:**
- Use Zod (TypeScript) or Pydantic (Python) for validation
- Include constraints and clear descriptions
- Define output schemas for structured data
- Add examples in field descriptions

**Annotations (MCP Standard):**
```json
{
  "readOnlyHint": true,
  "destructiveHint": false,
  "idempotentHint": true,
  "openWorldHint": false
}
```

### The "Fewer Tools" Pattern

> "Many popular general purpose agents use a surprisingly small number of tools. **Claude Code uses around a dozen tools. Manus uses fewer than 20.**"
> — [Agent Design Patterns](https://rlancemartin.github.io/2026/01/09/agent_design/)

**Why this works**: Composable primitives are more powerful than specialized tools. Basic utilities (glob, grep, read, write) can be composed to solve most problems.

**Sources:**
- [Tool Calling Explained - Composio](https://composio.dev/blog/ai-agent-tool-calling-guide)
- [MCP Best Practices](https://modelcontextprotocol.info/docs/best-practices/)
- [Optimizing Tool Calling - Paragon](https://www.useparagon.com/learn/rag-best-practices-optimizing-tool-calling/)

---

## Part 5: Prompt Engineering for Claude 4.x

### The Fundamental Shift

> "When Claude Sonnet 4.5 launched in September 2025, it broke a lot of existing prompts. Anthropic had rebuilt how Claude follows instructions. Earlier versions would infer your intent and expand on vague requests. **Claude 4.x takes you literally and does exactly what you ask for, nothing more.**"
> — [DreamHost Claude Testing](https://www.dreamhost.com/blog/claude-prompt-engineering/)

### Model-Specific Considerations

**Claude Opus 4.5:**
- More responsive to system prompts — may overtrigger on aggressive language
- Replace "CRITICAL: You MUST..." with "Use this tool when..."
- Sensitive to the word "think" — use "consider," "believe," "evaluate" instead
- Tends to overengineer — explicitly constrain scope

**Claude Sonnet 4.5:**
- Aggressive parallel tool execution
- May "correct" instructions it perceives as errors
- More concise, may skip verbose summaries
- Best for daily coding tasks

### Best Practices for Skills

1. **Be explicit**: "Suggest changes" vs "Make changes" produces different results
2. **Provide motivation**: Context helps Claude understand your goals
3. **Use structured prompts**: XML tags, JSON, labeled sections
4. **Dial back urgency**: Normal language works better than CAPS and exclamation marks
5. **Specify constraints**: "Summarize in exactly 3 sentences, each under 20 words"

### The CO-STAR Framework

```
C - Context: Background and information on the task
O - Objective: Define the task clearly
S - Style: Specify the writing style
T - Tone: Set the attitude
A - Audience: Who is this for
R - Response format: How to structure the output
```

**Sources:**
- [Claude 4 Best Practices - Anthropic Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices)
- [Claude Prompt Engineering Best Practices 2026](https://promptbuilder.cc/blog/claude-prompt-engineering-best-practices-2026)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

## Part 6: Multi-Agent Orchestration

### Core Patterns

| Pattern | Description | Best For |
|---------|-------------|----------|
| **Supervisor/Hub-and-Spoke** | Central orchestrator delegates to specialists | Compliance-heavy, traceable workflows |
| **Mesh** | Agents communicate directly, route around failures | Resilient, fault-tolerant systems |
| **Sequential Pipeline** | Linear chain of specialized transformations | Well-defined multi-step processes |
| **Hierarchical** | Layers of agents, higher oversees lower | Large, complex problem decomposition |
| **Group Chat** | Multiple agents collaborate in shared thread | Creative problem-solving, validation |

### The Hybrid Approach

> "Pure orchestration (central control) and pure choreography (distributed autonomy) each have limitations. The winning pattern involves **hybrid approaches** that use high-level orchestrators for strategic coordination while allowing local mesh networks for tactical execution."
> — [Kore.ai Multi-Agent Orchestration](https://www.kore.ai/blog/choosing-the-right-orchestration-pattern-for-multi-agent-systems)

### Code vs. LLM Orchestration

**Key insight**: While LLM orchestration is powerful, **code-based orchestration is more deterministic and predictable** in terms of speed, cost, and performance.

Pattern: Use structured outputs to generate well-formed data that code can inspect and route.

### Sub-Agent Context Isolation (Manus Pattern)

> "The primary goal of sub-agents in Manus is to **isolate context**. If there's a task to be done, Manus assigns it to a sub-agent with its own context window."

Architecture:
- **Planner**: Assigns tasks, maintains global view
- **Knowledge Manager**: Reviews conversations, determines what to persist
- **Executor**: Performs tasks in isolated context

**Sources:**
- [Google's Eight Essential Multi-Agent Design Patterns - InfoQ](https://www.infoq.com/news/2026/01/multi-agent-design-patterns/)
- [Multi-Agent Orchestration Patterns - Azure](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [Four Design Patterns for Event-Driven Multi-Agent Systems - Confluent](https://www.confluent.io/blog/event-driven-multi-agent-systems/)

---

## Part 7: Security & Safety

### The Fundamental Challenge

> "The core issue remains the same—models have no ability to reliably distinguish between instructions and data. There is no notion of untrusted content."
> — [OpenAI Prompt Injection Analysis](https://openai.com/index/prompt-injections/)

> "Prompt injection, much like scams and social engineering on the web, **is unlikely to ever be fully 'solved.'**"
> — OpenAI

### Defense-in-Depth Architecture

```
┌─────────────────────────────────────────┐
│         Input Validation Layer          │
├─────────────────────────────────────────┤
│         Context Isolation               │
├─────────────────────────────────────────┤
│         Tool Permission Boundaries      │
├─────────────────────────────────────────┤
│         Output Verification             │
├─────────────────────────────────────────┤
│         Human Approval Gates            │
└─────────────────────────────────────────┘
```

### Key Security Principles

1. **Least Privilege**: Default to read-only tools; enable writes behind explicit roles
2. **Zero Trust**: Authenticate every action as if it were a new request
3. **JIT Permissions**: Grant access only for required duration
4. **Trust Boundaries**: Separate untrusted data from instructions
5. **Output Verification**: Validate tool call results before acting

### Human-in-the-Loop Patterns

| Pattern | Description |
|---------|-------------|
| **Approval Gates** | High-impact actions route for human check |
| **Exception Triage** | Agents work queue; humans resolve ambiguous cases |
| **Shadow Mode** | Agents propose and simulate; humans approve |
| **Feedback Loops** | Overrides become training data for guardrails |

**Warning**: Research shows "Lies-in-the-Loop" attacks can exploit approval dialogs. HITL is necessary but not sufficient.

### Compliance Frameworks

- NIST AI RMF now mandates prompt injection controls
- ISO 42001 requires specific detection and prevention measures
- Target: Attack detection within 15 minutes, containment within 5 minutes

**Sources:**
- [AI Security in 2026 - Airia](https://airia.com/ai-security-in-2026-prompt-injection-the-lethal-trifecta-and-how-to-defend/)
- [Indirect Prompt Injection - Lakera](https://www.lakera.ai/blog/indirect-prompt-injection)
- [Human-in-the-Loop Complete Guide 2026 - Parseur](https://parseur.com/blog/human-in-the-loop-ai)

---

## Part 8: Evaluation & Testing

### The Shift to Agent-Level Evaluation

> "Building trustworthy AI no longer stops at model scorecards. In 2026, the standard for AI quality shifts decisively from static model benchmarks to **agent-level evaluation, simulation, and observability** across real user journeys."
> — [Maxim AI](https://www.getmaxim.ai/articles/the-evolution-of-ai-quality-from-model-benchmarks-to-agent-level-simulation-in-2026/)

### Key Benchmarks

| Benchmark | Focus | Top Score |
|-----------|-------|-----------|
| **GAIA** | General assistant capability | 61% (Level 3) |
| **WebArena** | Web-based task completion | ~20% |
| **Mind2Web** | Live website interaction | Varies |
| **τ-Bench** | Rule following, long context | Varies |
| **ToolEmu** | Safety in tool use | 36 tools, 144 cases |

### Evaluation Dimensions

**Agent-centric strategies:**
- Multi-turn personas with explicit success/failure criteria
- Tool stubs and sandboxes with error injection
- Adversarial probes (prompt injection, conflicting evidence)
- Session-level metrics: task success, safety adherence, trajectory quality, latency/cost

### The MCP Builder Evaluation Framework

1. **Tool Inspection**: List available tools, understand capabilities
2. **Content Exploration**: Use read-only operations to explore data
3. **Question Generation**: Create 10 complex, realistic questions
4. **Answer Verification**: Solve each yourself to verify

Requirements for good evaluation questions:
- Independent (not dependent on other questions)
- Read-only (non-destructive operations)
- Complex (requiring multiple tool calls)
- Realistic (based on real use cases)
- Verifiable (clear, single answer)
- Stable (answer won't change over time)

### Granular Analysis

> "Evaluations should be more granular. Rather than focus narrowly on agents getting the right answer, more attention should be paid to **intermediate steps** to see how they get there."
> — [IBM Research](https://research.ibm.com/blog/AI-agent-benchmarks)

**Sources:**
- [AI Agent Benchmarks - Evidently AI](https://www.evidentlyai.com/blog/ai-agent-benchmarks)
- [τ-Bench - Sierra](https://sierra.ai/blog/benchmarking-ai-agents)
- [AI Agent Performance 2026 - AIMultiple](https://research.aimultiple.com/ai-agent-performance/)

---

## Part 9: Self-Improving Agents — The Frontier

### Current State

> "In 2026, self-improving AI is both myth and reality. What we are looking at is quite close to the final prototype and partial implementation, which are an important milestone, but is still far from full autonomy."
> — [Times of AI](https://www.timesofai.com/industry-insights/self-improving-ai-myth-or-reality/)

### Memory-Based Learning

Recent research papers (January 2026):
- **MemRL**: Self-evolving agents via runtime reinforcement learning on episodic memory
- **Agentic Memory**: Unified long-term and short-term memory management
- **EverMemOS**: Self-organizing memory operating system for long-horizon reasoning

### Real-World Results

> "An e-commerce AI agent initially misclassified customer intent 30% of the time. After 60 days of feedback loops and sentiment analysis, its accuracy improved to 92%. No manual retraining—just structured learning from live data."

**Key metric**: AI agents with memory improve accuracy by up to **42% within 90 days**.

### Letta's Vision

> "Today's AI agents struggle to remember previous mistakes, and are unable to learn from new experiences. We're building machines with real memory that can continually learn and self-improve."
> — [Letta](https://www.letta.com/)

**Sources:**
- [Self-Evolving Agents Survey - GitHub](https://github.com/EvoAgentX/Awesome-Self-Evolving-Agents)
- [Agent Memory Paper List - GitHub](https://github.com/Shichun-Liu/Agent-Memory-Paper-List)
- [Self-Learning AI Agents - Beam AI](https://beam.ai/agentic-insights/self-learning-ai-agents-transforming-automation-with-continuous-improvement)

---

## Part 10: The Ecosystem — Adoption & Market

### Industry Adoption

**Agent Skills standard adopters** (as of January 2026):
- Microsoft
- OpenAI (via Codex)
- Atlassian
- Figma
- Cursor
- GitHub

**Partner skills at launch**: Canva, Stripe, Notion, Zapier

### Marketplace Emergence

The ecosystem is rapidly expanding:
- **31,000+ skills** in circulation (as of 2026)
- Multiple marketplaces: SkillsMP, Skillstore, SkillsDirectory, skills.sh
- Both open-source and commercial offerings

### Enterprise Features

Claude Team and Enterprise plans now include:
- Organization-wide skill management
- Centralized governance and visibility
- IT-manageable infrastructure

### Market Size

> "The AI agents market is rocketing from $5.25 billion in 2024 to $52.62 billion by 2030—a **46.3% CAGR**. Multi-agent systems represent the fastest-growing segment."

Performance claims:
- 45% faster problem resolution with multi-agent systems
- 60% more accurate outcomes vs. single-agent systems

**Sources:**
- [Anthropic Opens Agent Skills Standard - VentureBeat](https://venturebeat.com/technology/anthropic-launches-enterprise-agent-skills-and-opens-the-standard/)
- [Agent Skills: Anthropic's Bid to Define AI Standards - The New Stack](https://thenewstack.io/agent-skills-anthropics-next-bid-to-define-ai-standards/)
- [Awesome Agent Skills - GitHub](https://github.com/skillmatic-ai/awesome-agent-skills)

---

## Part 11: Practical Checklist for Building World-Class Skills

### SKILL.md Structure

```yaml
---
name: skill-name
description: Clear description including WHEN to use (triggers) and WHAT it does
license: MIT
argument-hint: <optional-argument-format>
---

# Skill Name

## Overview
[What problem this solves, in 2-3 sentences]

## When to Use This Skill
[Explicit trigger conditions - be specific]

## Instructions
[Step-by-step workflow for the agent]

## Output Format
[Structured format specification]

## Examples
[Concrete examples of input/output]

## Anti-Patterns
[What NOT to do - constraints enable creativity]
```

### Design Principles Checklist

**Context Management:**
- [ ] Uses progressive disclosure (metadata → body → references)
- [ ] Splits large content into separate reference files
- [ ] Defines clear context loading triggers
- [ ] Implements recoverable compression where possible

**Tool Design:**
- [ ] Minimal tool count (compose primitives)
- [ ] Clear, consistent naming conventions
- [ ] Complete input/output schemas
- [ ] Includes annotations (readOnly, destructive, idempotent)

**Prompting:**
- [ ] Explicit instructions (not implicit intent)
- [ ] Structured format (XML tags, JSON)
- [ ] Constraints specified clearly
- [ ] Anti-patterns documented

**Memory:**
- [ ] Defines what to persist vs. discard
- [ ] Uses file system for long-context work
- [ ] Implements state-based patterns for user data
- [ ] Considers todo.md for attention management

**Security:**
- [ ] Least privilege by default
- [ ] Read-only unless write is essential
- [ ] Human approval gates for destructive actions
- [ ] Input validation for untrusted data

**Evaluation:**
- [ ] 10+ realistic test questions
- [ ] Verifiable single answers
- [ ] Tests intermediate steps, not just final output
- [ ] Includes adversarial cases

### What Makes Skills "Proactive"

The best skills don't wait to be called—they trigger automatically:

1. **Pattern triggers**: Drupal-security skill activates when risky code is detected
2. **Event triggers**: Decisions skill suggests recording after architectural choices
3. **Context triggers**: Worktrees skill offers when parallel work is beneficial

**Key insight**: Proactive skills > reactive skills in user value.

---

## Part 12: Bleeding-Edge Research Directions

### Where the Field Is Heading

1. **Natural Language Tools (NLT)**: Replacing JSON tool calling with natural language outputs. Improves accuracy by 18.4 percentage points, reduces variance by 70%.

2. **Multi-Modal Skills**: MCP in 2026 will support images, video, audio. Skills that can "see" and "hear."

3. **Self-Evolving Agents**: MemRL, Agentic Memory, and similar research pushing toward continuous learning from experience.

4. **Agent-to-Agent Protocols**: A2A, ACP, ANP emerging alongside MCP for agent communication.

5. **Compiled Context Views**: Google ADK treating context as "compiled views over a richer stateful system" rather than string manipulation.

### Unsolved Problems

1. **Prompt injection**: Fundamentally unsolved; defense-in-depth required
2. **Long-horizon planning**: Agents still struggle with 50+ step tasks
3. **Belief updates**: How to reconcile conflicting information gracefully
4. **Multi-agent coordination**: Failure rates of 40-80% in complex systems
5. **Trust calibration**: When should agents ask vs. act autonomously?

---

## Conclusion

Building world-class skills in 2026 requires thinking beyond prompts to **context engineering**:

1. **Progressive disclosure** keeps context manageable
2. **File system as memory** enables long-horizon work
3. **Minimal, composable tools** beat specialized bloat
4. **Explicit instructions** work better than implicit intent
5. **Proactive triggers** deliver more value than manual invocation
6. **Defense-in-depth** is required for security
7. **Agent-level evaluation** replaces static benchmarks

The field is moving fast. Skills that seemed cutting-edge six months ago are now table stakes. The winners will be those who embrace the systems engineering mindset and build skills that are not just clever prompts, but **robust context management systems**.

---

## Sources Index

### Official Documentation
- [Claude Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices)
- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [MCP Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [Agent Skills Standard](https://agentskills.io/home)

### Technical Deep Dives
- [Context Engineering for Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
- [Agent Design Patterns - LangChain](https://rlancemartin.github.io/2026/01/09/agent_design/)
- [Claude Skills Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
- [Spring AI Agent Skills](https://spring.io/blog/2026/01/13/spring-ai-generic-agent-skills/)

### Research & Surveys
- [Memory in the Age of AI Agents - arXiv](https://arxiv.org/abs/2512.13564)
- [Self-Evolving Agents Survey](https://github.com/EvoAgentX/Awesome-Self-Evolving-Agents)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [IBM AI Agent Benchmarks](https://research.ibm.com/blog/AI-agent-benchmarks)

### Industry Analysis
- [7 Agentic AI Trends 2026](https://machinelearningmastery.com/7-agentic-ai-trends-to-watch-in-2026/)
- [Multi-Agent Design Patterns - InfoQ](https://www.infoq.com/news/2026/01/multi-agent-design-patterns/)
- [AI Security in 2026 - Airia](https://airia.com/ai-security-in-2026-prompt-injection-the-lethal-trifecta-and-how-to-defend/)
- [Anthropic Opens Skills Standard - VentureBeat](https://venturebeat.com/technology/anthropic-launches-enterprise-agent-skills-and-opens-the-standard/)
