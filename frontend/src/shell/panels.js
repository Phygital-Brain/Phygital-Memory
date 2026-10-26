// Two small panels from the sidebar's status icons: where this folder is stored, and what AI apps did with it.
// Everything from the server is put in as text only.
import { el, icon } from "./dom.js";
import { modal } from "./dialogs.js";
import { shortPath } from "./folders.js";

const ago = (s) => (s < 45 ? "just now" : s < 3600 ? `${Math.round(s / 60)} min ago` : `${Math.round(s / 3600)} h ago`);
const clock = (t) => new Date(t * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

// ctx: {name, storage: {path, cloud, places:[{name, path}], home}, pick(prompt) -> path|null, move(parent) -> Promise,
//       reveal()}
export function openStorage(ctx) {
  return modal((done) => {
    const s = ctx.storage;
    const err = el("div", { class: "dlg-err" });
    const busy = (b) => card.classList.toggle("busy", b);
    const moveTo = async (parent, label) => {
      err.textContent = "";
      busy(true);
      try { if (await ctx.move(parent, label)) done(true); else busy(false); }
      catch (e) { err.textContent = e.message; busy(false); }
    };
    const option = (key, title, text, on, body) => el("div", { class: "st-opt" + (on ? " on" : "") },
      el("div", { class: "st-opt-head" }, el("span", { class: "st-opt-icon" }, icon(key, 16)),
        el("div", {}, el("div", { class: "st-opt-title" }, title), el("div", { class: "st-opt-text" }, text)),
        on ? el("span", { class: "st-opt-now" }, "Now") : null),
      body || null);

    const local = !s.cloud;
    const cloudCards = el("div", { class: "st-places" }, ...s.places.map((p) => {
      const here = s.cloud && s.path.startsWith(p.path + "/");
      return el("button", { class: "st-place" + (here ? " on" : ""), type: "button", disabled: here, title: p.path,
                            onclick: () => moveTo(p.path, p.name) },
        icon("cloud", 15), el("span", {}, p.name), here ? el("span", { class: "st-here" }, "here") : null);
    }));
    if (!s.places.length) cloudCards.append(el("div", { class: "st-none" }, "No cloud apps found on this Mac (iCloud Drive, Dropbox, Google Drive, OneDrive, Nextcloud…)."));

    const card = el("div", { class: "dlg storage", role: "dialog" },
      el("div", { class: "dlg-title" }, `Where "${ctx.name}" is stored`),
      el("div", { class: "st-where" }, icon(s.cloud ? "cloud" : "laptop", 14), el("span", { title: s.path }, shortPath(s.path)),
        el("button", { class: "btn small", type: "button", onclick: () => ctx.reveal() }, "Show encrypted files")),
      option("laptop", "Only this Mac", "Your notes stay on this computer.", local,
        local ? null : el("button", { class: "btn small", type: "button", onclick: async () => {
          const p = await ctx.pick("Choose a place on this Mac for the folder"); if (p) moveTo(p, "this Mac");
        } }, "Move to a place on this Mac…")),
      option("cloud", "This Mac + cloud", "Kept on this Mac and synced by your cloud app. The cloud only ever sees scrambled files.", !local,
        el("div", {}, cloudCards,
          el("button", { class: "btn small st-other", type: "button", onclick: async () => {
            const p = await ctx.pick("Choose any synced folder"); if (p) moveTo(p, "that folder");
          } }, "Other synced folder…"))),
      option("sparkle", "Cloud only", "Nothing kept on this Mac: the app talks to your cloud directly (Nextcloud, WebDAV, S3). Coming next.", false),
      el("div", { class: "st-note" }, "Moving locks the folder first, so only scrambled files move. You unlock it again after."),
      err,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", onclick: () => done(null) }, "Close")));
    return { card };
  });
}

// ctx: {rows:[{t, ago, app, folderName, what, detail, path}], open(path), todo()}
export function openActivity(ctx) {
  return modal((done) => {
    const apps = [...new Set(ctx.rows.map((r) => r.app))];
    const filter = el("select", { class: "act-filter", "aria-label": "Which app" },
      el("option", { value: "" }, "All AI apps"), ...apps.map((a) => el("option", { value: a }, a)));
    const list = el("div", { class: "act-list" });
    const draw = () => {
      const rows = ctx.rows.filter((r) => !filter.value || r.app === filter.value);
      list.replaceChildren(...(rows.length ? rows.map((r) => {
        const pathBtn = r.path ? el("button", { class: "act-path", type: "button", title: "Open this note",
                                                onclick: () => { done(null); ctx.open(r.path); } }, r.path) : null;
        return el("div", { class: "act-row" + (/changed|added|created/.test(r.what) ? " write" : "") },
          el("div", { class: "act-time", title: new Date(r.t * 1000).toLocaleString() }, clock(r.t), el("span", {}, ago(r.ago))),
          el("div", { class: "act-main" },
            el("div", { class: "act-line" }, el("b", {}, r.app), ` ${r.what} `, pathBtn),
            r.detail ? el("div", { class: "act-detail" }, r.detail) : null,
            el("div", { class: "act-folder" }, r.folderName)));
      }) : [el("div", { class: "act-empty" }, "No AI app has used your notes since they were unlocked.")]));
    };
    filter.addEventListener("change", draw);
    draw();
    const card = el("div", { class: "dlg activity", role: "dialog" },
      el("div", { class: "act-head" }, el("div", { class: "dlg-title" }, "AI activity"),
        el("div", { class: "act-tools" }, el("button", { class: "btn small", type: "button", onclick: () => { done(null); ctx.todo(); } }, "AI tasks"), filter)),
      el("div", { class: "mf-hint" }, "What AI apps did with your unlocked notes. Kept only until you lock."),
      list,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", onclick: () => done(null) }, "Close")));
    return { card };
  });
}

// AI tasks: notes given to the AI, each with what to do. With ctx.path, a box on top gives that note.
// ctx: {path?, label(path), todo:[{id, path, ask, t, done, by, result}], give(ask) -> todo, set(id, done) -> todo,
//       remove(id) -> todo, load() -> todo, open(path)}
export function openAITodo(ctx) {
  return modal((done) => {
    let todo = ctx.todo;
    const err = el("div", { class: "dlg-err" });
    const list = el("div", { class: "act-list todo-list" });
    const act = async (fn) => {
      err.textContent = "";
      try { todo = await fn(); draw(); } catch (e) { err.textContent = e.message; }
    };
    const draw = () => {
      const items = [...todo].sort((a, b) => (a.done - b.done) || (b.t - a.t));
      list.replaceChildren(...(items.length ? items.map((i) => {
        const box = el("input", { type: "checkbox", class: "todo-check", "aria-label": "Done" });
        box.checked = !!i.done;
        box.addEventListener("change", () => act(() => ctx.set(i.id, box.checked)));
        return el("div", { class: "todo-row" + (i.done ? " done" : "") }, box,
          el("div", { class: "act-main" },
            el("button", { class: "act-path", type: "button", title: i.path, onclick: () => { done(null); ctx.open(i.path); } }, ctx.label(i.path)),
            el("div", { class: "act-detail" }, i.ask || "No request: just read it."),
            i.done ? el("div", { class: "todo-result" }, `${i.by && i.by !== "you" ? i.by : "Ticked off by you"}${i.result ? ": " + i.result : ""}`)
                   : el("div", { class: "act-folder" }, `Given ${ago(Math.max(0, Date.now() / 1000 - i.t))}`)),
          el("button", { class: "icon-btn todo-x", type: "button", title: "Remove from the list", "aria-label": "Remove",
                         onclick: () => act(() => ctx.remove(i.id)) }, icon("x", 14)));
      }) : [el("div", { class: "act-empty" }, "Nothing here yet. Open a note and press the sparkle button to give your AI a task.")]));
    };
    draw();
    // Stay current while open: the AI may tick things off meanwhile.
    const tick = setInterval(async () => {
      if (!list.isConnected) { clearInterval(tick); return; }
      try { const t = await ctx.load(); if (JSON.stringify(t) !== JSON.stringify(todo)) { todo = t; draw(); } } catch {}
    }, 4000);

    let give = null, ask = null;
    if (ctx.path) {
      ask = el("textarea", { class: "dlg-input todo-ask", rows: "3", spellcheck: "true",
                             placeholder: "What should the AI do with this note? (optional)\nFor example: fix typos and make it shorter." });
      const add = () => act(async () => {
        const t = await ctx.give(ask.value);
        ask.value = "";
        return t;
      });
      ask.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) { e.preventDefault(); add(); } });
      give = el("div", { class: "todo-give" },
        el("div", { class: "dlg-sub" }, el("b", {}, ctx.label(ctx.path))),
        ask,
        el("div", { class: "dlg-actions" }, el("button", { class: "btn primary", type: "button", onclick: add }, "Add task")));
    }
    const card = el("div", { class: "dlg activity", role: "dialog" },
      el("div", { class: "dlg-title" }, ctx.path ? "Give AI a task" : "AI tasks"),
      give,
      el("div", { class: "mf-hint" }, "Your AI works through these tasks when you ask it to, for example: “Do my Phygital Memory tasks.” Its changes can be undone in each note’s version history."),
      list, err,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", onclick: () => done(null) }, "Close")));
    return { card, focus: ask };
  });
}
