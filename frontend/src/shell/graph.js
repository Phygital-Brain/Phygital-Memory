// Graph view: every note is a dot, every [[link]] a line. Own small force simulation on a canvas.
import { el } from "./dom.js";

const REST = 70, SPRING = 0.05, REPEL = 900, GRAVITY = 0.012, DAMP = 0.62;

export function createGraph({ onOpen, colorFor, labelFor }) {
  const canvas = el("canvas", { class: "graph-canvas", tabindex: "0", "aria-label": "Graph of linked notes" });
  const info = el("span", { class: "graph-info" });
  const localBox = el("input", { type: "checkbox", "aria-label": "Local graph" });
  const bar = el("div", { class: "graph-bar" },
    el("label", { class: "set-check", title: "Only the open note and what it links to, two steps out" }, localBox, "Local graph"),
    el("button", { class: "btn small", onclick: () => fit() }, "Reset view"), info);
  const empty = el("div", { class: "graph-empty hidden" }, "No notes to show yet.");
  const root = el("div", { class: "graph" }, canvas, bar, empty);
  const ctx = canvas.getContext("2d");

  let data = { nodes: [], edges: [] };
  let current = null;
  let nodes = [], links = [], byPath = new Map();
  const pos = new Map();                     // remembered positions, so toggling "local" doesn't scramble things
  let view = { k: 1, x: 0, y: 0 };
  let w = 0, h = 0, dpr = 1;
  let alpha = 1, raf = 0, dirtyDraw = true;
  let hover = null, dragging = null, panning = null;
  const pointers = new Map();
  let pinch = null;
  let alive = true;
  let colors = null;

  function readColors() {
    const cs = getComputedStyle(document.documentElement);
    const g = (n) => cs.getPropertyValue(n).trim();
    colors = { text: g("--text"), dim: g("--text-2"), accent: g("--accent"), line: g("--text-faint") };
  }

  function rebuild() {
    const all = new Map(data.nodes.map((p) => [p, { path: p, deg: 0, nb: new Set() }]));
    const edges = data.edges.filter(([a, b]) => all.has(a) && all.has(b));
    for (const [a, b] of edges) { all.get(a).nb.add(b); all.get(b).nb.add(a); }
    for (const n of all.values()) n.deg = n.nb.size;
    let keep = [...all.keys()];
    if (localBox.checked && current && all.has(current)) {
      const seen = new Set([current]);
      let frontier = [current];
      for (let s = 0; s < 2; s++) {
        const next = [];
        for (const p of frontier) for (const q of all.get(p).nb) if (!seen.has(q)) { seen.add(q); next.push(q); }
        frontier = next;
      }
      keep = [...seen];
    }
    const keepSet = new Set(keep);
    nodes = keep.map((p, i) => {
      const n = all.get(p);
      let at = pos.get(p);
      if (!at) {
        const a = i * 2.399963, r = 18 * Math.sqrt(i + 1);
        at = { x: Math.cos(a) * r, y: Math.sin(a) * r };
      }
      return { path: p, label: labelFor(p), color: colorFor(p), deg: n.deg, nb: n.nb, x: at.x, y: at.y, vx: 0, vy: 0, r: 4 + Math.sqrt(n.deg) * 2.2, fixed: false };
    });
    byPath = new Map(nodes.map((n) => [n.path, n]));
    links = edges.filter(([a, b]) => keepSet.has(a) && keepSet.has(b)).map(([a, b]) => ({ a: byPath.get(a), b: byPath.get(b) }));
    info.textContent = `${nodes.length} notes · ${links.length} links`;
    empty.classList.toggle("hidden", nodes.length > 0);
    hover = null;
    alpha = 1;
    const warm = nodes.length > 400 ? 60 : 150;
    for (let i = 0; i < warm; i++) tick();
    fit();
    kick();
  }

  function tick() {
    const n = nodes.length;
    for (let i = 0; i < n; i++) {
      const a = nodes[i];
      for (let j = i + 1; j < n; j++) {
        const b = nodes[j];
        let dx = a.x - b.x, dy = a.y - b.y;
        let d2 = dx * dx + dy * dy;
        if (d2 > 160000) continue;
        if (d2 < 25) { dx = Math.random() - .5; dy = Math.random() - .5; d2 = 25; }
        const f = (REPEL * alpha) / d2, d = Math.sqrt(d2);
        const fx = (dx / d) * f * 10, fy = (dy / d) * f * 10;
        a.vx += fx; a.vy += fy; b.vx -= fx; b.vy -= fy;
      }
    }
    for (const l of links) {
      const dx = l.b.x - l.a.x, dy = l.b.y - l.a.y, d = Math.sqrt(dx * dx + dy * dy) || 1;
      const f = (d - REST) * SPRING * alpha, fx = (dx / d) * f, fy = (dy / d) * f;
      l.a.vx += fx; l.a.vy += fy; l.b.vx -= fx; l.b.vy -= fy;
    }
    for (const a of nodes) {
      a.vx -= a.x * GRAVITY * alpha; a.vy -= a.y * GRAVITY * alpha;
      if (a.fixed) { a.vx = a.vy = 0; continue; }
      a.vx *= DAMP; a.vy *= DAMP;
      a.x += a.vx; a.y += a.vy;
      pos.set(a.path, { x: a.x, y: a.y });
    }
    alpha *= 0.985;
  }

  function frame() {
    raf = 0;
    if (!alive) return;
    if (alpha > 0.02) { tick(); dirtyDraw = true; }
    if (dirtyDraw) draw();
    if (alpha > 0.02 || dirtyDraw) kick();
  }
  function kick() { if (!raf && alive) raf = requestAnimationFrame(frame); }
  function redraw() { dirtyDraw = true; kick(); }

  const toScreen = (x, y) => [x * view.k + view.x, y * view.k + view.y];
  const toWorld = (sx, sy) => [(sx - view.x) / view.k, (sy - view.y) / view.k];

  function fit() {
    if (!nodes.length || !w) { redraw(); return; }
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    for (const n of nodes) { x0 = Math.min(x0, n.x); y0 = Math.min(y0, n.y); x1 = Math.max(x1, n.x); y1 = Math.max(y1, n.y); }
    const pad = 60, bw = Math.max(x1 - x0, 60), bh = Math.max(y1 - y0, 60);
    const k = Math.min(1.6, Math.max(0.1, Math.min((w - pad * 2) / bw, (h - pad * 2) / bh)));
    view = { k, x: w / 2 - ((x0 + x1) / 2) * k, y: h / 2 - ((y0 + y1) / 2) * k };
    redraw();
  }

  function draw() {
    dirtyDraw = false;
    if (!colors) readColors();
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    const hl = hover ? new Set([hover.path, ...hover.nb]) : null;
    ctx.lineWidth = 1;
    ctx.strokeStyle = colors.line;
    ctx.globalAlpha = hl ? 0.12 : 0.4;
    ctx.beginPath();
    for (const l of links) {
      const [ax, ay] = toScreen(l.a.x, l.a.y), [bx, by] = toScreen(l.b.x, l.b.y);
      ctx.moveTo(ax, ay); ctx.lineTo(bx, by);
    }
    ctx.stroke();
    if (hover) {
      ctx.globalAlpha = 0.95; ctx.strokeStyle = colors.accent; ctx.lineWidth = 1.5; ctx.beginPath();
      for (const l of links) if (l.a === hover || l.b === hover) {
        const [ax, ay] = toScreen(l.a.x, l.a.y), [bx, by] = toScreen(l.b.x, l.b.y);
        ctx.moveTo(ax, ay); ctx.lineTo(bx, by);
      }
      ctx.stroke();
    }
    const showAll = view.k >= 1.25;
    ctx.font = "12px -apple-system, system-ui, sans-serif";
    ctx.textAlign = "center"; ctx.textBaseline = "top";
    const labels = [];
    for (const n of nodes) {
      const [sx, sy] = toScreen(n.x, n.y);
      if (sx < -30 || sy < -30 || sx > w + 30 || sy > h + 30) continue;
      const r = n.r * Math.min(1.8, Math.max(0.6, view.k));
      const lit = !hl || hl.has(n.path);
      ctx.globalAlpha = lit ? 1 : 0.18;
      ctx.fillStyle = n.color;
      ctx.beginPath(); ctx.arc(sx, sy, r, 0, 6.2832); ctx.fill();
      if (n.path === current) { ctx.strokeStyle = colors.text; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(sx, sy, r + 3, 0, 6.2832); ctx.stroke(); }
      if (lit && (showAll || (hl && hl.has(n.path)) || n.path === current)) labels.push([n.label, sx, sy + r + 3, n === hover]);
    }
    ctx.globalAlpha = 1;
    for (const [t, x, y, bold] of labels) {
      ctx.fillStyle = bold ? colors.text : colors.dim;
      ctx.fillText(t.length > 28 ? t.slice(0, 27) + "…" : t, x, y);
    }
  }

  function hit(sx, sy) {
    const [x, y] = toWorld(sx, sy);
    let best = null, bd = 1e9;
    for (const n of nodes) {
      const dx = n.x - x, dy = n.y - y, d = Math.sqrt(dx * dx + dy * dy), r = n.r + 5 / view.k;
      if (d < r && d < bd) { best = n; bd = d; }
    }
    return best;
  }

  const local = (e) => { const r = canvas.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
  canvas.addEventListener("pointerdown", (e) => {
    canvas.setPointerCapture(e.pointerId);
    const [sx, sy] = local(e);
    pointers.set(e.pointerId, [sx, sy]);
    if (pointers.size === 2) {
      const [p, q] = [...pointers.values()];
      pinch = { d: Math.hypot(p[0] - q[0], p[1] - q[1]) };
      dragging = null; panning = null;
      return;
    }
    const n = hit(sx, sy);
    if (n) { dragging = { n, sx, sy, moved: false }; n.fixed = true; }
    else panning = { sx, sy, vx: view.x, vy: view.y };
  });
  canvas.addEventListener("pointermove", (e) => {
    const [sx, sy] = local(e);
    if (pointers.has(e.pointerId)) pointers.set(e.pointerId, [sx, sy]);
    if (pinch && pointers.size === 2) {
      const [p, q] = [...pointers.values()];
      const d = Math.hypot(p[0] - q[0], p[1] - q[1]);
      zoomAt((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, d / pinch.d);
      pinch.d = d;
      return;
    }
    if (dragging) {
      if (Math.hypot(sx - dragging.sx, sy - dragging.sy) > 4) dragging.moved = true;
      if (dragging.moved) {
        const [x, y] = toWorld(sx, sy);
        dragging.n.x = x; dragging.n.y = y;
        pos.set(dragging.n.path, { x, y });
        alpha = Math.max(alpha, 0.25);
        redraw();
      }
    } else if (panning) {
      view.x = panning.vx + (sx - panning.sx); view.y = panning.vy + (sy - panning.sy);
      redraw();
    } else {
      const n = hit(sx, sy);
      if (n !== hover) { hover = n; canvas.style.cursor = n ? "pointer" : "grab"; redraw(); }
    }
  });
  const up = (e) => {
    pointers.delete(e.pointerId);
    if (pointers.size < 2) pinch = null;
    if (dragging) {
      const d = dragging; dragging = null;
      d.n.fixed = false;
      if (!d.moved) onOpen(d.n.path);
    }
    panning = null;
  };
  canvas.addEventListener("pointerup", up);
  canvas.addEventListener("pointercancel", up);
  canvas.addEventListener("pointerleave", () => { if (hover && !dragging) { hover = null; redraw(); } });
  canvas.style.cursor = "grab";

  function zoomAt(sx, sy, f) {
    const k = Math.min(6, Math.max(0.08, view.k * f)), real = k / view.k;
    view.x = sx - (sx - view.x) * real; view.y = sy - (sy - view.y) * real; view.k = k;
    redraw();
  }
  canvas.addEventListener("wheel", (e) => {
    e.preventDefault();
    const [sx, sy] = local(e);
    zoomAt(sx, sy, Math.exp(-e.deltaY * (e.ctrlKey ? 0.012 : 0.0018)));
  }, { passive: false });

  localBox.addEventListener("change", rebuild);

  const ro = new ResizeObserver(() => {
    const r = root.getBoundingClientRect();
    if (!r.width) return;
    const first = !w;
    dpr = window.devicePixelRatio || 1;
    w = r.width; h = r.height;
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
    canvas.style.width = w + "px"; canvas.style.height = h + "px";
    if (first && nodes.length) fit(); else redraw();
  });
  ro.observe(root);

  return {
    root,
    load(d, cur) { data = d; current = cur; colors = null; rebuild(); },
    setCurrent(p) { current = p; if (localBox.checked) rebuild(); else redraw(); },
    restyle() { colors = null; redraw(); },
    destroy() { alive = false; cancelAnimationFrame(raf); ro.disconnect(); },
  };
}
