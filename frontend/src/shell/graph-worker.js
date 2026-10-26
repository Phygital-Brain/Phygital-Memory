// Graph physics in a background thread (d3-force), so the window never stutters while the layout settles.
// In:  {type:"init", nodes:[{id, deg, x?, y?}], links:[[i, j]], settings}
//      {type:"settings", settings} · {type:"drag", i, x, y} · {type:"release", i} · {type:"reheat"} · {type:"stop"}
// Out: {type:"tick", xy: Float32Array [x0, y0, x1, y1, ...], alpha}   (the buffer is handed over, not copied)
import { forceSimulation, forceManyBody, forceLink, forceX, forceY, forceCollide } from "d3-force";

let sim = null, nodes = [], settings = {}, timer = 0;

function forces() {
  const s = settings;
  sim.force("charge", forceManyBody().strength(s.repel).distanceMax(s.repel < -400 ? 2400 : 1600).theta(0.9))
     .force("link", forceLink(sim.force("link")?.links() || []).distance(s.linkDistance).strength(s.linkStrength))
     .force("x", forceX(0).strength(s.gravity * 0.1))
     .force("y", forceY(0).strength(s.gravity * 0.1))
     .force("collide", forceCollide((n) => 4 + Math.sqrt(n.deg) * 3).strength(0.6).iterations(1));
}

function send() {
  const xy = new Float32Array(nodes.length * 2);
  for (let i = 0; i < nodes.length; i++) { xy[2 * i] = nodes[i].x; xy[2 * i + 1] = nodes[i].y; }
  postMessage({ type: "tick", xy, alpha: sim.alpha() }, [xy.buffer]);
}

function loop() {
  // a few physics steps per frame while it settles, then it rests (no work when nothing moves)
  timer = 0;
  if (!sim || sim.alpha() < sim.alphaMin()) return;
  const steps = nodes.length > 3000 ? 1 : 2;
  for (let k = 0; k < steps; k++) sim.tick();
  send();
  timer = setTimeout(loop, 16);
}
const wake = (alpha) => { if (!sim) return; sim.alpha(Math.max(sim.alpha(), alpha)); if (!timer) loop(); };

onmessage = ({ data: m }) => {
  if (m.type === "init") {
    settings = m.settings;
    nodes = m.nodes.map((n, i) => ({ index: i, deg: n.deg, x: n.x ?? Math.cos(i * 2.399963) * 14 * Math.sqrt(i + 1),
                                     y: n.y ?? Math.sin(i * 2.399963) * 14 * Math.sqrt(i + 1) }));
    const links = m.links.map(([a, b]) => ({ source: a, target: b }));
    sim?.stop();
    sim = forceSimulation(nodes).stop().alphaDecay(0.022).velocityDecay(0.42);
    sim.force("link", forceLink(links));
    forces();
    // settle quietly before the first picture when starting from scratch, so the graph doesn't explode on screen
    if (m.fresh) for (let i = 0, n = Math.min(120, 30000 / Math.max(1, nodes.length)); i < n; i++) sim.tick();
    send();
    wake(m.fresh ? 0.35 : 0.15);
  } else if (m.type === "settings") {
    settings = m.settings; if (sim) { forces(); wake(0.5); }
  } else if (m.type === "drag" && nodes[m.i]) {
    nodes[m.i].fx = m.x; nodes[m.i].fy = m.y; wake(0.15);
  } else if (m.type === "release" && nodes[m.i]) {
    nodes[m.i].fx = null; nodes[m.i].fy = null; wake(0.08);
  } else if (m.type === "reheat") {
    wake(0.9);
  } else if (m.type === "stop") {
    sim?.stop(); clearTimeout(timer); timer = 0;
  }
};
