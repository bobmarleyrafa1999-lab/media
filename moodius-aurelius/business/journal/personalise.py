#!/usr/bin/env python3
"""Makes and delivers personalised copies for shop orders.

    export SITE_URL=https://yourdomain  ADMIN_TOKEN=...      # the shop's admin token
    python3 personalise.py --list                    # orders waiting to be made
    python3 personalise.py ord_abc123                # build both editions into out/personal/ord_abc123/ and upload
    python3 personalise.py ord_abc123 --deliver      # ...and email the link (buyer, or gift recipient)
    python3 personalise.py --file order.json         # build only, from a JSON file (no shop needed)

A gift with a send date isn't delivered before that date unless you add --now.
"""
import argparse, datetime, json, os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_journal import build, clean_personal  # noqa: E402

SRC = os.path.join(HERE, "content", "the-unexamined-self.yaml")
EDITIONS = [("digital", "The-Unexamined-Self-Personal-A5-digital.pdf"), ("print", "The-Unexamined-Self-Personal-A4-print.pdf")]


def api(method, path, body=None, content_type="application/json"):
    site, token = os.environ.get("SITE_URL", "").rstrip("/"), os.environ.get("ADMIN_TOKEN", "")
    if not site or not token:
        sys.exit("Set SITE_URL and ADMIN_TOKEN first.")
    req = urllib.request.Request(f"{site}/api/shop/admin/{path}", data=body, method=method,
                                 headers={"authorization": f"Bearer {token}", "content-type": content_type})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path}: {e.code} {e.read().decode()[:300]}")


def make(personal, out_dir):
    clean_personal(personal)  # fail early with a readable message
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for edition, name in EDITIONS:
        out = os.path.join(out_dir, name)
        pages, fields = build(SRC, out, edition, personal)
        print(f"  {name}: {pages} pages, {fields} fields")
        paths.append((edition, out))
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("order", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--file")
    ap.add_argument("--deliver", action="store_true")
    ap.add_argument("--now", action="store_true", help="deliver a gift before its send date")
    a = ap.parse_args()

    if a.list:
        for o in api("GET", "personal-queue")["queue"]:
            p = o["personal"]
            when = f" send {p['send_date']}" if p.get("send_date") else ""
            print(f"{o['id']}  {o['personal_status']:9}  {o['product_slug']:30}  {p.get('name', '')}{when}{'  TEST' if o['test_mode'] else ''}")
        return
    if a.file:
        make(json.load(open(a.file)), os.path.join(HERE, "out", "personal", "from-file"))
        return
    if not a.order:
        ap.error("give an order id, --list or --file")

    o = api("GET", f"orders/{a.order}/personal")
    if o["status"] != "paid":
        sys.exit(f"{a.order} is {o['status']}; not making it.")
    print(f"{a.order} ({o['product_slug']}{', TEST' if o['test_mode'] else ''})")
    for edition, path in make(o["personal"], os.path.join(HERE, "out", "personal", a.order)):
        r = api("PUT", f"orders/{a.order}/personal-file?edition={edition}", open(path, "rb").read(), "application/pdf")
        print(f"  uploaded {edition}: {r['bytes']} bytes")
    if a.deliver:
        send = o["personal"].get("send_date")
        if send and send > datetime.date.today().isoformat() and not a.now:
            print(f"  not delivering yet: the buyer asked for {send}. Run again with --deliver on that day.")
            return
        api("POST", f"orders/{a.order}/personal-deliver", b"{}")
        print("  delivered: link emailed")


if __name__ == "__main__":
    main()
