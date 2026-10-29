// Makes the npm page show the project's full README: copies ../README.md over npm/README.md with every link and
// image that points into the repo turned into a full GitHub address (npm can't follow relative paths). Run by the
// npm release workflow just before publishing, with the release tag: node page.mjs v0.1.2
import { readFileSync, writeFileSync } from "node:fs";

const ref = process.argv[2] || "main";
const repo = "https://github.com/Phygital-Brain/Phygital-Memory";
const local = (p) => !/^(https?:|mailto:|#|\/\/)/.test(p);
const image = (p) => /\.(png|jpe?g|gif|svg|webp)$/i.test(p.split("#")[0]);
const full = (p) => image(p) ? `https://raw.githubusercontent.com/Phygital-Brain/Phygital-Memory/${ref}/${p}`
                             : `${repo}/blob/${ref}/${p}`;

const text = readFileSync(new URL("../README.md", import.meta.url), "utf8")
  .replace(/(\]\()([^)\s]+)(\))/g, (m, a, p, b) => local(p) ? a + full(p) + b : m)   // [text](path), ![alt](path)
  .replace(/\b(src|href)="([^"]+)"/g, (m, attr, p) => local(p) ? `${attr}="${full(p)}"` : m);   // <img src>, <a href>
writeFileSync(new URL("./README.md", import.meta.url), text);
