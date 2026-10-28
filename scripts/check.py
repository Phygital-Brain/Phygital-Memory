#!/usr/bin/env python3
"""Checks that the docs stay true. Run from anywhere, no installs needed:  python3 scripts/check.py

It checks:
- every link between Markdown files points to a file that exists, and every #anchor to a heading that exists
- no long dashes (em dashes, spaced en dashes) in the docs, workflows, .env.example, scripts and tests
- no three dots or ellipsis character in text people read (code blocks and `code` are skipped)
- every docs/*.md page has a row in the README's "All the guides" table (skipped until that heading exists)
- every environment variable in docs/settings.md is read by the code, and every one the code reads is in
  docs/settings.md and .env.example
- docs/tools.md names every MCP tool (@mcp.tool in core/phygital_memory/server.py) and says how many there are
- the version number is the same in CITATION.cff, core/pyproject.toml, the app (tauri.conf.json, Cargo.toml) and
  the top of CHANGELOG.md

tests/test_docs.py runs the same checks with pytest.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules", "target", "dist", "build", "release", ".venv", "web", ".signing"}
LINK = re.compile(r"\]\(([^)\s]+)\)|href=\"([^\"]+)\"|src=\"([^\"]+)\"")
EM, EN = chr(0x2014), chr(0x2013)
ELLIPSIS = chr(0x2026)
ENV = re.compile(r"PHYGITAL_MEMORY_[A-Z_]+[A-Z]")
CODE_DIRS = [ROOT / "core" / "phygital_memory", ROOT / "core" / "packaging", ROOT / "app" / "src-tauri" / "src"]
CODE_SUFFIXES = {".py", ".rs", ".js"}


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def markdown_files() -> list[Path]:
    """The docs people read: the top folder, docs/, .github/ and core/languages/. Not the Phygital Brain templates in
    core/phygital_memory/brain/ (they are notes the app writes for the person) and not built copies."""
    found = [*ROOT.glob("*.md"), *(ROOT / "docs").rglob("*.md"), *(ROOT / ".github").rglob("*.md"),
             *(ROOT / "core" / "languages").glob("*.md")]
    return sorted(set(found))


def prose(text: str) -> str:
    """The text without fenced code blocks and `inline code`, kept line for line."""
    text = re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


def slug(heading: str) -> str:
    """GitHub's anchor for a heading."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading.strip().lower())
    text = re.sub(r"[`*_]|<[^>]+>", "", text)
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def anchors(path: Path) -> set[str]:
    seen: dict[str, int] = {}
    out, in_code = set(), False
    for line in path.read_text("utf-8").splitlines():
        if line.startswith("```"):
            in_code = not in_code
        if in_code or not line.startswith("#"):
            continue
        s = slug(line.lstrip("#"))
        n = seen.get(s, 0)
        seen[s] = n + 1
        out.add(s if n == 0 else f"{s}-{n}")
    return out


def check_links() -> list[str]:
    problems = []
    for doc in markdown_files():
        text = re.sub(r"```.*?```", "", doc.read_text("utf-8"), flags=re.S)
        for m in LINK.finditer(text):
            target = next(g for g in m.groups() if g)
            if re.match(r"[a-z]+:", target) or target.startswith("//"):
                continue
            path, _, anchor = target.partition("#")
            dest = (doc.parent / path).resolve() if path else doc
            if not dest.exists():
                problems.append(f"{rel(doc)}: broken link {target}")
            elif anchor and dest.suffix == ".md" and anchor not in anchors(dest):
                problems.append(f"{rel(doc)}: no heading for {target}")
    return problems


def check_dashes() -> list[str]:
    files = markdown_files() + sorted((ROOT / ".github").rglob("*.yml"))
    files += [p for p in (ROOT / ".env.example", ROOT / "docs" / "images" / "README.txt") if p.exists()]
    files += sorted(p for d in ("scripts", "tests") for p in (ROOT / d).glob("*.py"))
    problems = []
    for f in files:
        for i, line in enumerate(f.read_text("utf-8").splitlines(), 1):
            if EM in line or f" {EN} " in line:
                problems.append(f"{rel(f)}:{i}: long dash")
    return problems


def check_three_dots() -> list[str]:
    problems = []
    for doc in markdown_files():
        for i, line in enumerate(prose(doc.read_text("utf-8")).splitlines(), 1):
            if "." * 3 in line or ELLIPSIS in line:
                problems.append(f"{rel(doc)}:{i}: three dots")
    return problems


def guides_table() -> str | None:
    """The README's "All the guides" section, or None while it has no such heading."""
    m = re.search(r"^#+ *All the guides *$(.*?)(?=^#+ |\Z)", (ROOT / "README.md").read_text("utf-8"), re.M | re.S)
    return m.group(1) if m else None


def check_guides_table() -> list[str]:
    table = guides_table()
    if table is None:
        return []
    listed = {Path(t.split("#")[0]).name for t in re.findall(r"\]\((?:\./)?docs/([^)\s]+)\)", table)}
    pages = sorted(p.name for p in (ROOT / "docs").glob("*.md") if p.name != "README.md")
    return [f"README.md: docs/{p} has no row in All the guides" for p in pages if p not in listed]


def code_env_vars() -> set[str]:
    names = set()
    for d in CODE_DIRS:
        for f in d.rglob("*"):
            if f.suffix in CODE_SUFFIXES and f.is_file() and not SKIP_DIRS & set(f.relative_to(ROOT).parts):
                names |= set(ENV.findall(f.read_text("utf-8", errors="replace")))
    return names


def check_settings() -> list[str]:
    in_docs = set(ENV.findall((ROOT / "docs" / "settings.md").read_text("utf-8")))
    in_code = code_env_vars()
    example = ROOT / ".env.example"
    in_example = set(ENV.findall(example.read_text("utf-8"))) if example.exists() else set()
    problems = [f"docs/settings.md: {n} is not read anywhere in the code" for n in sorted(in_docs - in_code)]
    problems += [f"docs/settings.md: {n} is read by the code but not listed" for n in sorted(in_code - in_docs)]
    problems += [f".env.example: {n} is missing" for n in sorted(in_code - in_example)]
    problems += [f".env.example: {n} is not read anywhere in the code" for n in sorted(in_example - in_code)]
    return problems


def mcp_tools() -> list[str]:
    server = (ROOT / "core" / "phygital_memory" / "server.py").read_text("utf-8")
    return re.findall(r"^@mcp\.tool\b.*\n(?:@.*\n)*(?:async )?def (\w+)", server, re.M)


def check_tools() -> list[str]:
    tools = mcp_tools()
    doc = (ROOT / "docs" / "tools.md").read_text("utf-8")
    problems = [f"docs/tools.md: tool `{n}` is missing" for n in tools if f"`{n}`" not in doc]
    rows = re.findall(r"^\| `(\w+)` \|", doc, re.M)
    problems += [f"docs/tools.md: `{n}` is not a tool in server.py" for n in rows if n not in tools]
    for n in re.findall(r"There are (\d+)|The (\d+) tools", doc):
        said = int(next(x for x in n if x))
        if said != len(tools):
            problems.append(f"docs/tools.md: says {said} tools, server.py has {len(tools)}")
    return problems


def check_versions() -> list[str]:
    def find(path: str, pattern: str) -> str | None:
        p = ROOT / path
        m = re.search(pattern, p.read_text("utf-8"), re.M) if p.exists() else None
        return m.group(1) if m else None

    versions = {
        "CITATION.cff": find("CITATION.cff", r"^version:\s*(\S+)"),
        "core/pyproject.toml": find("core/pyproject.toml", r'^version\s*=\s*"([^"]+)"'),
        "app/src-tauri/Cargo.toml": find("app/src-tauri/Cargo.toml", r'^version\s*=\s*"([^"]+)"'),
        "app/src-tauri/tauri.conf.json": json.loads((ROOT / "app/src-tauri/tauri.conf.json").read_text("utf-8")).get("version"),
        "CHANGELOG.md": find("CHANGELOG.md", r"^## (\d+\.\d+\.\d+)"),
    }
    versions = {k: v for k, v in versions.items() if v}
    return [f"version numbers disagree: {versions}"] if len(set(versions.values())) > 1 else []


CHECKS = [check_links, check_dashes, check_three_dots, check_guides_table, check_settings, check_tools, check_versions]

if __name__ == "__main__":
    problems = [p for check in CHECKS for p in check()]
    if guides_table() is None:
        print('Skipped: README.md has no "All the guides" heading yet, so the guides table was not checked.')
    if problems:
        print("\n".join(problems))
        print(f"\n{len(problems)} problem(s).")
        sys.exit(1)
    print(f"All checks passed: {len(markdown_files())} Markdown files, {len(mcp_tools())} tools, "
          f"{len(code_env_vars())} environment variables.")
