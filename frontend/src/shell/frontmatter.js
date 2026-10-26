// Simple YAML frontmatter: scalars, inline [a, b] lists and block "- item" lists. Anything else is "raw"
// and stays untouched.
export function splitFM(text) {
  const m = /^---[ \t]*\r?\n(?:([\s\S]*?)\r?\n)?---[ \t]*(?:\r?\n|$)/.exec(text);
  if (!m) return { head: "", yaml: null, body: text };
  return { head: m[0], yaml: m[1] || "", body: text.slice(m[0].length) };
}

export function parseYaml(yaml) {
  const lines = yaml.split(/\r?\n/);
  const props = [];
  const keys = new Set();
  for (let i = 0; i < lines.length; i++) {
    const m = /^([A-Za-z0-9_][A-Za-z0-9_\- ]*?):(?:[ \t]+(.*))?$/.exec(lines[i]);
    if (!m) return null;
    const key = m[1];
    if (keys.has(key)) return null;
    keys.add(key);
    const v = (m[2] || "").trim();
    if (v === "") {
      const items = [];
      while (i + 1 < lines.length) {
        const li = /^[ \t]*-(?:[ \t]+(.*))?$/.exec(lines[i + 1]);
        if (!li) break;
        items.push((li[1] || "").trim());
        i++;
      }
      if (items.length) props.push({ key, kind: "list", items, style: "block" });
      else props.push({ key, kind: "scalar", value: "" });
    } else if (v[0] === "[") {
      if (v[v.length - 1] !== "]" || /["'{}\[]/.test(v.slice(1, -1))) return null;
      const inner = v.slice(1, -1).trim();
      props.push({ key, kind: "list", items: inner ? inner.split(",").map((s) => s.trim()).filter(Boolean) : [], style: "inline" });
    } else if (/^[{|>&*!%@`]/.test(v)) {
      return null;
    } else {
      props.push({ key, kind: "scalar", value: v });
    }
  }
  return props;
}

export function serializeYaml(props) {
  const out = [];
  for (const p of props) {
    if (p.kind === "scalar") out.push(p.value === "" ? `${p.key}:` : `${p.key}: ${p.value}`);
    else if (p.style === "block" || p.items.some((s) => s.includes(","))) {
      out.push(`${p.key}:`);
      for (const it of p.items) out.push(`  - ${it}`);
    } else out.push(`${p.key}: [${p.items.join(", ")}]`);
  }
  return out.join("\n");
}

export function headFor(props) {
  return props.length ? "---\n" + serializeYaml(props) + "\n---\n" : "";
}
