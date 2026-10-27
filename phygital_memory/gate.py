"""The AI door's lock: which AI apps may come in, and what each one may reach.

Every AI app needs its own key. There are two ways to get one, and both end up as the same kind of record:
- a key made in Settings › AI apps, pasted into the AI app's setup (works with every MCP app);
- MCP sign-in (OAuth): the AI app opens a page, and the person presses Allow in the Phygital Memory app.

Each app record says which memories it may see ("all", or a list) and whether it may edit. A memory marked
"AI can't see this" is hidden from every app. Keys are never stored: only their SHA-256 fingerprint is, in
ai-apps.json next to the folder list, so the file can't be used to get in.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import secrets
import threading
import time
from urllib.parse import urlparse
from pathlib import Path

from mcp.server.auth.provider import (AccessToken, AuthorizationCode, AuthorizationParams, AuthorizeError,
                                      RefreshToken, RegistrationError, TokenError, construct_redirect_uri)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken

STATE = Path(os.environ.get("PHYGITAL_MEMORY_STATE", "~/Library/Application Support/Phygital Memory")).expanduser()
FILE = STATE / "ai-apps.json"
READ, WRITE = "notes:read", "notes:write"
ACCESS_DAYS, REFRESH_DAYS = 30, 365
KINDS = {"claude-code": "Claude Code", "claude-desktop": "Claude Desktop", "cursor": "Cursor", "codex": "Codex",
         "other": "AI app"}


def _fp(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class Gate:
    def __init__(self):
        self._lock = threading.RLock()
        try:
            d = json.loads(FILE.read_text())
        except (OSError, ValueError):
            d = {}
        self.apps: dict[str, dict] = d.get("apps", {})
        self.tokens: dict[str, dict] = d.get("tokens", {})       # fingerprint -> {app, type, expires}
        self.clients: dict[str, dict] = d.get("clients", {})     # MCP sign-in registrations (public, no secrets)
        self.pending: dict[str, dict] = {}                        # sign-ins waiting for Allow (in memory only)
        self.codes: dict[str, dict] = {}                          # one-time codes after Allow (in memory only)
        self._fails: list[float] = []
        self._saved = 0.0

    def _save(self) -> None:
        with self._lock:
            STATE.mkdir(parents=True, exist_ok=True)
            tmp = FILE.with_suffix(".tmp")
            tmp.write_text(json.dumps({"apps": self.apps, "tokens": self.tokens, "clients": self.clients}, indent=1))
            os.chmod(tmp, 0o600)
            os.replace(tmp, FILE)
            self._saved = time.time()

    # ---------- apps ----------

    def _new_app(self, name: str, kind: str, folders, write: bool, client_id: str | None = None) -> str:
        aid = secrets.token_hex(4)
        self.apps[aid] = {"name": name.strip()[:60] or KINDS.get(kind, "AI app"), "kind": kind,
                          "folders": _clean_folders(folders), "write": bool(write), "created": time.time(),
                          "last": None, **({"client": client_id} if client_id else {})}
        return aid

    def _token(self, aid: str, kind: str, days: int | None) -> str:
        token = ("pm_" if kind == "access" else "pmr_") + secrets.token_urlsafe(32)
        self.tokens[_fp(token)] = {"app": aid, "type": kind, "expires": time.time() + days * 86400 if days else None}
        return token

    def add_key(self, name: str, kind: str, folders, write: bool) -> tuple[dict, str]:
        """A new AI app with a key that doesn't run out. The key is returned once and never stored."""
        with self._lock:
            aid = self._new_app(name, kind, folders, write)
            key = self._token(aid, "access", None)
            self._save()
            return self.info(aid), key

    def update(self, aid: str, folders=None, write=None) -> dict:
        with self._lock:
            app = self.apps[aid]
            if folders is not None:
                app["folders"] = _clean_folders(folders)
            if write is not None:
                app["write"] = bool(write)
            self._save()
            return self.info(aid)

    def remove(self, aid: str) -> None:
        """Cut an app off at once: its record and every key it holds go."""
        with self._lock:
            self.apps.pop(aid, None)
            self.tokens = {fp: t for fp, t in self.tokens.items() if t["app"] != aid}
            self._save()

    def info(self, aid: str) -> dict:
        a = self.apps[aid]
        return {"id": aid, "name": a["name"], "kind": a["kind"], "folders": a["folders"], "write": a["write"],
                "created": a["created"], "last": a["last"], "signin": bool(a.get("client"))}

    def list(self) -> list[dict]:
        with self._lock:
            return sorted((self.info(a) for a in self.apps), key=lambda x: -(x["last"] or x["created"]))

    def app_of(self, token: str) -> dict | None:
        """The app a key belongs to, if the key is good. Marks it as used."""
        with self._lock:
            t = self.tokens.get(_fp(token))
            if not t or t["type"] != "access" or (t["expires"] and t["expires"] < time.time()):
                return None
            app = self.apps.get(t["app"])
            if not app:
                return None
            app["last"] = time.time()
            if time.time() - self._saved > 60:   # "last used" is written down at most once a minute
                self._save()
            return {**app, "id": t["app"]}

    def forget_folder(self, fid: str) -> None:
        with self._lock:
            for app in self.apps.values():
                if isinstance(app["folders"], list) and fid in app["folders"]:
                    app["folders"].remove(fid)
            self._save()

    # ---------- the MCP library's sign-in hooks (OAuthAuthorizationServerProvider) ----------

    async def load_access_token(self, token: str) -> AccessToken | None:
        app = self.app_of(token)
        if not app:
            now = time.time()   # wrong keys: after a few in a minute, each one waits a little longer
            self._fails = [t for t in self._fails if now - t < 60] + [now]
            if len(self._fails) > 5:
                await asyncio.sleep(min(len(self._fails) - 5, 10))
            return None
        return AccessToken(token=token, client_id=app["id"], scopes=[READ] + ([WRITE] if app["write"] else []))

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        c = self.clients.get(client_id)
        return OAuthClientInformationFull.model_validate(c) if c else None

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        # Sign-in codes may only go back to an app on this Mac: a loopback address (Claude Code's own little server)
        # or an app's own link scheme (claude://), never a website, which could catch the code.
        for uri in client_info.redirect_uris or []:
            u = urlparse(str(uri))
            loopback = u.scheme == "http" and u.hostname in ("127.0.0.1", "localhost", "::1")
            if not loopback and u.scheme in ("http", "https", "javascript", "data", "file", ""):
                raise RegistrationError(error="invalid_redirect_uri",
                                        error_description="Sign-in can only return to an app on this Mac.")
        with self._lock:
            if len(self.clients) > 200:   # registrations are free to make: keep the newest
                for cid in sorted(self.clients, key=lambda c: self.clients[c].get("client_id_issued_at") or 0)[:50]:
                    if not any(a.get("client") == cid for a in self.apps.values()):
                        self.clients.pop(cid)
            self.clients[client_info.client_id] = client_info.model_dump(mode="json", exclude_none=True)
            self._save()

    async def authorize(self, client: OAuthClientInformationFull, params: AuthorizationParams) -> str:
        """An AI app asks to come in: park the request until the person answers in the app, and send the browser
        to a page that waits for that answer."""
        with self._lock:
            now = time.time()
            self.pending = {r: p for r, p in self.pending.items() if now - p["at"] < 600}
            if len(self.pending) >= 10:
                raise AuthorizeError("temporarily_unavailable", "Too many sign-ins waiting. Try again in a few minutes.")
            rid = secrets.token_urlsafe(16)
            self.pending[rid] = {"at": now, "client": client.client_id, "params": params,
                                 "name": (client.client_name or "An AI app")[:60], "answer": None}
            return f"{ISSUER}/allow/{rid}"

    def name_of(self, rid: str) -> str:
        with self._lock:
            p = self.pending.get(rid)
            return p["name"] if p else "An AI app"

    def list_names(self) -> dict:
        with self._lock:
            return {aid: a["name"] for aid, a in self.apps.items()}

    def waiting(self) -> list[dict]:
        """Sign-ins the person hasn't answered yet, for the Allow window in the app."""
        with self._lock:
            now = time.time()
            return [{"id": r, "name": p["name"]} for r, p in self.pending.items()
                    if p["answer"] is None and now - p["at"] < 600]

    def answer(self, rid: str, allow: bool, folders=None, write: bool = False) -> None:
        with self._lock:
            p = self.pending.get(rid)
            if not p or p["answer"] is not None:
                raise ValueError("That request is gone. Start the sign-in again from the AI app.")
            params: AuthorizationParams = p["params"]
            if not allow:
                p["answer"] = construct_redirect_uri(str(params.redirect_uri), error="access_denied",
                                                     error_description="The person said no.", state=params.state)
                return
            # one app per AI app: signing in again replaces its old record (and keys)
            for aid in [a for a, rec in self.apps.items() if rec.get("client") == p["client"]]:
                self.apps.pop(aid)
                self.tokens = {fp: t for fp, t in self.tokens.items() if t["app"] != aid}
            aid = self._new_app(p["name"], "signin", folders, write, p["client"])
            code = secrets.token_urlsafe(32)
            self.codes[code] = {"app": aid, "obj": AuthorizationCode(
                code=code, scopes=[READ] + ([WRITE] if write else []), expires_at=time.time() + 300,
                client_id=p["client"], code_challenge=params.code_challenge, redirect_uri=params.redirect_uri,
                redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly, resource=params.resource)}
            p["answer"] = construct_redirect_uri(str(params.redirect_uri), code=code, state=params.state)
            self._save()

    def answered(self, rid: str) -> str | None:
        """Where the waiting browser page goes next (back to the AI app), once the person answered."""
        with self._lock:
            p = self.pending.get(rid)
            if not p:
                return ""
            if p["answer"]:
                self.pending.pop(rid)
            return p["answer"]

    async def load_authorization_code(self, client: OAuthClientInformationFull, authorization_code: str):
        c = self.codes.get(authorization_code)
        if not c or c["obj"].client_id != client.client_id or c["obj"].expires_at < time.time():
            return None
        return c["obj"]

    async def exchange_authorization_code(self, client: OAuthClientInformationFull, authorization_code) -> OAuthToken:
        with self._lock:
            c = self.codes.pop(authorization_code.code, None)
            if not c or c["app"] not in self.apps:
                raise TokenError("invalid_grant", "That code was already used or the app was removed.")
            return self._pair(c["app"], authorization_code.scopes)

    def _pair(self, aid: str, scopes: list[str]) -> OAuthToken:
        access = self._token(aid, "access", ACCESS_DAYS)
        refresh = self._token(aid, "refresh", REFRESH_DAYS)
        self._save()
        return OAuthToken(access_token=access, token_type="Bearer", expires_in=ACCESS_DAYS * 86400,
                          refresh_token=refresh, scope=" ".join(scopes))

    async def load_refresh_token(self, client: OAuthClientInformationFull, refresh_token: str):
        with self._lock:
            t = self.tokens.get(_fp(refresh_token))
            app = self.apps.get(t["app"]) if t else None
            if not t or t["type"] != "refresh" or not app or app.get("client") != client.client_id \
                    or (t["expires"] and t["expires"] < time.time()):
                return None
            return RefreshToken(token=refresh_token, client_id=client.client_id,
                                scopes=[READ] + ([WRITE] if app["write"] else []))

    async def exchange_refresh_token(self, client, refresh_token, scopes: list[str]) -> OAuthToken:
        with self._lock:
            t = self.tokens.pop(_fp(refresh_token.token), None)   # each refresh key works once
            if not t or t["app"] not in self.apps:
                raise TokenError("invalid_grant", "The app was removed. Sign in again.")
            app = self.apps[t["app"]]
            return self._pair(t["app"], [READ] + ([WRITE] if app["write"] else []))

    async def revoke_token(self, token) -> None:
        with self._lock:
            self.tokens.pop(_fp(token.token), None)
            self._save()


ISSUER = ""   # set by the server: http://127.0.0.1:PORT


def _clean_folders(folders):
    if folders == "all" or folders is None:
        return "all"
    return [str(f) for f in folders][:200]
