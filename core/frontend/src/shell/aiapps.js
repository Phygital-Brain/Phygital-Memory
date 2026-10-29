// Settings › AI apps: the AI apps that may use the notes, connecting a new one (a key shown once, with the setup to
// paste), changing or removing one, and the Allow window when an AI app signs in. Everything from the server is
// put in as text only.
import { t } from "./i18n.js";
const tr = t;   // (inside ago, "t" is the time)
import { el, icon } from "./dom.js";
import { modal } from "./dialogs.js";

const ago = (t) => {
  if (!t) return tr("never used");
  const s = Date.now() / 1000 - t;
  return s < 90 ? tr("used just now") : s < 3600 ? tr("used {0} min ago", Math.round(s / 60)) : s < 86400 ? tr("used {0} h ago", Math.round(s / 3600)) : tr("used {0} days ago", Math.round(s / 86400));
};
const reach = (app, folders) => {
  const names = app.folders === "all" ? "All memories" : folders.filter((f) => app.folders.includes(f.id)).map((f) => f.name).join(", ") || t("No memories");
  return `${names} · ${app.write ? "can read and edit" : "can only read"}`;
};

// Which memories, and read or edit. Returns {node, value()} with value() = {folders: "all" | [ids], write}.
function accessForm(folders, cur = { folders: "all", write: false }) {
  const all = el("input", { type: "checkbox", checked: cur.folders === "all" });
  const boxes = folders.map((f) => {
    const b = el("input", { type: "checkbox", checked: cur.folders === "all" || cur.folders.includes(f.id), disabled: cur.folders === "all" });
    return { f, b, row: el("label", { class: "set-check ai-mem" }, b, el("span", {}, f.name), f.aiHidden ? el("span", { class: "ai-note" }, t("AI can't see this")) : null) };
  });
  all.addEventListener("change", () => boxes.forEach(({ b }) => { b.disabled = all.checked; if (all.checked) b.checked = true; }));
  const write = el("input", { type: "checkbox", checked: !!cur.write, "aria-label": t("Allow edits") });
  const node = el("div", { class: "ai-access" },
    el("div", { class: "set-title" }, t("Which memories")),
    el("label", { class: "set-check ai-mem" }, all, el("span", {}, t("All memories, also new ones"))),
    ...boxes.map((x) => x.row),
    el("div", { class: "set-row ai-write" },
      el("div", { class: "set-text" }, el("div", { class: "set-title" }, t("Allow edits")),
        el("div", { class: "set-hint" }, t("Change, add, move and trash notes. You can undo every change."))),
      el("label", { class: "switch" }, write, el("span", { class: "switch-t" }))));
  return { node, value: () => ({ folders: all.checked ? "all" : boxes.filter((x) => x.b.checked).map((x) => x.f.id), write: write.checked }) };
}

// The setup to paste into each AI app, with the key in it. With the engine's place (the built app), the AI app starts
// the engine itself: it goes through the app when the app is open, and reaches Open memories by itself when it's closed.
function setupFor(kind, door, key, engine) {
  const name = "phygital-memory";
  if (engine) switch (kind) {
    case "claude-code":
      return { where: t("Run this in Terminal:"), text: `claude mcp add --scope user -e PHYGITAL_MEMORY_KEY=${key} ${name} -- "${engine}" mcp` };
    case "cursor":
      return { where: t("Add this to ~/.cursor/mcp.json:"), text: JSON.stringify({ mcpServers: { [name]: { command: engine, args: ["mcp"], env: { PHYGITAL_MEMORY_KEY: key } } } }, null, 2) };
    case "codex":
      return { where: t("Add this to ~/.codex/config.toml:"), text: `[mcp_servers.${name.replace("-", "_")}]\ncommand = '${engine}'\nargs = ["mcp"]\nenv = { PHYGITAL_MEMORY_KEY = "${key}" }` };
    case "other":
      return { where: t("In your AI app, add an MCP server it starts itself (stdio), with this command and setting:"), text: `"${engine}" mcp\nPHYGITAL_MEMORY_KEY=${key}` };
  }
  switch (kind) {
    case "claude-code":
      return { where: t("Run this in Terminal:"), text: `claude mcp add --scope user --transport http ${name} ${door} --header "Authorization: Bearer ${key}"` };
    case "cursor":
      return { where: t("Add this to ~/.cursor/mcp.json:"), text: JSON.stringify({ mcpServers: { [name]: { url: door, headers: { Authorization: `Bearer ${key}` } } } }, null, 2) };
    case "claude-desktop":   // the extension asks for the key itself; this is all there is to paste
      return { where: t("Your key. Paste it when Claude Desktop asks:"), text: key };
    case "codex":
      return { where: t("Add this to ~/.codex/config.toml:"), text: `[mcp_servers.${name.replace("-", "_")}]\nurl = "${door}"\nhttp_headers = { Authorization = "Bearer ${key}" }` };
    default:
      return { where: t("In your AI app, add an MCP server (streamable HTTP) with this address and header:"), text: `${door}\nAuthorization: Bearer ${key}` };
  }
}

const KINDS = [["claude-code", t("Claude Code")], ["claude-desktop", t("Claude Desktop")], ["cursor", "Cursor"], ["codex", "Codex"], ["other", t("Other AI app")]];

// ctx: {load() -> {apps, folders, door, waiting}, add(body) -> {app, key, door}, update(body), remove(id),
//       claudeCode(key) -> {ok, error}}
// The AI apps tab of the AI window: its own heading, steps and buttons inside the tab.
export function aiAppsView(ctx) {
    const body = el("div", { class: "cl-body" });
    const err = el("div", { class: "dlg-err" });
    const title = el("div", { class: "ai-sub" }, t("AI apps"));
    const actions = el("div", { class: "dlg-actions ai-apps-actions" });
    const card = el("div", { class: "ai-apps" }, title, body, err, actions);
    const busy = (b) => card.classList.toggle("busy", b);
    const btn = (label, fn, cls) => el("button", { class: "btn " + (cls || ""), type: "button", onclick: fn }, label);
    let data = null;

    const list = async () => {
      title.textContent = t("AI apps"); err.textContent = "";
      try { data = await ctx.load(); } catch (e) { err.textContent = e.message; return; }
      body.replaceChildren(
        el("div", { class: "mf-hint" }, t("Each AI app has its own key and only reaches memories that are open in the app. Remove an app to cut it off.")),
        el("div", { class: "act-list" }, ...(data.apps.length ? data.apps.map((a) =>
          el("div", { class: "todo-row repo-row ai-row" },
            el("span", { class: "trash-ic" }, icon("sparkle", 16)),
            el("div", { class: "act-main" },
              el("div", { class: "act-line" }, a.name),
              el("div", { class: "act-folder" }, `${reach(a, data.folders)} · ${ago(a.last)}${a.signin ? " · signed in" : ""}`)),
            el("div", { class: "set-btns" }, btn(t("Change"), () => change(a), "small"),
              btn(t("Remove"), async () => { busy(true); try { await ctx.remove(a.id); } catch (e) { err.textContent = e.message; } busy(false); list(); }, "small danger"))))
          : [el("div", { class: "act-empty" }, t("No AI app is connected yet."))])),
        el("div", { class: "st-gh-note" }, t("Apps that support sign-in can connect with this address. You approve them here.")),
        el("div", { class: "ai-door" }, el("code", {}, data.door), btn(t("Copy"), () => navigator.clipboard.writeText(data.door), "small")));
      actions.replaceChildren(btn(t("Connect an AI app"), pick, "primary"));
    };

    const pick = () => {
      title.textContent = t("Connect an AI app"); err.textContent = "";
      body.replaceChildren(el("div", { class: "act-list" }, ...KINDS.map(([k, label]) =>
        el("button", { class: "todo-row repo-row", type: "button", onclick: () => choose(k, label) },
          el("span", { class: "trash-ic" }, icon("sparkle", 16)), el("div", { class: "act-main" }, el("div", { class: "act-line" }, label))))));
      actions.replaceChildren(btn(t("Back"), list));
    };

    const choose = (kind, label) => {
      title.textContent = t("Connect {0}", label); err.textContent = "";
      const name = el("input", { class: "dlg-input", spellcheck: "false", value: kind === "other" ? "" : label, placeholder: t("Its name, like ChatGPT"), "aria-label": t("Name") });
      const access = accessForm(data.folders);
      body.replaceChildren(name, access.node);
      actions.replaceChildren(btn(t("Back"), pick), btn(t("Make the key"), async () => {
        if (!name.value.trim()) { err.textContent = t("Give it a name."); return; }
        busy(true);
        try { const j = await ctx.add({ name: name.value.trim(), kind, ...access.value() }); busy(false); show(kind, j); }
        catch (e) { err.textContent = e.message; busy(false); }
      }, "primary"));
      name.focus();
    };

    const show = (kind, j) => {
      title.textContent = t("{0} is connected", j.app.name); err.textContent = "";
      const s = setupFor(kind, j.door, j.key, j.engine);
      const copy = btn(t("Copy"), () => navigator.clipboard.writeText(s.text).then(() => { copy.textContent = t("Copied"); }), "small");
      const auto = kind === "claude-code" ? btn(t("Add to Claude Code for me"), async () => {
        busy(true);
        try { const r = await ctx.claudeCode(j.key); err.textContent = r.ok ? "" : r.error; if (r.ok) { auto.textContent = t("Added to Claude Code"); auto.disabled = true; } }
        catch (e) { err.textContent = e.message; }
        busy(false);
      }, "small primary") : null;
      const ext = kind === "claude-desktop" ? btn(t("Download for Claude Desktop"), async () => {
        busy(true);
        try { await ctx.claudeDesktop(); ext.textContent = t("Saved in Downloads"); } catch (e) { err.textContent = e.message; }
        busy(false);
      }, "small primary") : null;
      body.replaceChildren(
        el("div", { class: "st-warn" }, el("span", {}, t("This key shows only once. Paste it into the AI app now."))),
        ...(ext ? [el("div", { class: "set-hint" }, t("1. Download the extension. 2. Double-click it in Downloads: Claude Desktop opens and installs it. 3. Paste the key when it asks."))] : []),
        el("div", { class: "set-title" }, s.where),
        el("pre", { class: "ai-setup" }, s.text),
        el("div", { class: "set-btns" }, ext, copy, auto));
      actions.replaceChildren(btn(t("Done"), list, "primary"));
    };

    const change = (a) => {
      title.textContent = t("What {0} can reach", a.name); err.textContent = "";
      const access = accessForm(data.folders, a);
      body.replaceChildren(access.node);
      actions.replaceChildren(btn(t("Back"), list), btn(t("Save"), async () => {
        busy(true);
        try { await ctx.update({ id: a.id, ...access.value() }); busy(false); list(); } catch (e) { err.textContent = e.message; busy(false); }
      }, "primary"));
    };

    const again = () => { if (!card.isConnected) document.removeEventListener("ai-apps-changed", again); else if (title.textContent === t("AI apps")) list(); };
    document.addEventListener("ai-apps-changed", again);
    list();
    return { tools: [], body: [card], refresh: () => { if (title.textContent === t("AI apps")) list(); } };
}

// Connect an AI app, as its own window (AI menu), shaped like Link a computer: AI agents on this computer, or the
// ways in for agents on the web and phones (docs/phone.md). ctx: as aiAppsView, plus onServer, door, storage(), linkServer().
export function connectDialog(ctx) {
  return modal((done) => {
    const view = aiAppsView(ctx);
    const body = el("div", { class: "lk-body" });
    const seg = el("div", { class: "seg lk-seg", role: "tablist", "aria-label": t("Where the AI app runs") });
    const copyBtn = (text) => { const b = el("button", { class: "btn small", type: "button", onclick: () => navigator.clipboard.writeText(text).then(() => { b.textContent = t("Copied"); }) }, t("Copy")); return b; };
    // One way in: a name, a line, a note on what it opens, and a button where the app can take the next step itself
    const way = (ic, title, line, note, action) => el("div", { class: "aw-row" },
      el("span", { class: "aw-ic" }, icon(ic, 16)),
      el("div", { class: "aw-text" }, el("div", { class: "aw-title" }, title), el("div", { class: "aw-line" }, line), el("div", { class: "aw-note" }, note)),
      action ? el("button", { class: "btn small", type: "button", onclick: () => { done(null); action[1](); } }, action[0]) : null);
    const online = () => ctx.onServer
      ? [el("p", {}, t("Add this address as a custom connector in your agent. Sign in with your passphrase, then press Allow.")),
         el("div", { class: "ai-door" }, el("code", {}, ctx.door), copyBtn(ctx.door))]
      : [el("p", {}, t("Agents on the web and phones can't reach this computer directly. Pick a way in:")),
         el("div", { class: "aw-list" },
           way("laptop", t("Remote control"), t("Control an agent on this computer from your phone."), t("Nothing opens to the internet.")),
           way("cloud", t("Your cloud"), t("Keep an Open memory in iCloud Drive, Dropbox, Google Drive or GitHub."), t("For Open memories."),
             ctx.storage ? [t("Storage"), ctx.storage] : null),
           way("sync", t("Your own server"), t("Run the app on your own server. Works when this computer is off."), t("Protected by your passphrase."),
             ctx.linkServer ? [t("Link@@verb"), ctx.linkServer] : null),
           way("link", t("A tunnel"), t("Give this computer a web address, with Cloudflare Tunnel or similar."), t("Turn it off when you're done."))),
         el("a", { class: "aw-guide", href: "https://github.com/Phygital-Brain/Phygital-Memory/blob/main/docs/phone.md", target: "_blank", rel: "noopener",
           onclick: (e) => { if (ctx.openDoc) { e.preventDefault(); ctx.openDoc("phone"); } } }, t("Read the full guide"), icon("arrow", 13))];
    const tabs = [["here", ctx.onServer ? t("With a key") : t("On this computer")], ["online", t("On the web and phones")]];
    const show = (k) => {
      for (const b of seg.children) { const on = b.dataset.k === k; b.classList.toggle("on", on); b.setAttribute("aria-selected", on); }
      body.replaceChildren(...(k === "here" ? view.body : online()));
    };
    for (const [k, label] of tabs) seg.append(el("button", { class: "seg-b", type: "button", role: "tab", "data-k": k, onclick: () => show(k) }, label));
    const card = el("div", { class: "dlg lk ai-connect", role: "dialog", "aria-label": t("Connect an AI app") },
      el("div", { class: "dlg-title" }, t("Connect an AI app")),
      el("p", { class: "lk-intro" }, t("Each AI app gets its own key and reaches only the memories you pick. You can undo every change it makes.")),
      seg, body,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", type: "button", onclick: () => done(null) }, t("Close"))));
    show("here");
    return { card };
  });
}

// The Allow window: an AI app signed in and waits for the person. Resolves {allow, folders, write}.
export function allowDialog(name, folders, who = "") {
  return modal((done) => {
    const access = accessForm(folders);
    // The buttons wake up after a second, so a click already on its way when this window appears can't say yes.
    const deny = el("button", { class: "btn", type: "button", disabled: true, onclick: () => done({ allow: false }) }, t("Deny"));
    const allow = el("button", { class: "btn primary", type: "button", disabled: true, onclick: () => done({ allow: true, ...access.value() }) }, t("Allow"));
    setTimeout(() => { deny.disabled = allow.disabled = false; }, 1000);
    const card = el("div", { class: "dlg storage ai-apps", role: "dialog" },
      el("div", { class: "dlg-title" }, t("An app that calls itself “{0}” wants to use your notes", name)),
      el("div", { class: "ai-who" }, el("span", { class: "set-hint" }, t("The answer goes to: ")), el("b", {}, who || "a program this Mac can't name")),
      el("div", { class: "st-warn" }, el("span", {}, t("Allow it only if you just started connecting that app, and the line above names it."))),
      el("div", { class: "mf-hint" }, t("It only reaches memories that are open in the app. Change or remove it in Settings › AI apps.")),
      access.node,
      el("div", { class: "dlg-actions" }, deny, allow));
    return { card };
  }).then((v) => v || { allow: false });
}
