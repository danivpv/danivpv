# AI Engineering Series Plan

**GitHub repo**: TBD — own standalone repo (`danivpv/ai-engineering` or similar). Not an extension of `ml-platform`.
**Local repo**: TBD — will live at `../ai-engineering/` relative to `danivpv/` once created.
**Status**: Phase 1 **ACTIVE** — execution starting (August 2026). The series has pivoted to focus purely on declarative AI engineering with DSPy and enterprise governance, dropping the LLMOps infrastructure focus.
**Format**: 5 independent posts, culminating in a migration/unification post once the thesis is established in isolation.
**Primary audience**: Persona C (senior engineers, tech leads, ML directors, hiring managers who make architectural decisions). Persona B (senior SWEs entering the AI/ML space) benefits as a secondary reader — the systems argument and governance discussion give them language to defend AI investments in meetings.

---

## Series-Level Thesis

> *"The imperative prompt engineering era is over. Building reliable AI systems is no longer about chaining API calls—it is about defining metrics, compiling declarative execution graphs, and tracking lineage. This series treats a DSPy program as what it truly is: an uncompiled machine learning model. By focusing on evaluation, optimization, and MLflow governance, we build a Vertical AI Agent that enterprises can actually trust, and prove that AI Engineering is just classical ML Engineering with a new algorithm."*

### The Convergence Arc (Foreshadowing)

Every post in this series is written with the final post in mind. The final post argues:

> *An AI agent is a new kind of algorithm. Like a scikit-learn model, it has: a training set (the evaluation dataset), a metric (the DSPy evaluation score), an optimizer (MIPROv2 or BootstrapFewShot), a checkpoint (the compiled DSPy program versioned in MLflow), and a serving runtime (FastAPI). The operational infrastructure is not new. The algorithm is.*

### Why a Separate Repo

The AI Engineering series **starts as a completely independent repository** with its own MLflow tracking server and minimal deployment stack. 
- The thesis that AI models need the same infrastructure as classical ML models is *argued across the series*, not assumed. 
- 5 posts build the AI engineering system independently. The final post asks: what would it take to merge this into `ml-platform`? 

---

## Arc Overview: Building Vertical AI Agents for the Enterprise

| Phase | Focus | Core Tools | Status |
|---|---|---|---|
| **1** | The Imperative Mess vs. The Declarative Graph | DSPy Signatures, MLflow Tracing | Planning |
| **2** | The "Lawful Good" Compliance Agent | DSPy Retrievers (ColBERTv2), Pydantic Schemas | TBD |
| **3** | The Engine of Trust (Evaluation) | DSPy Metrics, LLM-as-a-Judge | TBD |
| **4** | Continuous Optimization | DSPy MIPROv2 / GEPA | TBD |
| **5 (final)** | The ML-Platform Convergence | MLflow Model Registry, existing `ml-platform` | TBD |

---

## Phase 1 — The Imperative Mess vs. The Declarative Graph

**Status**: **ACTIVE — starting execution (August 2026)**.
**Thesis**: *"Writing prompts is a liability. An untyped chain of LLM calls cannot be audited, versioned, or trusted. By moving to a declarative execution graph, we gain the one thing enterprise AI is missing: traceability."*

### Goal
Establish the foundational thesis by rewriting a fragile imperative script into a robust DSPy program. Introduce MLflow tracing from day one so every reasoning step is logged.

### Deliverables
- A fragile LangChain or vanilla Python script demonstrating the "imperative mess."
- Rewrite using DSPy Signatures (`InputField`, `OutputField`) and basic modules (`Predict`, `ChainOfThought`).
- Integration of `mlflow.dspy.autolog()` to capture traces automatically.
- Own MLflow tracking server (separate from `ml-platform`'s MLflow).
- **Dependabot** configured from day one to manage supply chain risks.

---

## Phase 2 — The "Lawful Good" Compliance Agent

**Status**: TBD.
**Thesis**: *"Enterprise RAG is not just retrieval—it is about enforcing strict output schemas and maintaining data lineage. If you cannot prove which document generated which claim, you cannot deploy to production."*

### Goal
Build a Vertical AI Agent for a Compliance / Legal Audit use case (directly targeting YC's "Compliance and Audit" RFS). 

### Deliverables
- Integration of a retrieval module (e.g., `ColBERTv2` or similar).
- Contextual modules ensuring the agent grounds its answers in the retrieved text.
- Pydantic schema validation built into the DSPy signatures to enforce structured outputs.
- MLflow tracing used to prove data lineage (showing the exact retrieved chunk that led to a specific boolean decision).

---

## Phase 3 — The Engine of Trust (Evaluation)

**Status**: TBD.
**Thesis**: *"You cannot optimize what you cannot measure. Human vibe-checks do not scale. Building an automated evaluation pipeline is the single most important engineering task in AI."*

### Goal
Build the testing harness that will allow the agent to improve. Define strict metrics and use LLMs as judges to evaluate the agent's performance on the Compliance use case.

### Deliverables
- Creation of a golden evaluation dataset for the compliance use case.
- Implementation of custom DSPy metrics (`answer_exact_match`, `SemanticF1`).
- Building an LLM-as-a-Judge pipeline within DSPy to evaluate groundedness and hallucination rates.
- Logging baseline evaluation runs to MLflow to establish the "before" state.

---

## Phase 4 — Continuous Optimization

**Status**: TBD.
**Thesis**: *"Frameworks like DSPy write better prompts than humans. Once you have a metric and a dataset, prompt engineering becomes an optimization problem solved by compute, not by intuition."*

### Goal
Run the evaluation pipeline through advanced DSPy optimizers to compile a highly performant program. Show how the framework rewrites its own internal logic.

### Deliverables
- Running the program through `BootstrapFewShot` and `MIPROv2` or `COPRO`.
- Demonstration of the framework bootstrapping its own few-shot examples and rewriting task instructions.
- Tracking the optimization curve in MLflow (comparing the compiled program's metric against the Phase 3 baseline).
- Outputting the final "compiled" program ready for deployment.

---

## Phase 5 (Final) — The ML-Platform Convergence

**Status**: TBD.
**Thesis**: *"An AI agent is a new kind of algorithm. Like a classical ML model, it has a training dataset, a metric, an optimizer, a checkpoint, and a serving runtime. The operational substrate is the same. It belongs in the ML platform."*

### Goal
Unify the AI Engineering series with the classical ML Platform series. Prove that a DSPy program is just another model checkpoint.

### Deliverables
- The conceptual argument written out explicitly: AI model lifecycle ↔ classical ML model lifecycle.
- Saving the compiled DSPy program via `mlflow.dspy.log_model()`.
- Registering the program in the MLflow Model Registry.
- Deploying the agent using the existing `ml-platform` infrastructure (FastAPI serving).

---

## Open Items

- [ ] Repo name decision: `danivpv/ai-engineering` vs. more specific branding.
- [ ] Agent dataset for Phase 2: identify a good open-source legal or compliance dataset to use.
- [ ] Series name/brand: "AI Engineering" sufficient or "Declarative AI Engineering"?
