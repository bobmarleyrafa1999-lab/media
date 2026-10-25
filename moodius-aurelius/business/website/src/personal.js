// Personalised and gift editions. The buyer's choices are checked here, stored with the
// checkout, copied to the order, and turned into a PDF by journal/personalise.py (same
// rules as clean_personal() in journal/build_journal.py; keep the two in step).

export const HIGHLIGHTS = {
  manifesto: "Feel everything. Be ruled by none of it.",
  daily: "One honest look a day is enough to change a year.",
  tools: "A feeling named is a feeling you can work with.",
  discipline: "Discipline is choosing, again, who you said you'd be.",
  truths: "Most of what hurts is a story told too quickly.",
  journal: "Write it down. Then read it as if a friend had written it.",
  identity: "You are not your worst day, and not your best one either.",
};
export const ACCENTS = ["ember", "ash", "bone"];
export const COVERS = ["dark", "light"];

const bad = (msg) => Object.assign(new Error(msg), { status: 400 });

function text(input, key, limit, label) {
  const v = String(input[key] ?? "").replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim();
  if (v.length > limit) throw bad(`${label} can be at most ${limit} characters.`);
  return v;
}

function isoDate(v) {
  if (!v) return null;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(v) || Number.isNaN(Date.parse(`${v}T00:00:00Z`))) throw bad("Please pick a valid date.");
  return v;
}

// kind: "personal" | "gift". Returns a clean object or throws a 400 error with a readable message.
export function cleanPersonal(input, kind, today = new Date().toISOString().slice(0, 10)) {
  input = input || {};
  const out = {
    name: text(input, "p_name", 40, "The name"),
    monogram: text(input, "p_monogram", 3, "The monogram").replace(/[^A-Za-z]/g, "").toUpperCase(),
    accent: input.p_accent || "ember",
    cover: input.p_cover || "dark",
    highlight: String(input.p_highlight || "").toLowerCase(),
    start_date: isoDate(input.p_start_date),
    dedication: text(input, "p_dedication", 280, "The dedication"),
  };
  if (!out.name) throw bad(kind === "gift" ? "Please add the name of the person it's for." : "Please add the name for the cover.");
  if (!ACCENTS.includes(out.accent)) throw bad("Please choose one of the accent colours.");
  if (!COVERS.includes(out.cover)) throw bad("Please choose a dark or light cover.");
  if (out.highlight && !HIGHLIGHTS[out.highlight]) throw bad("Please choose one of the opening lines.");
  if (kind === "gift") {
    out.from_name = text(input, "p_from_name", 40, "Your name");
    if (!out.from_name) throw bad("Please add your name for the gift page.");
    out.send_date = isoDate(input.p_send_date);
    if (out.send_date && out.send_date < today) throw bad("The send date can't be in the past.");
    const r = String(input.p_recipient_email || "").trim().toLowerCase();
    if (r && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(r)) throw bad("Please check the recipient's email address.");
    out.recipient_email = r || null;
  }
  for (const k of Object.keys(out)) if (out[k] === "" || out[k] === null) delete out[k];
  return out;
}

export function describePersonal(p) {
  if (!p) return "";
  const lines = [`Name on the cover: ${p.name}`];
  if (p.monogram) lines.push(`Monogram: ${p.monogram}`);
  lines.push(`Cover: ${p.cover || "dark"}, ${p.accent || "ember"} accent`);
  if (p.highlight) lines.push(`Opening line (${p.highlight}): "${HIGHLIGHTS[p.highlight]}"`);
  if (p.start_date) lines.push(`Dated from ${p.start_date}`);
  if (p.dedication) lines.push(`Dedication: "${p.dedication}"`);
  if (p.from_name) lines.push(`From: ${p.from_name}`);
  if (p.send_date) lines.push(`Send on: ${p.send_date}`);
  if (p.recipient_email) lines.push(`Send to: ${p.recipient_email}`);
  return lines.join("\n");
}
