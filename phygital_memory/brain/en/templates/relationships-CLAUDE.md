<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Clients/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Everyone {Name} works with: one note per person or organisation.

## Subfolders

| Folder | Who goes there |
|---|---|
| `Clients/` | People and companies {Name} delivers work for |
| `Collaborators/` | Creative partners, mutual exchange, no money involved |
| `Team/` | People who work with or for {Name} (freelancers, assistants) |
| `Partners/` | Organisations {Name} is building a presence with (press, venues, platforms) |

## Where a new lead goes

- A first contact with no real brief yet: a line under `## New` in `Clients/_Leads.md` (created on first use).
- A reply that says "maybe later": a line under `## Keep warm` in `Clients/_Leads.md`.
- A real brief, call or quote in progress: a client note `Clients/{client-name}.md` with `status: prospect`.

When a lead moves up a step, move it to the next home and remove it from the previous one.

## Info block (frontmatter)

Every note here (except `CLAUDE.md` files and `_Leads.md`) starts with:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "One plain sentence on who they are and the relationship with {Name}."
---
```

- `type`: `client`, `collaborator`, `team` or `partner`.
- `status`: `active` (work or contact in the last 12 months), `prospect` (talking, never worked together), `dormant` (no contact for 12+ months), `closed` (ended for good).
- `last-contact`: the most recent month with real contact or work, `YYYY-MM`. Leave it empty if unknown.
- `tags`: `relationship`, then the type, then 2 to 5 topic tags (industry, country, kind of work), English, lowercase, hyphens.
- `description`: one sentence, in double quotes. Always the last line.
- Optional: `aliases` (other names used for them), `project` (current project).

## Rules

- **No duplicates.** Before creating a note, search for the name and its variants (accents, short names, brand vs company name). If a note exists, use it and add the new spelling to `aliases`. Never make a second note for the same person or company.
- **Compiled-truth format** (root rule 17): who they are and the current state at the top, dated history below.
- **Keep it current.** When {Name} has real contact with someone (an email, a call, delivered work), update `last-contact` to this month, and `status` if it changed.
- **Contact people** at a company (an agent, a manager, an editor) are plain text inside the company note, never `[[links]]`, and get no note of their own. To mention them elsewhere, link the company: `[[Company Name|Contact Name]]`.
- **Private details** (phones, emails, home addresses) live only in that person's or company's note. Never copy them into daily notes or other notes.
- Link people from projects and daily notes with `[[wikilinks]]`.
- Create a new subfolder only when a new kind of relationship appears. Ask first.
