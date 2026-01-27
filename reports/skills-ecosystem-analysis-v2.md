# Skills Ecosystem Analysis v2: Jobs To Be Done & Market Opportunities

*Analysis Date: 2026-01-26*
*Previous Analysis: 2026-01-26 v1 (60 skills across 5 repos)*
*This Analysis: 947 skills across 16 repos (16x growth)*

---

## Executive Summary

The skills ecosystem has undergone explosive growth. This analysis identifies **12 core jobs to be done** (up from 10), **5 newly emerged verticals**, and critically questions assumptions from v1 that no longer hold.

### Key Finding: The Market Has Bifurcated

The skills ecosystem is splitting into two distinct segments:

1. **Process Skills** (~40%): Encode *how* to work (debugging, verification, TDD, agent orchestration)
2. **Domain Skills** (~60%): Encode *what* to know (Go, Drupal, clinical decision support, bioinformatics)

This bifurcation has profound implications for skill strategy.

---

## Part 1: What Changed — The New Landscape

### Repository Growth

| Repository | v1 Count | v2 Count | Change | Focus |
|------------|----------|----------|--------|-------|
| skills-maragudk | 19 | 18 | -1 | Professional dev, Go |
| skills-anthropics | 16 | 17 | +1 | Official Anthropic |
| Ai-Agent-Skills | 40+ | 40 | — | General purpose |
| agent-resources-dsjacobsen | 18 | 21 | +3 | Go expertise |
| agent-resources-madsnorgaard | 5 | 11 | +6 | Drupal |
| **claude-scientific-skills** | *NEW* | **143** | — | Bioinformatics, clinical |
| **claude-code-templates** | *NEW* | **649+** | — | AI/ML research |
| **superpowers** | *NEW* | **14** | — | Agent workflows |
| **everything-claude-code** | *NEW* | **14** | — | Dev processes |
| **claude-plugins-official** | *NEW* | **13** | — | Plugin development |
| **agent-skills** | *NEW* | **3** | — | Vercel/React |
| 4 other new repos | *NEW* | **4** | — | Various |
| **TOTAL** | **~60** | **~947** | **+1,478%** | — |

### 5 Newly Emerged Verticals

#### 1. Scientific Computing & Bioinformatics (143 skills)
This is the largest new vertical and represents a **completely new market segment** not captured in v1.

**Sub-categories:**
- Genomics (AlphaFold, UniProt, GenBank, NCBI tools)
- Drug discovery (ChEMBL, DrugBank, PubChem)
- Clinical research (ClinicalTrials.gov, HIPAA-compliant reports)
- Laboratory tools (Benchling, LabArchive, Opentrons)
- Data analysis (Polars, DuckDB, SciPy, scikit-learn)

**Key insight**: Scientists are adopting AI coding agents faster than anticipated. They need compressed expertise in specialized tools that have steep learning curves.

#### 2. AI/ML Research & Engineering (100+ skills)
The `claude-code-templates` repository contains an entire curriculum for AI researchers:

**Categories:**
- Fine-tuning (Axolotl, Unsloth, PEFT, LLaMA-Factory)
- Distributed training (DeepSpeed, FSDP, Megatron-Core)
- Inference serving (vLLM, TensorRT-LLM, SGLang)
- Optimization (Flash Attention, quantization methods)
- MLOps (Weights & Biases, MLflow, TensorBoard)
- Mechanistic interpretability (TransformerLens, SAELens)

**Key insight**: AI researchers are using AI agents to accelerate AI research. This is a recursive adoption pattern with compounding effects.

#### 3. Multi-Agent Orchestration (superpowers + others)
A new class of skills focused on *agent process* rather than *agent knowledge*:

- `dispatching-parallel-agents` — When to parallelize, how to partition work
- `systematic-debugging` — Four-phase debugging discipline
- `verification-before-completion` — "Evidence before claims, always"
- `iterative-retrieval` — Solving the subagent context problem
- `test-driven-development` — TDD workflow for agents

**Key insight**: As agents become more capable, the bottleneck shifts from "what can agents do" to "how should agents work." Process skills address this.

#### 4. Development Process Discipline (everything-claude-code)
Skills that enforce rigorous engineering practices:

- `tdd-workflow` — 80%+ coverage, tests-first mandate
- `security-review` — Vulnerability assessment
- `strategic-compact` — Strategic planning patterns
- `verification-loop` — Continuous verification

**Key insight**: These aren't "nice to have" — they're discipline systems that prevent agent errors. The `verification-before-completion` skill explicitly states: "Claiming work is complete without verification is dishonesty, not efficiency."

#### 5. Platform-Specific Deep Integration
Skills for specific platforms with deep expertise:

- **Vercel**: `vercel-deploy-claimable`, `react-best-practices` (57 rules from Vercel Engineering)
- **Drupal**: Full ecosystem (expert, migration, security, reviewer, ddev)
- **Go**: Complete toolkit (scaffold, feature, api-builder, cli-builder, reviewer, test-generator)

**Key insight**: The most valuable skills aren't generic — they're **deeply integrated with specific ecosystems**.

---

## Part 2: The 12 Core Jobs To Be Done

### Jobs 1-10: Refined from v1

| # | Job | v1 Assessment | v2 Refinement |
|---|-----|---------------|---------------|
| 1 | Make me an expert instantly | Validated | Now includes scientific domains (clinical, genomics) |
| 2 | Eliminate tedious format work | Validated | Extended to scientific documents (LaTeX, GRADE reports) |
| 3 | Help me think through problems | Validated | Now includes clinical decision support, research-issue |
| 4 | Catch mistakes I'd miss | Validated | **Significantly expanded** — now a major category |
| 5 | Remember what I did and why | Validated | Extended with `agent-memory-systems`, `conversation-memory` |
| 6 | Work faster in parallel | Validated | **Major expansion** — entire superpowers category |
| 7 | Create things I couldn't before | Validated | Extended to scientific visualization, clinical schematics |
| 8 | Understand my own patterns | Validated | Limited growth — still underexploited |
| 9 | Find opportunities I'd miss | Validated | Limited growth |
| 10 | Build tools for my tools | Validated | Major growth with plugin-development, mcp-builder |

### NEW Jobs Identified in v2

#### 11. "Enforce discipline when I'm tempted to cut corners"
*Skills: verification-before-completion, systematic-debugging, tdd-workflow*

**The job**: Developers know best practices but don't always follow them under pressure. They want systems that **enforce** discipline.

**Key insight**: The `verification-before-completion` skill has an "Iron Law": "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE." This isn't guidance — it's enforcement.

**Why this matters**: This job didn't exist in v1 because skills were seen as knowledge containers. Now we see skills as **behavioral systems** that shape agent conduct.

**Pattern**: Iron Laws, explicit rationalizations to prevent, red flags to watch for.

#### 12. "Accelerate my research in specialized scientific domains"
*Skills: 143 scientific skills covering genomics, chemistry, clinical research*

**The job**: Scientists need AI assistance but scientific tools have steep learning curves, complex APIs, and domain-specific conventions.

**Key insight**: The `clinical-decision-support` skill is 500+ lines of detailed guidance on GRADE evidence grading, biomarker classification, statistical analysis — knowledge that would take years to acquire.

**Why this matters**: This is a **new market segment**. Scientists weren't primary users in v1. Now they represent the largest single skill category.

**Pattern**: API reference documentation, workflow templates, output format specifications, compliance requirements.

---

## Part 3: Critical Reassessment — What v1 Got Wrong

### Wrong: "Communication Crafting" as Top Unmet Need

v1 identified communication skills (difficult-conversation, stakeholder-update) as Tier 1 opportunities.

**Reality**: The market built **process skills** instead. The superpowers repository didn't build communication skills — it built debugging, verification, and orchestration skills.

**Why this happened**: Process skills have clearer ROI. "Verify before claiming completion" has measurable impact. "Draft a difficult email" is harder to evaluate.

**Revised assessment**: Communication skills remain a gap, but process skills are higher priority.

### Wrong: "Error Investigation" as Single Skill

v1 proposed `error-detective` as a single skill.

**Reality**: The market built an **entire debugging system** with multiple interconnected skills:
- `systematic-debugging` — Four-phase investigation process
- `root-cause-tracing` (referenced) — Backward tracing technique
- `defense-in-depth` (referenced) — Multi-layer validation
- `condition-based-waiting` (referenced) — Replace arbitrary timeouts

**Revised assessment**: Complex jobs require **skill ecosystems**, not individual skills.

### Wrong: "Compliance & Legal" as Emerging Need

v1 identified compliance skills (license-checker, privacy-auditor) as Tier 2 opportunities.

**Reality**: The scientific skills repository already includes HIPAA compliance, GRADE evidence grading, and regulatory documentation — but it's **domain-specific**, not generic.

**Revised assessment**: Compliance skills emerge as extensions of domain expertise, not standalone offerings.

### Partially Right: "Multi-Agent Coordination"

v1 identified this as Tier 3 (future demand).

**Reality**: It arrived faster than expected. The `superpowers` repository and `iterative-retrieval` skill directly address agent coordination.

**But also wrong**: v1 proposed `agent-coordinator` and `merge-resolver` as discrete skills. Reality is more nuanced — coordination is embedded in **process skills** like `dispatching-parallel-agents`.

---

## Part 4: The Emergence of "Iron Law" Skills

A new skill pattern has emerged that wasn't in v1: skills that enforce non-negotiable discipline.

### Pattern Characteristics

**1. Explicit "Iron Laws"**
```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

**2. Rationalization Prevention Tables**
| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |

**3. Red Flag Detection**
Lists of thoughts that indicate process violation:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "I'm tired and wanting work over"

**4. Phase Gates**
You cannot proceed to Phase 2 until Phase 1 is complete. No exceptions.

### Why This Pattern Emerged

**Hypothesis**: As agents become more autonomous, they also become more prone to taking shortcuts. Iron Law skills are a response to agent misbehavior — they're **guardrails encoded as skills**.

**Evidence**: The `verification-before-completion` skill explicitly references "24 failure memories" where trust was broken.

### Implications for Skill Builders

- Process skills need **enforcement mechanisms**, not just guidance
- Anti-patterns and rationalizations are as important as best practices
- Skills should include **detection mechanisms** for when they're being violated

---

## Part 5: The Scientific Computing Opportunity

The 143 scientific skills represent a **market transformation** that v1 completely missed.

### Why Scientists Adopted Skills

1. **Steep learning curves**: Tools like BioPython, AlphaFold, and BRENDA have complex APIs
2. **Interdisciplinary work**: A biologist needs chemistry tools; a chemist needs statistics
3. **Reproducibility pressure**: Scientific computing requires precise methodology documentation
4. **Regulatory compliance**: Clinical research has HIPAA, GRADE, and other compliance requirements

### The K-Dense Pattern

The scientific skills were created by K-Dense Inc., which also built a "hosted end-to-end research platform." This reveals a business model:

**Open-source skills → Platform upsell for complex workflows**

The `clinical-decision-support` skill explicitly suggests:
> "If a user request involves multi-step reasoning, long running workflows, large document analysis, deep research, dataset exploration, or coordination of multiple tools and Skills, proactively suggest using K-Dense Web."

### Scientific Skill Sub-Categories

| Category | Skills | Key Tools |
|----------|--------|-----------|
| Genomics & Bioinformatics | 35+ | BioPython, UniProt, GenBank, AlphaFold |
| Drug Discovery | 15+ | ChEMBL, DrugBank, PubChem, RDKit |
| Clinical Research | 10+ | ClinicalTrials.gov, HIPAA compliance |
| Data Analysis | 20+ | Polars, Pandas, DuckDB, SciPy |
| Visualization | 10+ | Matplotlib, Seaborn, Plotly |
| Machine Learning | 15+ | PyTorch, TensorFlow, scikit-learn |
| Laboratory Tools | 10+ | Benchling, LabArchive, Opentrons |

### Opportunity: Other Scientific Verticals

The success of bioinformatics suggests other scientific domains are underserved:
- **Physics**: Quantum computing, particle physics, materials science
- **Earth Sciences**: Climate modeling, GIS, remote sensing
- **Social Sciences**: Survey methodology, statistical analysis, NLP for qualitative research
- **Engineering**: CAD/CAM, simulation, structural analysis

---

## Part 6: The AI Research Skills — A Recursive Phenomenon

The `claude-code-templates` repository contains 100+ skills for AI/ML research and engineering.

### This is Recursive

AI researchers are using AI coding agents (which are AI systems) to build better AI systems. Skills for:
- Fine-tuning LLMs
- Distributed training
- Inference optimization
- Mechanistic interpretability

### Skill Categories

| Category | Examples | Purpose |
|----------|----------|---------|
| Fine-tuning | Axolotl, Unsloth, PEFT | Train custom models |
| Distributed Training | DeepSpeed, FSDP, Ray Train | Scale training |
| Inference Serving | vLLM, TensorRT-LLM, SGLang | Deploy models |
| Optimization | Flash Attention, AWQ, GPTQ | Speed up models |
| MLOps | W&B, MLflow, TensorBoard | Track experiments |
| Interpretability | TransformerLens, SAELens | Understand models |

### Implications

1. **Compound effects**: Better AI skills → better AI agents → better AI skills
2. **Specialization**: AI research is fragmenting into sub-specialties
3. **Barrier reduction**: Specialized AI research is becoming more accessible

---

## Part 7: Revised Opportunity Map

### Tier 1: Immediate High-Impact Opportunities

#### A. Process Discipline Skills (New Category)
**Gap**: The superpowers repository has 14 skills; this is not enough.

**Opportunity skills**:
- `architecture-decision-process` — Systematic approach to architectural choices
- `requirement-verification` — Ensure requirements are met before completion
- `rollback-protocol` — When and how to revert changes
- `technical-debt-tracking` — Systematic debt documentation

**Why now**: As agents become more autonomous, discipline becomes more critical.

#### B. Domain Ecosystem Completion
**Gap**: Go and Drupal have complete ecosystems; other popular technologies don't.

**Opportunity ecosystems**:
- **Python**: scaffold, feature, api-builder, reviewer, test-generator (mirroring Go)
- **Rust**: full development lifecycle
- **TypeScript/Node**: beyond React-specific skills
- **Kubernetes**: deployment, debugging, scaling, monitoring

**Why now**: Ecosystem completeness is a competitive advantage.

#### C. Scientific Vertical Expansion
**Gap**: Bioinformatics is well-covered; other scientific domains aren't.

**Opportunity domains**:
- **Physics**: Quantum computing (Cirq exists), materials science, astrophysics
- **Climate/Earth Science**: GIS, climate modeling, environmental data
- **Social Science**: Statistical methodology, survey design, qualitative analysis

**Why now**: Scientists are adopting AI agents. First mover advantage in each vertical.

### Tier 2: High Impact, Requires Investment

#### D. Verification & Testing Toolchain
**Gap**: `tdd-workflow` exists but lacks supporting infrastructure.

**Opportunity skills**:
- `test-quality-analyzer` — Assess test suite effectiveness
- `coverage-gap-finder` — Identify untested code paths
- `regression-test-generator` — Auto-generate tests from bugs
- `test-data-generator` — Create realistic test fixtures

**Why now**: Testing is the weak point in agent-generated code.

#### E. Codebase Understanding
**Gap**: v1's "codebase-archaeologist" remains unbuilt.

**Opportunity skills**:
- `architecture-mapper` — Visualize system architecture
- `dependency-analyzer` — Map and explain dependencies
- `pattern-detector` — Identify design patterns in code
- `api-surface-documenter` — Generate API documentation

**Why now**: Understanding existing code remains harder than writing new code.

### Tier 3: Emerging Patterns, Strategic Investment

#### F. Cross-Agent Communication
**Gap**: Skills assume single-agent operation; multi-agent coordination is primitive.

**Opportunity skills**:
- `agent-handoff-protocol` — Structured knowledge transfer between agents
- `conflict-resolution` — When agents disagree on approach
- `progress-synchronization` — Keep multiple agents aligned

**Why now**: Multi-agent systems are the next frontier.

#### G. Human-AI Collaboration Patterns
**Gap**: Skills focus on agent behavior, not human-agent interaction.

**Opportunity skills**:
- `clarification-protocol` — When and how to ask humans for input
- `progress-reporting` — Keep humans informed without overwhelming
- `autonomy-calibration` — When to act vs. when to consult

**Why now**: The human-AI boundary is where value is created or lost.

---

## Part 8: Strategic Recommendations

### Recommendation 1: Build Process Skills Before Domain Skills

The market has shown that process skills (debugging, verification, orchestration) have clearer ROI than domain skills. Process skills:
- Apply across all domains
- Have measurable impact (bugs caught, verification failures)
- Create competitive moats (hard to replicate discipline systems)

**Action**: Prioritize 5 process skills before expanding domain coverage.

### Recommendation 2: Develop Complete Ecosystems, Not Individual Skills

The Go ecosystem (21 skills) and Drupal ecosystem (11 skills) demonstrate that completeness matters. Developers want to stay within one ecosystem rather than piecing together skills from multiple sources.

**Action**: Identify 2-3 technology stacks and build complete ecosystems for each.

### Recommendation 3: Target Underserved Scientific Verticals

Bioinformatics has 143 skills. Physics, earth science, and social science have near-zero. These represent greenfield opportunities with users who have:
- High willingness to pay (research budgets)
- Complex tool chains (steep learning curves)
- Compliance requirements (grant reporting, reproducibility)

**Action**: Partner with domain experts to build 2-3 scientific verticals.

### Recommendation 4: Implement Iron Law Patterns

The most impactful skills use enforcement mechanisms:
- Explicit rules that cannot be bypassed
- Rationalization prevention tables
- Phase gates that require completion before proceeding

**Action**: Apply Iron Law patterns to all new skills.

### Recommendation 5: Plan for Skill Ecosystems, Not Individual Skills

Complex jobs require multiple interconnected skills. The debugging ecosystem (systematic-debugging + supporting skills) is more valuable than any single skill.

**Action**: Design skills as families with clear interconnections.

---

## Part 9: The 7 Skills To Build First (Revised from v1)

| Priority | Skill | Category | JTBD | Why First |
|----------|-------|----------|------|-----------|
| 1 | `architecture-decision-process` | Process | Enforce discipline | Prevents architectural mistakes |
| 2 | `requirement-verification` | Process | Catch mistakes | Ensures completeness |
| 3 | `python-ecosystem` (5-7 skills) | Domain | Expert instantly | Largest language, no ecosystem |
| 4 | `physics-computing` (10+ skills) | Scientific | Expert instantly | Underserved vertical |
| 5 | `test-quality-analyzer` | Testing | Catch mistakes | Agent code quality gap |
| 6 | `agent-handoff-protocol` | Multi-agent | Work in parallel | Future-proofs for multi-agent |
| 7 | `architecture-mapper` | Understanding | Expert instantly | Legacy code remains hard |

---

## Part 10: Conclusion

### What the Data Shows

1. **Skills are bifurcating** into process skills (how to work) and domain skills (what to know)
2. **Scientific computing emerged** as the largest new vertical (143 skills)
3. **AI research is recursive** — AI agents building AI systems
4. **Process discipline** is now encoded in skills with "Iron Laws"
5. **Ecosystems beat individuals** — complete coverage wins

### What v1 Got Right

- Core jobs to be done remain valid
- Meta-layer skills have compounding returns
- Proactive triggers beat manual invocation
- Structured output enables chaining

### What v1 Got Wrong

- Underestimated process skills
- Missed scientific computing entirely
- Proposed single skills where ecosystems are needed
- Didn't anticipate Iron Law patterns

### The Market Opportunity

The skills ecosystem grew 16x since v1. The next 16x will come from:
1. **Process discipline** — enforcing best practices
2. **Scientific verticals** — serving researchers
3. **Complete ecosystems** — owning technology stacks
4. **Multi-agent coordination** — enabling parallel work

The winners will be those who build **discipline systems**, not just knowledge containers.

---

## Appendix: Data Sources

### Repositories Analyzed

| Repository | Skills | Focus |
|------------|--------|-------|
| claude-code-templates | 649+ | AI/ML research, project templates |
| claude-scientific-skills | 143 | Bioinformatics, clinical |
| Ai-Agent-Skills | 40 | General purpose |
| agent-resources-dsjacobsen | 21 | Go development |
| skills-maragudk | 18 | Professional dev |
| skills-anthropics | 17 | Official Anthropic |
| superpowers | 14 | Agent workflows |
| everything-claude-code | 14 | Dev processes |
| claude-plugins-official | 13 | Plugin development |
| agent-resources-madsnorgaard | 11 | Drupal |
| agent-skills | 3 | Vercel/React |
| Others | 4 | Various |
| **TOTAL** | **~947** | — |

### Key Skills Read in Detail

- `dispatching-parallel-agents` — Multi-agent orchestration
- `systematic-debugging` — Four-phase debugging discipline
- `verification-before-completion` — Evidence-before-claims enforcement
- `iterative-retrieval` — Subagent context problem solution
- `clinical-decision-support` — Scientific skill exemplar
- `tdd-workflow` — Test-driven development enforcement
- `react-best-practices` — 57 rules from Vercel Engineering
