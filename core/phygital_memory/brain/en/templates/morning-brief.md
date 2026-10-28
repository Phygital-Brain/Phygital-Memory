---
type: skill
status: active
tags: [morning-brief, planning]
---

A short plan for the day. Two modes: **Brief** (on request) and **Schedule** (every work day).

## Brief

Trigger: "morning brief", or the same in {Language}.

1. Read `Daily/tasks.md`, the latest daily note, the "Status and next step" of every project with `status: active`, and decisions with status `open` or `waiting`.
2. If a calendar is connected, read today's events.
3. Reply in 6 short lines at most:
   - Today's 3 most important things, each with a `[[link]]` to its note.
   - What {Name} is waiting on from others.
   - One decision to make, if any.
   - Today's events, if a calendar is connected.
4. Don't write any file. If {Name} reacts with new info, save it by root rule 9.

## Schedule

Trigger: "set up my morning brief", or the same in {Language}.

1. Ask the time (click options: 7:00, 8:00, 9:00, 10:00), on {Name}'s work days. Skip the question if the setup already set the time.
2. Create a scheduled task in the agent app, running on this folder, with this prompt:

   > Open my second brain folder. Read `Skills/morning-brief/morning-brief.md` and give me my morning brief.

3. If scheduled tasks aren't available, tell {Name} to say "morning brief" when they start the day.
