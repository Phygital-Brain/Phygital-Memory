<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

{Name}'s daily journal. One file per day: `YYYY-MM-DD.md`. Open tasks live in `tasks.md`.

## Info block (frontmatter)

Every daily note starts with this block. No exceptions.

```yaml
---
type: daily
date: 2026-10-13
day: Tuesday
week: W42
month: October
status: active
tags: [daily, meeting]
---
```

- `type`: always `daily`.
- `date`: the note's date, `YYYY-MM-DD`.
- `day`: day of the week, in English (Monday, Tuesday...).
- `week`: ISO week number, `WNN`.
- `month`: month, in English (January, February...).
- `status`: `active` while the day is open, `completed` once it's 2 or more days old.
- `tags`: always `daily`, plus any from this fixed list that happened that day. Never invent other tags.
  - `problem`: something broke or went wrong
  - `clients`: client work or client contact
  - `meeting`: a call or meeting
  - `money`: invoices, payments, taxes, investments
  - `research`: research done or findings
  - `decision`: {Name} decided something
  - `travel`: {Name} was travelling
  - `personal`: health, life, anything outside work

## Rules

- Dates follow root rule 30 (computer's time zone first, then {Time zone}).
- Whoever creates the note (your agent or a scheduled task) writes the info block first. A note without one gets it added at the top the next time it's edited.
- No `# YYYY-MM-DD` title heading. The file name is the title.
- The daily note holds the day's current state: one tidy document per day, sections updated in place, never a pile of repeated entries.
- Session logs: bold headline plus 1 or 2 sentences, people and projects as `[[wikilinks]]`, details go in the linked note.
- Today's note holds today's activity only. Open tasks from earlier days go to `tasks.md`. Never copy them forward.
- When you create today's note, look at the notes from 2, 3 and 4 days ago. Any still `status: active` become `completed`, and get tags from the fixed list for what clearly happened that day. Don't look further back.

## tasks.md

Open tasks that don't belong to a project. Project tasks go in that project's README ("Status and next step"). Created on first use:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Open

- [ ] 2026-10-13: Send the invoice to [[Ana]]

## Done

- [x] 2026-10-12: Book the dentist (done 2026-10-13)
```

- Newest open tasks at the top, with the date they were added.
- When a task is done, tick it, add the date it was done, and move it to `## Done`.
- Done tasks older than 30 days can be removed (ask first, root rule 9).
