"""The licences of the Rust crates inside the Mac window (Tauri and what it uses): only the ones compiled into the app
for this Mac, not build or test tools. Writes one text file.

Run: python3 packaging/rust_licences.py ../app/src-tauri OUT.txt
"""
import json
import re
import subprocess
import sys
from pathlib import Path

crate_dir, out = Path(sys.argv[1]), Path(sys.argv[2])
meta = json.loads(subprocess.run(["cargo", "metadata", "--format-version", "1", "--filter-platform", "aarch64-apple-darwin"],
                                 cwd=crate_dir, capture_output=True, text=True, check=True).stdout)
pkgs = {p["id"]: p for p in meta["packages"]}
nodes = {n["id"]: n for n in meta["resolve"]["nodes"]}
root = meta["resolve"]["root"]

seen, todo = set(), [root]   # walk only normal dependencies: what ends up in the app
while todo:
    nid = todo.pop()
    for d in nodes[nid]["deps"]:
        if any(k["kind"] is None for k in d["dep_kinds"]) and d["pkg"] not in seen:
            seen.add(d["pkg"])
            todo.append(d["pkg"])


def texts(p) -> str:
    here = Path(p["manifest_path"]).parent
    files = sorted(f for f in here.iterdir() if f.is_file() and re.match(r"(licen[cs]e|copying|notice|copyright)", f.name, re.I))
    return "\n\n".join(f.read_text(errors="replace").strip() for f in files)


parts = []
for pid in sorted(seen, key=lambda i: (pkgs[i]["name"].lower(), pkgs[i]["version"])):
    p = pkgs[pid]
    body = texts(p)
    parts.append(f"{p['name']} {p['version']}, {p.get('license') or 'see the text below'}\n\n"
                 + (body or f"(The crate ships no licence file. Its licence is {p.get('license') or 'named in its project'}.)"))
mpl = [f"{pkgs[i]['name']} {pkgs[i]['version']}" for i in sorted(seen, key=lambda i: pkgs[i]["name"]) if "MPL" in (pkgs[i].get("license") or "")]
note = (f"The crates under MPL-2.0 ({', '.join(mpl)}) are used unchanged. Their source code is on crates.io.\n\n" if mpl else "")
out.write_text("MAC WINDOW: TAURI AND THE RUST CRATES IT USES\n============================================\n\n" + note
               + "\n\n---\n\n".join(parts) + "\n")
print(f"{len(parts)} crates, {sum('ships no licence file' in x for x in parts)} without a licence file")
