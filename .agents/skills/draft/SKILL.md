---
name: draft
description: >
  Draft any written career output for Daniel Iván Parra Verde: cover letters, short-form application answers, CV bullet points, warm lead replies to recruiters, and LinkedIn outreach messages to founders or hiring managers. Use when asked to write or improve a cover letter, answer an application form question, tailor a CV bullet, reply to a recruiter, or write an outreach message. Enforces the canonical LaTeX cover letter format, persona-specific link strategy, and the no-em-dash rule.
---

# Career Draft

Read `_SKILL.md` for private candidate context (role anchors, verified metrics, compensation rules). Never leak this data into public files or git history.

## Gotchas

- **NO EM DASHES** (`—`). Replace with commas, periods, or parentheses. No exceptions.
- Never state salary expectations unprompted. Wait until directly asked.
- NEVER invent unverified skills. Restrict to verified achievements in `_SKILL.md`.
- Experience claim: exactly **+4 years** Python/ML.
- Cover letter file path: `../../applications/<company>/<role>_cover_letter.md`
- PDF export: `make letter company="<company>" role="<role>"`

## Cover Letters

Canonical template: `../../applications/deloitte/data_scientist_cover_letter.md`

```yaml
geometry: margin=1in
fontsize: 11pt
fontfamily: mathpazo
```

LaTeX structure: `\begin{flushleft}` sender block → `\vspace{1em}` → `\begin{flushleft}` addressee block → `\vspace{1em}` → `\textbf{Re: <Role Title>}` → body →
`Sincerely,` + `\vspace{1em}` + `\textbf{Daniel Iván Parra Verde}`

Writing structure:
1. **Hook** — 1 sentence on a concrete production fact (metric, scale, tech)
2. **Body** — 2-3 paragraphs matching JD requirements, verifiable metrics, named technologies.
   Every paragraph needs at least one metric.
3. **Stack pivot** — 1 sentence acknowledging a different cloud/tool if required
4. **CTA** — 1 sentence call to action

## Role-Specific Anchors

- **Data Science** → Kuona (forecasting, price elasticity analysis)
- **AI Engineering** → Entropía (end-to-end prototype in production) + Arkham
  (optimized reliability, 0-1 capabilities). Do NOT claim "fully scalable agent."
- **ML Engineering** → Arkham (scaling AWS trainings, SDK integration for FDE teams)

## Warm Lead & Recruiter Replies

Output: 4-5 sentences OR 3-4 bullets with line breaks for skimmability.
Write the draft title at the top. Mirror the exact job title from the JD in the opening hook.

**Link strategy by persona:**

| Persona | Link |
|---|---|
| **Founders/Startups** | `github.com/danivpv/ml-platform` + `danivpv.com/blog` |
| **MLOps/Platform Recruiters** | `danivpv.com/blog` |
| **Agency Recruiters** | `danivpv.com` + `github.com/danivpv` |

Weave ONE domain URL naturally into the closing sentence. Never use robotic link dumps.

Categorization:
- **Founders** — 1 concrete metric matching their stack, agree to call
- **Agency** — tight matrix (+4 yrs ML, 2-wk availability), 0 for unknowns, no rate upfront
- **Academic/Unpaid** — politely decline

## Other Output Types

- **Form answers**: concise, direct, within character limits
- **CV bullets**: active verbs, quantifiable impact, zero line-wrap, 1-page XeLaTeX constraint
- **Email replies**: Keep concise and direct. End with a simple sign-off line (e.g. "Warm regards,"). Never generate candidate signature, title, phone, links, or contact blocks; the candidate uses an automated client signature with verified Credly badges.
