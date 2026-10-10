# ML Engineering Series Plan

**GitHub repo**: https://github.com/danivpv/ml-platform
**Local repo**: ../ml-platform
**Status**: Part 1 codebase ready (v1 deployed). Part 2 written (Aug 7, 2026 — API Boundary & Stateful Orchestration). Parts 3–6 TBD (refine as builds complete).
**Format**: 4–6 focused deep dives, one per month.
**Primary audience**: Persona A (DS turned ML engineer) and Persona B (senior SWE entering ML)

---

## Series-Level Thesis

> *"The gap between a notebook model and a model that does something useful in the real world is not algorithms. It's operational infrastructure — the systems that make models reproducible, auditable, and safely iterable. Without them, models silently fail, can't be iterated, and slowly lose the trust of the humans who depend on them. This series documents what those systems actually need to be."*

The series also argues for a clear **rolestack separation**:
- **Data engineers**: own the data pipelines and versioned feature data
- **ML engineers / ML platform engineers**: own the operational substrate (this series)
- **Data scientists**: own the last-mile problem — model selection, domain reasoning, stakeholder interface

Engineering these subsystems is what sustains real operations. Without experiment tracking, debugging a degraded model becomes a forensic guessing game instead of a systematic audit. Without a feature store, training-serving skew corrupts model quality silently and the bug is nearly impossible to reproduce because the training environment no longer exists. These are not best practices — they are the mechanical requirements for a model to be trustworthy.

---

## Audience Personas

| Persona | Background | What they want | Central question this series answers for them |
|---|---|---|---|
| **A** — DS turned ML engineer | Pandas, scikit-learn, Jupyter, maybe Docker | "How do I get my notebook model into something that runs on a schedule in the cloud without becoming an infra engineer for 6 months?" | *What systems do I need to close the feedback loop from production back to retraining — and who builds them?* |
| **B** — Senior SWE entering ML | AWS, CDK, Docker, Terraform | "What is Feast/MLflow actually for? Is it just hype or does it solve a real problem?" | *What are the component boundaries I need to engineer so a data science team can do their job without depending on me for every run?* |
| **C** — Hiring manager / tech lead / ML director | Systems-level thinking, no code depth needed | "What does building this from scratch tell me about this person's architectural judgment and ability to communicate trade-offs?" | *What are the system components needed to support an existing ML operation — and how does each one prevent a class of failure?* |
| **D** — Non-technical stakeholder | Business operations, product, finance | "Why does my team need this? What breaks without it? What does 'the model is broken' actually mean and who is responsible?" | *Why does my team need this infrastructure? What breaks without it, and who is responsible when it does?* |

Primary: Persona C across all parts — written for senior engineers, tech leads, and ML directors who make architectural decisions and communicate trade-offs. Persona B benefits from the same content. The framing sections of Parts 1 and 4 are deliberately legible to Persona D. Persona A (junior DS) is not the primary target — 1,315 lines of CDK infrastructure cannot be taught in a blog post.

---

## Opinion Pillars (Argued Across the Series)

| Opinion | Argument | Evidence | Where it lands |
|---|---|---|---|
| **IaC makes infrastructure legible, auditable, and safe** | AWS CDK codifies infrastructure as versioned Python — every resource is traceable, every cost is attributable, teardown is a single command. The alternative (console-clicked resources, opaque managed platforms) creates silent financial risk that is nearly impossible to audit after the fact. | PRD §2.1: CDK chosen over Terraform and manual console for "Python end-to-end; constructs allow logical units to be composed and tested independently." Personal: left a SageMaker compute resource running for a month as a student with no visibility into why costs accumulated. | Parts 1 + 4 |
| **Two-pizza teams with CI/CD culture enable faster iteration — but senior judgment still matters** | Bezos's two-pizza model, combined with a CI/CD culture, eliminates handoff overhead. AI tools lower the floor for domain-crossing at junior/intermediate levels. But at senior and above, the bottleneck shifts to knowing *what not to build*, long-term system evolution, and communicating trade-offs to non-technical stakeholders — judgment that AI does not yet replace. | PRD §2.2: monorepo chosen because "one component with tightly coupled parts that deploy together — split only when packages are reused across independent applications or owned by separate teams." That is a judgment call, not a search result. | Parts 1 + 2 |
| **Building from scratch teaches what managed platforms actually do — and at what cost** | Rather than certifying for SageMaker, building equivalent infrastructure from first principles reveals what managed ML platforms solve, what they abstract away, and the exact cost of that abstraction. Empirically: Aurora Serverless v2 has no true zero floor (PRD §2.7 — minimum ACU bills continuously, making it more expensive than a fixed micro RDS at this scale despite the "serverless" label); a NAT Gateway adds ~$32/month for private subnets that aren't needed at MVP scale (PRD §2.10); an ALB adds ~$16/month that isn't justified for a single-user v1 (PRD §2.9). These are not opinions — they are measured AWS pricing tradeoffs documented in the decision log. The outcome of building this is not a faster platform — it is the ability to evaluate options and communicate tradeoffs with authority. | PRD §2.7, §2.9, §2.10: concrete cost decisions with documented alternatives and rationale. | Part 1 |

---

## Part 1 — "Beyond the Notebook: The Operational Reality of an Enterprise ML Platform"

**Status**: ✅ Published (July 18, 2026).
**Thesis**: *The gap between a working ML model and a reliable production ML service is not algorithms. It is operational infrastructure: the systems that make models reproducible, auditable, and safely iterable.*
**Target persona**: C primary. A/B in technical sections. D in framing sections.
**Format**: Narrative + architecture diagram + condensed pattern prose. No inline code. ~9 min read.

### Opening Hook (final)
> "Data scientists solve the last-mile problem. Engineers build the road. Most organizations get this wrong: they collapse all roles into one person, or silo them so hard the systems never talk and operations suffer. This post deconstructs the ML engineer's piece: built from scratch across 2 CDK stacks, 4 Fargate tasks, and 3 persistent stores. Total AWS spend to build and validate the v1: ~$1."

### Structure (as published)
1. **Maturing from Data Scientist to ML Engineer** — Personal scar: translating graph features to SQL with no feature store, no lineage, no reproducibility. The motivation to build these systems from scratch rather than certifying for SageMaker.
2. **The Platform: 4 Subsystems, 1 Operational Goal** — Architecture diagram. Each subsystem as an AWS CDK component (`infrastructure.py` + `runtime/`), wired in `component.py` aligned with AWS Well-Architected vocabulary. Condensed table: subsystem → operational question → stack → structural guarantee.
3. **Core Architectural Patterns** — 4 patterns in prose with failure class labels and progressive disclosure links to pinned commit: Two-Stack CDK boundary (eliminates data loss from compute iteration), Feast dual-store (eliminates training-serving skew), MLflow `@champion` alias (eliminates deployment coupling), decoupled compute (eliminates resource waste and lifecycle coupling).
4. **Two Pesky Bugs** — Table only: Bug F (YAML apostrophe, `os.path.expandvars` behavior) and Bug K (IGW hairpinning, VPC security group metadata stripping).
5. **Conclusion & Next Steps** — Bridges to Part 2.

---

## Part 2 — "The API Boundary: Enterprise Networking and Stateful ML Orchestration"

**Status**: ✅ Written (August 7, 2026). Distribution pending (requires distribution setup day first).
**Thesis**: *v1 works for one ML engineer with AWS CLI access. It does not work for a data scientist who needs to register a model, trigger a training run, or inspect predictions without touching CDK or Fargate directly. The API layer is not a convenience: it is the boundary that separates ML engineers who own the infrastructure from data scientists who use it as clients. Without it, the platform is just a collection of glue scripts, intelligible only to whoever deployed them.*
**Target persona**: B (Senior SWE) + C (Tech Lead/Hiring Manager). This directly targets Senior Backend / Platform engineering roles by demonstrating mastery of FastAPI, CQRS, async migrations, and AWS Networking.
**Format**: Systems architecture + CDK snippets

### Opening Hook
> *"In v1, triggering a training run meant modifying AWS primitives via the CLI. To scale, we need a standardized communication protocol (a CQRS API) and stateful orchestration (RDS/Alembic) to track models. But an API is only a suggestion until network isolation (NAT/ALB) enforces it by making the underlying compute invisible to the public internet. This post bridges the gap between ML scripts and enterprise software."*

### Outline
1. **The transition from scripts to systems** — Why a collection of scripts is a dead end, and how moving to an API decouples the data scientist from the underlying ECS infrastructure.
2. **The FastAPI Boundary (CQRS)** — Implementing Command Query Responsibility Segregation to cleanly separate model registration queries from long-running training commands.
3. **State Management (Alembic & SQLModel)** — Why ML platforms need relational databases for cataloging (vs hardcoded CDK config), and how async migrations keep the schema safe.
4. **Network Hardening (ALB + NAT Proxy)** — Refactoring Fargate tasks into `PRIVATE_WITH_EGRESS` subnets. Why public IPs on training containers are an unacceptable security risk for real customer data, and how the ALB + NAT topology solves this.
5. **Dynamic Job Scheduling** — Utilizing `aioboto3` to programmatically create EventBridge schedules for model inference dynamically via API, rather than relying on static CDK definitions.
6. **PlatformContext Injection** — Decoupling the CDK infrastructure to cleanly pass runtime ARNs to the FastAPI layer.

---

## Part 3 — "The Training Subsystem: Developer Loop and Pipeline Hardening"

**Status**: ⏳ Planning phase. Next to be built.
**Thesis**: *A 15-minute cloud deployment cycle per code change kills iteration velocity. This part collapses the loop to 3 seconds with local Docker Compose mocking, then hardens the training pipeline with a strict OOP protocol so onboarding a new model is a configuration decision, not a code change.*
**Target persona**: B + C. Proves engineering velocity and systems design discipline.
**Format**: Architecture decision log (problem → decision → rationale)

### Title (Working)
> "The Training Subsystem: Developer Loop and Pipeline Hardening"

### Opening Hook
> *Hook to be drafted.*

### Outline

1. **The iteration velocity problem** — Why 15-minute cloud deployments kill the training development cycle. The cost of testing a single code change in a Fargate environment.
2. **Local Docker Compose mocking (Epic 1)** — Dropping iteration time to 3 seconds by mocking the FastAPI catalog, MLflow, and RDS locally. What components need mocking and why.
3. **The `BaseMLModel` Protocol (Epic 2)** — Defining a strict OOP contract so a generic `TrainingDispatcher` can dynamically pull features and train any model without touching core platform code.
4. **A second use case** — Introducing a real use case to force the decoupling and prove the abstraction holds under different model types.

### Pesky Bug
TBD from build log.

---

## Part 4 — "The Inference Subsystem: From Batch to Online Serving"

**Status**: ⏳ TBD.
**Thesis**: *Batch inference is the starting point, not the destination. This part irons the batch pipeline to production quality, then extends the platform to real-time online serving, introducing process isolation so one degraded model cannot take down all inference.*
**Target persona**: B + C. Proves readiness for ML Engineer roles focused on high-throughput, low-latency serving.
**Format**: Systems argument + architecture diagram + code evidence

### Title (Working)
> "The Inference Subsystem: From Batch to Online Serving"

### Opening Hook
> *Hook to be drafted.*

### Outline

1. **Hardening batch inference** — What production-grade batch inference requires beyond a scheduled Fargate task: retry logic, failure alerting, output validation.
2. **The case for online serving** — When batch latency is no longer acceptable: latency requirements, real-time feature retrieval, on-demand prediction.
3. **BentoML on Fargate** — Process isolation as the core design choice: decoupling the HTTP API server from model execution runners so one memory-leaking model cannot crash all inference.
4. **Online feature retrieval** — Transitioning from S3 batch joins to Feast's DynamoDB online store for real-time, low-latency lookups.
5. **Dynamic model loading** — Resolving models from the catalog DB and pulling `@champion` aliases from MLflow at runtime without framework coupling.

### Pesky Bug
TBD from build log.

---

## Part 5 — "The Application Layer: Real-World Case Studies"

**Status**: ⏳ TBD.
**Thesis**: *A platform's true value is proven by the applications built on top of it. True operational limits are only discovered when onboarding complex, messy, real-world data science workloads.*
**Target persona**: C primary (ML Directors). Directly appeals to Data Science leadership by proving you can solve complex DS math (causal inference, OR) *and* deploy it on your own infrastructure.
**Format**: Case studies (one per post)

### Title 
> "WIP"

### Opening Hook
> *"WIP"*

### Outline
1. **Case Study Series** — We will run a series of blogs, each implementing a concrete business case on top of our API. Examples include:
   - *CPG Promotional Spend (Double Machine Learning)*: Testing the platform's ability to handle causal inference and endogeneity traps.
   - *B2B SaaS Churn (HistGradientBoosting)*: Testing the platform's ability to optimize for precision-under-capacity constraints (Precision @ K).
   - *Fraud Detection (Isolation Forest + XGBoost)*: Testing zero-day anomaly detection and extreme class imbalance in the online serving path.

---

## Part 6 — "The Monitoring Subsystem: Drift Detection and Operational Observability"

**Status**: ⏳ TBD.
**Thesis**: *A model that degrades silently is worse than a model that fails loudly. This part adds the monitoring layer: data drift detection, prediction distribution tracking, and alerting pipelines that close the operational feedback loop from production serving back to retraining.*
**Target persona**: C primary (ML directors, senior engineers). Demonstrates operational maturity beyond initial deployment.
**Format**: Systems argument + monitoring architecture

### Title (Working)
> "The Monitoring Subsystem: Drift Detection and Operational Observability"

### Outline

1. **The silent failure problem** — Why infrastructure health monitoring (Part 1) is not the same as model quality monitoring. What "the model is degrading" actually means and who is responsible.
2. **Data drift detection** — Monitoring input feature distributions against training baselines. When to trigger retraining.
3. **Prediction distribution tracking** — Monitoring output score distributions for anomaly detection.
4. **Closing the feedback loop** — How monitoring alerts connect back to the training subsystem (Part 3) to trigger retraining pipelines.

### Pesky Bug
TBD.

---

## Part 7 — "The Capstone: Next.js UI Integration"

**Status**: ⏳ TBD.
**Thesis**: *A platform becomes a product when it has a user interface. Integrating a modern web dashboard proves the robustness of the underlying API and democratizes access to the model catalog.*
**Target persona**: C + D. Demonstrates Full-Stack capability (Next.js) and product sense.
**Format**: UI walkthrough + frontend-to-backend architecture

### Title
> "WIP"

### Outline

1. **Next.js UI Integration** — Building a high-level web dashboard for real-time model interaction, prediction debugging, and catalog discovery.
2. **Model Promotion GUI** — Exposing the `@champion` promotion and rollback APIs to the end user.
3. **Close** — A retrospective on the entire platform build.

---



## Call to Action (Per Post)

CTA is finalized at write time. Tentative anchors by part:

| Part | Target persona for CTA | Tentative CTA |
|---|---|---|
| **1** | C — hiring managers, tech leads, ML directors | *What subsystem do you think is missing from this v1 architecture? And which one do you wish you had known about at the start of your career? For me, the feature store would have been a lifesaver.* |
| **2** | B + C — Backend / Platform engineers | *When building platforms, do you prefer opinionated architectures with strict boundaries (CQRS, private subnets, NAT/ALBs), or do you favor the speed and flexibility of monolithic designs with relaxed security gates?* |
| **3** | B + C — SWEs entering ML, platform engineers | *What is the longest deployment cycle you've had to endure just to test a simple code change? Moving from a 15-minute cloud deploy to a 3-second local loop changed how I build.* |

---

## Open Items

- [ ] Publishing platform: dev.to primary (recommended) vs. Medium primary
- [ ] Author byline: "Daniel Iván Parra Verde" vs. "danivpv"
- [ ] Cross-post to LinkedIn Articles after each post?
- [ ] AWS User Group talk — time to coincide with Part 1 publication
- [ ] Measure CDK infra lines before writing Part 1
- [ ] Parts 2–4 theses: refine once respective builds are complete
