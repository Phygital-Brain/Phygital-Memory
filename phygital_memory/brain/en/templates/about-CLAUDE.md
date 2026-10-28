<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

This folder holds the core facts about {Name}. These notes are the source of truth for all other work.

## Files

| File | Purpose | Category tag |
|---|---|---|
| `me.md` | Who {Name} is, how they work, how they want their agent to work | `identity` |
| `biography.md` | {Name}'s story | `identity` |
| `goals.md` | Goals and priorities | `goals` |
| `business.md` | The business | `business` |
| `services.md` | Services, products, offers | `business` |
| `customers.md` | Who buys and how they find {Name} | `customers` |
| `pain-points.md` | Problems to solve | `customers` (or `goals` if {Name} doesn't sell) |
| `brand.md` | Voice, tone, words to use and avoid | `brand` |
| `tools.md` | Tools and where each kind of thing lives | `tools` |
| `cv.md` | Work history, education, press, awards | `career` |

## Info block (frontmatter)

Every file here (except this one) starts with:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Who {Name} is and how they want their agent to work."
---
```

- `type`: always `about`.
- `status`: `active`, or `outdated` when a fact is known to be stale.
- `updated`: the date the facts last changed. Not touched for typo or style edits.
- `tags`: `about`, then the file's category tag from the table above, then topic tags naming what the file covers (English, lowercase, hyphens). Update the topic tags when a section is added or removed.
- `description`: one sentence, in double quotes, saying what this file holds. Always the last line.

## Rules

- These files are the source of truth. Don't copy their content elsewhere: link to them.
- Compiled-truth format (root rule 17): current truth at the top, dated evidence below.
- {Name}'s full date of birth lives only in `me.md`. Never copy it or quote it in a reply. The birth year is fine.
- Create a new file only when a new topic needs one. Ask first (root rule 9).
- In a check-up, flag goals in `goals.md` that have no active project.
