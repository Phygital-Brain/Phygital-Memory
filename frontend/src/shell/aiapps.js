// Settings › AI apps: the AI apps that may use the notes, connecting a new one (a key shown once, with the setup to
// paste), changing or removing one, and the Allow window when an AI app signs in. Everything from the server is
// put in as text only.
import { el, icon } from "./dom.js";
import { modal } from "./dialogs.js";

const ago = (t) => {
  if (!t) return "never used";
  const s = Date.now() / 1000 - t;
  return s < 90 ? "used just now" : s < 3600 ? `used ${Math.round(s / 60)} min ago` : s < 86400 ? `used ${Math.round(s / 3600)} h ago` : `used ${Math.round(s / 86400)} days ago`;
};
const reach = (app, folders) => {
  const names = app.folders === "all" ? "All memories" : folders.filter((f) => app.folders.includes(f.id)).map((f) => f.name).join(", ") || "No memories";
  return `${names} · ${app.write ? "can read and edit" : "can only read"}`;
};

// Which memories, and read or edit. Returns {node, value()} with value() = {folders: "all" | [ids], write}.
function accessForm(folders, cur = { folders: "all", write: false }) {
  const all = el("input", { type: "checkbox", checked: cur.folders === "all" });
  const boxes = folders.map((f) => {
    const b = el("input", { type: "checkbox", checked: cur.folders === "all" || cur.folders.includes(f.id), disabled: cur.folders === "all" });
    return { f, b, row: el("label", { class: "set-check ai-mem" }, b, el("span", {}, f.name), f.aiHidden ? el("span", { class: "ai-note" }, "AI can't see this") : null) };
  });
  all.addEventListener("change", () => boxes.forEach(({ b }) => { b.disabled = all.checked; if (all.checked) b.checked = true; }));
  const write = el("input", { type: "checkbox", checked: !!cur.write, "aria-label": "Allow edits" });
  const node = el("div", { class: "ai-access" },
    el("div", { class: "set-title" }, "Which memories"),
    el("label", { class: "set-check ai-mem" }, all, el("span", {}, "All memories, also new ones")),
    ...boxes.map((x) => x.row),
    el("div", { class: "set-row ai-write" },
      el("div", { class: "set-text" }, el("div", { class: "set-title" }, "Allow edits"),
        el("div", { class: "set-hint" }, "Change, add, move and put notes in the trash. Changes can be undone, and trashed notes put back.")),
      el("label", { class: "switch" }, write, el("span", { class: "switch-t" }))));
  return { node, value: () => ({ folders: all.checked ? "all" : boxes.filter((x) => x.b.checked).map((x) => x.f.id), write: write.checked }) };
}

// The setup to paste into each AI app, with the key in it.
function setupFor(kind, door, key) {
  const name = "phygital-memory";
  switch (kind) {
    case "claude-code":
      return { where: "Run this in Terminal:", text: `claude mcp add --scope user --transport http ${name} ${door} --header "Authorization: Bearer ${key}"` };
    case "cursor":
      return { where: "Add this to ~/.cursor/mcp.json:", text: JSON.stringify({ mcpServers: { [name]: { url: door, headers: { Authorization: `Bearer ${key}` } } } }, null, 2) };
    case "claude-desktop":
      return { where: "Add this to Claude Desktop's config (Settings › Developer › Edit Config), then restart it:",
               text: JSON.stringify({ mcpServers: { [name]: { command: "npx", args: ["-y", "mcp-remote", door, "--header", `Authorization: Bearer ${key}`] } } }, null, 2) };
    case "codex":
      return { where: "Add this to ~/.codex/config.toml:", text: `[mcp_servers.${name.replace("-", "_")}]\nurl = "${door}"\nhttp_headers = { Authorization = "Bearer ${key}" }` };
    default:
      return { where: "In your AI app, add an MCP server (streamable HTTP) with this address and header:", text: `${door}\nAuthorization: Bearer ${key}` };
  }
}

const KINDS = [["claude-code", "Claude Code"], ["claude-desktop", "Claude Desktop"], ["cursor", "Cursor"], ["codex", "Codex"], ["other", "Other AI app"]];

// ctx: {load() -> {apps, folders, door, waiting}, add(body) -> {app, key, door}, update(body), remove(id),
//       claudeCode(key) -> {ok, error}}
export function openAIApps(ctx) {
  return modal((done) => {
    const body = el("div", { class: "cl-body" });
    const err = el("div", { class: "dlg-err" });
    const title = el("div", { class: "dlg-title" }, "AI apps");
    const actions = el("div", { class: "dlg-actions" });
    const card = el("div", { class: "dlg storage ai-apps", role: "dialog" }, title, body, err, actions);
    const busy = (b) => card.classList.toggle("busy", b);
    const btn = (label, fn, cls) => el("button", { class: "btn " + (cls || ""), type: "button", onclick: fn }, label);
    let data = null;

    const list = async () => {
      title.textContent = "AI apps"; err.textContent = "";
      try { data = await ctx.load(); } catch (e) { err.textContent = e.message; return; }
      body.replaceChildren(
        el("div", { class: "mf-hint" }, "Each AI app needs its own key to reach your notes, and only while a memory is unlocked. Remove one to cut it off at once."),
        el("div", { class: "act-list" }, ...(data.apps.length ? data.apps.map((a) =>
          el("div", { class: "todo-row repo-row ai-row" },
            el("span", { class: "trash-ic" }, icon("sparkle", 16)),
            el("div", { class: "act-main" },
              el("div", { class: "act-line" }, a.name),
              el("div", { class: "act-folder" }, `${reach(a, data.folders)} · ${ago(a.last)}${a.signin ? " · signed in" : ""}`)),
            el("div", { class: "set-btns" }, btn("Change", () => change(a), "small"),
              btn("Remove", async () => { busy(true); try { await ctx.remove(a.id); } catch (e) { err.textContent = e.message; } busy(false); list(); }, "small danger"))))
          : [el("div", { class: "act-empty" }, "No AI app is connected yet.")])),
        el("div", { class: "st-gh-note" }, "AI apps that support sign-in (like Claude Code) can also connect by themselves: add the address below, and press Allow here when they ask."),
        el("div", { class: "ai-door" }, el("code", {}, data.door), btn("Copy", () => navigator.clipboard.writeText(data.door), "small")));
      actions.replaceChildren(btn("Close", () => done(null)), btn("Connect an AI app…", pick, "primary"));
    };

    const pick = () => {
      title.textContent = "Connect an AI app"; err.textContent = "";
      body.replaceChildren(el("div", { class: "act-list" }, ...KINDS.map(([k, label]) =>
        el("button", { class: "todo-row repo-row", type: "button", onclick: () => choose(k, label) },
          el("span", { class: "trash-ic" }, icon("sparkle", 16)), el("div", { class: "act-main" }, el("div", { class: "act-line" }, label))))));
      actions.replaceChildren(btn("Back", list));
    };

    const choose = (kind, label) => {
      title.textContent = `Connect ${label}`; err.textContent = "";
      const name = el("input", { class: "dlg-input", spellcheck: "false", value: kind === "other" ? "" : label, placeholder: "Its name, like ChatGPT", "aria-label": "Name" });
      const access = accessForm(data.folders);
      body.replaceChildren(name, access.node);
      actions.replaceChildren(btn("Back", pick), btn("Make the key", async () => {
        if (!name.value.trim()) { err.textContent = "Give it a name."; return; }
        busy(true);
        try { const j = await ctx.add({ name: name.value.trim(), kind, ...access.value() }); busy(false); show(kind, j); }
        catch (e) { err.textContent = e.message; busy(false); }
      }, "primary"));
      name.focus();
    };

    const show = (kind, j) => {
      title.textContent = `${j.app.name} is connected`; err.textContent = "";
      const s = setupFor(kind, j.door, j.key);
      const copy = btn("Copy", () => navigator.clipboard.writeText(s.text).then(() => { copy.textContent = "Copied"; }), "small");
      const auto = kind === "claude-code" ? btn("Add to Claude Code for me", async () => {
        busy(true);
        try { const r = await ctx.claudeCode(j.key); err.textContent = r.ok ? "" : r.error; if (r.ok) { auto.textContent = "Added to Claude Code"; auto.disabled = true; } }
        catch (e) { err.textContent = e.message; }
        busy(false);
      }, "small primary") : null;
      body.replaceChildren(
        el("div", { class: "st-warn" }, el("span", {}, "This key is shown only now. Paste it into the AI app before you close this. If you lose it, remove the app and connect it again.")),
        el("div", { class: "set-title" }, s.where),
        el("pre", { class: "ai-setup" }, s.text),
        el("div", { class: "set-btns" }, copy, auto));
      actions.replaceChildren(btn("Done", list, "primary"));
    };

    const change = (a) => {
      title.textContent = `What ${a.name} can reach`; err.textContent = "";
      const access = accessForm(data.folders, a);
      body.replaceChildren(access.node);
      actions.replaceChildren(btn("Back", list), btn("Save", async () => {
        busy(true);
        try { await ctx.update({ id: a.id, ...access.value() }); busy(false); list(); } catch (e) { err.textContent = e.message; busy(false); }
      }, "primary"));
    };

    const again = () => { if (!card.isConnected) document.removeEventListener("ai-apps-changed", again); else if (title.textContent === "AI apps") list(); };
    document.addEventListener("ai-apps-changed", again);
    list();
    return { card };
  });
}

// The Allow window: an AI app signed in and waits for the person. Resolves {allow, folders, write}.
export function allowDialog(name, folders) {
  return modal((done) => {
    const access = accessForm(folders);
    // The buttons wake up after a second, so a click already on its way when this window appears can't say yes.
    const deny = el("button", { class: "btn", type: "button", disabled: true, onclick: () => done({ allow: false }) }, "Deny");
    const allow = el("button", { class: "btn primary", type: "button", disabled: true, onclick: () => done({ allow: true, ...access.value() }) }, "Allow");
    setTimeout(() => { deny.disabled = allow.disabled = false; }, 1000);
    const card = el("div", { class: "dlg storage ai-apps", role: "dialog" },
      el("div", { class: "dlg-title" }, `“${name}” wants to use your notes`),
      el("div", { class: "mf-hint" }, "That's the name the app gives itself. It can only reach memories that are unlocked. You can change this or remove it later in Settings › AI apps."),
      access.node,
      el("div", { class: "dlg-actions" }, deny, allow));
    return { card };
  }).then((v) => v || { allow: false });
}
