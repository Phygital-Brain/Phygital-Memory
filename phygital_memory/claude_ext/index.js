// Phygital Memory for Claude Desktop: a small bridge, no packages. Claude Desktop speaks MCP over stdin and stdout;
// this passes each message to the Phygital Memory app on this Mac (MCP over HTTP, with the key) and passes the
// answers back. It only ever talks to this Mac.
const DOOR = process.env.PM_URL || "http://127.0.0.1:8790/mcp";
const KEY = (process.env.PM_KEY || "").trim();
const host = new URL(DOOR).hostname;
if (!["127.0.0.1", "localhost", "[::1]", "::1"].includes(host)) {
  console.error("Phygital Memory: the address must be on this Mac (127.0.0.1).");
  process.exit(1);
}

let session = null, hello = null, queue = Promise.resolve(), buf = "";
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
  try { res = await post(msg); }
  catch { return fail(msg, "Phygital Memory isn't open on this Mac. Open the app, unlock a memory, then try again."); }
  const sid = res.headers.get("mcp-session-id");
  if (sid) session = sid;
  if (res.status === 404 && session && again && hello) {   // the app restarted: say hello again, then retry once
    session = null;
    const r = await post(hello);
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
