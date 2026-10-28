---
type: skill
status: active
tags: [brain-keeper, check-up]
---

The Brain Keeper's check-up: a full look at the whole brain, when {Name} asks. Nothing changes until {Name} says yes. (The daily tidy is in `daily.md`.)

Trigger: "check up my brain", "tidy my brain", "brain check-up", or the same in {Language}.

## 1. Look (change nothing yet)

Search the whole folder and list problems in these groups:

- **Broken links**: `[[links]]` pointing to notes that don't exist. Never fix these by creating a blank note: the real note may still be syncing (root rule 28).
- **Orphans**: notes no other note links to.
- **Empty or near-empty notes**, and leftover placeholders (`[name]`, `TBD`).
- **Wrong place**: files in the folder root (except `CLAUDE.md`, `.claudeignore`, `.backups/` and another agent's one-line rule file, like `AGENTS.md`), notes that don't match their folder's routing table.
- **Routing tables out of date**: a `CLAUDE.md` lists files or folders that don't exist, or misses ones that do (rows marked "created on first use" are fine).
- **Info blocks**: missing or incomplete, against the folder's `CLAUDE.md`. No `status:`, fewer than 2 `tags:`, a project note without `project:`, daily tags outside the fixed list.
- **Stale projects**: no update in 60+ days. Suggest a status update, `paused`, or archive.
- **Drifting goals**: goals in `About/goals.md` with no active project.
- **Decisions needing review**: `updated` more than 30 days ago and status not `closed`.
- **Old relationships**: `status: active` but `last-contact` more than 12 months ago. Suggest `dormant`.
- **Old tasks**: open tasks in `Daily/tasks.md` older than 30 days.
- **Duplicates**: the same facts in more than one note, or two notes for the same person or company.
- **Out-of-date truth**: About or Relationships pages where old updates bury the current state (root rule 17).
- **Rule conflicts**: rules in the root `CLAUDE.md` that contradict each other.
- **Privacy**: passwords, keys or private numbers sitting in ordinary notes (root rules 25 and 26). Report the note, never the value.
- **Writing**: em dashes and Writing Check patterns in notes.
- **New version**: compare this brain's version (the first line of the root `CLAUDE.md`) with the newest Phygital Brain. If you can browse the web, the newest is the latest release at https://github.com/Phygital-Brain/phygital-brain/releases/latest. If you can't, use the version of Phygital Brain installed in your agent, if you can see it. If you can't tell, skip this.

## 2. Report

A short list in plain words, grouped as above. For each problem: the note, what's wrong, the fix you suggest. Put the simple, safe fixes first (em dashes, missing tags, routing table rows).

If a newer version is out, start the report with one line. If your agent already has it: "A new version of Phygital Brain is out. Say 'Upgrade my second brain' to see what's new." If not: "A new version of Phygital Brain is out. Update it in your agent first, then say 'Upgrade my second brain'."

## 3. Fix only what's approved

Before the first fix, back up every file you'll change (Backups and Undo in the root `CLAUDE.md`).

Ask (with clickable choices when possible): **Fix all safe ones**, **Go one by one**, **Just the report**.

- Never delete or move without the link check and a clear yes (root rule 21).
- Archive instead of delete when in doubt.
- Log one line in today's `Daily/` note: what was checked and fixed.
