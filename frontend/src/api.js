// Talks to the local Phygital Memory program. Each locked folder has its own pass, which comes only from unlocking
// and lives in this module's memory: never in storage, cookies or the URL.
const passes = new Map();   // folder id -> pass
let current = null;         // the folder id every call is about, unless the call names another
const lockedListeners = new Set();

export function setFolder(id) { current = id || null; }
export function currentFolder() { return current; }
export function setPass(p, folderId = current) { if (p) passes.set(folderId, p); else passes.delete(folderId); }
export function forgetPass(folderId = current) { passes.delete(folderId); }
export function hasPass(folderId = current) { return passes.has(folderId); }
export function onLocked(fn) { lockedListeners.add(fn); }   // fn(folderId)

export async function api(action, body = {}) {
  const folder = body.folder || current;
  const headers = { "Content-Type": "application/json" };
  const pass = passes.get(folder);
  if (pass) headers["X-App-Pass"] = pass;
  const r = await fetch("/api/" + action, { method: "POST", headers, body: JSON.stringify(folder && !body.folder ? { ...body, folder } : body) });
  const j = await r.json().catch(() => ({}));
  if (r.status === 423 && action !== "unlock" && action !== "devunlock") {
    const id = j.folder || folder;
    passes.delete(id);
    lockedListeners.forEach((fn) => fn(id));
    throw new Error("locked");
  }
  if (!r.ok) throw new Error(j.error || `Error ${r.status}`);
  return j;
}

// Images and other files come back as base64; the page shows them through short-lived blob URLs.
const blobCache = new Map();
const MIME = { png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", gif: "image/gif", webp: "image/webp",
               svg: "image/svg+xml", avif: "image/avif", pdf: "application/pdf",
               mp4: "video/mp4", m4v: "video/mp4", mov: "video/quicktime", webm: "video/webm",
               mp3: "audio/mpeg", m4a: "audio/mp4", aac: "audio/aac", wav: "audio/wav", ogg: "audio/ogg",
               oga: "audio/ogg", flac: "audio/flac", csv: "text/csv", tsv: "text/tab-separated-values" };

export function mimeOf(path) { return MIME[(path.split(".").pop() || "").toLowerCase()] || "application/octet-stream"; }

export async function fileURL(path) {
  const key = current + "\0" + path;
  if (blobCache.has(key)) return blobCache.get(key);
  const promise = api("readfile", { path }).then((j) => {
    const bytes = Uint8Array.from(atob(j.base64), (c) => c.charCodeAt(0));
    return URL.createObjectURL(new Blob([bytes], { type: mimeOf(path) }));
  });
  blobCache.set(key, promise);
  promise.catch(() => blobCache.delete(key));
  return promise;
}

export function forgetFiles() {   // on lock or folder switch: drop every decrypted image from memory
  for (const p of blobCache.values()) p.then((u) => URL.revokeObjectURL(u)).catch(() => {});
  blobCache.clear();
}

export async function uploadFile(path, file) {
  const buf = new Uint8Array(await file.arrayBuffer());
  let bin = "";
  for (let i = 0; i < buf.length; i += 0x8000) bin += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
  return api("savefile", { path, base64: btoa(bin) });
}

// A file's text (for previews like CSV): decoded as UTF-8.
export async function readFileText(path) {
  const j = await api("readfile", { path });
  const bytes = Uint8Array.from(atob(j.base64), (c) => c.charCodeAt(0));
  return new TextDecoder("utf-8").decode(bytes);
}
