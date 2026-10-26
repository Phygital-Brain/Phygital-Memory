"""What AI apps did with the notes: which app, when, and what (searched, read, changed...). In memory only; a
folder's lines go away when it locks. The app shows it behind the small AI light."""
import time

seen: dict[str, float] = {}       # app name -> last time it did anything
log: list[dict] = []
MAX = 300


def add(app: str, folder_id: str, what: str, detail: str = "", path: str = "") -> None:
    log.append({"t": time.time(), "app": app, "folder": folder_id, "what": what, "detail": detail[:200], "path": path})
    del log[:-MAX]


def forget(folder_id: str) -> None:
    log[:] = [a for a in log if a["folder"] != folder_id]


handed: list[dict] = []   # notes the person handed to their AI from the app: {folder, path, t}
