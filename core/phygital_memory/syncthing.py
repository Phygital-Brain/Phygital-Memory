"""The app's own private Syncthing: shared memories sync straight between people's Macs, with no cloud and no accounts.

- Its own settings and keys, in the app's folder (never a Syncthing the person runs themselves), on its own ports.
- Off until something is shared. No usage reports, no crash reports, no auto-updates.
- Each shared memory is one Syncthing folder, "pm-VAULTID", holding only the memory's encrypted files.
- Computers find each other on the same network, or through Syncthing's public discovery and relays, which only ever
  see encrypted traffic of encrypted files. Tests turn all of that off and connect on 127.0.0.1.
- A computer may connect only if its name carries proof of an invite (an HMAC of its Syncthing ID with the invite's
  one-time code). It then gets one small "pmq-" folder, which only carries its request to join (name and public
  key) to the owner. The memory's files go to it only after the owner says yes, together with its own key."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

from .folders import STATE

HOME = Path(os.environ.get("PHYGITAL_MEMORY_SYNCTHING_HOME", STATE / "syncthing"))
OFFLINE = bool(os.environ.get("PHYGITAL_MEMORY_SYNCTHING_LOCAL"))   # tests: no discovery, relays or NAT, 127.0.0.1 only
NO_LAN = bool(os.environ.get("PHYGITAL_MEMORY_SYNCTHING_NO_LAN"))   # tests: found only through internet discovery
IGNORE = ".DS_Store\n._*\n.encryptor-*\n.git\n.github\n.gitignore\n.gitattributes\n"


class SyncthingError(Exception):
    pass


def binary() -> str:
    """Next to the server inside the app; in the test setup the one on this Mac."""
    from .system import exe
    for p in (str(Path(sys.executable).parent / exe("syncthing")) if getattr(sys, "frozen", False) else None,
              shutil.which("syncthing"), "/opt/homebrew/bin/syncthing"):
        if p and Path(p).is_file():
            return p
    raise SyncthingError("Syncthing is missing from this copy of the app.")


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def proof(code: str, device_id: str) -> str:
    return hmac.new(code.encode(), device_id.encode(), hashlib.sha256).hexdigest()[:24]


class Syncthing:
    def __init__(self, home: Path = HOME):
        self.home = Path(home)
        self.proc: subprocess.Popen | None = None
        self.gui = self.key = None
        self.listen = None
        self._lock = threading.RLock()

    # ---------- start and stop ----------

    def _configure(self) -> None:
        cfg = self.home / "config.xml"
        if not cfg.exists():
            self.home.mkdir(parents=True, exist_ok=True)
            os.chmod(self.home, 0o700)
            r = subprocess.run([binary(), "generate", f"--home={self.home}", "--no-port-probing"], capture_output=True, text=True)
            if r.returncode != 0:
                raise SyncthingError("Couldn't set up Syncthing: " + (r.stderr.strip().splitlines() or ["?"])[-1])
        x = cfg.read_text()
        self.gui = f"127.0.0.1:{_free_port()}"
        self.key = secrets.token_urlsafe(24)
        self.listen = _free_port()

        def put(tag: str, value: str, text: str) -> str:
            return re.sub(rf"<{tag}>[^<]*</{tag}>", f"<{tag}>{value}</{tag}>", text, count=1) if f"<{tag}>" in text \
                else text.replace("</options>", f"    <{tag}>{value}</{tag}>\n    </options>", 1)
        x = re.sub(r"(<gui[^>]*>.*?<address>)[^<]*(</address>)", rf"\g<1>{self.gui}\g<2>", x, count=1, flags=re.S)
        x = re.sub(r"(<gui[^>]*>.*?<apikey>)[^<]*(</apikey>)", rf"\g<1>{self.key}\g<2>", x, count=1, flags=re.S)
        x = re.sub(r"<listenAddress>[^<]*</listenAddress>\s*", "", x)
        listen = f"<listenAddress>tcp://{'127.0.0.1' if OFFLINE else '0.0.0.0'}:{self.listen}</listenAddress>"
        x = x.replace("<options>", "<options>\n        " + listen, 1)
        for tag, value in (("urAccepted", "-1"), ("urSeen", "3"), ("crashReportingEnabled", "false"),
                           ("autoUpgradeIntervalH", "0"), ("startBrowser", "false"),
                           ("globalAnnounceEnabled", "false" if OFFLINE else "true"),
                           ("localAnnounceEnabled", "false" if OFFLINE or NO_LAN else "true"),
                           ("relaysEnabled", "false" if OFFLINE else "true"), ("natEnabled", "false" if OFFLINE else "true")):
            x = put(tag, value, x)
        cfg.write_text(x)
        os.chmod(cfg, 0o600)

    def start(self) -> None:
        with self._lock:
            if self.proc and self.proc.poll() is None:
                return
            # A copy left running by an app that was force quit holds this folder: stop it first.
            subprocess.run(["pkill", "-f", "syncthing serve --home=" + re.escape(str(self.home)) + " "], capture_output=True)
            time.sleep(0.5)
            self._configure()
            env = {**os.environ, "STNOUPGRADE": "1", "STNORESTART": "1"}
            self.proc = subprocess.Popen([binary(), "serve", f"--home={self.home}", "--no-browser", "--no-restart"],
                                         env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            end = time.time() + 30
            while time.time() < end:
                try:
                    self.rest("GET", "/rest/system/ping")
                    return
                except Exception:
                    if self.proc.poll() is not None:
                        raise SyncthingError("Syncthing stopped while starting.")
                    time.sleep(0.3)
            raise SyncthingError("Syncthing didn't start.")

    def running(self) -> bool:
        return bool(self.proc and self.proc.poll() is None)

    def stop(self) -> None:
        with self._lock:
            if self.running():
                try:
                    self.rest("POST", "/rest/system/shutdown")
                    self.proc.wait(timeout=10)
                except Exception:
                    self.proc.kill()
            self.proc = None

    def rest(self, method: str, path: str, body=None):
        req = urllib.request.Request(f"http://{self.gui}{path}", None if body is None else json.dumps(body).encode(),
                                     method=method, headers={"X-API-Key": self.key or "", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
            return json.loads(raw) if raw.strip().startswith((b"{", b"[")) else raw.decode()

    # ---------- this computer ----------

    def device_id(self) -> str:
        self.start()
        return self.rest("GET", "/rest/system/status")["myID"]

    def address(self) -> str:
        """Where others reach this computer directly (tests: 127.0.0.1); otherwise found through discovery."""
        return f"tcp://127.0.0.1:{self.listen}" if OFFLINE else "dynamic"

    def set_name(self, name: str) -> None:
        me = self.device_id()
        d = self.rest("GET", f"/rest/config/devices/{me}")
        d["name"] = name[:60]
        self.rest("PUT", f"/rest/config/devices/{me}", d)

    # ---------- other computers and shared folders ----------

    def add_device(self, device_id: str, name: str, address: str = "dynamic") -> None:
        self.start()
        self.rest("PUT", f"/rest/config/devices/{device_id}", {
            "deviceID": device_id, "name": name[:60], "addresses": [address if address else "dynamic"],
            "compression": "metadata", "introducer": False, "autoAcceptFolders": False, "paused": False})

    def remove_device(self, device_id: str) -> None:
        try:
            self.rest("DELETE", f"/rest/config/devices/{device_id}")
        except Exception:
            pass

    def add_folder(self, folder_id: str, path: Path, label: str, devices: list[str] = (), kind: str = "sendreceive") -> None:
        self.start()
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        (path / ".stignore").write_text(IGNORE)   # this side's own list; Syncthing never syncs it
        me = self.device_id()
        self.rest("PUT", f"/rest/config/folders/{folder_id}", {
            "id": folder_id, "label": label[:60], "path": str(path), "type": kind,
            "devices": [{"deviceID": d} for d in dict.fromkeys([me, *devices])],
            "rescanIntervalS": 60, "fsWatcherEnabled": True, "fsWatcherDelayS": 2, "ignorePerms": True,
            "maxConflicts": 10, "paused": False})

    def share_folder(self, folder_id: str, device_id: str) -> None:
        f = self.rest("GET", f"/rest/config/folders/{folder_id}")
        if not any(d["deviceID"] == device_id for d in f["devices"]):
            f["devices"].append({"deviceID": device_id})
            self.rest("PUT", f"/rest/config/folders/{folder_id}", f)

    def unshare_folder(self, folder_id: str, device_id: str) -> None:
        try:
            f = self.rest("GET", f"/rest/config/folders/{folder_id}")
        except Exception:
            return
        f["devices"] = [d for d in f["devices"] if d["deviceID"] != device_id]
        self.rest("PUT", f"/rest/config/folders/{folder_id}", f)

    def move_folder(self, folder_id: str, path: Path) -> None:
        f = self.rest("GET", f"/rest/config/folders/{folder_id}")
        f["path"] = str(path)
        Path(path, ".stignore").write_text(IGNORE)
        self.rest("PUT", f"/rest/config/folders/{folder_id}", f)

    def remove_folder(self, folder_id: str) -> None:
        try:
            self.rest("DELETE", f"/rest/config/folders/{folder_id}")
        except Exception:
            pass

    def has_folder(self, folder_id: str) -> bool:
        try:
            self.rest("GET", f"/rest/config/folders/{folder_id}")
            return True
        except Exception:
            return False

    def pending_devices(self) -> dict:
        return self.rest("GET", "/rest/cluster/pending/devices") or {}

    def pending_folders(self) -> dict:
        """Folders other computers offer us: {folder id: {"offeredBy": {device id: {...}}}}."""
        return self.rest("GET", "/rest/cluster/pending/folders") or {}

    def connected(self) -> list[str]:
        c = self.rest("GET", "/rest/system/connections").get("connections", {})
        return [d for d, v in c.items() if v.get("connected")]
