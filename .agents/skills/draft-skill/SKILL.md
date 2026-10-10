---
name: draft-skill
description: >
  Create, refine, or audit Agent Skills following the official agentskills.io specification. Use when asked to write a new skill, improve an existing SKILL.md, audit skill structure, optimize a skill description for triggering, or convert ad-hoc instructions into a proper skill. Produces spec-compliant skills for .agents/skills/<skill-name>/SKILL.md.
---

# Skill Writer

This skill produces Agent Skills that conform to the agentskills.io specification.

## Specification Quick Reference

**One skill = one folder = one focused capability.**

Each skill directory handles exactly one task or workflow. Never bundle multiple commands (e.g., /prep, /draft, /lead, /triage) into a single SKILL.md — create a separate folder for each.

**Canonical directory structure:**
```
.agents/skills/
└── <skill-name>/           # One capability per folder
    ├── SKILL.md            # Required: YAML frontmatter + instructions
    ├── scripts/            # Optional: executable scripts
    ├── references/         # Optional: docs loaded on demand
    ├── assets/             # Optional: templates, data files
    └── _SKILL.md           # Optional: private supplement (gitignored)
```

**Example — correct:**
```
.agents/skills/
├── prep/SKILL.md       # interview prep
├── draft/SKILL.md      # cover letters / CV bullets
├── lead/SKILL.md       # warm lead replies
└── triage/SKILL.md     # job description triage
```

**Example — wrong:**
```
.agents/skills/
└── career-assistant/SKILL.md   # defines /prep, /draft, /lead, /triage — too broad
```

**Frontmatter fields:**
- `name` (required): lowercase, hyphens only, 1-64 chars, must match directory name
- `description` (required): 1-1024 chars, describes what + when to use
- `compatibility` (optional): environment requirements (tools, platform, Python version)
- `license`, `metadata`, `allowed-tools` (all optional)

**Progressive disclosure — the loading order:**
1. `name` + `description` only → loaded at agent startup for all skills
2. Full `SKILL.md` body → loaded when skill activates
3. `references/`, `scripts/`, `assets/` files → loaded on demand only when needed

**SKILL.md body rules:**
- Under 500 lines
- Tell the agent *when* to load each reference file, not just that they exist
- Use gotchas sections for non-obvious environment-specific facts
- Favor procedures over declarations; provide defaults not menus

## Workflow

### Creating a new skill

1. Ask for (or infer from context): skill name, purpose, commands/workflows, private vs. public content, and whether scripts are needed.
2. Draft `SKILL.md` with proper frontmatter. Write the body:
   - Gotchas section first (environment-specific surprises)
   - Command summaries with explicit `references/<file>.md` links + trigger conditions
   - Keep body under 500 lines
3. Create `references/<command>.md` for each command with mechanistic execution steps.
4. If private context is needed, create `_SKILL.md` alongside `SKILL.md` — note that this file should be gitignored and is a non-standard private extension.
5. If scripts are needed, create them in `scripts/` and document usage in `SKILL.md`.

### Refining an existing skill

1. Read the current `SKILL.md`. Check:
   - Does `name` match the directory name?
   - Is `description` 1-1024 chars? Does it say both *what* and *when*?
   - Is the body under 500 lines?
   - Are `references/` files pointed to with explicit trigger conditions?
2. Apply fixes. Do not rewrite content that is already correct.

### Auditing skill structure

Run a directory listing and check against the canonical structure above. Flag: missing `SKILL.md`, `name` mismatch, `description` too short/vague, body over 500 lines, reference files that are never mentioned in `SKILL.md`.

## Description Quality Checklist

A good `description` field:
- Uses imperative phrasing: "Use when..." not "This skill does..."
- Focuses on user intent, not internal mechanics
- Lists trigger keywords explicitly (including indirect ones)
- Is concise: a few sentences to a short paragraph
- Is under 1024 characters

## Gotchas

- The `name` field must exactly match the parent directory name — validation will fail otherwise.
- `_SKILL.md` is not part of the official spec. It is a private extension pattern that works when the file is gitignored. Never reference it in public docs.
- References files are loaded **on demand** — tell the agent the exact condition for loading each one ("read X if Y happens"), not just "see references/ for details."
- `scripts/` files must be self-contained or clearly document their dependencies.
