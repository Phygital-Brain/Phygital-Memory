// Phygital Memory for Claude Desktop: a small bridge, no packages. Claude Desktop speaks MCP over stdin and stdout;
// this passes each message to the Phygital Memory app on this Mac (MCP over HTTP, with the key) and passes the
// answers back. It only ever talks to this Mac.
// When the app wrote the engine's place into the extension (PM_ENGINE), the engine does all of this itself and also
// answers with the app closed, for Open memories (server.py, main: mcp): start it and pass stdin and stdout through.
const ENGINE = (process.env.PM_ENGINE || "").trim();
if (ENGINE && require("node:fs").existsSync(ENGINE)) {
  const child = require("node:child_process").spawn(ENGINE, ["mcp"], {
    stdio: "inherit", env: { ...process.env, PHYGITAL_MEMORY_KEY: (process.env.PM_KEY || "").trim() } });
  child.on("exit", (code) => process.exit(code ?? 0));
  return;
}
const DOOR = process.env.PM_URL || "http://127.0.0.1:8790/mcp";
const KEY = (process.env.PM_KEY || "").trim();
const host = new URL(DOOR).hostname;
if (!["127.0.0.1", "localhost", "[::1]", "::1"].includes(host)) {
  console.error("Phygital Memory: the address must be on this Mac (127.0.0.1).");
  process.exit(1);
}

const crypto = require("node:crypto");
let session = null, hello = null, queue = Promise.resolve(), buf = "";

// Before the key goes anywhere: is this really the Phygital Memory app? It must answer a fresh challenge with
// HMAC(sha256(key), challenge), which only something holding this key's fingerprint can do. A program squatting on
// the port while the app is closed can't, so it never sees the key. Checked before every message: the app may have
// closed in between.
async function prove() {
  const n = crypto.randomBytes(24).toString("hex");
  const want = crypto.createHmac("sha256", crypto.createHash("sha256").update(KEY).digest("hex")).update(n).digest("hex");
  const res = await fetch(new URL(`/mcp-proof?n=${n}`, DOOR));
  const got = res.ok ? (await res.json()).proofs || [] : [];
  return got.some((p) => typeof p === "string" && p.length === want.length && crypto.timingSafeEqual(Buffer.from(p), Buffer.from(want)));
}
const out = (msg) => process.stdout.write(JSON.stringify(msg) + "\n");
const fail = (msg, message) => { if (msg.id !== undefined && msg.id !== null) out({ jsonrpc: "2.0", id: msg.id, error: { code: -32000, message } }); };

async function post(msg) {
  return fetch(DOOR, { method: "POST", body: JSON.stringify(msg), headers: {
    "Content-Type": "application/json", Accept: "application/json, text/event-stream", Authorization: `Bearer ${KEY}`,
    ...(session ? { "Mcp-Session-Id": session } : {}) } });
}

async function answers(res) {   // a plain JSON answer, or an event stream that ends with the answer
  const text = await res.text();
  if ((res.headers.get("content-type") || "").includes("text/event-stream")) {
    return text.split(/\r?\n\r?\n/).map((block) => block.split(/\r?\n/).filter((l) => l.startsWith("data:"))
      .map((l) => l.slice(5).trimStart()).join("\n")).filter(Boolean).map((d) => JSON.parse(d));
  }
  return text ? [].concat(JSON.parse(text)) : [];
}

async function pass(msg, again = true) {
  let res;
  try {
    if (!(await prove())) {
      return fail(msg, "The program at Phygital Memory's address isn't your Phygital Memory app, or the key was removed. Open the app, check Settings › AI apps, then try again.");
    }
    res = await post(msg);
  }
  catch { return fail(msg, "Phygital Memory isn't open on this Mac. Open the app, unlock a memory, then try again."); }
  const sid = res.headers.get("mcp-session-id");
  if (sid) session = sid;
  if (res.status === 404 && session && again && hello) {   // the app restarted: prove it again, say hello, retry once
    session = null;
    if (!(await prove().catch(() => false))) return fail(msg, "The program at Phygital Memory's address isn't your Phygital Memory app. Open the app, then try again.");
    const r = await post(hello);   // checked just above
    session = r.headers.get("mcp-session-id") || session;
    await r.text();
    await (await post({ jsonrpc: "2.0", method: "notifications/initialized" })).text();
    return pass(msg, false);
  }
  if (res.status === 401) return fail(msg, "Phygital Memory refused the key. Make a new one in its Settings › AI apps, then paste it in Claude Desktop › Settings › Extensions › Phygital Memory.");
  if (res.status === 202 || res.status === 204) return;
  if (!res.ok) return fail(msg, `Phygital Memory answered with an error (${res.status}).`);
  try { (await answers(res)).forEach(out); } catch { fail(msg, "Phygital Memory sent an answer this bridge couldn't read."); }
}

process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => {
  buf += chunk;
  let i;
  while ((i = buf.indexOf("\n")) >= 0) {
    const line = buf.slice(0, i).trim();
    buf = buf.slice(i + 1);
    if (!line) continue;
    let msg;
    try { msg = JSON.parse(line); } catch { continue; }
    if (msg.method === "initialize") hello = msg;
    queue = queue.then(() => pass(msg));   // one at a time, in order
  }
});
process.stdin.on("end", () => queue.then(() => process.exit(0)));
