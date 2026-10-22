"""Local dashboard: Discover, Analyse, Create, Library, Performance. Standard library only.

    python3 -m hookintel dashboard              # http://127.0.0.1:8765 (local only)
    python3 -m hookintel dashboard --static out.html   # one self-contained file with the data baked in
"""
import http.server, json, os, urllib.parse

from . import config, db, performance, report

HTML = os.path.join(config.PKG, "dashboard.html")


def snapshot(con):
    base = performance.baseline(con)
    performance.load_experiments(con)
    own = db.rows(con, "SELECT * FROM own_posts ORDER BY published")
    for p in own:
        p["bands"] = performance.compare_post(p, base)
    exps = [performance.review_experiment(con, e["id"], base) for e in db.rows(con, "SELECT * FROM experiments")]
    concepts = db.rows(con, "SELECT * FROM concepts ORDER BY id")
    for c in concepts:
        c["data"] = json.loads(c["data"]) if c["data"] else {}
        c["qc"] = json.loads(c["qc"]) if c["qc"] else {}
    pats = db.rows(con, "SELECT * FROM patterns ORDER BY rank")
    for p in pats:
        p["examples"] = json.loads(p["examples"] or "[]")
    acc = {k: {"ok": v["ok"], "failed": v["failed"], "errors": sorted(v["errors"])}
           for k, v in report.access_summary().items()}
    return {
        "videos": db.rows(con, """SELECT v.*, h.hook_text, h.hook_text_source, h.category, h.secondary, h.structure,
                                         h.hook_score, h.priority, h.pillar, h.tone, h.visual_style, h.flags, h.why,
                                         h.adaptation, h.first_frame, h.music, h.length_s, h.confidence, h.evidence,
                                         h.strong, h.specificity, h.clarity, h.originality, h.emotional, h.visual, h.alignment
                                  FROM videos v LEFT JOIN hooks h ON h.video_id = v.id
                                  ORDER BY h.priority DESC NULLS LAST, v.views DESC"""),
        "patterns": pats, "concepts": concepts, "own": own, "baseline": base, "experiments": exps,
        "recommendations": performance.recommendations(con, base), "access": acc,
    }


def write_static(con, path):
    page = open(HTML, encoding="utf-8").read()
    blob = json.dumps(snapshot(con), ensure_ascii=False, default=str).replace("</", "<\\/")
    page = page.replace("/*__DATA__*/null", blob)
    open(path, "w", encoding="utf-8").write(page)
    return path


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, body, ctype="application/json", code=200):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802
        url = urllib.parse.urlparse(self.path)
        con = db.connect()
        try:
            if url.path in ("/", "/index.html"):
                self._send(open(HTML, encoding="utf-8").read(), "text/html")
            elif url.path == "/api/all":
                self._send(json.dumps(snapshot(con), ensure_ascii=False, default=str))
            elif url.path == "/api/search":
                q = urllib.parse.parse_qs(url.query).get("q", [""])[0]
                self._send(json.dumps([r["id"] for r in db.search(con, q, 200)]))
            elif url.path.startswith("/export/"):
                name = os.path.basename(url.path)
                report.export(con)
                path = os.path.join(config.EXPORTS, name)
                if os.path.exists(path):
                    self._send(open(path, "rb").read(), "text/csv" if name.endswith(".csv") else "application/json")
                else:
                    self._send("not found", "text/plain", 404)
            else:
                self._send("not found", "text/plain", 404)
        finally:
            con.close()

    def log_message(self, *args):
        pass


def serve(port=8765):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"dashboard on http://127.0.0.1:{port}  (Ctrl+C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
