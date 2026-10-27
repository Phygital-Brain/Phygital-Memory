// The folder switcher menu and the "create a locked folder" form. Names and paths from the server are only ever
// put in as text.
import { el, icon } from "./dom.js";
import { modal } from "./dialogs.js";
import { closeMenu } from "./menu.js";

// The paths people see: the home folder written as ~.
export const shortPath = (p) => (p || "").replace(/^\/Users\/[^/]+/, "~");

// A small square with the folder's colour and a lock that shows whether it's open.
export function folderTile(f, open, size = 30) {
  return el("span", { class: "fo-tile" + (open ? " open" : ""), style: `width:${size}px;height:${size}px` },
    icon(open ? "unlock" : "lock", Math.round(size * 0.52), 1.8));
}

// One menu row with an icon, a label, and an optional quiet action or shortcut on the right (like Baalda's).
function actionRow(iconName, label, onClick, right) {
  const row = el("div", { class: "fo-action", role: "menuitem", tabindex: "0",
                          onclick: () => { closeMenu(); onClick(); } },
    el("span", { class: "fo-action-icon" }, icon(iconName, 15)), el("span", { class: "fo-action-label" }, label));
  if (right) {
    const r = right.fn
      ? el("button", { class: "fo-action-right link", type: "button",
                       onclick: (e) => { e.stopPropagation(); closeMenu(); right.fn(); } }, right.label)
      : el("span", { class: "fo-action-right" }, right.label);
    row.append(r);
  }
  return { node: row };
}

// ctx: {list, currentId, unlocked(id), switchTo(id), openOther(), createNew(), manage(), storage(), ai(), settings(), lockThis(),
//       lockAll(), home(), finder?: {shown, toggle()}}
export function switcherItems(ctx) {
  const rows = ctx.list.map((f, i) => {
    const on = f.id === ctx.currentId, open = ctx.unlocked(f.id);
    const sub = !f.exists ? "Not found" : (open ? "Unlocked" : "Locked") + (f.finder ? " · open in Finder" : "");
    return {
      node: el("button", {
        class: "fo-row" + (on ? " on" : ""), role: "menuitem", title: f.path,
        onclick: () => { closeMenu(); if (!on) ctx.switchTo(f.id); },
      },
      folderTile(f, open),
      el("span", { class: "fo-text" },
        el("span", { class: "fo-name" }, f.name),
        el("span", { class: "fo-sub" + (f.finder ? " warn" : "") }, sub)),
      i < 9 ? el("span", { class: "fo-key" }, `⌘${i + 1}`) : null),
    };
  });
  const cur = ctx.list.find((f) => f.id === ctx.currentId);
  const anyOpen = ctx.list.some((f) => ctx.unlocked(f.id));
  const items = [...rows, { sep: true },
    actionRow("plus", "New memory", ctx.createNew),
    { label: "Open memory", icon: "folder", cls: "fo-menu-item", sub: [
      { label: "From this Mac", fn: ctx.openOther },
      ...(ctx.fromGithub ? [{ label: "From GitHub", fn: ctx.fromGithub }] : []),
      ...(ctx.fromCloud ? [{ label: "From WebDAV", fn: ctx.fromCloud }] : []),
      ...(ctx.fromS3 ? [{ label: "From Amazon S3 or Cloudflare R2", fn: ctx.fromS3 }] : []),
      ...(ctx.fromBackup ? [{ label: "From a backup file", fn: ctx.fromBackup }] : [])] },
    actionRow("grid", "Manage memories", ctx.manage)];
  if (cur) {
    items.push({ sep: true },
      ...(ctx.storage ? [actionRow(cur.cloudOnly || cur.webdav ? "cloud" : "laptop", "Storage and backup", ctx.storage)] : []),
      ...(ctx.ai ? [actionRow("pulse", "AI tasks and activity", ctx.ai)] : []),
      ...(ctx.finder ? [actionRow("folder", ctx.finder.shown ? "Close the Finder view" : "Show in Finder", ctx.finder.toggle)] : []),
      ...(ctx.settings ? [actionRow("gear", "Settings", ctx.settings, { label: "⌘," })] : []),
      actionRow("lock", "Lock memory", ctx.lockThis, anyOpen ? { label: "Lock all", fn: ctx.lockAll } : null));
  }
  return items;
}

// "Manage folders": every folder with its place and what you can do with it. Nothing here deletes notes.
// actions: {switchTo(id), rename(id), lock(id), forget(id), unlocked(id), createNew(), openOther()}
export function manageFolders(list, actions) {
  return modal((done) => {
    const body = el("div", { class: "mf-list" });
    for (const f of list) {
      const open = actions.unlocked(f.id);
      const btn = (label, fn, cls) => el("button", { class: "btn small " + (cls || ""), type: "button",
                                                     onclick: async () => { done(null); await fn(f.id); } }, label);
      body.append(el("div", { class: "mf-row" },
        folderTile(f, open, 34),
        el("div", { class: "mf-text" },
          el("div", { class: "mf-name" }, f.name),
          el("div", { class: "mf-path", title: f.path }, shortPath(f.path)),
          el("div", { class: "mf-state" + (f.finder ? " warn" : "") },
            !f.exists ? "Not found at this place" : (open ? "Unlocked" : "Locked") + (f.finder ? " · open in Finder" : ""))),
        el("div", { class: "mf-actions" },
          btn(open ? "Open" : "Unlock", actions.switchTo),
          btn("Rename", actions.rename),
          open ? btn("Lock", actions.lock) : null,
          btn("Remove", actions.forget, "danger"))));
    }
    if (!list.length) body.append(el("div", { class: "mf-empty" }, "No folders yet."));
    const card = el("div", { class: "dlg mf", role: "dialog" },
      el("div", { class: "dlg-title" }, "Folders"),
      el("div", { class: "mf-hint" }, "Each memory is encrypted with its own password. Remove only takes it off this list. Nothing is deleted."),
      body,
      el("div", { class: "dlg-actions" },
        el("button", { class: "btn", onclick: () => { done(null); actions.openOther(); } }, "Open memory"),
        el("button", { class: "btn primary", onclick: () => { done(null); actions.createNew(); } }, "New memory")));
    return { card };
  });
}

// A form for a brand new locked folder. `pick()` asks the server to open the Mac's folder chooser and gives
// back a path (or null). Resolves {parent, name, password} or null.
export function createFolderForm(pick) {
  return modal((done) => {
    let parent = "";
    const name = el("input", { class: "dlg-input", spellcheck: "false", placeholder: "Folder name", "aria-label": "Folder name" });
    const pw = el("input", { class: "dlg-input", type: "password", autocomplete: "off", placeholder: "Password (8 or more characters)", "aria-label": "Password" });
    const pw2 = el("input", { class: "dlg-input", type: "password", autocomplete: "off", placeholder: "Password again", "aria-label": "Password again" });
    const where = el("span", { class: "dlg-where" }, "Choose where to make it");
    const err = el("div", { class: "dlg-err" });
    const choose = el("button", { class: "btn small", type: "button", onclick: async () => {
      choose.disabled = true;
      try { const p = await pick(); if (p) { parent = p; where.textContent = p; where.title = p; } }
      catch (e) { err.textContent = e.message; }
      choose.disabled = false;
    } }, icon("folder", 13), "Choose");
    const submit = () => {
      const n = name.value.trim();
      if (!n || /[\/\\:*?"<>|]/.test(n) || n.startsWith(".")) { err.textContent = "Pick a simple name (no / \\ : * ? \" < > |)."; return; }
      if (!parent) { err.textContent = "Choose where to make the folder."; return; }
      if (pw.value.length < 8) { err.textContent = "The password needs at least 8 characters."; return; }
      if (pw.value !== pw2.value) { err.textContent = "The two passwords differ."; return; }
      const out = { parent, name: n, password: pw.value };
      pw.value = pw2.value = "";
      done(out);
    };
    const card = el("div", { class: "dlg", role: "dialog" },
      el("div", { class: "dlg-title" }, "New folder"),
      name, pw, pw2,
      el("div", { class: "dlg-where-row" }, where, choose),
      err,
      el("div", { class: "dlg-actions" },
        el("button", { class: "btn", onclick: () => { pw.value = pw2.value = ""; done(null); } }, "Cancel"),
        el("button", { class: "btn primary", onclick: submit }, "Create")));
    return { card, focus: name, submit };
  });
}
