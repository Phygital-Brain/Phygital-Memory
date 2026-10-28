// "Make it a Phygital Brain": one page of clicks, no typing. Pick blocks (every one starts on a sensible answer), the
// app builds the folders, rules and first notes at once, then connect an AI (or skip), then one sentence to paste
// that lets the AI finish the rest. ctx: {api, language(), openAI(tab), done(), files()}.
import { el, icon, knot } from "./dom.js";
import { t } from "./i18n.js";
import { toastOk, toastErr } from "./toast.js";

const STEPS = () => [t("Pick"), t("Build"), t("Connect"), t("Finish")];

export function renderSetup(body, ctx) {
  const picks = { you: "creator", help: ["projects", "people"], people: ["Clients"], brief: "yes", talk: "short", lang: "en" };
  const BLOCKS = () => [
    { key: "you", title: t("You are"), one: true, options: [["creator", t("Freelancer or creator")], ["business", t("Small business")], ["job", t("Employee")], ["personal", t("Personal projects")]] },
    { key: "help", title: t("It helps you with"), options: [["projects", t("Projects")], ["people", t("People")], ["writing", t("Writing")], ["goals", t("Goals and decisions")]] },
    { key: "people", title: t("You work with"), options: [["Clients", t("Clients")], ["Collaborators", t("Collaborators")], ["Team", t("A team")], ["Partners", t("Partners or press")], ["none", t("Just me")]] },
    { key: "brief", title: t("A morning brief"), one: true, options: [["yes", t("Every work day")], ["no", t("Not now")]] },
    { key: "talk", title: t("Your AI talks"), one: true, options: [["short", t("Short and plain")], ["detailed", t("Detailed")], ["friendly", t("Friendly")], ["formal", t("Formal")]] },
  ];
  const label = (b) => { const o = Object.fromEntries(b.options); const v = picks[b.key]; return [].concat(v).map((x) => o[x]).join(", "); };
  let step = 0;

  const rail = el("ol", { class: "su-rail", "aria-label": t("Steps") });
  const drawRail = () => rail.replaceChildren(...STEPS().map((s, i) =>
    el("li", { class: "su-step" + (i === step ? " on" : i < step ? " done" : ""), "aria-current": i === step ? "step" : null },
      i < step ? icon("check", 12, 2.4) : null, s)));
  const stage = el("div", { class: "su-stage" });
  const go = (i, draw) => { step = i; drawRail(); stage.replaceChildren(...draw()); stage.querySelector("button.primary")?.focus(); };

  // 1. Pick: blocks, all clicks
  const pickView = () => {
    const blocks = BLOCKS().map((b) => {
      const row = el("div", { class: "su-chips", role: b.one ? "radiogroup" : "group", "aria-label": b.title });
      const draw = () => row.replaceChildren(...b.options.map(([v, text]) => {
        const on = b.one ? picks[b.key] === v : picks[b.key].includes(v);
        return el("button", { class: "su-chip" + (on ? " on" : ""), type: "button", role: b.one ? "radio" : "checkbox",
          "aria-checked": on ? "true" : "false",
          onclick: () => {
            if (b.one) picks[b.key] = v;
            else if (v === "none") picks[b.key] = ["none"];
            else {
              const cur = picks[b.key].filter((x) => x !== "none");
              picks[b.key] = cur.includes(v) ? (cur.length > 1 ? cur.filter((x) => x !== v) : cur) : [...cur, v];
            }
            draw();
          } }, on ? icon("check", 12, 2.4) : null, text);
      }));
      draw();
      return el("section", { class: "su-block" }, el("h3", { class: "su-q" }, b.title), row);
    });
    // Language first: the app's, the Mac's, or any other ready one
    const langRow = el("div", { class: "su-chips", role: "radiogroup", "aria-label": t("Brain language") });
    const other = el("select", { class: "set-select su-lang hidden", "aria-label": t("Other language") });
    ctx.api("brainlanguages").then((j) => {
      const all = j.languages || [["en", "English"]];
      const name = (c) => (all.find(([x]) => x === c) || [])[1];
      const fit = (want) => (all.find(([c]) => c.toLowerCase() === want.toLowerCase()) || all.find(([c]) => c.split("-")[0] === want.split("-")[0].toLowerCase()) || [])[0];
      const app = fit(ctx.language()), mac = fit(navigator.language || "en");
      other.replaceChildren(...all.map(([c, n]) => el("option", { value: c }, n)));
      const choices = [];
      if (app) choices.push(["app", t("App language ({0})", name(app)), app]);
      if (mac && mac !== app) choices.push(["mac", t("Mac language ({0})", name(mac)), mac]);
      choices.push(["other", t("Other"), null]);
      let picked = choices[0][0];
      picks.lang = choices[0][2] || "en";
      other.value = picks.lang;
      const draw = () => langRow.replaceChildren(...choices.map(([k, text, code]) => el("button", {
        class: "su-chip" + (k === picked ? " on" : ""), type: "button", role: "radio", "aria-checked": k === picked ? "true" : "false",
        onclick: () => {
          picked = k;
          other.classList.toggle("hidden", k !== "other");
          picks.lang = code || other.value;
          if (k === "other") other.focus();
          draw();
        } }, k === picked ? icon("check", 12, 2.4) : null, text)));
      draw();
    }).catch(() => {});
    other.addEventListener("change", () => { picks.lang = other.value; });
    return [
      el("p", { class: "su-lead" }, t("Tap what fits. Everything starts on a good answer, so you can build right away.")),
      el("section", { class: "su-block" }, el("h3", { class: "su-q" }, t("Your brain's language")),
        langRow, other, el("p", { class: "su-note" }, t("For folder names and rules. Your notes stay in whatever language you write."))),
      ...blocks,
      el("div", { class: "su-actions" },
        el("button", { class: "btn", type: "button", onclick: () => ctx.done() }, t("Not now")),
        el("button", { class: "btn primary", type: "button", onclick: () => go(1, buildView) }, t("Build my brain"))),
    ];
  };

  // 2. Build: the folders appear one by one while the app makes them
  const buildView = () => {
    const list = el("ul", { class: "su-build", "aria-live": "polite" });
    const status = el("p", { class: "su-lead" }, t("Building your brain"));
    const next = el("button", { class: "btn primary", type: "button", disabled: true, onclick: () => go(2, connectView) }, t("Next"));
    const choice = {
      people: picks.people.filter((x) => x !== "none"), brief: picks.brief === "yes",
      labels: Object.fromEntries(BLOCKS().map((b) => [b.title, label(b)])),
    };
    (async () => {
      try {
        const plan = (await ctx.api("brainplan", { picks: choice, lang: picks.lang })).folders || [];
        const built = ctx.api("brainbuild", { picks: choice, lang: picks.lang, tz: Intl.DateTimeFormat().resolvedOptions().timeZone });
        for (const [i, f] of plan.entries()) {   // a calm, quick roll call: the build itself takes about a second
          await new Promise((r) => setTimeout(r, i ? 70 : 0));
          list.append(el("li", { class: "su-row" }, icon("folder", 14), el("span", {}, f)));
        }
        const j = await built;
        list.append(el("li", { class: "su-row su-done" }, icon("check", 14, 2.4), el("span", {}, t("Rules, today's note and your About note"))));
        status.textContent = t("Built: {0} folders and notes. Yours to use now.", (j.made || []).length + plan.length);
        next.disabled = false;
        next.focus();
        ctx.files();
      } catch (e) { status.textContent = e.message; toastErr(e.message); }
    })();
    return [status, list, el("div", { class: "su-actions" }, next)];
  };

  // 3. Connect an AI: one button per app, or skip
  const connectView = () => {
    const out = el("div", { class: "su-connected", "aria-live": "polite" });
    const key = async (name, kind) => (await ctx.api("aiappadd", { name, kind, folders: "all", write: true })).key;
    const tick = (text) => out.replaceChildren(el("span", { class: "su-ok" }, icon("check", 14, 2.4), text));
    const way = (title, hint, btn, fn) => el("div", { class: "su-way" },
      el("div", {}, el("div", { class: "su-way-t" }, title), el("div", { class: "su-note" }, hint)),
      el("button", { class: "btn", type: "button", onclick: async (e) => {
        const b = e.currentTarget; b.disabled = true;
        try { await fn(); } catch (x) { toastErr(x.message); }
        b.disabled = false;
      } }, btn));
    const already = el("p", { class: "su-note" });
    ctx.api("aiapps").then((j) => { if ((j.apps || []).length) already.textContent = t("Already connected: {0}.", j.apps.map((a) => a.name).join(", ")); }).catch(() => {});
    return [
      el("p", { class: "su-lead" }, t("Your AI finishes the brain: it asks a few questions and writes your About notes. Connect one, or skip and do it later.")),
      already,
      way("Claude Code", t("Adds it for you."), t("Add to Claude Code"), async () => {
        const r = await ctx.api("claudecodeadd", { key: await key("Claude Code", "claude-code") });
        if (!r.ok) throw new Error(r.error || t("Claude Code isn't on this Mac."));
        tick(t("Claude Code is connected."));
      }),
      way("Claude Desktop", t("Saves an extension in Downloads. Double-click it, then paste the key it asks for."), t("Download"), async () => {
        const k = await key("Claude Desktop", "claude-desktop");
        await ctx.api("claudedesktopext");
        await navigator.clipboard.writeText(k).catch(() => {});
        tick(t("Saved in Downloads. Your key is copied: paste it when Claude Desktop asks."));
      }),
      way(t("Another AI app"), t("Codex, Cursor and others: the AI window has the setup."), t("Open"), async () => ctx.openAI("apps")),
      out,
      el("div", { class: "su-actions" },
        el("button", { class: "btn", type: "button", onclick: () => go(3, finishView) }, t("Skip")),
        el("button", { class: "btn primary", type: "button", onclick: () => go(3, finishView) }, t("Next"))),
    ];
  };

  // 4. Finish: one sentence for the AI; the task with everything it needs is already waiting
  const finishView = () => {
    const say = t("Do my Phygital Memory tasks.");
    const copy = el("button", { class: "btn primary", type: "button", onclick: async () => {
      await navigator.clipboard.writeText(say).catch(() => {});
      copy.textContent = t("Copied"); toastOk(t("Paste it in your AI chat."));
    } }, t("Copy"));
    return [
      el("p", { class: "su-lead" }, t("Paste this in your AI's chat. It reads your picks from its task, asks what it still needs, and finishes your brain.")),
      el("div", { class: "su-say" }, el("span", {}, say), copy),
      el("p", { class: "su-note" }, t("No AI yet? Your brain works already. The task waits on Home until you connect one.")),
      el("div", { class: "su-actions" }, el("button", { class: "btn primary", type: "button", onclick: () => ctx.done() }, t("Open my brain"))),
    ];
  };

  drawRail();
  body.replaceChildren(el("div", { class: "su" },
    el("header", { class: "su-head" }, knot(40), el("div", {},
      el("h1", { class: "su-title" }, t("Make it a Phygital Brain")),
      el("p", { class: "su-sub" }, t("Folders, rules and notes your AI files into. About a minute, all clicks.")))),
    rail, stage));
  go(0, pickView);
}
