# Workspace Rules

## This Repo Is Special

`danivpv/danivpv` is a [GitHub profile repository](https://github.com/danivpv/danivpv). The root `README.md` renders directly on Daniel's public GitHub profile page — it is the first thing recruiters, hiring managers, and collaborators see. Treat every edit to `README.md` with the same care as a public product page.

The repo also doubles as a private career workspace. 
- **`_AGENTS.md`**: Global private candidate context (metrics, timeline, salary anchors).
- **`_TODO.md`**: Active application pipeline, priorities, and interview stages.
- **`applications/`**: Contains generated cover letters, lead tracking, and interview notes.

All of these are `.gitignore`d. **Never leak their contents into `README.md`, public docs, or git commit messages.**

## PDF Compilation

All document compilation is handled by `Makefile`. Never invoke `pandoc` or `xelatex` directly.

| Use case | Command |
|---|---|
| CV by role (from `tex/<role>.tex` → `pdfs/`) | `make cv role="<role>"` |
| CV by company (from `applications/<company>/cv.tex`) | `make cv company="<company>"` |
| Cover letter (`.md` → `.pdf`) | `make letter company="<company>" role="<role>"` |
| Clean build artifacts | `make clean` |

Core primitives (`tex-to-pdf`, `md-to-pdf`) exist for direct use when needed.

## Skills

All task-specific execution context lives in `.agents/skills/`. Load the relevant skill before acting. Each `SKILL.md` holds public instructions; each `_SKILL.md` holds private context (gitignored).

| Skill | Trigger |
|---|---|
| `draft` | Write cover letters, CV bullets, recruiter replies, warm leads |
| `interview-prep` | Prepare for an interview or research a company |
| `triage` | Rank and triage a batch of job descriptions |
| `draft-blog` | Write or refine a blog post |
| `plan-blog-series` | Structure or update a blog series plan |
| `draft-skill` | Create or audit an Agent Skill |
| `session-recovery` | Recover an interrupted session |

## Global Rules

- **Underscore Prefix (`_`)**: Any file prefixed with `_` (e.g., `_draft.md`, `_SKILL.md`) is private and gitignored. Only unprefixed files are public.
- **No Hard Line Breaks**: Do not hard-wrap text at arbitrary character limits. Write paragraphs as single continuous lines and let the markdown reader handle visual wrapping.
- No em dashes (`—`) in any output. Replace with commas, periods, or parentheses.
- Never invent metrics. Pull all verifiable numbers from `draft/_SKILL.md`.
