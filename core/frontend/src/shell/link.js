// Linking your own computers (server: linking.py), in one window with three ways in:
// - A server: type its address and passphrase; this computer signs in there, makes the link, has the server join
//   it and checks both sides show the same safety words, so only the memories and the Link press are left.
// - Show a link: this computer shows a one-time link; the other one pastes it.
// - Paste a link: the other way round.
// Both sides show the same four safety words. The memories picked then stay in step, still locked.
import { t } from "./i18n.js";
import { el, icon } from "./dom.js";
import { modal } from "./dialogs.js";

// ctx: {onServer (only says how to link from the computer), address, start(), status(), answer(ids, seen), cancel(), join(link), wait(), serverStart(url, pass),
// serverWait(), serverCancel()}. tab: "server" | "show" | "paste". Resolves {name, memories} or {from, memories} once
// linked, or null.
export function linkDialog(ctx, tab = "server") {
  return modal((done) => {
    let timer = null, gen = 0, cleanup = null;
    const stopTimer = () => { clearInterval(timer); timer = null; };
    const leave = async () => { stopTimer(); const c = cleanup; cleanup = null; if (c) await c(); };
    const stop = async (v) => { if (!v) await leave(); else stopTimer(); done(v); };
    const body = el("div", { class: "lk-body" });
    const err = el("div", { class: "dlg-err", role: "alert" });
    const go = el("button", { class: "btn primary", type: "button" });
    const tabs = [["server", t("To my server")], ["show", t("Send to a computer")], ["paste", t("Receive from a computer")]];
    // Which way the memories go, said first on every tab
    const way = (from, to) => el("div", { class: "lk-way" }, el("b", {}, from), icon("arrow", 14, 2), el("b", {}, to));
    const seg = el("div", { class: "seg lk-seg", role: "tablist", "aria-label": t("How to link") });
    const card = el("div", { class: "dlg lk", role: "dialog", "aria-label": t("Link a computer") },
      el("div", { class: "dlg-title" }, t("Link a computer")),
      el("p", { class: "lk-intro" }, t("The memories you pick stay in step between your computers, each still locked with its same password.")),
      seg, body, err,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", type: "button", onclick: () => stop(null) }, t("Cancel")), go));

    const steps = (items) => el("ol", { class: "lk-steps" }, ...items.map(([text, state]) =>
      el("li", { class: "lk-step " + state }, el("span", { class: "lk-dot", "aria-hidden": "true" }, state === "done" ? icon("check", 12, 2.2) : null), el("span", {}, text))));
    const button = (label, fn) => { go.textContent = label; go.classList.toggle("hidden", !label); go.disabled = false; go.onclick = fn; };

    // The memories to send, and the Link press (this computer is the one that showed or made the link)
    const asking = (s, my, intro) => {
      const boxes = s.memories.map((m) => el("input", { type: "checkbox", checked: true, value: m.id, "aria-label": m.name }));
      body.replaceChildren(intro,
        el("div", { class: "lk-sub" }, s.memories.length ? t("Memories it gets") : t("No memories on this computer to send yet.")),
        ...s.memories.map((m, i) => el("label", { class: "link-mem" }, boxes[i], " ", m.name)),
        el("p", { class: "lk-note" }, t("It becomes you: it can open what's shared with you. Things you share keep running from this computer.")));
      button(t("Link"), async () => {
        go.disabled = true; err.textContent = "";
        try {
          const r = await ctx.answer(boxes.filter((b) => b.checked).map((b) => b.value), s.seen);
          if (my !== gen) return;
          if (tab !== "server") return stop(r);
          body.replaceChildren(steps([[t("Linked here"), "done"], [t("The server takes it in"), "now"]]));
          button("", null);
          let polling = false;
          timer = setInterval(async () => {
            if (polling) return;
            polling = true;
            try {
              const w = await ctx.serverWait();
              if (w.state === "done") { cleanup = null; stop(r); }
              if (w.state === "none") { stopTimer(); err.textContent = t("The server stopped the link. Start again."); }
            } catch (e) { err.textContent = e.message; } finally { polling = false; }
          }, 2000);
        } catch (e) { err.textContent = e.message; go.disabled = false; }
      });
    };

    // Wait here until the other side's request comes in, then hand over to onAsk
    const waitForRequest = (my, onAsk) => {
      let seen = false;
      timer = setInterval(async () => {
        if (seen || my !== gen) return;
        let st;
        try { st = await ctx.status(); } catch { return; }
        if (st.state === "expired") { stopTimer(); err.textContent = t("This link ran out. Start again."); }
        if (st.state === "asking") { seen = true; stopTimer(); onAsk(st); }
      }, 2000);
    };

    const views = {
      server(my) {
        const addr = el("input", { class: "dlg-input", placeholder: "memory.example.com", spellcheck: "false", autocomplete: "url", "aria-label": t("Server address") });
        const pass = el("input", { class: "dlg-input", type: "password", placeholder: t("Server passphrase"), "aria-label": t("Server passphrase") });
        body.replaceChildren(way(t("This computer"), t("Your server")),
          el("label", { class: "lk-sub" }, t("Server address")), addr,
          el("label", { class: "lk-sub" }, t("Server passphrase")), pass,
          el("p", { class: "lk-note" }, t("This computer signs in to your server, links it and checks the safety words for you.")));
        const connect = async () => {
          if (!addr.value.trim() || !pass.value) { err.textContent = t("Type the server's address and passphrase."); return; }
          button("", null); err.textContent = "";
          const typed = addr.value.trim();
          body.replaceChildren(steps([[t("Signing in to your server and getting this computer ready. The first time takes up to half a minute."), "now"],
            [t("Linking"), ""], [t("Checking the safety words"), ""]]));
          let s;
          try { s = await ctx.serverStart(typed, pass.value); }
          catch (e) { if (my === gen) { views.server(my); err.textContent = e.message; } return; }
          if (my !== gen) return;
          cleanup = ctx.serverCancel;
          body.replaceChildren(steps([[t("Signed in to {0}", s.server.replace(/^https?:\/\//, "")), "done"],
            [t("Waiting for the server to answer. This can take a minute."), "now"], [t("Checking the safety words"), ""]]));
          button("", null);
          waitForRequest(my, (st) => {
            if (st.words !== s.words) { err.textContent = t("The safety words don't match, so nothing was linked. Start again."); leave(); return; }
            asking(st, my, steps([[t("Signed in"), "done"], [t("The server asked to link"), "done"], [t("Safety words match: {0}", st.words), "done"]]));
          });
        };
        button(t("Connect"), connect);
        pass.addEventListener("keydown", (e) => { if (e.key === "Enter") connect(); });
        setTimeout(() => addr.focus(), 0);
      },
      async show(my) {
        button("", null);
        body.replaceChildren(el("p", { class: "lk-note" }, t("Making a link.")));
        let s;
        try { s = await ctx.start(); } catch (e) { err.textContent = e.message; return; }
        if (my !== gen) return;
        cleanup = ctx.cancel;
        const box = el("textarea", { class: "dlg-input rk-input link-box", rows: "3", readonly: true, spellcheck: "false", "aria-label": t("Link") }, s.link);
        const copy = el("button", { class: "btn small", type: "button", onclick: () => navigator.clipboard.writeText(s.link).then(() => { copy.textContent = t("Copied"); }) }, t("Copy"));
        body.replaceChildren(way(t("This computer"), t("Your other computer")),
          steps([[t("Copy this link. It works once, for {0} minutes.", s.minutes), "now"],
            [t("On the other computer, open Link a computer, choose Receive from a computer and paste it."), ""],
            [t("Check the safety words match, then press Link here."), ""]]),
          box, el("div", { class: "lk-row" }, copy, el("span", { class: "lk-note" }, t("Waiting for the other computer."))));
        waitForRequest(my, (st) => asking(st, my, el("div", {},
          el("div", { class: "lk-sub" }, t("\"{0}\" asks to be linked. Its safety words must match:", st.name)),
          el("div", { class: "link-words" }, st.words))));
      },
      paste(my) {
        const box = el("textarea", { class: "dlg-input rk-input link-box", rows: "3", spellcheck: "false", placeholder: t("Paste the link from your other computer"), "aria-label": t("Link") });
        body.replaceChildren(way(t("Your other computer"), t("This computer")),
          steps([[t("On the other computer, open Link a computer and choose Send to a computer."), "now"], [t("Paste that link here and press Next."), ""], [t("Check the safety words match, then press Link there."), ""]]),
          box);
        button(t("Next"), async () => {
          go.disabled = true; err.textContent = "";
          let w;
          try { w = await ctx.join(box.value.trim()); }
          catch (e) { err.textContent = e.message; go.disabled = false; return; }
          if (my !== gen) return;
          cleanup = ctx.cancel;
          button("", null);
          body.replaceChildren(el("div", { class: "lk-sub" }, t("Check the other computer shows these same safety words, then press Link there:")),
            el("div", { class: "link-words" }, w.words), el("p", { class: "lk-note" }, t("Keep this window open.")));
          let polling = false;
          timer = setInterval(async () => {
            if (polling) return;
            polling = true;
            let s;
            try { s = await ctx.wait(); } catch (e) { err.textContent = e.message; return; } finally { polling = false; }
            if (s.state === "done") { cleanup = null; stop(s); }
            if (s.state === "none") { stopTimer(); err.textContent = t("The link stopped. Start again on the other computer."); }
          }, 2000);
        });
        setTimeout(() => box.focus(), 0);
      },
    };

    const pick = async (k) => {
      await leave();
      tab = k; gen += 1; err.textContent = "";
      seg.replaceChildren(...tabs.map(([key, label]) => el("button", { class: "seg-b" + (key === k ? " on" : ""), type: "button", role: "tab",
        "aria-selected": String(key === k), onclick: () => { if (key !== tab) pick(key); } }, label)));
      views[k](gen);
    };
    if (ctx.onServer) {   // a server is linked from the computer, which dials it directly: say how, with the address
      const copy = el("button", { class: "btn small", type: "button", onclick: () => navigator.clipboard.writeText(ctx.address).then(() => { copy.textContent = t("Copied"); }) }, t("Copy"));
      seg.replaceWith(el("div", { class: "lk-tip" },
        el("p", {}, t("Link this server from your computer: in the Phygital Memory app, open Link a computer, choose To my server and type this address:")),
        el("div", { class: "lk-row" }, el("code", {}, ctx.address), copy),
        el("p", {}, t("Then type this server's passphrase and press Connect. The app does the rest."))));
      body.remove();
      button("", null);
      return { card };
    }
    pick(tab);
    return { card };
  });
}
