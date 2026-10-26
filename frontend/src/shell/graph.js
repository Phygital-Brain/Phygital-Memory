// Graph view: every note is a glowing dot, every [[link]] a soft thread, on a deep gradient (the Obsidian / Baalda
// look). sigma.js draws it on the GPU (WebGL) with our glow program; d3-force lays it out in a background thread.
// Both libraries are free (MIT / ISC) and load only when the graph is first opened.
import { el } from "./dom.js";

const SETTINGS_KEY = "pm.graph.settings.v1";
const DEFAULTS = { repel: -220, linkDistance: 70, linkStrength: 0.35, gravity: 0.6, nodeSize: 1, lineWidth: 1,
                   labels: 1, colorBy: "links", hideOrphans: false };
const RANGES = {
  repel: ["Repel force", -1200, -10, 10], linkDistance: ["Link distance", 10, 300, 5], linkStrength: ["Link force", 0, 1, 0.05],
  gravity: ["Centre force", 0, 2, 0.05], nodeSize: ["Node size", 0.4, 3, 0.1], lineWidth: ["Line thickness", 0.3, 3, 0.1],
  labels: ["Labels", 0, 3, 0.1],
};

let libs = null;
function loadLibs() {
  libs ??= Promise.all([import("sigma"), import("graphology"), import("./graph-glow.js")])
    .then(([sigma, graphology, glow]) => ({ Sigma: sigma.default, Graph: graphology.default, Glow: glow.NodeGlowProgram }));
  return libs;
}

const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
function rgb(color) {
  const c = document.createElement("canvas").getContext("2d");
  c.fillStyle = color || "#888"; const s = c.fillStyle;
  if (s.startsWith("#")) return [1, 3, 5].map((i) => parseInt(s.slice(i, i + 2), 16));
  return (s.match(/[\d.]+/g) || [136, 136, 136]).slice(0, 3).map(Number);
}
const mix = (a, b, t) => a.map((v, i) => Math.round(v + (b[i] - v) * t));
const hex = (c) => "#" + c.map((v) => v.toString(16).padStart(2, "0")).join("");
// sigma blends with premultiplied alpha: the colour must already be scaled by its transparency
const rgba = (c, a) => `rgba(${Math.round(c[0] * a)},${Math.round(c[1] * a)},${Math.round(c[2] * a)},${a})`;

function loadSettings() {
  try { return { ...DEFAULTS, ...JSON.parse(localStorage.getItem(SETTINGS_KEY) || "{}") }; } catch { return { ...DEFAULTS }; }
}
function saveSettings(s) { try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(s)); } catch {} }

export function createGraph({ onOpen, colorFor, labelFor }) {
  const host = el("div", { class: "graph-canvas", tabindex: "0", "aria-label": "Graph of linked notes" });
  const info = el("span", { class: "graph-info" });
  const localBox = el("input", { type: "checkbox", "aria-label": "Local graph" });
  const find = el("input", { type: "search", class: "graph-find", placeholder: "Find a note…", "aria-label": "Find a note in the graph" });
  const panelBtn = el("button", { class: "btn small", onclick: () => panel.classList.toggle("hidden") }, "Settings");
  const bar = el("div", { class: "graph-bar" },
    find,
    el("label", { class: "set-check", title: "Only the open note and what it links to, two steps out" }, localBox, "Local"),
    el("button", { class: "btn small", onclick: () => worker?.postMessage({ type: "reheat" }) }, "Shake"),
    el("button", { class: "btn small", onclick: () => fit() }, "Fit"),
    panelBtn, info);
  const panel = el("div", { class: "graph-panel hidden" });
  const empty = el("div", { class: "graph-empty hidden" }, "No notes to show yet.");
  const root = el("div", { class: "graph" }, host, bar, panel, empty);

  let s = loadSettings();
  let data = { nodes: [], edges: [] }, current = null, alive = true;
  let L = null, graph = null, renderer = null, worker = null, ids = [], idx = new Map();
  const pos = new Map();
  let hovered = null, hood = null, query = "", dragged = null, dragMoved = false, settled = false;
  let theme = {};

  // ---------- settings panel ----------
  function buildPanel() {
    const rows = Object.entries(RANGES).map(([key, [label, min, max, step]]) => {
      const out = el("span", { class: "graph-val" }, String(s[key]));
      const input = el("input", { type: "range", min, max, step, value: s[key], "aria-label": label });
      input.addEventListener("input", () => {
        s[key] = Number(input.value); out.textContent = String(s[key]); saveSettings(s);
        if (["repel", "linkDistance", "linkStrength", "gravity"].includes(key)) worker?.postMessage({ type: "settings", settings: s });
        else restyle();
      });
      return el("label", { class: "graph-row" }, el("span", {}, label), input, out);
    });
    const colorSel = el("select", { "aria-label": "Colour by" },
      el("option", { value: "links" }, "Colour by links"), el("option", { value: "folder" }, "Colour by folder"));
    colorSel.value = s.colorBy;
    colorSel.addEventListener("change", () => { s.colorBy = colorSel.value; saveSettings(s); restyle(); });
    const orphans = el("input", { type: "checkbox" }); orphans.checked = s.hideOrphans;
    orphans.addEventListener("change", () => { s.hideOrphans = orphans.checked; saveSettings(s); rebuild(); });
    const reset = el("button", { class: "btn small", onclick: () => { s = { ...DEFAULTS }; saveSettings(s); buildPanel(); worker?.postMessage({ type: "settings", settings: s }); restyle(); } }, "Reset");
    panel.replaceChildren(el("div", { class: "graph-panel-title" }, "Graph"), colorSel,
      el("label", { class: "set-check" }, orphans, "Hide notes without links"), ...rows, reset);
  }

  function readTheme() {
    const dark = (document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark")) === "dark";
    theme = { dark, text: css("--text"), dim: css("--text-2"), faint: css("--text-faint"), accent: rgb(css("--accent")),
              textRgb: rgb(css("--text")), low: rgb(dark ? "#5d5d72" : "#a9a6bd"), bg: css("--bg-surface"),
              font: css("--font-body") || "system-ui" };
  }

  // ---------- data -> graph ----------
  function nodeColor(p, deg, maxDeg) {
    if (s.colorBy === "folder") return colorFor(p);
    const t = maxDeg ? Math.pow(deg / maxDeg, 0.55) : 0;
    return hex(mix(theme.low, theme.accent, t));
  }

  function build() {
    const { Graph } = L;
    const all = new Set(data.nodes);
    const edges = data.edges.filter(([a, b]) => all.has(a) && all.has(b) && a !== b);
    const nb = new Map(data.nodes.map((p) => [p, new Set()]));
    for (const [a, b] of edges) { nb.get(a).add(b); nb.get(b).add(a); }
    let keep = data.nodes;
    if (localBox.checked && current && all.has(current)) {
      const seen = new Set([current]); let frontier = [current];
      for (let k = 0; k < 2; k++) {
        const next = [];
        for (const p of frontier) for (const q of nb.get(p)) if (!seen.has(q)) { seen.add(q); next.push(q); }
        frontier = next;
      }
      keep = [...seen];
    }
    if (s.hideOrphans) keep = keep.filter((p) => nb.get(p).size > 0 || p === current);
    const keepSet = new Set(keep);
    const maxDeg = Math.max(1, ...keep.map((p) => nb.get(p).size));
    graph = new Graph({ type: "undirected", allowSelfLoops: false });
    for (const p of keep) {
      const deg = nb.get(p).size, at = pos.get(p);
      graph.addNode(p, { x: at?.x ?? 0, y: at?.y ?? 0, label: labelFor(p), deg, size: 1, color: nodeColor(p, deg, maxDeg) });
    }
    for (const [a, b] of edges) if (keepSet.has(a) && keepSet.has(b) && !graph.hasEdge(a, b)) graph.addEdge(a, b, { size: 1 });
    ids = graph.nodes(); idx = new Map(ids.map((n, i) => [n, i]));
    applySizes();
    info.textContent = `${graph.order} notes · ${graph.size} links`;
    empty.classList.toggle("hidden", graph.order > 0);
    return { fresh: ids.filter((n) => pos.has(n)).length < ids.length * 0.8 };
  }

  function applySizes() {
    const maxDeg = Math.max(1, ...graph.mapNodes((n, a) => a.deg));
    graph.updateEachNodeAttributes((n, a) => ({ ...a, size: (2.2 + Math.sqrt(a.deg) * 1.7) * s.nodeSize, color: nodeColor(n, a.deg, maxDeg) }),
      { attributes: ["size", "color"] });
    const edgeCol = rgba(theme.textRgb, theme.dark ? 0.16 : 0.22);
    graph.updateEachEdgeAttributes((e, a) => ({ ...a, size: 0.7 * s.lineWidth, color: edgeCol }), { attributes: ["size", "color"] });
  }

  // ---------- drawing ----------
  function mount() {
    renderer?.kill();
    const { Sigma, Glow } = L;
    renderer = new Sigma(graph, host, {
      allowInvalidContainer: true, zIndex: true, stagePadding: 60, minCameraRatio: 0.03, maxCameraRatio: 6,
      defaultNodeType: "glow", nodeProgramClasses: { glow: Glow },
      labelFont: theme.font, labelSize: 12, labelWeight: "500", labelColor: { color: theme.dim },
      labelRenderedSizeThreshold: 9 - s.labels * 2.4, labelDensity: 0.35 + s.labels * 0.25, labelGridCellSize: 90,
      defaultDrawNodeHover: drawHover, nodeReducer, edgeReducer,
    });
    wireEvents();
  }

  function nodeReducer(node, a) {
    const out = { ...a };
    const dim = () => { out.color = rgba(theme.textRgb, theme.dark ? 0.12 : 0.15); out.label = ""; out.zIndex = 0; };
    if (query) {
      if (a.label.toLowerCase().includes(query)) { out.forceLabel = true; out.zIndex = 2; } else dim();
    }
    if (hovered) {
      if (node === hovered) { out.highlighted = true; out.zIndex = 3; out.forceLabel = true; out.size = a.size * 1.25; }
      else if (hood.has(node)) { out.zIndex = 2; out.forceLabel = true; }
      else dim();
    }
    if (node === current) { out.forceLabel = true; out.zIndex = Math.max(out.zIndex || 0, 2); }
    return out;
  }
  function edgeReducer(edge, a) {
    const out = { ...a };
    if (hovered) {
      const [x, y] = graph.extremities(edge);
      if (x === hovered || y === hovered) { out.color = rgba(theme.accent, 0.8); out.size = a.size * 1.8; out.zIndex = 2; }
      else out.color = rgba(theme.textRgb, 0.04);
    } else if (query) out.color = rgba(theme.textRgb, 0.05);
    return out;
  }

  // the hover label: a soft pill in the app's colours
  function drawHover(ctx, d, settings) {
    const size = settings.labelSize + 1, label = d.label || "";
    ctx.font = `600 ${size}px ${settings.labelFont}`;
    const w = ctx.measureText(label).width + 16, h = size + 12, x = d.x + d.size + 8, y = d.y - h / 2;
    ctx.save();
    ctx.shadowColor = "rgba(0,0,0,.35)"; ctx.shadowBlur = 12;
    ctx.fillStyle = theme.bg; ctx.beginPath(); ctx.roundRect(x, y, w, h, h / 2); ctx.fill();
    ctx.restore();
    ctx.strokeStyle = rgba(theme.accent, 0.7); ctx.lineWidth = 1; ctx.beginPath(); ctx.roundRect(x, y, w, h, h / 2); ctx.stroke();
    ctx.fillStyle = theme.text; ctx.textBaseline = "middle"; ctx.fillText(label, x + 8, d.y + 0.5);
  }

  function wireEvents() {
    renderer.on("enterNode", ({ node }) => {
      hovered = node; hood = new Set(graph.neighbors(node)); host.style.cursor = "pointer"; renderer.refresh({ skipIndexation: true });
    });
    renderer.on("leaveNode", () => {
      if (dragged) return;
      hovered = null; hood = null; host.style.cursor = "grab"; renderer.refresh({ skipIndexation: true });
    });
    renderer.on("downNode", ({ node }) => {
      dragged = node; dragMoved = false;
      if (!renderer.getCustomBBox()) renderer.setCustomBBox(renderer.getBBox());
    });
    renderer.getMouseCaptor().on("mousemovebody", (e) => {
      if (!dragged) return;
      dragMoved = true;
      const p = renderer.viewportToGraph(e);
      graph.mergeNodeAttributes(dragged, { x: p.x, y: p.y });
      worker?.postMessage({ type: "drag", i: idx.get(dragged), x: p.x, y: p.y });
      e.preventSigmaDefault(); e.original.preventDefault(); e.original.stopPropagation();
    });
    const release = () => {
      if (!dragged) return;
      const node = dragged; dragged = null;
      worker?.postMessage({ type: "release", i: idx.get(node) });
      if (!dragMoved) onOpen(node);
    };
    renderer.getMouseCaptor().on("mouseup", release);
    renderer.on("upNode", release);
    host.style.cursor = "grab";
  }

  // ---------- physics in the worker ----------
  function startWorker(fresh) {
    worker?.terminate();
    worker = new Worker("/assets/graph-worker.js", { type: "module" });
    settled = false;
    let first = true;
    worker.onmessage = ({ data: m }) => {
      if (m.type !== "tick" || !graph || !alive) return;
      const xy = m.xy;
      graph.updateEachNodeAttributes((n, a) => {
        const i = idx.get(n);
        if (n !== dragged) { a.x = xy[2 * i]; a.y = xy[2 * i + 1]; }
        pos.set(n, { x: a.x, y: a.y });
        return a;
      }, { attributes: ["x", "y"] });
      // let the camera follow while the layout grows, then hold still so the view doesn't drift
      if (first) { first = false; renderer?.setCustomBBox(null); renderer?.refresh(); renderer?.getCamera().setState({ x: 0.5, y: 0.5, ratio: 1 }); }
      if (!settled && m.alpha < 0.08) { settled = true; if (!dragged) fit(); }
    };
    worker.postMessage({
      type: "init", fresh, settings: s,
      nodes: ids.map((n) => ({ deg: graph.getNodeAttribute(n, "deg"), x: pos.get(n)?.x, y: pos.get(n)?.y })),
      links: graph.mapEdges((e, a, x, y) => [idx.get(x), idx.get(y)]),
    });
  }

  function fit() {
    if (!renderer) return;
    renderer.setCustomBBox(null);
    renderer.refresh();
    renderer.getCamera().animatedReset({ duration: 300 });
    requestAnimationFrame(() => renderer?.setCustomBBox(renderer.getBBox()));
  }

  async function rebuild() {
    try {
      L ??= await loadLibs();
      if (!alive) return;
      readTheme();
      const { fresh } = build();
      mount();
      startWorker(fresh);
    } catch (e) {
      console.error(e);
      empty.textContent = `The graph couldn't be drawn: ${e.message}`;
      empty.classList.remove("hidden");
    }
  }

  function restyle() {
    if (!graph || !renderer) return;
    readTheme(); applySizes();
    renderer.setSetting("labelColor", { color: theme.dim });
    renderer.setSetting("labelRenderedSizeThreshold", 9 - s.labels * 2.4);
    renderer.setSetting("labelDensity", 0.35 + s.labels * 0.25);
    renderer.refresh();
  }

  find.addEventListener("input", () => { query = find.value.trim().toLowerCase(); renderer?.refresh({ skipIndexation: true }); });
  find.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" || !graph || !query) return;
    const hit = graph.findNode((n, a) => a.label.toLowerCase().includes(query));
    if (!hit) return;
    const d = renderer.getNodeDisplayData(hit);
    renderer.getCamera().animate({ x: d.x, y: d.y, ratio: 0.3 }, { duration: 450 });
  });
  localBox.addEventListener("change", () => rebuild());
  buildPanel();
  // the tab may be hidden (zero size) when the graph is first built: redraw as soon as it has a size
  const ro = new ResizeObserver(() => { if (renderer && host.clientWidth) { renderer.resize(); renderer.refresh(); } });
  ro.observe(host);

  return {
    root,
    load(d, cur) { data = d; current = cur; rebuild(); },
    setCurrent(p) {
      if (p === current) return;
      current = p;
      if (localBox.checked) rebuild(); else renderer?.refresh({ skipIndexation: true });
    },
    restyle,
    destroy() { alive = false; ro.disconnect(); worker?.terminate(); renderer?.kill(); },
  };
}
