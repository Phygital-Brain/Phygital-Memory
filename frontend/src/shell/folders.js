// The folder switcher menu and the "create a locked folder" form. Names and paths from the server are only ever
// put in as text.
import { el, icon } from "./dom.js";
import { modal } from "./dialogs.js";
import { closeMenu } from "./menu.js";

// ctx: {list, currentId, unlocked(id), switchTo(id), openOther(), createNew(), rename(), lockThis(), lockAll(), forget()}
export function switcherItems(ctx) {
  const rows = ctx.list.map((f) => {
    const on = f.id === ctx.currentId, open = ctx.unlocked(f.id);
    return {
      node: el("button", {
        class: "fo-row" + (on ? " on" : ""), role: "menuitem", title: f.path,
        onclick: () => { closeMenu(); if (!on) ctx.switchTo(f.id); },
      },
      el("span", { class: "fo-dot" + (open ? " open" : ""), title: open ? "Unlocked" : "Locked" }),
      el("span", { class: "fo-text" },
        el("span", { class: "fo-name" }, f.name),
        el("span", { class: "fo-path" }, f.exists ? f.path : f.path + " (not found)")),
      f.finder ? el("span", { class: "fo-badge", title: "Open in Finder: any app can read these files" }, "Finder") : null,
      on ? el("span", { class: "mi-check" }, "✓") : null),
    };
  });
  const items = [...rows, { sep: true },
    { label: "Open another locked folder…", fn: ctx.openOther },
    { label: "Create a new locked folder…", fn: ctx.createNew }];
  if (ctx.list.some((f) => f.id === ctx.currentId)) {
    items.push({ sep: true },
      { label: "Rename…", fn: ctx.rename },
      { label: "Lock this folder", fn: ctx.lockThis },
      { label: "Remove from list…", cls: "danger", fn: ctx.forget });
  }
  if (ctx.list.some((f) => ctx.unlocked(f.id))) items.push({ sep: true }, { label: "Lock all", fn: ctx.lockAll });
  return items;
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
    } }, icon("folder", 13), "Choose…");
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
      el("div", { class: "dlg-title" }, "Create a new locked folder"),
      name, pw, pw2,
      el("div", { class: "dlg-where-row" }, where, choose),
      err,
      el("div", { class: "dlg-actions" },
        el("button", { class: "btn", onclick: () => { pw.value = pw2.value = ""; done(null); } }, "Cancel"),
        el("button", { class: "btn primary", onclick: submit }, "Create")));
    return { card, focus: name, submit };
  });
}
