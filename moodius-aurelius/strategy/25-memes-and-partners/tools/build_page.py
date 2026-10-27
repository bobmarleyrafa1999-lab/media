#!/usr/bin/env python3
"""Build the one-page summary + tap-to-approve tracker (page.html).
Decisions are stored in the artifact's db collection "decisions" (doc id = item id),
which Claude reads back and copies into data/queue.csv and data/commercial.csv."""
import base64, csv, html, io, json, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = html.escape


def thumb(path, w=540, quality=82):
    im = Image.open(path).convert("RGB")
    im = im.resize((w, int(im.height * w / im.width)))
    b = io.BytesIO()
    im.save(b, "JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def main(out):
    concepts = json.load(open(os.path.join(ROOT, "data", "concepts.json")))["concepts"]
    commercial = list(csv.DictReader(open(os.path.join(ROOT, "data", "commercial.csv"))))
    cal = [r for r in csv.DictReader(open(os.path.join(ROOT, "04-calendar-14-day.csv"))) if r["lane"] != "stories"]
    covers = thumb(os.path.join(ROOT, "highlights", "text-cards", "preview.png"), 620, 88)

    memes = []
    for c in concepts:
        s = c["scores"]
        foot = f'<p class="foot">Slide 2: {E(c["footnote"])}</p>' if c["footnote"] else ""
        memes.append(f'''
<article class="meme" data-id="{c['id']}" data-pillar="{c['pillar']}">
  <img src="{thumb(os.path.join(ROOT, 'renders', c['id'] + '.png'))}" alt="{E(c['setup'] + ' ' + c['punch'])}" loading="lazy" width="540" height="675">
  <div class="meta">
    <div class="row"><span class="id">{c['id']}</span><span class="chip">{c['pillar']}</span><span class="chip ok">Original · cleared</span></div>
    <p class="cap">“{E(c['caption'])}” <span class="tags">{E(' '.join(c['hashtags']))}</span></p>
    <p class="score">Humour {s['humour']} · Relevance {s['relevance']} · Thought {s['thought']}</p>
    <p class="why">{E(c['why'])}</p>
    <p class="concern"><b>Watch:</b> {E(c['concerns'])}</p>{foot}
    <p class="fmt">{E(c['format'])}</p>
    <div class="actions" role="group" aria-label="Decision for {c['id']}">
      <button data-v="approve">Approve</button><button data-v="edit">Edit</button><button data-v="reject">Reject</button>
    </div>
    <input class="note" id="note-{c['id']}" placeholder="Note (what to change, or why not)" aria-label="Note for {c['id']}">
    <p class="state" aria-live="polite"></p>
  </div>
</article>''')

    cards = []
    for r in commercial:
        rows = "".join(f"<tr><th>{k}</th><td>{E(r[f])}</td></tr>" for k, f in [
            ("Product", "product"), ("Fit", "audience_fit"), ("Content & claims", "content_and_claims"),
            ("Payment", "payment"), ("Paid when", "payment_timing"), ("Deliverables", "deliverables"),
            ("Your time", "workload"), ("Exclusivity", "exclusivity"), ("Usage rights", "usage_rights"),
            ("Paid amplification", "paid_amplification"), ("Account access", "account_access"),
            ("Disclosure", "disclosure"), ("Concerns", "concerns"), ("Recommendation", "recommendation"),
            ("Next action", "next_action")])
        cards.append(f'''
<article class="card" data-id="{r['id']}">
  <div class="row"><span class="id">{r['id']}</span><h3>{E(r['brand'])}</h3><span class="chip">{E(r['status'])}</span></div>
  <div class="tablewrap"><table>{rows}</table></div>
  <div class="actions" role="group" aria-label="Decision for {r['id']}">
    <button data-v="approve">Approve</button><button data-v="edit">Request changes</button><button data-v="reject">Reject</button>
  </div>
  <input class="note" id="note-{r['id']}" placeholder="Note" aria-label="Note for {r['id']}">
  <p class="state" aria-live="polite"></p>
</article>''')

    lane = {"meme": "Meme", "educational": "Learn", "recommendation": "Pick"}
    calrows = "".join(
        f'<tr><td class="num">{r["date"][8:]} {["","","","","","","","","","","","Nov","Dec"][int(r["date"][5:7])]}</td><td>{r["day"]} {r["time_madrid"]}</td>'
        f'<td><span class="lane {r["lane"]}">{lane[r["lane"]]}</span></td><td>{E(r["content"])}</td><td class="st">{E(r["status"])}</td></tr>'
        for r in cal)

    page = TEMPLATE.replace("{{MEMES}}", "".join(memes)).replace("{{CARDS}}", "".join(cards)) \
        .replace("{{CAL}}", calrows).replace("{{COVERS}}", covers)
    open(out, "w").write(page)
    print(out, len(page) // 1024, "KB")


TEMPLATE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "page_template.html")).read()

if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "page.html"))
