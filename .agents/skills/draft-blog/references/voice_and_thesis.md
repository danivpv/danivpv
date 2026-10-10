# Voice & Thesis Reference

This document is the extended articulation of the authorial voice and intellectual thesis for Daniel Iván Parra Verde's engineering blog. It is **series-agnostic** — it applies equally to the ML Platform and AI Engineering series.

Personal details (professional background, credibility anchors, timeline) are kept in `applications/personal_context.md` and `tex/english.tex`. Do not duplicate them here.

---

## The Series-Level Thesis

### The Operational Gap Argument

What makes a model useful in the real world is not the model. It is the **operational infrastructure around the model** — the systems that make it reproducible, auditable, safely iterable, and trustworthy to the humans who depend on it.

Most data scientists never see this infrastructure built because:
- Someone else built it badly (ad hoc scripts, no lineage, no versioning)
- The org paid for managed services that abstract it away expensively
- It was built so well it became invisible — which is the best case

Building it from scratch teaches you what it actually needs to be.

### The Rolestack Argument

Three engineering disciplines share the ML production problem, each owning a distinct layer:

| Role | What they own | What breaks without them |
|---|---|---|
| **Data Engineers** | Data pipelines, ETL, data quality, versioned feature data | Models train on stale or incorrect data; feature engineering can't scale |
| **ML Engineers / ML Platform Engineers** | Feature stores, experiment tracking, training infra, serving infra, the reproducibility and auditability layer | Train-serve skew goes undetected; experiments can't be reproduced; models can't be safely iterated; feedback loops break |
| **Data Scientists** | Model selection, problem framing, last-mile domain reasoning, stakeholder interface | The business question never gets answered precisely |

This is not a complaint about one person doing three jobs. It is an observation that **engineering the subsystems is what sustains real operations**.

Without experiment tracking: debugging a degraded model becomes a forensic guessing game instead of a systematic audit. Without a feature store: training-serving skew corrupts model quality silently. Without a versioned serving layer: rollback is a manual/mental crisis, not a one-command operation. Without clear model lineage: trust in the model erodes slowly — not because the math is wrong, but because **the system around the math has no integrity**.

Knowing what these subsystems are — and being able to communicate that clearly to non-technical stakeholders — is a distinct, high-value engineering skill.

### The Trust Argument (The Thesis in One Sentence)

> *Models don't fail because the math is wrong. They fail because the systems that keep the math honest — reproducible, current, and auditable — were never built.*

---

## The Personal Scar That Grounds This

*(Use in author voice, not as a victim narrative — as a systems diagnosis)*

At an early job: suddenly tasked with translating graph-based feature engineering into SQL for online serving. No feature store. No experiment tracking. No ability to reproduce the training environment. The task was technically possible, but without a system to keep offline and online feature logic in sync, any result was structurally fragile.

Separately: asked to integrate feedback with no experimentation infrastructure and training-serving skew already baked into the existing pipeline. The despair was not about difficulty — it was about not being able to diagnose or fix the problem directly because the supporting systems didn't exist.

That experience is the emotional core of this series. These aren't abstract engineering best practices. They are the difference between being able to do your job and not being able to.

---

## Role Taxonomy (What "ML Platform Engineering" Actually Is)

Use this to position accurately in posts and author bios:

| Title | What it means | This series |
|---|---|---|
| **Data Scientist** | Model development, problem framing, stakeholder interface, last-mile | Consumer of the platform |
| **ML Engineer** | Production training and inference code, bridges research → production | Builds runtimes on top of the platform |
| **ML Platform Engineer** | Feature stores, experiment tracking, training infra, serving infra, the CDK stacks | **This is what the ML Engineering series documents** |
| **MLOps Engineer** | CI/CD for models, monitoring, drift detection, operational health (ops on top of the platform) | v3/v4 scope — not yet built |
| **AI Engineer** | LLM applications, RAG, agents, agentic pipelines | **This is what the AI Engineering series documents** |

Daniel spans AI Engineer, Data Science, ML Engineer and now ML Platform Engineer — he wrote both the CDK infrastructure and the training/inference runtimes. Most ML Platform Engineers haven't run `feast materialize` themselves. He has. This is a meaningful credibility anchor.

---

## Hook Options

### Option A — The Honest Confession
> *"Most ML models don't fail because the model is wrong. They fail because no one built the system around the model. I spent 16 hours finding out what that system actually needs to be."*

### Option B — The Systems Framing
> *"What does a team of data scientists, ML engineers, and data engineers actually need in place before a model can do anything useful in production? Here's my attempt to build the minimum viable answer."*

### Option C — The Rolestack Argument (Recommended)
> *"Data scientists solve the last-mile problem. Engineers build the road. Most organizations get this wrong: they collapse all roles into one person, or silo them so hard the systems never talk and operations suffer. This post deconstructs the ML engineer's piece: built from scratch across 2 CDK stacks, 4 Fargate tasks, and 3 persistent stores."*

**Why Option C:** It's the most intellectually original, sets up the entire series arc, and only Daniel can write it credibly because it comes from direct experience straddling all roles.

---

## Tone Calibration

**Do:**
- State opinions plainly ("The right choice here is X, because...")
- Quote the actual code when making a technical claim
- Name the bugs and what they cost
- Explain what you would do differently now
- Audit structure top to bottom when revising (`minify and unify`); never append disconnected or orphaned sections to the end of a post (`stop just adding stuff`). Every section must directly serve the core driving thread.
- **Pattern formatting**: Format architectural patterns as: `**Pattern Name.** Eliminates **[failure class].** [Prose explanation.] See [link].`
- **Save cuts**: When minifying a post, save removed deep-dives to `_cuts.md`.
- Anchor all repository links and code excerpts to exact git commit hashes (`commit 4c60434`) so architectural claims remain immutable and reproducible as future series parts evolve.
- Bridge technical trade-offs to official vendor literature (`e.g., AWS Engineering & DevOps Blogs, Well-Architected Framework`) to anchor authorial credibility and demonstrate alignment with industry standards.

**Don't:**
- Hedge valid architectural claims ("It might potentially be worth considering...")
- Sell the scope as larger than it is
- Use the personal story as a complaint — use it as a systems diagnosis
- Write a post that could have been a Stack Overflow answer
- Over-index on "the ugly parts" as a primary framing device. Bugs should be a brief, contained section, not the driving narrative.
- Allow fractured, multi-section conclusions (`e.g., multiple competing 'Next Steps', 'Repo', and 'Call to Action' headings separated by horizontal rules`). Consolidate all closing elements into one unified, structured conclusion heading.

---

## What Was and Was Not Built (Honest Scope Anchor)

Use this whenever describing the ML platform project to prevent scope inflation:

**Built (ML Engineering series, v1):**
- Two CDK stacks (stateful + stateless, data plane separate from control plane)
- Feast feature store: S3 offline store + DynamoDB online store + registry (train-serve skew fixed structurally)
- MLflow: experiment tracking, artifact lineage, model registry, `@champion` alias promotion
- ECS Fargate batch training and inference runtimes
- EventBridge Scheduler for nightly batch inference
- CloudWatch monitoring + alarms + SNS
- Least-privilege IAM, cost-zero idle posture, versioned IaC
- Architectural conditions for team collaboration (DDD bounded contexts, decoupled stacks)

**Not built (honest omissions):**
- Data platform (no ETL, no Glue/Spark/dbt — synthetic data scripts are stand-ins)
- Real-time serving (batch-only in v1/v2 — deliberate, not a gap)
- CI/CD pipeline (scaffolded, not wired — deferred deliberately)
- UI / feedback loop (v3 scope)
- Custom VPC / private subnets / NAT (v4 scope — cost-deferred deliberately)
- Production-grade security hardening (v4 scope — documented explicitly in PRD §6)

---

## The Decision Log (Credibility Anchor)

Every architectural decision in the ML platform has a corresponding entry in `docs/ml-platform-prd.md §2` — the decision log. Each entry documents: the user story it satisfies, the alternatives considered, the decision made, and the rationale.

This is not incidental. The decision log is the argument. It is what separates a blog post that says "I used DynamoDB" from one that says "I used DynamoDB because its schemaless key-value structure lets Feast serialize composite entity keys (`customer#1004`, `merchant#552`) into a single partition key, meaning one table serves all models without schema migrations — and on-demand billing means it costs nothing at idle unlike Redis which bills a node 24/7 (PRD §2.5)."

When writing about any component, the default move is: find the decision log entry, quote the alternatives considered, and explain the rationale in plain English for Persona D while surfacing the code evidence for Persona C.

Key decision log entries to ground claims:
- **§2.1** — CDK vs. Terraform vs. manual console (IaC legibility argument)
- **§2.4** — Feast offline store: S3 vs. Redshift/Athena (MVP cost + ETL separation)
- **§2.5** — Feast online store: DynamoDB vs. Redis (idle cost; multi-model key schema generalization)
- **§2.7** — MLflow backend: RDS Postgres vs. Aurora Serverless (Aurora's "no true zero" floor)
- **§2.9** — MLflow compute: Fargate vs. EC2 (pay-per-second; no ALB cost in v1)
- **§2.10** — Networking: custom VPC vs. default VPC + locked SG (NAT cost deferral)
- **§2.13** — Inference: scheduled batch Fargate vs. always-on endpoint (batch-first; additive real-time path)
- **§2.18** — Stack separation: stateful vs. stateless (data plane protection from compute iteration)
- **§2.22** — EventBridge Scheduler vs. EventBridge Rules (native ECS Fargate network config)
- **§2.23** — Model catalog: Postgres vs. DynamoDB/JSON/MLflow tags (relational integrity; least-privilege scoping)
