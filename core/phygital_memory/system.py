"""What differs between Mac, Windows and Linux, in one place. The rest of the app asks here and never checks which
system it runs on. On a Mac everything works as it always has.

- state_dir(): the app's own folder (lists, keys kept on this computer, shares, Syncthing).
- open_path(), reveal(), open_url(): open a file or folder, show it in the file manager, open a web page.
- pick_folder(), pick_files(), pick_save(): the system's own pickers. The person chooses; nothing comes from the
  page, and a name is never written into a command (it travels as an argument or in the environment).
- first_name(): the account's first name, to greet the person.
- trash_dir(): where a whole memory moved off this computer goes, so it can come back.
- exe(): a program's file name (".exe" on Windows).
- beside(): a file the built app keeps next to the engine (rclone, Syncthing, the licences).
"""
from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
from pathlib import Path

MAC = sys.platform == "darwin"
WINDOWS = sys.platform == "win32"
LINUX = sys.platform.startswith("linux")
NAME = "Phygital Memory"


def state_dir() -> Path:
    if os.environ.get("PHYGITAL_MEMORY_STATE"):
        return Path(os.environ["PHYGITAL_MEMORY_STATE"]).expanduser()
    if MAC:
        return Path.home() / "Library" / "Application Support" / NAME
    if WINDOWS:
        return Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming") / NAME
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "phygital-memory"


def exe(name: str) -> str:
    return name + ".exe" if WINDOWS else name


def beside(name: str) -> Path:
    """A file next to the built engine. The Mac app carries a second engine for Intel Macs one folder down
    (server/intel); it shares the folder above's tools and licences."""
    here = Path(sys.executable).parent
    return here / name if (here / name).exists() or here.name != "intel" else here.parent / name


def trash_dir() -> Path:
    if os.environ.get("PHYGITAL_MEMORY_TRASH"):
        return Path(os.environ["PHYGITAL_MEMORY_TRASH"]).expanduser()
    if MAC:
        return Path.home() / ".Trash"
    if LINUX:   # the freedesktop trash that file managers show
        return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "Trash" / "files"
    return state_dir() / "Moved away"   # Windows' Recycle Bin can't be filled by moving a folder into it


def _run(args: list[str]) -> None:
    try:
        subprocess.run(args, capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        pass


def open_path(path: str | Path) -> None:
    """Open a file in its own app, or a folder in the file manager."""
    p = str(path)
    if MAC:
        _run(["open", p])
    elif WINDOWS:
        os.startfile(p)   # noqa: the path is the app's own (a note's file or a memory's folder)
    else:
        _run(["xdg-open", p])


def reveal(path: str | Path) -> None:
    """Show a file or folder selected in the file manager."""
    p = Path(path)
    if MAC:
        _run(["open", "-R", str(p)])
    elif WINDOWS:
        _run(["explorer", f"/select,{p}"])
    else:
        _run(["xdg-open", str(p.parent if p.is_file() else p)])


def open_url(url: str) -> None:
    if MAC:
        _run(["open", url])
    else:
        webbrowser.open(url)


def first_name() -> str:
    try:
        if WINDOWS:
            full = os.environ.get("USERNAME", "")
        else:
            import pwd
            full = (pwd.getpwuid(os.getuid()).pw_gecos or "").split(",")[0] or pwd.getpwuid(os.getuid()).pw_name
    except (KeyError, OSError):
        full = ""
    return full.split(" ")[0]


# ---------- the system's own pickers ----------

def _osascript(lines: list[str], *args: str) -> subprocess.CompletedProcess:
    """AppleScript with names passed as arguments (item 1 of argv...), never written into the script itself, so a
    folder or note name can't break out of its quotes."""
    script = ["on run argv", *lines, "end run"]
    return subprocess.run(["osascript", *sum((["-e", line] for line in script), []), *args], capture_output=True,
                          text=True, timeout=600)


def _powershell(script: str, **env: str) -> subprocess.CompletedProcess:
    """A Windows dialog. What the person sees (the prompt, a start folder) goes in the environment, never into the
    script, so a name can't break out of its quotes."""
    # $owner: a hidden window that stays on top. The engine has no window of its own, so a dialog without an owner
    # opens behind the app, where nobody sees it (seen on Windows 11).
    full = ("Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::EnableVisualStyles(); "
            "$owner = New-Object System.Windows.Forms.Form -Property @{TopMost = $true; ShowInTaskbar = $false}; " + script)
    return subprocess.run(["powershell", "-NoProfile", "-STA", "-Command", full], capture_output=True, text=True,
                          timeout=600, env={**os.environ, **{f"PM_{k.upper()}": v for k, v in env.items()}},
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))   # no console flashing up


def _linux_dialog(zenity: list[str], kdialog: list[str]) -> subprocess.CompletedProcess | None:
    import shutil
    for tool, args in (("zenity", zenity), ("kdialog", kdialog)):
        if shutil.which(tool):
            return subprocess.run([tool, *args], capture_output=True, text=True, timeout=600)
    return None


def pick_files(prompt: str) -> list[str]:
    """Several files at once."""
    if MAC:
        out = _osascript(["set picked to choose file with prompt (item 1 of argv) with multiple selections allowed",
                          'set out to ""', "repeat with f in picked", "set out to out & POSIX path of f & linefeed",
                          "end repeat", "return out"], prompt)
    elif WINDOWS:
        out = _powershell("$d = New-Object System.Windows.Forms.OpenFileDialog; $d.Title = $env:PM_PROMPT; "
                          "$d.Multiselect = $true; if ($d.ShowDialog($owner) -eq 'OK') { $d.FileNames -join \"`n\" }",
                          prompt=prompt)
    else:
        out = _linux_dialog(["--file-selection", "--multiple", "--separator=\n", f"--title={prompt}"],
                            ["--getopenfilename", str(Path.home()), "--multiple", "--separate-output", "--title", prompt])
    return [p for p in out.stdout.splitlines() if p.strip()] if out and out.returncode == 0 else []


def pick_save(prompt: str, name: str) -> str | None:
    """Where to put an exported file. The dialog itself asks before replacing one."""
    if MAC:
        out = _osascript(["return POSIX path of (choose file name with prompt (item 1 of argv) default name (item 2 of argv))"],
                         prompt, name)
    elif WINDOWS:
        out = _powershell("$d = New-Object System.Windows.Forms.SaveFileDialog; $d.Title = $env:PM_PROMPT; "
                          "$d.FileName = $env:PM_NAME; $d.OverwritePrompt = $true; "
                          "if ($d.ShowDialog($owner) -eq 'OK') { $d.FileName }", prompt=prompt, name=name)
    else:
        out = _linux_dialog(["--file-selection", "--save", "--confirm-overwrite", f"--title={prompt}", f"--filename={name}"],
                            ["--getsavefilename", str(Path.home() / name), "--title", prompt])
    return (out.stdout.strip() or None) if out and out.returncode == 0 else None


def pick_folder(prompt: str, start: str | None = None) -> str | None:
    """A folder. start: where the picker opens."""
    start = start if start and Path(start).is_dir() else None
    if MAC:
        if start:
            out = _osascript(["return POSIX path of (choose folder with prompt (item 1 of argv) default location (POSIX file (item 2 of argv)))"],
                             prompt, start)
        else:
            out = _osascript(["return POSIX path of (choose folder with prompt (item 1 of argv))"], prompt)
    elif WINDOWS:
        out = _powershell("$d = New-Object System.Windows.Forms.FolderBrowserDialog; $d.Description = $env:PM_PROMPT; "
                          "if ($env:PM_START) { $d.SelectedPath = $env:PM_START }; "
                          "if ($d.ShowDialog($owner) -eq 'OK') { $d.SelectedPath }", prompt=prompt, start=start or "")
    else:
        out = _linux_dialog(["--file-selection", "--directory", f"--title={prompt}", *([f"--filename={start}/"] if start else [])],
                            ["--getexistingdirectory", start or str(Path.home()), "--title", prompt])
    path = (out.stdout.strip() or None) if out and out.returncode == 0 else None
    return path if MAC or not path else path.rstrip("/\\") or path
