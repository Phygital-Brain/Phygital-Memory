// Talks to the local Phygital Memory program. The app pass comes only from unlocking and lives in this
// module's memory: never in storage, cookies or the URL.
let pass = null;
const lockedListeners = new Set();

export function setPass(p) { pass = p; }
export function hasPass() { return pass !== null; }
export function onLocked(fn) { lockedListeners.add(fn); }

export async function api(action, body = {}) {
  const headers = { "Content-Type": "application/json" };
  if (pass) headers["X-App-Pass"] = pass;
  const r = await fetch("/api/" + action, { method: "POST", headers, body: JSON.stringify(body) });
  const j = await r.json().catch(() => ({}));
  if (r.status === 423 && action !== "unlock") {
    pass = null;
    lockedListeners.forEach((fn) => fn());
    throw new Error("locked");
  }
  if (!r.ok) throw new Error(j.error || `Error ${r.status}`);
  return j;
}

// Images and other files come back as base64; the page shows them through short-lived blob URLs.
const blobCache = new Map();
const MIME = { png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", gif: "image/gif", webp: "image/webp",
               svg: "image/svg+xml", avif: "image/avif", pdf: "application/pdf" };

export function mimeOf(path) { return MIME[(path.split(".").pop() || "").toLowerCase()] || "application/octet-stream"; }

export async function fileURL(path) {
  if (blobCache.has(path)) return blobCache.get(path);
  const promise = api("readfile", { path }).then((j) => {
    const bytes = Uint8Array.from(atob(j.base64), (c) => c.charCodeAt(0));
    return URL.createObjectURL(new Blob([bytes], { type: mimeOf(path) }));
  });
  blobCache.set(path, promise);
  promise.catch(() => blobCache.delete(path));
  return promise;
}

export function forgetFiles() {   // on lock: drop every decrypted image from memory
  for (const p of blobCache.values()) p.then((u) => URL.revokeObjectURL(u)).catch(() => {});
  blobCache.clear();
}

export async function uploadFile(path, file) {
  const buf = new Uint8Array(await file.arrayBuffer());
  let bin = "";
  for (let i = 0; i < buf.length; i += 0x8000) bin += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
  return api("savefile", { path, base64: btoa(bin) });
}
