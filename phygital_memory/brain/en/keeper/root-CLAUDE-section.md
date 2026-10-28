## Brain Keeper

The Brain Keeper looks after this brain in two ways. Its files are in `Skills/brain-keeper/`.

- **Every day, on its own:** a scheduled run of `Skills/brain-keeper/daily.md`. Small safe fixes, a report, and a list of things only {Name} can decide in `Skills/brain-keeper/queue.md`.
- **Check-up, when {Name} asks:** "check up my brain", "tidy my brain", or the same in {Language}: read `Skills/brain-keeper/check-up.md` and follow it.
- "run the brain keeper", or the same in {Language}: read `Skills/brain-keeper/daily.md` and do a run now.
- "run the brain keeper in the cloud", or the same in {Language}: follow Step 3, "In the cloud", of the Phygital Brain `brain-keeper` skill.
- "pause the brain keeper", or the same in {Language}: create `Skills/brain-keeper/PAUSED.md` with one line: today's date and "Paused by {Name}". Confirm in one line.
- "resume the brain keeper", or the same in {Language}: delete `Skills/brain-keeper/PAUSED.md` (no link check needed for this file). Confirm in one line.
- "what did the brain keeper do", or the same in {Language}: read the latest reports in `Skills/brain-keeper/reports/` and explain them in plain words. Point out anything unexpected.
- To change what the daily run does, {Name} asks in chat. Edit `daily.md` only then.
- The check-up skips `Skills/brain-keeper/reports/` and `queue.md` when looking for orphan notes.
