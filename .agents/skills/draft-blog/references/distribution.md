# Distribution & Strategy Reference

Declarative setup, strategic cadence, and publishing workflow for Daniel Iván Parra Verde's engineering blog.

---

## 1. Strategy: SEO vs. LinkedIn Distribution

### The SEO Layer: Keep Clusters Separate, Bridge Them Once
Search engines reward topical focus per cluster, not breadth per site. Mixing ML-platform and DSPy/AI-engineering content dilutes both.
- **Two distinct clusters:** `ml-platform` posts link to each other; `ai-engineering` posts link to each other. Do not cross-link between them early on.
- **Consistent tagging:** Keep URL/slug structure and tags consistent within each cluster (e.g., `#mlops #aws #mlflow #feast` vs. `#dspy #aiengineering`). Do not blend the hashtag sets.
- **The Pillar Post:** Your Phase 5 convergence post is the pillar-in-waiting. That's the *only* post allowed to bridge both clusters. It becomes a massive backlink magnet ("the post that unifies MLOps and DSPy") once both clusters have enough depth to support the argument.

### The LinkedIn Layer: Interleave, Don't Sequence
On LinkedIn, you optimize for human attention span and your positioning as a job-seeker, not crawlers.
- **Persona coverage:** ML-platform posts pull in infra/MLOps hiring managers; AI-engineering posts pull in applied-AI hiring managers. Running both in parallel keeps you visible to both distinct hiring pools.
- **Personal branding:** Interleaving allows each post to carry a light throughline ("same operational discipline, different algorithm class"). This signals your convergence thesis early without needing to state it outright, compounding your personal brand week-over-week.

### Execution Tactics
- **Don't announce the convergence early:** Let each series stand alone for the first 2–3 posts. If people smell a "pitch" or a marketing arc, they disengage.
- **Signature post skeleton:** Reuse the same structure across both series (last-mile framing, deliverables bullet list, structural claim, closing question). This consistency acts as the glue that unifies your voice.
- **Comment-window discipline:** Being online and replying for the first 60 minutes after publishing is the single highest-leverage lever per post. It matters more than the exact day/hour.

---

## 2. 10-Week Interleaved Cadence

One post per week, alternating series. Publish on **Wednesdays, ~10–11am CST** (except Week 2 due to setup). 
This consistency trains LinkedIn's algorithm to distribute your content to the same audience repeatedly.

| Week | Series | Post / Topic |
|---|---|---|
| **1** | ML-Platform | Part 1 (already live) |
| **2** | AI-Engineering | Phase 1 — "The Imperative Mess" |
| **3** | ML-Platform | Part 2 — CQRS FastAPI layer |
| **4** | AI-Engineering | Phase 2 — Compliance Agent |
| **5** | ML-Platform | Part 3 |
| **6** | AI-Engineering | Phase 3 — Evaluation |
| **7** | ML-Platform | Part 4 |
| **8** | AI-Engineering | Phase 4 — Optimization |
| **9** | ML-Platform | Part 5 (monitoring/dashboard) |
| **10** | AI-Engineering | Phase 5 — Convergence (pillar moment) |

---

## 3. SEO & Canonical Syndication

When publishing across multiple platforms (`dev.to`, Medium, `danivpv.com`), always use a canonical URL pointing to your primary **Source of Truth** (`https://danivpv.com/blog/<slug>`). This passes 100% of the SEO ranking authority to your personal domain. Do not embed external article widgets on your site.

### Frontmatter Ground Truth Schema (Non-Negotiable)
Every draft (`blogs/<series-name>/<part-number>/blog.md`) MUST use this schema:
```yaml
---
canonical_url: https://danivpv.com/blog/<slug>
published: false
series: ML Engineering
part: 1
title: "Full Post Title Here"
tags: [mlops, aws, python, engineering]
date: YYYY-MM-DD
summary: "Concise 1-2 sentence executive summary for portfolio cards and SEO meta tags."
cover_image:
---
```

---

## 4. Platforms & One-Time Setup

| Platform | Role | Setup Notes |
|---|---|---|
| **dev.to** | Primary Automated Target | Cleanest REST API. `DEVTO_API_KEY` saved in env. |
| **X (Twitter)** | Long-form Practitioner Reach | Requires `X_API_KEY`, `X_ACCESS_TOKEN`, etc. with `tweet.write` and `article.write` scopes. |
| **Medium** | Secondary Canonical Host | Massive general tech reach. API access may require emailing Medium support for new accounts. |

---

## 5. Publishing Workflow (The Hub-and-Spoke Engine)

All scripts are in `blogs/scripts/` and push as **DRAFT** by default.

- **Hub:** `portfolio/content/blog/<slug>.md` (Indexed first, holds SEO authority).
- **Automated Spokes:**
  - `publish_devto.py`: Natively supports tables, syntax highlighting, canonical URLs.
  - `publish_medium.py`: Pre-processes Markdown into Medium-friendly HTML (converts tables to `<ul><li>` bulleted lists so data isn't garbled, maps headings to Medium DOM classes).
  - `post_x_article.py`: Pushes native Markdown via X API v2 `/2/articles`.

**Execution Commands:**
```bash
# 1. Push draft to dev.to
uv run python blogs/scripts/publish_devto.py blogs/ml-platform/1/<slug>.md

# 2. Push draft to X Articles
uv run python blogs/scripts/post_x_article.py blogs/ml-platform/1/<slug>.md

# 3. Post summary thread to X
uv run python blogs/scripts/post_x_thread.py blogs/ml-platform/1/thread.json

# 4. Push draft to Medium (Auto-converts Markdown tables)
uv run python blogs/scripts/publish_medium.py blogs/ml-platform/1/<slug>.md
```
