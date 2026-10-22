#!/usr/bin/env python3
"""Moodius Aurelius -> Pinterest, direct API (v5).

Two steps, so nothing goes public without a look first:

  python3 pins.py plan  [--from 2026-10-21] [--to 2026-11-01] [--link URL]
      Reads strategy/upload-pack/manifest.json, makes 2 pins per carousel
      (cover + one quote slide) at 1000x1500 in pinterest/out/, and writes
      pinterest/pins-plan.json. Edit titles, boards or slides there freely.

  python3 pins.py post  [--limit 2] [--sandbox]
      Creates missing boards, then posts the next N unposted pins from the
      plan and records them in pinterest/pins-log.csv (never posts twice).

Token: PINTEREST_ACCESS_TOKEN in the environment, or the file written by the
quickstart's `get_access_token.py -w` (common/oauth_tokens/access_token.json,
path in PINTEREST_TOKEN_FILE). Scopes: boards:read boards:write pins:read
pins:write. The token is never written by this script.
"""
import argparse, base64, csv, json, os, re, sys, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent          # moodius-aurelius/
HERE = ROOT / "pinterest"
PACK = ROOT / "strategy" / "upload-pack"
FONTS = ROOT / "tools" / "fonts"
PLAN, LOG, OUT = HERE / "pins-plan.json", HERE / "pins-log.csv", HERE / "out"
DEFAULT_LINK = "https://www.instagram.com/moodiusaurelius/"   # swap for the Kit page once it exists

SLATE, BONE, ASH, EMBER = (27, 31, 36), (243, 239, 231), (184, 179, 169), (201, 116, 46)

BOARDS = {   # from strategy/13-distribution-channels.md
    "Stoic tools for anxiety": "anxious overthink rehears disaster 2am heavy feeling avoid comment",
    "Anger and patience": "rude anger argument patience insult",
    "Self-trust and discipline": "discipline self-trust promise lazy habit burnout do less philosophy show",
    "Grief and loss": "grief loss death mourning",
    "Evening review and journaling": "evening review journal night reflect horses mind close",
}
BOARD_DESC = "Stoicism for people who feel things. Cited lines from Marcus Aurelius, Seneca and Epictetus, made usable."


def pick_board(text):
    t = text.lower()
    scores = {b: sum(w in t for w in kw.split()) for b, kw in BOARDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "Self-trust and discipline"


def clean_caption(caption):
    lines = [l for l in caption.split("\n") if not l.strip().startswith("#")]
    body = "\n".join(lines).strip()
    body = re.sub(r"\n*(Save this|Send (it|this)).*$", "", body, flags=re.S | re.I).strip()
    return body


def search_title(first_line):
    t = first_line.strip().rstrip(".")
    return (t[:97] + "...") if len(t) > 100 else t


def render(src, dst, footer):
    canvas = Image.new("RGB", (1000, 1500), SLATE)
    slide = Image.open(src).convert("RGB").resize((1000, 1250), Image.LANCZOS)
    canvas.paste(slide, (0, 0))
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 1250, 1000, 1253], fill=EMBER)
    serif = ImageFont.truetype(str(FONTS / "Playfair-SemiBold.ttf"), 44)
    sans = ImageFont.truetype(str(FONTS / "Inter-Medium.ttf"), 30)
    d.text((500, 1340), footer, font=serif, fill=BONE, anchor="mm")
    d.text((500, 1420), "@moodiusaurelius  ·  free guide at the link", font=sans, fill=ASH, anchor="mm")
    canvas.save(dst, "JPEG", quality=90)


def cmd_plan(a):
    manifest = json.loads((PACK / "manifest.json").read_text())
    OUT.mkdir(exist_ok=True)
    pins = []
    for day in manifest:
        if not (a.date_from <= day["date"] <= a.date_to):
            continue
        for item in day["items"]:
            if item["type"] != "CAROUSEL":
                continue
            files, cap = item["files"], item["caption"]
            first = cap.split("\n")[0]
            board = pick_board(cap)
            desc = clean_caption(cap)[:780]
            picks = [(files[0], "cover", "Stoicism for people who feel things")]
            if len(files) > 2:
                picks.append((files[1], "quote", "Save it for a loud day"))
            for f, kind, footer in picks:
                name = f"{day['date']}-{kind}.jpg"
                render(PACK / day["date"] / f, OUT / name, footer)
                pins.append({
                    "id": f"{day['date']}-{kind}", "image": f"out/{name}",
                    "source": f"strategy/upload-pack/{day['date']}/{f}",
                    "board": board,
                    "title": search_title(first if kind == "cover" else first.rstrip(".") + " | Stoic quote"),
                    "description": desc, "link": a.link,
                    "alt_text": (item.get("alt") or first)[:490],
                })
    PLAN.write_text(json.dumps({"link": a.link, "boards": list(BOARDS), "pins": pins}, indent=1, ensure_ascii=False))
    print(f"{len(pins)} pins planned -> {PLAN}")


def token():
    t = os.environ.get("PINTEREST_ACCESS_TOKEN")
    if t:
        return t
    f = Path(os.environ.get("PINTEREST_TOKEN_FILE", "common/oauth_tokens/access_token.json"))
    if f.exists():
        return json.loads(f.read_text())["access_token"]
    sys.exit("No token: set PINTEREST_ACCESS_TOKEN or PINTEREST_TOKEN_FILE.")


class Api:
    def __init__(self, tok, sandbox):
        self.base = "https://api-sandbox.pinterest.com/v5" if sandbox else "https://api.pinterest.com/v5"
        self.h = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}

    def call(self, method, path, body=None):
        req = urllib.request.Request(self.base + path, method=method, headers=self.h,
                                     data=json.dumps(body).encode() if body is not None else None)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            sys.exit(f"{method} {path} -> {e.code}: {e.read().decode()[:400]}")

    def boards(self):
        out, bookmark = {}, None
        while True:
            q = "/boards?page_size=100" + (f"&bookmark={bookmark}" if bookmark else "")
            r = self.call("GET", q)
            out.update({b["name"]: b["id"] for b in r.get("items", [])})
            bookmark = r.get("bookmark")
            if not bookmark:
                return out


def cmd_post(a):
    plan = json.loads(PLAN.read_text())
    done = set()
    if LOG.exists():
        done = {r["id"] for r in csv.DictReader(LOG.open())}
    todo = [p for p in plan["pins"] if p["id"] not in done][: a.limit]
    if not todo:
        return print("Nothing left to post.")
    api = Api(token(), a.sandbox)
    boards = api.boards()
    for name in {p["board"] for p in todo} - boards.keys():
        boards[name] = api.call("POST", "/boards", {"name": name, "description": BOARD_DESC, "privacy": "PUBLIC"})["id"]
        print("created board", name)
    new = not LOG.exists()
    with LOG.open("a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["id", "pin_id", "board", "posted_at", "sandbox"])
        for p in todo:
            data = base64.b64encode((HERE / p["image"]).read_bytes()).decode()
            r = api.call("POST", "/pins", {
                "board_id": boards[p["board"]], "title": p["title"], "description": p["description"],
                "link": p["link"], "alt_text": p["alt_text"],
                "media_source": {"source_type": "image_base64", "content_type": "image/jpeg", "data": data},
            })
            w.writerow([p["id"], r.get("id"), p["board"], datetime.now(timezone.utc).isoformat(timespec="seconds"), a.sandbox])
            print("posted", p["id"], r.get("id"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--from", dest="date_from", default="2026-10-21")
    p.add_argument("--to", dest="date_to", default="2099-12-31")
    p.add_argument("--link", default=DEFAULT_LINK)
    q = sub.add_parser("post")
    q.add_argument("--limit", type=int, default=2)
    q.add_argument("--sandbox", action="store_true", help="use api-sandbox (needed while the app is on Trial access)")
    a = ap.parse_args()
    {"plan": cmd_plan, "post": cmd_post}[a.cmd](a)
