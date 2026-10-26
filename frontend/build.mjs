// Builds the app page into ../phygital_memory/web: index.html, assets/app.js, assets/app.css,
// and THIRD-PARTY-LICENSES.txt for the free libraries inside the bundle.
import * as esbuild from "esbuild";
import { copyFileSync, mkdirSync, readFileSync, writeFileSync, existsSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";

const OUT = new URL("../phygital_memory/web/", import.meta.url).pathname;
rmSync(join(OUT, "assets"), { recursive: true, force: true });   // no old chunks left behind
mkdirSync(join(OUT, "assets"), { recursive: true });

const options = {
  entryPoints: { app: "src/main.js", "graph-worker": "src/shell/graph-worker.js" },
  splitting: true,
  chunkNames: "chunk-[hash]",
  bundle: true,
  format: "esm",
  minify: !process.argv.includes("--watch"),
  sourcemap: false,
  legalComments: "none",
  outdir: join(OUT, "assets"),
  metafile: true,
  logLevel: "info",
  plugins: [{
    name: "page",
    setup(build) {
      build.onEnd((result) => {
        copyFileSync("src/index.html", join(OUT, "index.html"));
        if (result.metafile) writeLicences(result.metafile);
      });
    },
  }],
};

function writeLicences(meta) {
  const seen = new Map();
  for (const input of Object.keys(meta.inputs)) {
    const m = input.match(/node_modules\/((?:@[^/]+\/)?[^/]+)/);
    if (!m || seen.has(m[1])) continue;
    const dir = join("node_modules", m[1]);
    const pkg = JSON.parse(readFileSync(join(dir, "package.json"), "utf8"));
    const file = ["LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE"].map((f) => join(dir, f)).find(existsSync);
    seen.set(m[1], `${m[1]} ${pkg.version} (${pkg.license})\n${file ? readFileSync(file, "utf8").trim() : ""}`);
  }
  const text = "Phygital Memory includes these free libraries.\n\n" + [...seen.values()].join("\n\n---\n\n") + "\n";
  writeFileSync(join(OUT, "THIRD-PARTY-LICENSES.txt"), text);
}

if (process.argv.includes("--watch")) {
  const ctx = await esbuild.context(options);
  await ctx.watch();
} else {
  await esbuild.build(options);
}
