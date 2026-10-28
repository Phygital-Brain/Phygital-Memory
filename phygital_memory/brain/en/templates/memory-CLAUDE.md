Knowledge that builds up over time: decisions, research, applications and the archive.

## Routing

| Content | Route to |
|---|---|
| Decision with reasoning, or a study of an outside thing (app, website, course, competitor) | `decisions/YYYY-MM-DD-{title}.md` |
| Research (market, trends, options) | `research/{topic}.md` |
| Applications: jobs, grants, awards, open calls (created on first use) | `applications/{name}/` |
| Competitor profiles (created on first use) | `competitors/{name}.md` |
| Money: invoices, taxes, payments. Private | `finances/` |
| Archived decisions | `archive/decisions/` |
| Finished or outdated research | `archive/research/` |
| Finished projects | `archive/{name}/` |
| Meeting notes | `decisions/` if a decision came out of it, otherwise that day's `Daily/` note. Suggest a meetings folder only when there are many. |

## Info block (frontmatter)

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type`: `decision`, `research`, `application`, `competitor`.
- `date`: the date the note was written.
- `status`: see below for decisions and applications. Everything else: `active` or `closed`.
- `tags`: the type, then the topic.
- Optional: `project`, `deadline`, `description` (one sentence, in double quotes, last line).

## Decision notes

Always include the why: who was involved, what prompted it, what trade-off was made. Use `> [!important]` for the decision itself and `> [!warning]` for known risks.

Decisions also carry `updated:` right after `date:`. `date` is when it was created, `updated` is the last time it was reviewed or changed.

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`: `open` (still being decided or worked on), `waiting` (on someone else), `paused`, `closed`.
- A decision whose `updated` is more than 30 days old needs review. The Brain Keeper flags it until {Name} keeps it, closes it or archives it (each one sets `updated` to that day).
- A decision moves to `archive/decisions/` only when {Name} says so.

## Applications

One folder per application: `applications/{name}/`, with a `README.md` holding the deadline, the link, the status and what was sent. Other files (answers, statement) sit next to it.

- `status`: `draft`, `submitted`, `accepted`, `rejected` or `withdrawn`.
- Keep answers in markdown. Large PDFs and slides stay outside the vault: summarise them in a note.

## Rules

- Research is neutral by default (root rule 23).
- Move superseded research to `archive/research/` instead of deleting it.
- `finances/` is private and listed in `.claudeignore`. Open it only when {Name} asks for a specific file (root rule 8).
