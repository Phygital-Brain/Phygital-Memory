"""What AI apps did with the notes: which app, when, and what (searched, read, changed...). In memory only; a
folder's lines go away when it locks. The app shows it behind the small AI light."""
import time

seen: dict[str, float] = {}       # app name -> last time it did anything
log: list[dict] = []
MAX = 300


UNDO_MAX = 50
UNDO_BYTES = 20_000_000
undo: dict[str, dict] = {}       # undo id -> {folder, path, before (text or None for a new note), after (sha256)}


def add(app: str, folder_id: str, what: str, detail: str = "", path: str = "", undo_id: str = "") -> None:
    log.append({"t": time.time(), "app": app, "folder": folder_id, "what": what, "detail": detail[:200], "path": path,
                "undo": undo_id})
    del log[:-MAX]
    keep = {a["undo"] for a in log if a.get("undo")}
    for k in list(undo):
        if k not in keep:
            del undo[k]
    # Caps: the last UNDO_MAX AI changes, and at most UNDO_BYTES of old text held in memory. Oldest go first.
    while len(undo) > UNDO_MAX or sum(len(u["before"] or "") for u in undo.values()) > UNDO_BYTES:
        del undo[next(iter(undo))]


def forget(folder_id: str) -> None:
    log[:] = [a for a in log if a["folder"] != folder_id]
    for k in [k for k, u in undo.items() if u["folder"] == folder_id]:
        del undo[k]

