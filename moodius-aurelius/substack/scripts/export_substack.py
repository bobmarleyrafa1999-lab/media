#!/usr/bin/env python3
"""Turn an approved essay into Substack-ready files. Publishes nothing.

Usage: python3 scripts/export_substack.py essays/01-writing-to-no-one.md [...]

For each essay, writes to exports/<slug>/:
  post.html      - body HTML to paste into Substack's editor (title/subtitle go in their own fields)
  preview.html   - the same body in Moodius type and colours, for reading before approval
  meta.txt       - title, subtitle, A/B alt title, suggested URL slug, SEO description
Substack's editor ignores pasted Markdown but keeps pasted rich text, so open
preview.html in a browser, select the article body and copy-paste (see 09-setup.md).
Requires pandoc.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = """
body{margin:0;background:#F3EFE7;color:#1B1F24;font:18px/1.65 Inter,system-ui,sans-serif}
main{max-width:680px;margin:0 auto;padding:48px 20px}
h1,h2{font-family:'Playfair Display',Georgia,serif;font-weight:600;line-height:1.2}
h1{font-size:2.2em;margin:0 0 .2em} h2{font-size:1.35em;margin-top:2em}
.subtitle{font-family:'Playfair Display',Georgia,serif;font-style:italic;color:#3A4049;font-size:1.15em}
blockquote{margin:1.5em 0;padding-left:1em;border-left:3px solid #C9742E;font-family:'Playfair Display',Georgia,serif;font-style:italic}
strong{font-weight:600} a{color:#1B1F24} hr{border:0;border-top:1px solid #B8B3A9;margin:2em 0}
.note{font-size:.85em;color:#3A4049;background:#fff8;padding:8px 12px;border-radius:6px}
"""


def front(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta


def export(path):
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    meta = front(text)
    pub = re.search(r"<!-- publish:start -->(.*?)<!-- publish:end -->", text, re.S).group(1).strip()
    # Title and subtitle go into Substack's own fields, so drop them from the body.
    pub = re.sub(r"^# .*\n+", "", pub)
    pub = re.sub(r"^\*[^*\n].*\*\n+", "", pub, count=1)
    html = subprocess.run(["pandoc", "-f", "markdown", "-t", "html", "--wrap=none"],
                          input=pub, capture_output=True, text=True, check=True).stdout
    slug = re.sub(r"[^a-z0-9]+", "-", meta.get("title", path.stem).lower().replace("'", "").replace("’", "")).strip("-")
    out = ROOT / "exports" / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / "post.html").write_text(html, encoding="utf-8")
    preview = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
               f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
               f"<title>{meta.get('title', '')}</title><style>{CSS}</style></head><body><main>"
               f"<p class='note'>Preview for approval. Paste the title and subtitle into Substack's own fields, then copy from the first paragraph down.</p>"
               f"<h1>{meta.get('title', '')}</h1><p class='subtitle'>{meta.get('subtitle', '')}</p>{html}</main></body></html>")
    (out / "preview.html").write_text(preview, encoding="utf-8")
    first_para = re.sub(r"<[^>]+>", "", html.split("</p>")[0]).strip()
    seo = (meta.get("subtitle", "") or first_para)[:155]
    (out / "meta.txt").write_text(
        f"Title: {meta.get('title', '')}\nSubtitle: {meta.get('subtitle', '')}\n"
        f"A/B alternative title: {meta.get('ab_alt_title', '')}\nURL slug: {slug}\n"
        f"SEO description (155 chars): {seo}\nSection: {meta.get('series', '')}\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    targets = sys.argv[1:] or sorted(str(p) for p in (ROOT / "essays").glob("*.md"))
    for t in targets:
        print("exported", export(t).relative_to(ROOT))
