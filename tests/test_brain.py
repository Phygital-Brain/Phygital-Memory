"""Phygital Brain inside a memory, built from clicks with no AI (phygital_memory/brain.py): the folders in the
brain's language, every placeholder filled, the person's own notes never written over, a second run changes nothing,
and the finishing task names the brain's real About note. A throwaway memory, no server, no Keychain.

Run: uv run python test_brain.py
"""
import re
import shutil
import tempfile
from pathlib import Path

from phygital_memory import brain
from phygital_memory.memory import Memory

ok = []


def check(cond, what):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what)


tmp = Path(tempfile.mkdtemp(prefix="pm-brain-"))
try:
    check(len(brain.languages()) >= 41, f"{len(brain.languages())} brain languages ship with the app")
    picks = {"people": ["Clients", "Team"], "brief": True, "labels": {"You are": "Freelancer or creator"}}
    for lang, about, clients in (("en", "About", "Relationships/Clients"), ("pt-BR", "Sobre", "Contatos/Clientes")):
        Memory.create(tmp / lang, "test password 1")
        m = Memory(tmp / lang)
        m.unlock("test password 1")
        m.save("Mine.md", "my own note")
        m.save(f"{about}/me.md", "what I wrote about me")
        r = brain.build(m, picks, lang, "Ana", "Europe/Lisbon")
        files = {f["path"] for f in m.list_files()}
        check({"CLAUDE.md", ".claudeignore", clients, f"{about}/CLAUDE.md"} <= files, f"{lang}: folders and rules in the brain's language")
        left = [p for p in files if p.endswith(".md") and re.search(r"\{(Name|Time zone|Language|lang)\}", m.read(p))]
        check(not left, f"{lang}: every placeholder filled ({left[:2]})")
        check(m.read("Mine.md") == "my own note" and m.read(f"{about}/me.md") == "what I wrote about me",
              f"{lang}: the person's own notes are never written over")
        check(not brain.build(m, picks, lang, "Ana", "Europe/Lisbon")["made"], f"{lang}: a second run changes nothing")
        check(f"{about}/me.md" in brain.finish_ask(picks, r["language"], "CLAUDE.md", r["me"]), f"{lang}: the task names the real About note")
        m.lock()
finally:
    shutil.rmtree(tmp)
print(f"\n{sum(ok)}/{len(ok)} passed")
