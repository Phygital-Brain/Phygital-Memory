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
# Phygital Brain's rules name another notes app and the cloud drive's history; in Phygital Memory both lines say this
# app instead: [the line above the note syntax list, the last backups bullet] per language
OWN = Path(__file__).resolve().parent / "brain_memory.json"
PEOPLE = ("Clients", "Collaborators", "Team", "Partners")
# The About pages and their category tag (About/CLAUDE.md)
ABOUT = {"me": "identity", "biography": "identity", "goals": "goals", "business": "business", "services": "business",
         "customers": "customers", "pain-points": "customers", "brand": "brand", "tools": "tools", "cv": "career"}

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


def _for_memory(text: str, lang: str) -> str:
    """The root rules with Phygital Memory's two lines in place of the ones meant for other apps."""
    try:
        own = json.loads(OWN.read_text())
    except (OSError, ValueError):
        return text
    notes, versions = own.get(lang) or own["en"]
    lines = text.split("\n")
    for i, l in enumerate(lines):
        if l.startswith("- **") and "[[" in l:   # the note syntax list; the sentence above it names the app
            j = i - 1
            while j > 0 and not lines[j].strip():
                j -= 1
            if not lines[j].startswith("#"):
                lines[j] = notes
            break
    for i, l in enumerate(lines):
        if ".backups/YYYY" in l:   # the backups paragraph; its last bullet is the cloud drive's history
            j = i + 1
            while j < len(lines) and not lines[j].startswith("- "):
                j += 1
            while j + 1 < len(lines) and lines[j + 1].startswith("- "):
                j += 1
            if j < len(lines) and lines[j].startswith("- "):
                lines[j] = versions
            break
    return "\n".join(lines)


ADAPTING = re.compile(r"<!-- ADAPTING.*?-->\n+", re.S)


def _adapt(text: str, where: str, picks: dict) -> str:
    """Do what each file's ADAPTING note asks, so the AI has nothing left to adapt: every folder and skill is made,
    so only the client rules and the people folders' notes depend on the answers."""
    text = ADAPTING.sub("", text, count=1)
    if where == "CLAUDE.md" and not picks.get("clients"):
        lines = [l for l in text.split("\n") if not re.match(r"3[12]\. ", l)]   # rules 31, 32: client messages
        text = "\n".join(l.replace("33", "31").replace("34", "32") if l.startswith("<!--") and "33" in l else l for l in lines)
    m = re.match(r"Relationships/(\w+)/CLAUDE\.md$", where)
    if m:
        kind = PEOPLE.index(m.group(1))
        def intro(mt):   # {Clients: "…" / Collaborators: "…" / …}: this folder's line, without its label and quotes
            parts = mt.group(1).split(" / ")
            one = parts[kind] if kind < len(parts) else parts[0]
            return one.split(":", 1)[-1].strip().strip("\"“”„«»「」『』'").strip()
        text = re.sub(r"^\{(.+)\}$", intro, text, count=1, flags=re.M)
        if kind:   # only Clients keeps the Leads section, the last one
            text = text[:text.rindex("\n## ")].rstrip() + "\n"
    return text


def plan(picks: dict, lang: str) -> list[str]:
    """The folders the memory gets, in its language: all of them, so the AI never has to make one."""
    paths = _names(lang).get("paths", {})
    return [_local(f, paths) for f in FOLDERS + [f"Relationships/{p}" for p in PEOPLE] + ["Skills/morning-brief"]]


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
    rules += [("relationships-subfolder-CLAUDE.md", f"Relationships/{p}/CLAUDE.md") for p in PEOPLE]
    rules.append(("morning-brief.md", "Skills/morning-brief/morning-brief.md"))
    for tpl, where in rules:
        text = _template(lang, "templates", tpl)
        if text is not None:
            text = _adapt(text, where, picks)
            if where == "CLAUDE.md":   # the Brain Keeper's part of the root rules comes with it
                text = _for_memory(text.rstrip() + "\n\n" + (_template(lang, "keeper", "root-CLAUDE-section.md") or ""), lang)
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
        line=picks.get("first_line") or "Phygital Memory set up."))
    # The About pages, written by the app from the answers (picks["pages"]: {me: {desc, tags, body}, goals: ...}):
    # every one is made, with "To add" where only the person or their AI can say more
    me = loc("About/me.md")
    for key, page in (picks.get("pages") or {}).items():
        if key not in ABOUT or not isinstance(page, dict):
            continue
        tags = ", ".join(["about", ABOUT[key]] + [re.sub(r"[^a-z0-9-]", "", re.sub(r"\s+", "-", str(x).strip().lower())) for x in page.get("tags", [])][:4])
        desc = str(page.get("desc", "")).replace('"', "'")
        put(loc(f"About/{key}.md"), f"---\ntype: about\nstatus: active\nupdated: {day}\ntags: [{tags}]\ndescription: \"{desc}\"\n---\n\n"
            + str(page.get("body", "")).strip() + f"\n\n## Evidence\n\n- {day}: {page.get('evidence') or 'from the setup questions.'}\n")
    # A note for each project and person typed in: the README a project starts with, a profile per person
    todo = str(picks.get("todo") or "To add.")[:40]
    clean = lambda v, n: re.sub(r"[\x00-\x1f/\\:*?\"<>|#^\[\]]", "", str(v or "")).strip().lstrip(".").strip()[:n]
    for p in (picks.get("projects") or [])[:30]:
        title, what = clean(p.get("name"), 80), clean(p.get("what"), 300)
        slug = "-".join(w[:1].upper() + w[1:] for w in title.split())
        if not slug:
            continue
        folder = loc("Projects") + "/" + slug
        try:
            memory.make_folder(folder)
        except Exception:
            pass
        put(f"{folder}/README.md", f"---\ntype: project\nstatus: active\nproject: {slug}\ncreated: {day}\nupdated: {day}\n"
            f"tags: [{slug.lower()}, project]\ndescription: \"{what or title}\"\n---\n\n## {picks.get('h_what') or 'What it is'}\n\n{what or todo}\n\n"
            f"## {picks.get('h_status') or 'Status and next step'}\n\n{todo}\n")
    kinds = {"clients": ("Clients", "client"), "collaborators": ("Collaborators", "collaborator"), "team": ("Team", "team"), "partners": ("Partners", "partner")}
    for p in (picks.get("people") or [])[:60]:
        who, what = clean(p.get("name"), 80), clean(p.get("what"), 300)
        folder, kind = kinds.get(p.get("kind"), kinds["clients"])
        if who:
            put(loc(f"Relationships/{folder}/{who}.md"), f"---\ntype: {kind}\nstatus: active\nlast-contact:\ntags: [relationship, {kind}]\n"
                f"description: \"{what or who}\"\n---\n\n## {picks.get('h_who') or 'Who they are'}\n\n{what or todo}\n\n"
                f"## {picks.get('h_contacts') or 'Contacts'}\n\n{todo}\n\n## {picks.get('h_work') or 'Work together'}\n\n{todo}\n")
    return {"made": made, "me": me, "language": lang_name}


def finish_ask(picks: dict, lang_name: str, rules: str, me: str = "About/me.md") -> str:
    """The one AI task left after setup: add detail. The app already made everything from the person's answers."""
    return (f"Make my Phygital Memory more complete. The app already set it all up from my answers: every folder, "
            f"the rules, the About pages, and a note for each project and person I typed in. First read {rules} "
            f"(the rules). Then read the About pages, projects and people. Where a page is thin or says \"To add\", "
            f"ask me for the details, a few questions at a time with click options where you can. If I gave links, "
            f"read them first and ask only what they don't answer. Add details; keep what I wrote. Write in {lang_name}.")[:1990]
