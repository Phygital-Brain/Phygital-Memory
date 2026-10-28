// The folder switcher menu. Names and paths from the server are only ever
// put in as text.
import { t } from "./i18n.js";
import { el, icon } from "./dom.js";
import { modal } from "./dialogs.js";
import { closeMenu } from "./menu.js";

// The paths people see: the home folder written as ~.
export const shortPath = (p) => (p || "").replace(/^\/Users\/[^/]+/, "~");

// A small square with the folder's colour and a lock that shows whether it's open.
// Open memories are purple with lime, Encrypted ones lime with purple.
export function folderTile(f, open, size = 30) {
  const plain = f?.kind === "open";
  return el("span", { class: "fo-tile" + (open ? " open" : "") + (plain ? " k-open" : " k-encrypted"), style: `width:${size}px;height:${size}px` },
    icon(plain ? "folder" : open ? "unlock" : "lock", Math.round(size * 0.52), 1.8));
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
    const sub = !f.exists ? "Not found" : f.kind === "open" ? t("Open · a normal folder") : (open ? "Unlocked" : "Locked") + (f.finder ? " · open in Finder" : "");
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
  const anyOpen = ctx.list.some((f) => ctx.unlocked(f.id) && f.kind !== "open");
  const mine = rows.filter((_, i) => !ctx.list[i].joined), theirs = rows.filter((_, i) => ctx.list[i].joined);
  const items = [...mine, ...(theirs.length ? [{ sep: true }, { node: el("div", { class: "fo-head" }, t("Shared with me")) }, ...theirs] : []), { sep: true },
    actionRow("plus", t("New memory"), ctx.createNew),
    { label: t("Add memory"), icon: "folder", cls: "fo-menu-item", sub: [
      { label: t("From this Mac"), fn: ctx.openOther },
      ...(ctx.fromGithub ? [{ label: t("From GitHub"), fn: ctx.fromGithub }] : []),
      ...(ctx.fromCloud ? [{ label: t("From WebDAV"), fn: ctx.fromCloud }] : []),
      ...(ctx.fromS3 ? [{ label: t("From Amazon S3 or Cloudflare R2"), fn: ctx.fromS3 }] : []),
      ...(ctx.fromBackup ? [{ label: t("From a backup file"), fn: ctx.fromBackup }] : []),
      ...(ctx.fromInvite ? [{ label: t("From an invite"), fn: ctx.fromInvite }] : []),
      ...(ctx.fromMac ? [{ label: t("From my other Mac"), fn: ctx.fromMac }] : [])] },
    actionRow("grid", t("Manage memories"), ctx.manage)];
  if (cur) {
    items.push({ sep: true },
      ...(ctx.storage ? [actionRow(cur.cloudOnly || cur.webdav ? "cloud" : "laptop", t("Storage and backup"), ctx.storage)] : []),
      ...(ctx.share ? [actionRow("share", "Share", ctx.share)] : []),
      ...(ctx.ai ? [actionRow("pulse", t("AI tasks and activity"), ctx.ai)] : []),
      ...(ctx.finder ? [actionRow("folder", ctx.finder.shown && cur.kind !== "open" ? "Close the Finder view" : t("Show in Finder"), ctx.finder.toggle)] : []),
      ...(ctx.settings ? [actionRow("gear", "Settings", ctx.settings, { label: "⌘," })] : []),
      ...(ctx.lockThis ? [actionRow("lock", t("Lock memory"), ctx.lockThis, anyOpen ? { label: t("Lock all"), fn: ctx.lockAll } : null)] : []));
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
            !f.exists ? "Not found at this place" : f.kind === "open" ? t("Open · a normal folder") : (open ? "Unlocked" : "Locked") + (f.finder ? " · open in Finder" : ""))),
        el("div", { class: "mf-actions" },
          btn(open || f.kind === "open" ? t("Open") : t("Unlock"), actions.switchTo),
          btn(t("Rename"), actions.rename),
          open && f.kind !== "open" ? btn(t("Lock"), actions.lock) : null,
          btn(t("Remove"), actions.forget, "danger"))));
    }
    if (!list.length) body.append(el("div", { class: "mf-empty" }, t("No memories yet.")));
    const card = el("div", { class: "dlg mf", role: "dialog" },
      el("div", { class: "dlg-title" }, t("Memories")),
      el("div", { class: "mf-hint" }, t("Open memories are normal folders. Encrypted ones each have their own password. Remove only takes a memory off this list. Nothing is deleted.")),
      body,
      el("div", { class: "dlg-actions" },
        el("button", { class: "btn", onclick: () => { done(null); actions.openOther(); } }, t("Add memory")),
        el("button", { class: "btn primary", onclick: () => { done(null); actions.createNew(); } }, t("New memory"))));
    return { card };
  });
}
