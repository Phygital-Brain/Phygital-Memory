// Builds the app page into ../phygital_memory/web: index.html, assets/app.js, assets/app.css,
// and THIRD-PARTY-LICENSES.txt for the free libraries inside the bundle.
import * as esbuild from "esbuild";
import { copyFileSync, mkdirSync, readFileSync, writeFileSync, existsSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const OUT = fileURLToPath(new URL("../phygital_memory/web/", import.meta.url));   // works with spaces in the path
rmSync(join(OUT, "assets"), { recursive: true, force: true });   // no old chunks left behind
mkdirSync(join(OUT, "assets"), { recursive: true });

// The app's languages (core/languages, see scripts/i18n.py): their list goes into the page, each one next to it.
const LANG_DIR = fileURLToPath(new URL("../languages/", import.meta.url));
const langs = existsSync(join(LANG_DIR, "languages.json")) ? JSON.parse(readFileSync(join(LANG_DIR, "languages.json"), "utf8")) : [["en", "English"]];
function copyLanguages() {
  for (const [code] of langs) {
    const f = join(LANG_DIR, `${code}.json`);
    if (code !== "en" && existsSync(f)) copyFileSync(f, join(OUT, "assets", `lang-${code}.json`));
  }
}

const options = {
  define: { "globalThis.PM_LANGUAGES": JSON.stringify(langs) },
  entryPoints: { app: "src/main.js", "graph-worker": "src/shell/graph-worker.js" },
  splitting: true,
  chunkNames: "chunk-[hash]",
  bundle: true,
  format: "esm",
  minify: !process.argv.includes("--watch"),
  sourcemap: false,
  legalComments: "none",
  loader: { ".woff2": "file" },   // the brand fonts ship inside the app, nothing loads from the internet
  assetNames: "[name]-[hash]",
  outdir: join(OUT, "assets"),
  metafile: true,
  logLevel: "info",
  plugins: [{
    name: "page",
    setup(build) {
      build.onEnd((result) => {
        copyFileSync("src/index.html", join(OUT, "index.html"));
        copyLanguages();
        if (result.metafile) writeLicences(result.metafile);
      });
    },
  }],
};

// The libraries in groups by what they do, the same groups as the overview in Settings › General › Licences.
const GROUPS = [
  ["Note editor", (n) => /^@(codemirror|lezer|marijn)\//.test(n) || ["style-mod", "w3c-keyname", "crelt"].includes(n)],
  ["Graph view", (n) => /^(sigma|graphology|events|d3-force)$|^graphology-/.test(n)],
  ["Safe pasting", (n) => n === "dompurify"],
  ["Fonts", (n) => n.startsWith("@fontsource")],
  ["Diagrams in notes", () => true],   // Mermaid and everything it brings
];
const ORDER = ["Note editor", "Diagrams in notes", "Graph view", "Safe pasting", "Fonts"];
const LICENCE_FIX = { khroma: "MIT" };   // its package.json names no licence; its LICENSE file is MIT

function writeLicences(meta) {
  const groups = new Map(ORDER.map((g) => [g, []]));
  const seen = new Set();
  for (const input of Object.keys(meta.inputs)) {
    const m = input.match(/node_modules\/((?:@[^/]+\/)?[^/]+)/);
    if (!m || seen.has(m[1])) continue;
    seen.add(m[1]);
    const dir = join("node_modules", m[1]);
    const pkg = JSON.parse(readFileSync(join(dir, "package.json"), "utf8"));
    const file = ["LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "license", "license.md", "OFL.txt"].map((f) => join(dir, f)).find(existsSync);
    const lic = LICENCE_FIX[m[1]] || pkg.license || "see the text below";
    const readme = join(dir, "README.md");   // a few keep the licence only at the end of their README
    const body = file ? readFileSync(file, "utf8").trim()
      : existsSync(readme) ? (readFileSync(readme, "utf8").split(/^## Licen[cs]e\s*$/m)[1] || "").trim() : "";
    groups.get(GROUPS.find(([, has]) => has(m[1]))[0]).push(`${m[1]} ${pkg.version}, ${lic}\n\n${body}`);
  }
  const text = [...groups].filter(([, list]) => list.length)
    .map(([g, list]) => `${g.toUpperCase()}\n${"=".repeat(g.length)}\n\n` + list.join("\n\n---\n\n")).join("\n\n\n") + "\n";
  writeFileSync(join(OUT, "THIRD-PARTY-LICENSES.txt"), text);
}

if (process.argv.includes("--watch")) {
  const ctx = await esbuild.context(options);
  await ctx.watch();
} else {
  await esbuild.build(options);
}
