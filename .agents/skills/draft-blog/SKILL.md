---
name: draft-blog
description: >
  Draft or refine a blog post for Daniel Iván Parra Verde's engineering blog at danivpv.com/blog. Use when asked to write, draft, refine, or improve a blog post, section, hook, or intro. Applies strict voice rules (no em-dashes, concrete over vague, one thesis per post, ~9 min read target) across the ML Platform and AI Engineering series.
---

# Write Blog Post

Read `_SKILL.md` for private authorial context (voice rules, anti-patterns, audience strategy). Read `references/voice_and_thesis.md` when making structural decisions about hook, pattern sections, conclusion, or series arc framing.

## Gotchas

- **NEVER use em-dashes** (`—` or `--`). Use commas, colons, semicolons, or a new sentence.
- **Never cite `#` ASCII comment blocks** as code. Show actual executable code.
- **Never blindly append** sections when refining. Audit structure top-to-bottom.
- **Never link to floating branches** (`main`). Link to specific commit hashes.
- **Target ~9 min read** (~1,800 words). Aggressively cut to this target. Save removed content to `../../blogs/<series-name>/<part-number>/_cuts.md` so it is available for future deep-dive posts — never discard it.
- Write output to `../../blogs/<series-name>/<part-number>/<slug>.md` where `<slug>` is the exact string in `canonical_url`. The filename must be the slug, not `blog.md`.
- Portfolio integration path is `../../portfolio/content/blog/<slug>.md` (not `portfolio_v2`).

## Inputs (ask for any missing)

1. Series name (`ml-platform` or `ai-engineering`)
2. Part number and working title
3. What to write: `hook`, `intro`, `section: <name>`, `close`, or `full-draft`
4. Any additional constraints or focus areas

## Execution Workflow

1. **Update target repo docs** — Review and update architecture decision logs (PRD, road-to-prod) in `../../<series-name>/docs/` to reflect latest commits.

2. **Update series plan** (`../../blogs/<series-name>/plan.md`) — Ensure thesis is precise, CTA works natively on LinkedIn, title sells, hook is authoritative. Proactively ask the user questions to find the best hook.

3. **Copy reference docs** — Copy timestamped PRD, road-to-prod, and deployment logs from the live repo into `../../blogs/<series-name>/<part-number>/` to freeze ground truth at time of writing.

4. **Draft the blog** to `../../blogs/<series-name>/<part-number>/<slug>.md`.

5. **Post structure (canonical)** — Title → Opening Hook (1-2 paragraphs) → `## Maturing / Personal Scar` (why this matters, first person) → `## The Platform / What Was Built` (diagram + subsystem table, no deep-dive code) → `## Core Architectural Patterns` (4-6 patterns in prose, each labeled with its **failure class eliminated**, progressive disclosure links, no inline code blocks) → `## Two Pesky Bugs` (table only, 2 bugs max, brief prose intro) → `## Conclusion` (thesis landing + series bridge + CTA) → blockquote author bio → `### Appendix` (source code, decision log, bug log, key docs).

6. **Pattern paragraph format** — Each pattern follows this exact structure: `**Pattern Name.** Eliminates **[failure class].** [Prose explanation.] See [link to pinned commit file] and [official docs link].`

7. **Cutting aggressively** — When content exceeds the ~9 min target, save removed subsystem deep-dives, code sections, and trade-off discussions to `_cuts.md` in the part folder. These become source material for future deep-dive posts.

8. **Author bio** — Use a `>` blockquote (not `*italic*`) so it renders with the accent-colored left border in the portfolio renderer.

9. **Code snippets** — Explain what the design choice reveals, not how to run it. Numbers come only from `plan.md` memorabilia and verified values — never fabricated.

10. **Refinement (`--refine`)** — Never blindly append. Audit top-to-bottom. Merge complementary ideas. Maintain exactly one conclusion section.

11. **Portfolio integration** (when finalized) — Copy to `../../portfolio/content/blog/<slug>.md`. Filename must match the slug from `canonical_url` in frontmatter exactly.

## Distribution

Read `references/distribution.md` when preparing to publish or set up distribution channels.
