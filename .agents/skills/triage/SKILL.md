---
name: triage
description: >
  Rank and triage multiple job descriptions for Daniel Iván Parra Verde. Use when given a list of job postings to evaluate, or asked which jobs to prioritize or skip. Produces three output tiers: senior applied AI and MLOps roles to apply now, adjacent roles to evaluate and tailor, and roles to defer or skip.
---

# Job Description Triage

Read `_SKILL.md` for private candidate context (location, visa status, and role constraints). Do not copy that file into public drafts, commit messages, or git history.

## Triage Rules

1. **Anti-Targets.** Skip immediately: pure frontend, pure non-coding research, and roles that require an active US security clearance. Do not skip an AI or ML role only because the corporate HR posting lists an adjacent tech stack.

2. **Relocation and visa.** Check `_SKILL.md` for current location, acceptable relocation targets, and visa sponsorship requirements. Flag any visa requirement in the triage note.

3. **Stack flexibility.** Python and AWS experience transfers. Pivot to an adjacent cloud or language when the core work is applied AI, ML engineering, or ML platform engineering.

4. **Seniority bar.** The public persona is a Senior AI / MLOps Engineer. Prefer roles with architectural ownership: production LLM systems, evaluation, ML platforms, and cloud ML infrastructure. Skip junior tasking and roles that do not use that seniority.

5. **Blog signal.** Flag roles where an active or planned blog series (see `_SKILL.md`) would materially strengthen the application. Recommend deferring those until the post is live.

## Output Format

Three tiers, in this order:

**(a) Tier 1: Senior Applied AI / MLOps and Platform (apply now)**
- High architectural overlap with production LLM systems or AWS and cloud ML infrastructure.
- Brief fit assessment and the immediate next step (tailored draft, or apply as-is).

**(b) Tier 2: Adjacent / high-growth roles (evaluate, then tailor)**
- Strong ML engineering scope that needs a stack pivot or a narrower overlap.
- What to tailor, and whether the pivot is credible.

**(c) Tier 3: Defer or skip**
- Anti-targets (pure frontend, pure non-coding research, cleared roles), or roles to defer until a named blog series is live.
- One sentence on the reason.
