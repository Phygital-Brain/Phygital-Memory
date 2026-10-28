"""Setting up a memory from clicks, no AI (phygital_memory/brain.py): every folder in its language, every
placeholder filled and every ADAPTING note done, the About pages written, the person's own notes never written over,
a second run changes nothing. A throwaway memory, no server, no Keychain.

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
    pages = {k: {"desc": f"the {k} page", "tags": ["Setup Test"], "body": f"{k} from the answers\n\nTo add."} for k in brain.ABOUT}
    picks = {"work": True, "pages": pages}
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
        texts = {p: m.read(p) for p in files if p.endswith(".md") or p.endswith("CLAUDE.md")}
        check(not [p for p, x in texts.items() if "ADAPTING" in x], f"{lang}: every ADAPTING note done by the app")
        made_about = [p for p in files if p.startswith(f"{about}/") and p.endswith(".md") and p != f"{about}/CLAUDE.md"]
        check(len(made_about) == len(brain.ABOUT), f"{lang}: all {len(brain.ABOUT)} About pages there ({len(made_about)})")
        goals = next(p for p in made_about if "goals from the answers" in m.read(p))
        check("tags: [about, goals, setup-test]" in m.read(goals) and 'description: "the goals page"' in m.read(goals), f"{lang}: About info block written")
        subs = [p for p in files if re.match(rf"{clients.split('/')[0]}/[^/]+/CLAUDE\.md$", p)]
        check(len(subs) == 4 and not [p for p in subs if "{" in m.read(p).split("\n## ")[0]], f"{lang}: 4 people folders, each with its own intro")
        heads = sorted(m.read(p).count("\n## ") for p in subs)
        check(heads[-1] == heads[0] + 1 and heads.count(heads[0]) == 3, f"{lang}: only Clients keeps its Leads section")
        check(re.search(r"^31\. ", m.read("CLAUDE.md"), re.M), f"{lang}: client rules kept when there are clients")
        m.lock()
    Memory.create(tmp / "solo", "test password 1")
    m = Memory(tmp / "solo")
    m.unlock("test password 1")
    brain.build(m, {"personal": True}, "en", "Ana", "")
    rules = m.read("CLAUDE.md")
    check(not re.search(r"^3[12]\. ", rules, re.M) and "Number them 31, 32" in rules, "no clients: rules 31 and 32 left out, numbering follows")
    files = {f["path"] for f in m.list_files()}
    check("Relationships/Clients" not in files and "Relationships" in files and "Projects" in files, "personal: the simple skeleton, no people folders")
    ask = brain.finish_ask({"personal": True}, "English", "Home", "Ana")
    check(brain.GUIDE in ask and "phygital-memory tools" in ask and '"Home"' in ask and "personal life" in ask and "Ana" in ask,
          "the message for the AI: the guide on GitHub, the memory's tools, its name, what it's for")
    m.lock()
finally:
    shutil.rmtree(tmp)
for code, _ in brain.languages():
    sub = brain._adapt(brain._template(code, "templates", "relationships-subfolder-CLAUDE.md"), "Relationships/Team/CLAUDE.md", {})
    check("{Clients" not in sub and "ADAPTING" not in sub, f"{code}: Team folder note has its own intro line")
for code, _ in brain.languages():
    text = brain._for_memory(brain._template(code, "templates", "root-CLAUDE.md"), code)
    check("Baald" not in text and text.count("Phygital Memory") == 2, f"{code}: the rules name Phygital Memory, not Baalda or the cloud drive")
print(f"\n{sum(ok)}/{len(ok)} passed")

