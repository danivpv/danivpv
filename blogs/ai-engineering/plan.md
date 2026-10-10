# AI Engineering Series Plan

**GitHub repo**: https://github.com/danivpv/finops-agent
**Local repo**: ../finops-agent
**Status**: Part 1 codebase ready (v1 deployed). Parts 2 to 4 TBD (refine as builds complete).
**Format**: 3 posts, one per deployed increment of one repository.
**Primary audience**: Persona C (senior engineers, tech leads, ML directors, hiring managers) and Persona B (senior SWEs entering AI engineering).

---

## Series-Level Thesis

> *"Frontier models can write code and solve open math problems, yet they still fail at designing cohesive cloud architectures that hold up under real cost, security, and operational constraints. A senior AI engineer's value lies in architectural judgment and ultimately SLA ownership: combining deep knowledge of cloud-native primitives with the restraint to know what not to build so a service is useful to third parties from day one. This series deconstructs a production-grade FinOps agent on AWS and its evolution into general lakehouse queries."*

The series also connects to the **rolestack argument** established in the [ML Engineering series](../ml-platform/plan.md):
- **Data engineers**: own the governed lakehouse, catalog schemas, and curated S3 Parquet tables (built in Part 2, then shared with `ml-platform` in Part 3)
- **AI / ML platform engineers**: own the runtime boundaries, IAM topology, tool gateways, prompt lifecycle, and spend guardrails (this series)
- **Domain analysts / Data scientists**: own the financial risk formulas, commitment models, and last-mile business decisions

---

## Audience Personas

| Persona | Background | What they want | Central question this series answers for them |
|---|---|---|---|
| **A** — Early/mid-career developer or DS exploring open-source AI | Python, open-source agent frameworks, notebooks | "An exciting open-source ecosystem is constantly inventing patterns, but how do those patterns become reliable, useful systems?" | *Where do open-source patterns get consolidated for developer ergonomics and production reliability?* (Not the primary target of this series; the main takeaway for Persona A is that structured cloud certifications at early and mid-career accelerate this jump.) |
| **B** — Senior SWE entering AI engineering | AWS, CDK, Docker, distributed systems | "How do I ship tool-loop agents rapidly without ticket-driven handoffs between app developers and infrastructure teams?" | *How do Bedrock AgentCore (for the managed tool loop) and AWS CDK (co-locating infrastructure and runtime code in one repo) let a two-pizza team iterate with high velocity under uncertainty?* |
| **C** — Hiring manager / tech lead / ML director | Systems-level thinking, architectural trade-offs | "Does this engineer have the judgment to design a secure, cost-predictable architecture on the first pass, or will they build an expensive science project?" | *What does senior architectural judgment look like when translating cloud and GenAI patterns into a deployed system?* |
| **D** — Non-technical stakeholder | Finance, product, business operations | "Can I trust the numbers this assistant reports, and what guarantees it won't invent figures or blow through our cloud budget?" | *What structural guardrails keep the assistant honest, auditable, and strictly bounded in cost?* |

Primary: Persona C across all parts, written for senior engineers, tech leads, and directors who evaluate architectural judgment and operational trade-offs. Persona B benefits directly from the AgentCore + CDK co-location patterns. Framing sections remain legible to Persona D. Persona A is not the primary target: this series is an architectural reference rather than an introductory tutorial, though it demonstrates why early/mid-career engineers benefit from learning consolidated cloud-vendor patterns early.

---

## Opinion Pillars (Argued Across the Series)

| Opinion | Argument | Evidence | Where it lands |
|---|---|---|---|
| **Structured cloud mastery + operational experience prevent expensive PoC thrashing** | Preparing for AWS SAA-C03 (13 calendar days) and AWS AIP-C01 (21 calendar days) on top of prior delivery experience builds a mental catalog of mature cloud primitives. Knowing what the cloud provider already solves natively lets you design a secure, serverless, zero-idle-cost architecture on day one instead of rewriting a fragile PoC multiple times. | `finops-agent` v1 shipped directly with AgentCore Runtime, Gateway, Memory, Bedrock Prompt Management, SigV4 SSR proxy, and automatic budget `Deny` actions with zero standing servers. | Part 1 |
| **Senior engineering judgment is knowing what not to build (and where LLMs still fail at architecture)** | Frontier models can solve open problems in mathematics, yet asking an LLM for three architectural options still produces broken cross-region IAM policies, hallucinated CDK constructs, or unnecessary standing compute. Until training datasets with verifiable solutions-architecture SLOs close that gap, leaving human engineers primarily as the reputational and contractual liability anchor for trust and capital allocation, human judgment on what *not* to build (no NAT Gateway, no Cognito login wall for a public sample, no custom LLM proxy server, no long-term memory extraction) is what keeps systems lean and useful. | PRD §AI.1–§AI.8: every subsystem documents the heavier alternatives rejected (OpenRouter/MLflow AI Gateway, Cognito User Pool, long-term memory strategies, duplicated DuckDB stores) and why the smaller design wins. | Parts 1 + 2 |
| **Open-source frameworks are for fast PoCs and research; cloud-consolidated primitives are for tight SLAs and third-party service** | Researchers prefer implementing everything from scratch, and open-source frameworks excel at testing unverified research patterns, smoothing the learning curve, and building shiny demos quickly. When serving third parties under tight operational, security, and cost SLAs, cloud providers consolidate the battle-tested patterns (AgentCore Runtime and Gateway, IAM SigV4 at every hop, Bedrock Prompt Management, AWS Budgets IAM actions) with CDK developer ergonomics so a two-pizza team can own both application and infrastructure without handoff queues. | `ai/infrastructure.py`, `frontend/infrastructure.py`, `component.py`: zero shared API keys in `.env`, zero EC2/Fargate idle floor, and synthesized CloudFormation template tests (`tests/test_cdk_stack.py`) proving every IAM statement offline. | Parts 1 + 3 |
| **The agent's analytical store and the ML platform's feature store are the same lakehouse asset** | An AI agent querying governed business tables through typed tools and an ML platform materializing historical features into Feast read the same curated S3 Parquet zone. Building one governed lakehouse serves both series. | Part 2 builds CUR 2.0 + Glue + Athena. Part 3 generalizes the query surface and points `ml-platform` Feast at the same curated zone. | Parts 2 + 3 |

---

## Part 1 — "From Cloud Patterns to Production: Building a Bounded FinOps Agent on Amazon Bedrock AgentCore"

**Status**: ⏳ Ready to draft (`finops-agent` v1 code complete, synthetic data and CDK L2 alignment committed). Target post date: Tue Oct 27, 2026.
**Thesis**: *Structured cloud mastery and engineering judgment let you translate AWS architecture patterns directly into a deployed, cost-bounded agent design on day one, knowing exactly which native primitives to compose and what not to build to have a live implementation in days, not weeks.*
**Target persona**: C primary, B secondary. Authoritative, direct, no tutorial fluff.
**Format**: Narrative + architecture diagram + subsystem table + 6 patterns in prose + 2 pesky bugs + conclusion bridging to Part 2. ~9 min read.

### Opening Hook
> *"Frontier models can solve open problems in mathematics, yet asking Claude for three ways to deploy a local PoC with a recommendation still yields unnecessarily expensive servers, several avoidable migrations, and permanent tech debt. Getting an agent to run in a notebook takes hours; getting it to production across cost, security, and operational boundaries without redoing the work three times requires knowing the cloud primitives cold. This post deconstructs a bounded FinOps agent built across 2 CDK stacks on Amazon Bedrock AgentCore in less than a week."*

### Outline
1. **Maturing: 34 Days of Cloud Patterns and the Limits of GenAI Architecture** — The 13-day SAA-C03 sprint (Aug 26, 2026) and 21-day AIP-C01 sprint (Sep 21, 2026). It is easy to believe you know it all after shipping a couple of production AI systems, yet staying humble means staying open to structured learning. How structured study builds the judgment to design for cost, security, and operations on day one and ship a live implementation in under a week. Why asking Claude for 3 architectural options fails today on AWS-native design, why datasets with verifiable infrastructure SLOs will eventually close that gap, and why, until human engineers mostly serve as the reputational and contractual liability anchor for capital and trust, deep technical judgment still gives you a decisive edge.
2. **The Platform: 4 Subsystems, 1 Operational Goal** — Architecture diagram (`docs/finops-agent-architecture.drawio.svg`) + 4-row subsystem table (`Agent`, `Data`, `Frontend`, `Infrastructure`). Brief mention that the CDK app follows the official AWS CDK Python structure and best-practices guides (`infrastructure.py` + `runtime/` composed in `component.py`). One sentence stating that a real-shaped hourly AWS billing extract was replaced by a deterministic synthetic generator (`scripts/generate_synthetic_data.py`) with the same schema.
3. **Core Architectural Patterns** — 6 patterns in prose, each labeled with the **failure class eliminated**, showing the native primitive chosen and heavier options left unbuilt:
   - **One Query, Two Doors**: Eliminates **divergent implementations and model-invented numbers** (`run_query` behind API Gateway and AgentCore Gateway).
   - **Server-Side Tool Budget**: Eliminates **runaway tool loops that a prompt cannot stop** (`_QueryBudget` enforcing `MAX_QUERY_STEPS = 2` in Python).
   - **Keyless Browser, IAM at Every Hop**: Eliminates **credential leakage and shared-secret drift** (Amplify SSR compute role signing SigV4 to API Gateway and invoking AgentCore Runtime via `runtime.grant_invoke_runtime`).
   - **Versioned Prompt, Fail Closed**: Eliminates **unreviewed prompt drift between git and production, and silent degradation** (Bedrock Prompt Management highest published version, ignoring `DRAFT`, failing closed with `AGT-2504`).
   - **Budget-Triggered Deny**: Eliminates **unbounded model spend** ($17 project stack-tag budget and $14 regional Nova token budget, each attaching an automatic IAM `Deny` policy at 100% actual spend).
   - **Two-Stack Boundary with Template Tests**: Eliminates **loss of retained state from compute iteration and template mistakes found at deploy time** (`FinopsAgentStatefulStack` holds only the 7-day L2 `Memory`; the precomputed tables are files in the Data image, not an S3 bucket. Proven offline in `tests/test_cdk_stack.py`).
4. **Two Pesky Bugs** — Brief prose intro + 2-row table (`Bug`, `Symptom`, `Root Cause`, `Fix`): (a) Nova 2 Lite cross-region inference profile IAM scoping; (b) `InvokeAgentRuntime` authorization failing on base ARN due to endpoint sub-resource dispatch.
5. **Conclusion & Bridge to Part 2** — Land the thesis, state the bounded scope, bridge to Part 2 (replacing baked DuckDB data with Daniel's own AWS account CUR 2.0 export to S3 Parquet, Glue, and Athena behind the same `run_query` seam), thank the authors of the AWS CDK best-practices blogs (Eric Z. Beard, Rico Huijbers, Pahud Hsieh, Nathan Peck), Stéphane Maarek & Frank Kane for their Udemy courses, and the AWS exam teams, closing with the community CTA.

---

## Part 2 — Own CUR, a smaller tool surface, and one surprise AgentCore capability

**Status**: ⏳ TBD. Decide the AgentCore increment at the start of the build.
**Thesis**: *The seam from Part 1 is what makes the data swap boring. Replacing baked DuckDB with Daniel's own CUR is also the moment to shrink the tool vocabulary, and to add one surprise AgentCore capability, so the post stays an AI engineering post.*
**Target persona**: B + C.
**Locked**: CUR 2.0 Data Exports to S3 Parquet, Glue Data Catalog, Athena with a per-query scan limit, `run_query` reimplemented behind the same Gateway tool, one source for dimensions and metrics (today they are copied across `agent.py`, `constants.py`, `data/constants.py`, `scripts/precompute_data.py`, and `run_finops_query.json`).
**Pick one AgentCore increment** (do not do all of them):
- Online evaluation of the two-query answers (AgentCore evaluation, or a small harness if the managed evaluator is the wrong shape).
- Per-session identity beyond the single `demo` actor, still IAM, no Cognito login wall unless the product needs one.
- Short-term memory as it is, plus one measured note on why long-term extraction stays off.

**CTA**: TBD.

---

## Part 3 — General lakehouse queries, then the `ml-platform` bridge

**Status**: ⏳ TBD. Engine and governance choices below are open until the build starts.
**Thesis**: *A tool that only knows one billing schema is still a demo. One general query surface over the lakehouse is the whole remaining product, and it is the same curated zone `ml-platform`'s Feast offline store should read.*
**Target persona**: C primary.
**Locked**: one query contract the agent already calls; the store can see more than the FinOps dice; Feast offline store pointed at that curated zone; one IAM or Lake Formation boundary for the agent role and the platform training role.
**Decide at build time**:
- Athena over S3 Parquet (already in Part 2) versus S3 Tables (Iceberg) only if table maintenance is the pain.
- Lake Formation as the data boundary, or IAM on the Glue table and S3 prefix if Lake Formation is more product than this demo needs.
- A second dataset versus teaching the same tool to query arbitrary catalog tables. Prefer the general tool. A second dataset is only a test of that tool.

**CTA**: TBD.

Exposing MLflow over MCP, and the rest of the platform surface, stays in the ML Engineering series. It is not a part of this one.

---

## Call to Action (Per Post)

| Part | Target persona for CTA | Tentative CTA |
|---|---|---|
| **1** | C + B | *For engineers and tech leads building on AWS: do you believe structured cloud certifications accelerate architectural judgment for production AI? And for already certified practitioners, how have those certifications concretely impacted your live systems?* |
| **2** | B + C | TBD with the AgentCore increment. |
| **3** | C | *Do your agent and your training jobs read the same curated tables, or two pipelines that happen to look similar?* |
