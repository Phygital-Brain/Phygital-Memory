<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Notes and preferences for the skills the agent uses, plus the Brain Keeper.

## Structure

```
Skills/{skill-name}/
  {skill-name}.md or SKILL.md   what the skill does
  notes.md                      {Name}'s voice and preferences for this skill
  references/                   examples and longer material
```

## Installed

| Skill | Folder | What it does |
|---|---|---|
| Brain Keeper | `brain-keeper/` | Daily tidy on its own, and a check-up when {Name} asks |
| Morning Brief | `morning-brief/` | A short plan of the day, on request or every work day |
| Import | `import/` | Brings in notes from other apps, with a plan {Name} approves first |
| Meeting Prep | `meeting-prep/` | A short brief before a call, from the brain's notes |
| Thinking Tools | `thinking/` | Challenge an idea, find patterns, find notes that disagree |
| Connected Apps | `connected-apps/` | Which apps the brain reads from, and the rules for them |
| No AI Slop | `no-ai-slop/` | The Writing Check: edits writing so it sounds human, or flags AI patterns (by Peter Yang, MIT License, never edited) |

## Rules

- One folder per skill, named in kebab-case.
- When a new skill is added, add a row to the table above.
- To add a skill or connect an app, check Phygital Brain's suggestions first: `suggested-skills/README.md` and `suggested-apps/README.md` through the Phygital Brain connector, or online at https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. If it's there, follow its page. When {Name} asks "what can I add to my brain?", show both lists, the ones that fit {Name}'s work first, and leave out apps already connected and skills already installed.
- A `SKILL.md` that came from someone else is never edited. To customise a skill, add `notes.md` in its folder.
- `brain-keeper/daily.md` is read by a scheduled task. Change it only to change what the daily run does, and keep it plain: no links, no callouts.
