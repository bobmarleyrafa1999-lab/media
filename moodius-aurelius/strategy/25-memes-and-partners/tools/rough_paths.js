#!/usr/bin/env node
// Reads one JSON shape on stdin, prints Rough.js SVG paths as JSON. Offline, no browser.
// {"kind": "line"|"rectangle"|"ellipse"|"curve"|"linearPath", "args": [...], "options": {...}}
const rough = require("./vendor/roughjs/rough.cjs.js");
let input = "";
process.stdin.on("data", (c) => (input += c));
process.stdin.on("end", () => {
  const s = JSON.parse(input);
  const gen = rough.generator();
  if (!["line", "rectangle", "ellipse", "curve", "linearPath"].includes(s.kind)) {
    throw new Error("unknown shape " + s.kind);
  }
  const drawable = gen[s.kind](...s.args, s.options || {});
  process.stdout.write(JSON.stringify(gen.toPaths(drawable)));
});
