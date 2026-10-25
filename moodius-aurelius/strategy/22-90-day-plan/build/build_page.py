"""Build plan.html (the artifact page) from plan.md. Run with a Python that has markdown==3.7."""
import html, re, sys
from pathlib import Path
import markdown

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "plan.md"
OUT = HERE.parent / "plan.html"

md = SRC.read_text()
md = md.split("\n", 1)[1]  # drop the H1; the page header carries it
body = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"])

# Wrap every table so only the table scrolls on a phone.
body = body.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")

# Number-free section ids + nav built from the h2s.
nav = []
def h2(m):
    text = re.sub("<[^>]+>", "", m.group(1))
    slug = re.sub(r"[^a-z0-9]+", "-", re.sub(r"^\d+\.\s*", "", text.lower())).strip("-")[:40]
    nav.append((slug, re.sub(r"^\d+\.\s*", "", text)))
    return f'<h2 id="{slug}">{m.group(1)}</h2>'
body = re.sub(r"<h2>(.*?)</h2>", h2, body)

# Copy buttons on code blocks (name and bio).
body = body.replace("<pre><code>", '<div class="copy"><button type="button" class="cbtn">Copy</button><pre><code>').replace("</code></pre>", "</code></pre></div>")

# Daily reach chart after the baseline challenge heading.
days = [("12", 227, "2 reels + quote card"), ("13", 159, "3 reels"), ("14", 206, "2 reels + meme"), ("15", 123, "2 reels"),
        ("16", 2, "nothing posted"), ("17", 3, "nothing posted"), ("18", 1, "nothing posted"), ("19", 1, "stories only"),
        ("20", 220, "stories"), ("21", 2141, "first carousel + reel"), ("22", 5734, "carousel + reel"),
        ("23", 2398, "carousel + reel"), ("24", 804, "calm carousel + reel")]
W, H, L, B, T = 640, 260, 48, 34, 18
pw, ph = W - L - 8, H - B - T
bw = pw / len(days)
def y(v): return T + ph - v / 6000 * ph
bars = []
for i, (d, v, what) in enumerate(days):
    x = L + i * bw + 3
    car = int(d) >= 21
    hgt = max(ph * v / 6000, 1.5)
    tip = f"{d} Oct: {v:,} reached · {what}"
    bars.append(f'<g class="bar" data-tip="{html.escape(tip)}"><rect x="{x:.1f}" y="{T}" width="{bw-6:.1f}" height="{ph}" fill="transparent"/>'
                f'<path d="M{x:.1f},{T+ph} v-{hgt-4 if hgt>4 else 0:.1f} q0,-4 4,-4 h{bw-14:.1f} q4,0 4,4 v{hgt-4 if hgt>4 else 0:.1f} z" class="{"m2" if car else "m1"}"/>'
                f'<text x="{x+(bw-6)/2:.1f}" y="{H-B+16}" class="ax" text-anchor="middle">{d}</text></g>')
grid = "".join(f'<line x1="{L}" x2="{W-8}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="gl"/><text x="{L-8}" y="{y(v)+4:.1f}" class="ax" text-anchor="end">{v:,}</text>' for v in (0, 2000, 4000, 6000))
peak_x = L + 10 * bw + 3 + (bw - 6) / 2
chart = f'''<figure class="chart" aria-label="Daily account reach, 12 to 24 October 2026">
<figcaption><strong>Accounts reached per day, 12–24 Oct</strong><span class="legend"><span><i class="k1"></i>Reels or no feed post</span><span><i class="k2"></i>Daily carousel began</span></span></figcaption>
<div class="cwrap"><svg viewBox="0 0 {W} {H}" role="img" aria-label="Reach was 1 to 227 a day before 21 October, then 2,141, 5,734, 2,398 and 804 once a daily carousel started.">
{grid}{"".join(bars)}
<text x="{peak_x:.1f}" y="{y(5734)-8:.1f}" text-anchor="middle" class="dl">5,734</text>
<text x="{L+(pw)/2:.1f}" y="{H-2}" class="ax" text-anchor="middle">October 2026 · source: Metricool, brand account totals</text>
</svg><div class="tip" hidden></div></div>
<details><summary>Show as a table</summary><div class="tbl"><table><thead><tr><th>Date</th><th>Reached</th><th>What went out</th></tr></thead><tbody>
{"".join(f"<tr><td>{d} Oct</td><td class='n'>{v:,}</td><td>{w}</td></tr>" for d, v, w in days)}
</tbody></table></div></details></figure>'''
anchor = "<h3>First, a challenge to the baseline</h3>"
assert anchor in body
body = body.replace(anchor, anchor + chart, 1)

navhtml = "".join(f'<a href="#{s}">{html.escape(t)}</a>' for s, t in nav)

page = f'''<title>Moodius 90-Day Plan</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;500;600&display=swap">
<style>
/* Layout: one reading column with a sticky section bar; wide tables scroll inside their own frame. */
:root {{
  --bg: #F3EFE7; --surface: #FBF8F2; --fg: #1B1F24; --muted: #565B62; --line: #D9D2C4;
  --accent: #A3561B; --accent-soft: #EBDCC9; --m1: #2F6DB5; --m2: #B5621F;
  --display: "Cormorant Garamond", "Iowan Old Style", Georgia, serif;
  --body: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #1B1F24; --surface: #23282E; --fg: #F3EFE7; --muted: #B8B3A9; --line: #3A4049;
  --accent: #E0965A; --accent-soft: #3A2F26; --m1: #5B8FD6; --m2: #C9742E; color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --bg: #1B1F24; --surface: #23282E; --fg: #F3EFE7; --muted: #B8B3A9; --line: #3A4049;
  --accent: #E0965A; --accent-soft: #3A2F26; --m1: #5B8FD6; --m2: #C9742E; color-scheme: dark; }}
body {{ background: var(--bg); color: var(--fg); font: 15px/1.6 var(--body); }}
body::before {{ content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10; background: var(--bg); }}
.wrap {{ max-width: 980px; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 0 64px; }}
header.top {{ padding-block: 40px 20px; border-bottom: 1px solid var(--line); }}
.eyebrow {{ font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }}
h1 {{ font-family: var(--display); font-weight: 600; font-size: clamp(34px, 6vw, 54px); line-height: 1.05; margin: 8px 0 12px; text-wrap: balance; }}
h1 em {{ color: var(--accent); font-style: italic; }}
.lede {{ max-width: 65ch; color: var(--muted); margin: 0; }}
nav.sec {{ position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--bg); border-bottom: 1px solid var(--line); display: flex; gap: 4px 18px; flex-wrap: wrap; padding-block: 10px; font-size: 13px; }}
nav.sec a {{ color: var(--fg); text-decoration: none; padding: 2px 0; border-bottom: 2px solid transparent; }}
nav.sec a:hover, nav.sec a:focus-visible {{ border-color: var(--accent); outline: none; }}
main {{ min-width: 0; }}
main > p, main > ul, main > ol, main > blockquote, main h3, main h4 {{ max-width: 70ch; }}
h2 {{ font-family: var(--display); font-weight: 600; font-size: clamp(28px, 4.4vw, 38px); line-height: 1.1; margin: 56px 0 12px; text-wrap: balance; scroll-margin-top: 64px; }}
h3 {{ font-family: var(--display); font-weight: 600; font-size: 24px; line-height: 1.2; margin: 36px 0 8px; text-wrap: balance; }}
h4 {{ font-size: 13px; letter-spacing: .08em; text-transform: uppercase; margin: 28px 0 6px; color: var(--accent); }}
hr {{ border: 0; border-top: 1px solid var(--line); margin: 40px 0 0; }}
a {{ color: var(--accent); }}
strong {{ font-weight: 600; }}
blockquote {{ margin: 12px 0; padding: 12px 16px; background: var(--surface); border-left: 3px solid var(--accent); }}
blockquote p {{ margin: 0 0 8px; }} blockquote p:last-child {{ margin: 0; }}
code {{ font-family: var(--mono); font-size: .9em; }}
.copy {{ position: relative; max-width: 70ch; }}
.copy pre {{ background: var(--surface); border: 1px solid var(--line); padding: 14px 16px; overflow-x: auto; margin: 6px 0; white-space: pre; }}
.cbtn {{ position: absolute; top: 8px; right: 8px; font: 500 12px var(--body); background: var(--accent); color: var(--bg); border: 0; padding: 5px 10px; cursor: pointer; }}
.cbtn:focus-visible {{ outline: 2px solid var(--fg); outline-offset: 2px; }}
.tbl {{ overflow-x: auto; margin: 12px 0 18px; border: 1px solid var(--line); background: var(--surface); }}
table {{ border-collapse: collapse; width: 100%; font-size: 13.5px; font-variant-numeric: tabular-nums; }}
th, td {{ text-align: left; vertical-align: top; padding: 8px 10px; border-bottom: 1px solid var(--line); }}
th {{ font-size: 12px; letter-spacing: .04em; text-transform: uppercase; color: var(--muted); font-weight: 600; white-space: nowrap; }}
tr:last-child td {{ border-bottom: 0; }}
td.n {{ text-align: right; }}
#the-priority-table + p + h3 + figure ~ .tbl table, .wide table {{ min-width: 900px; }}
.tbl table {{ min-width: 640px; }}
figure.chart {{ margin: 16px 0 24px; padding: 16px; background: var(--surface); border: 1px solid var(--line); max-width: 720px; }}
figcaption {{ display: flex; flex-wrap: wrap; gap: 6px 18px; justify-content: space-between; font-size: 14px; margin-bottom: 8px; }}
.legend {{ display: flex; gap: 14px; color: var(--muted); font-size: 12.5px; }}
.legend i {{ display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 6px; vertical-align: -1px; }}
.k1 {{ background: var(--m1); }} .k2 {{ background: var(--m2); }}
.cwrap {{ position: relative; }}
svg {{ width: 100%; height: auto; display: block; }}
.m1 {{ fill: var(--m1); }} .m2 {{ fill: var(--m2); }}
.gl {{ stroke: var(--line); stroke-width: 1; }}
.ax {{ fill: var(--muted); font: 11px var(--body); }}
.dl {{ fill: var(--fg); font: 600 12px var(--body); }}
.bar:hover path {{ opacity: .8; }}
.tip {{ position: absolute; pointer-events: none; background: var(--fg); color: var(--bg); font-size: 12px; padding: 6px 8px; white-space: nowrap; transform: translate(-50%, -110%); }}
details {{ margin-top: 8px; font-size: 13px; }} summary {{ cursor: pointer; color: var(--accent); }}
#my-three-actions-today + p + ol {{ background: var(--accent-soft); padding: 18px 18px 18px 38px; }}
@media (max-width: 600px) {{ nav.sec {{ position: static; font-size: 12.5px; gap: 2px 12px; }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ scroll-behavior: auto !important; }} }}
html {{ scroll-behavior: smooth; }}
</style>
<div class="wrap">
<header class="top">
<div class="eyebrow">@moodiusaurelius · 26 Oct 2026 – 23 Jan 2027</div>
<h1>Ninety days of <em>old wisdom, new evidence</em></h1>
<p class="lede">A 90-day organic growth plan built on the account's own Metricool numbers to 24 Oct, the posts already scheduled to 7 Nov, and Instagram's current guidance. Every number marked as a hypothesis is one.</p>
</header>
<nav class="sec" aria-label="Sections">{navhtml}</nav>
<main>
{body}
</main>
</div>
<script>
document.querySelectorAll('.cbtn').forEach(b => b.addEventListener('click', () => {{
  const t = b.parentElement.querySelector('code').innerText.trim();
  const done = () => {{ b.textContent = 'Copied'; setTimeout(() => b.textContent = 'Copy', 1500); }};
  try {{ navigator.clipboard.writeText(t).then(done, () => sel(b)); }} catch (e) {{ sel(b); }}
}}));
function sel(b) {{ const r = document.createRange(); r.selectNodeContents(b.parentElement.querySelector('code')); const s = getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent = 'Selected'; }}
const tip = document.querySelector('.tip'), cw = document.querySelector('.cwrap');
document.querySelectorAll('.bar').forEach(g => {{
  g.addEventListener('mousemove', e => {{ const r = cw.getBoundingClientRect(); tip.textContent = g.dataset.tip; tip.style.left = (e.clientX - r.left) + 'px'; tip.style.top = (e.clientY - r.top) + 'px'; tip.hidden = false; }});
  g.addEventListener('mouseleave', () => tip.hidden = true);
}});
</script>
'''
OUT.write_text(page)
print("wrote", OUT, len(page))
