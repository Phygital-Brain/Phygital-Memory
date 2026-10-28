"""Phygital Brain inside a memory: the folders, rules and first notes, built from a few clicks, no AI needed.

The files come from Phygital Brain (brain/, kept in step by scripts/brain_sync.py), in the brain's language. What
only an AI can do well (adapting the rules to the person, asking the rest, writing About) is left as one AI task:
the ADAPTING notes in the files say what, and the task points the AI at them.
"""
from __future__ import annotations

import json
import re
import shutil
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent / "brain"
PEOPLE = ("Clients", "Collaborators", "Team", "Partners")

# (template, where it goes in the brain); paths are the brain's English names, turned into the language's below
RULES = [("root-CLAUDE.md", "CLAUDE.md"), ("about-CLAUDE.md", "About/CLAUDE.md"), ("projects-CLAUDE.md", "Projects/CLAUDE.md"),
         ("daily-CLAUDE.md", "Daily/CLAUDE.md"), ("memory-CLAUDE.md", "Memory/CLAUDE.md"),
         ("library-CLAUDE.md", "Library/CLAUDE.md"), ("skills-CLAUDE.md", "Skills/CLAUDE.md"),
         ("relationships-CLAUDE.md", "Relationships/CLAUDE.md"), ("claudeignore.txt", ".claudeignore"),
         ("import.md", "Skills/import/import.md"), ("meeting-prep.md", "Skills/meeting-prep/meeting-prep.md"),
         ("thinking.md", "Skills/thinking/thinking.md"), ("connected-apps.md", "Skills/connected-apps/connected-apps.md")]
KEEPER = [("check-up.md", "Skills/brain-keeper/check-up.md"), ("daily.md", "Skills/brain-keeper/daily.md"),
          ("queue.md", "Skills/brain-keeper/queue.md")]
FOLDERS = ["About", "Daily", "Projects", "Memory/decisions", "Memory/research", "Memory/finances", "Memory/archive",
           "Library", "Relationships", "Skills/brain-keeper", "Skills/no-ai-slop", "Skills/import", "Skills/meeting-prep",
           "Skills/thinking", "Skills/connected-apps"]


def languages() -> list[list[str]]:
    try:
        return json.loads((HERE / "languages.json").read_text())
    except (OSError, ValueError):
        return [["en", "English"]]


def _names(lang: str) -> dict:
    try:
        return json.loads((HERE / lang / "strings.json").read_text())
    except (OSError, ValueError):
        return {}


def _local(path: str, paths: dict) -> str:
    """An English brain path in the language's names (About/me.md -> Sobre/me.md)."""
    return "/".join(paths.get(p, p) for p in path.split("/"))


def _template(lang: str, part: str, name: str) -> str | None:
    for code in (lang, "en"):
        f = HERE / code / part / name
        if f.is_file():
            return f.read_text()
    return None


def plan(picks: dict, lang: str) -> list[str]:
    """The folders this brain will have, in its language: what the window shows while it builds."""
    paths = _names(lang).get("paths", {})
    folders = list(FOLDERS) + [f"Relationships/{p}" for p in PEOPLE if p in picks.get("people", [])]
    if picks.get("brief"):
        folders.append("Skills/morning-brief")
    return [_local(f, paths) for f in folders]


def build(memory, picks: dict, lang: str, name: str, tz: str, today: time.struct_time | None = None) -> dict:
    """Make the brain in an unlocked memory. Never writes over a note that's already there. Returns
    {made: [paths], me: the About note's path, language: its name}."""
    info = _names(lang)
    paths, lang_name = info.get("paths", {}), (info.get("language") or {}).get("name", "English")
    loc = lambda p: _local(p, paths)
    fill = lambda s: (s.replace("{Name}", name or "you").replace("{Time zone}", tz or "")
                      .replace("{Language}", lang_name).replace("{lang}", lang))
    made = []

    def put(rel: str, text: str) -> None:
        try:
            if rel.endswith(".md"):
                memory.save(rel, text, new=True)   # new=True: a note already there stays as the person left it
            elif not any(f["path"] == rel for f in memory.list_files()):
                memory.put_file(rel, text.encode())   # .claudeignore, a LICENSE: kept as they are, not as notes
            else:
                return
            made.append(rel)
        except Exception:
            pass

    for f in plan(picks, lang):
        try:
            memory.make_folder(f)
        except Exception:
            pass   # there already
    rules = list(RULES)
    rules += [("relationships-subfolder-CLAUDE.md", f"Relationships/{p}/CLAUDE.md") for p in PEOPLE if p in picks.get("people", [])]
    if picks.get("brief"):
        rules.append(("morning-brief.md", "Skills/morning-brief/morning-brief.md"))
    for tpl, where in rules:
        text = _template(lang, "templates", tpl)
        if text is not None:
            if where == "CLAUDE.md":   # the Brain Keeper's part of the root rules comes with it
                text = text.rstrip() + "\n\n" + (_template(lang, "keeper", "root-CLAUDE-section.md") or "")
            put(loc(where), fill(text))
    for tpl, where in KEEPER:
        text = _template(lang, "keeper", tpl)
        if text is not None:
            put(loc(where), fill(text))
    for f in sorted((HERE / "bundled" / "no-ai-slop").glob("*")):
        if f.is_file():
            put(loc(f"Skills/no-ai-slop/{f.name}"), f.read_text())

    t = today or time.localtime()
    day = time.strftime("%Y-%m-%d", t)
    put(loc(f"Daily/{day}.md"), "---\ntype: daily\ndate: {d}\nday: {wd}\nweek: W{w:02d}\nmonth: {m}\nstatus: active\ntags: [daily]\n---\n\n{line}\n".format(
        d=day, wd=time.strftime("%A", t), w=int(time.strftime("%V", t)), m=time.strftime("%B", t),
        line=picks.get("first_line") or "Phygital Brain set up."))
    me = loc("About/me.md")
    about = "\n".join(f"- {k}: {v}" for k, v in (picks.get("labels") or {}).items())
    put(me, "---\ntype: about\nstatus: active\nupdated: {d}\ntags: [about, identity]\n---\n\n{name}\n\n{about}\n\n## Evidence\n\n- {d}: set up as a Phygital Brain.\n".format(
        d=day, name=name or "", about=about))
    return {"made": made, "me": me, "language": lang_name}


def finish_ask(picks: dict, lang_name: str, rules: str, me: str = "About/me.md") -> str:
    """The one AI task that finishes the brain: what the app couldn't do without an AI."""
    said = "; ".join(f"{k}: {v}" for k, v in (picks.get("labels") or {}).items())
    return (f"Finish setting up my Phygital Brain. The app already made the folders, the rules and today's note. "
            f"First read {rules} (the brain's rules). Then: 1) follow every ADAPTING note in the brain's files and "
            f"remove it; 2) ask me, a few at a time with click options where you can, what you still need: what I do "
            f"and my strengths, my current projects, the people I work with, when I work; 3) write {me} and the "
            f"other About files from my answers, and make a note for each project and person I name. Write everything "
            f"in {lang_name}. What I picked in the app: {said}.")[:1990]
