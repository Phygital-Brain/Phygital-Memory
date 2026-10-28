Each project is a folder that grows as information arrives. `README.md` is the one entry point.

## Routing

| Content | Route to |
|---|---|
| Overview, status, deadline, next steps | `Projects/{name}/README.md` |
| {Name}'s working notes | `Projects/{name}/notes/{topic}.md` |
| Research | `Projects/{name}/research/{topic}.md` |
| Brief, spec, requirements | `Projects/{name}/briefs/{name}.md` |
| Drafts, scripts, written content | `Projects/{name}/drafts/{name}.md` |
| Ideas | `Projects/{name}/ideas/{name}.md` |
| Feedback | `Projects/{name}/feedback/{name}.md` |
| Images and media | `Projects/{name}/assets/` |
| Old material from this project | `Projects/{name}/archive/` |

Folder names are lowercase with hyphens, no number prefixes (`research/`, not `01-Research/`). A project can add its own folder when none of these fit.

## README layout

1. Info block (below), with a `description`.
2. `## What it is`: one or two lines, linked to [[goals]].
3. `## Status and next step`: where it stands, the next step.
4. `## How it runs`: only if something automatic writes here (a scheduled task, a script).
5. `## Where things are`: only once subfolders exist. A small table linking each one.

## Info block (frontmatter)

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`: `project` (the README, which also has `created`, `updated` and `description`), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused` or `done`. The README's status is the project's status.
- `project`: the project folder name.
- `tags`: the project, then the type.

## Rules

- A new project is just a `README.md`. Create subfolders only when content arrives that needs them, and link them from the README.
- The README is the index. Don't repeat subfolder content in it.
- No `CLAUDE.md` inside a project. Rules for one project go in "Rules per project" below.
- Include `project:` in the info block of every related note.
- A finished project moves to `Memory/archive/{name}/` only when {Name} says so.
- Every project should serve a goal in [[goals]]. In a check-up, flag goals with no project and projects with no goal.

## Rules per project

<!-- Rules for one project only. Add a line when a project needs its own rule: "**Project-Name:** the rule." -->
