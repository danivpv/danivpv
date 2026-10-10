---
name: plan-blog-series
description: >
  Structure or update a blog series plan for Daniel Iván Parra Verde's engineering blog. Use when asked to plan a new series, outline future posts, update a series plan, or decide how many parts a topic should span. Produces a structured outline saved to blogs/<series-name>/plan.md.
---

# Plan Series

Read `_SKILL.md` for private authorial context (voice rules, audience strategy).

## Inputs (ask for any missing)

1. Series name and working title
2. Target audience persona
3. Number of parts and overall arc

## Execution Workflow

1. **Answer the 5 pre-writing questions**:
   - Who is the reader persona?
   - What is the one thing to remember from each post?
   - What action should the reader take after reading?
   - What credibility anchors ground this series?
   - What is the call to action?

2. **Read the relevant codebase** PRD and road-to-prod to understand what is currently built vs. planned:
   - `../../<series-name>/docs/ml-platform-prd.md`
   - `../../<series-name>/docs/road-to-prod.md`

3. **Draft the structured outline** for each part: thesis, outline sections, source material references, target persona.

4. **Create or update** `../../blogs/<series-name>/plan.md`. Flag all open items explicitly.
