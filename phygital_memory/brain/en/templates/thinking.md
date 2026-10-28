---
type: skill
status: active
tags: [thinking, review]
---

Thinking tools: your agent uses {Name}'s own notes to test an idea, find patterns, and find notes that disagree. None of them change a note unless {Name} asks.

## Challenge my idea

Trigger: "challenge my idea", "push back on this", "what am I missing?", or the same in {Language}.

1. Restate the idea in one line, and ask once if it's unclear.
2. Search the brain for evidence: past decisions in `Memory/decisions/` (and their reasons and results), research in `Memory/research/`, what clients and partners said in `Relationships/`, goals in `About/goals.md`, pain points in `About/pain-points.md`, and the last 60 days of daily notes.
3. Reply with three short parts:
   - **For it:** up to 3 points from the notes, each with its `[[link]]`.
   - **Against it:** up to 3 points from the notes, each with its `[[link]]`. Include a past decision that went the other way, if there is one.
   - **Questions to answer first:** up to 3.
4. Use only what's in the notes, plus plain reasoning. Say "nothing in your notes" when there's nothing. Don't decide for {Name}.
5. If {Name} decides, offer to write a decision note.

## What patterns do you see?

Trigger: "what patterns do you see?", "what keeps coming up?", "review my last month", or the same in {Language}.

1. Read the daily notes from the last 30 days (or the period {Name} names), and `Daily/tasks.md`.
2. Count what repeats: people, projects, tags (`problem`, `money`, `meeting`...), blockers, tasks that move from day to day, and anything {Name} mentioned more than three times.
3. Reply with up to 5 patterns, each with how often it came up, two or three `[[links]]` to the days, and one plain question ("Three calls with the printer slipped. Want a fixed slot for them?").
4. Note what didn't come up but matters: goals in `About/goals.md` with no mention in the period.

## Find contradictions

Trigger: "find contradictions", "what disagrees in my brain?", or the same in {Language}.

1. Compare facts that should match: About pages against newer decisions, prices in `About/services.md` against recent quotes in daily notes and projects, people's details across notes, project status against the last daily mentions.
2. For each one: both notes as `[[links]]`, the two lines that disagree, and which one looks newer.
3. Suggest a fix for each, and ask (click options when possible): `Fix them one by one` · `Just the list`. Fixing follows root rule 9, with a backup first.
