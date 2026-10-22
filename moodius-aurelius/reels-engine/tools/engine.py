#!/usr/bin/env python3
"""Moodius reels engine: quality gate + deterministic batch renderer (Phase 1 design system).

    python3 engine.py check   scripts/batch-01.json            # QC only, no rendering
    python3 engine.py render  scripts/batch-01.json [--only R001,R002] [--variant b]
                              [--layout upper|centre] [--force] [--out ../renders]
    python3 engine.py registry                                  # every citation already used on the account

Extends tools/reels_v2.py: same tokens (tools/design.py), adds card kinds (hook/body/quote/cite/cta),
a rise-and-fade text animation, optional background footage, an ambient bed (ambient.py) or a
score.py cue, a cover JPG and caption file per reel, and a render cache so unchanged scripts
are skipped. No AI calls, no paid software: Python 3, Pillow, NumPy/SciPy and FFmpeg.
"""
import argparse, glob, hashlib, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE_DIR = os.path.dirname(HERE)                       # reels-engine/
PROJECT = os.path.dirname(ENGINE_DIR)                    # moodius-aurelius/
sys.path.insert(0, os.path.join(PROJECT, "tools"))
from design import *  # noqa: E402,F401  (SLATE, BONE, ASH, EMBER, fonts, MARGIN, HANDLE)
ENGINE_TOOLS = os.path.dirname(os.path.abspath(__file__))  # design.py also defines HERE

VERSION = "1.0"
W, H = 1080, 1920
MAX_W = W - 2 * MARGIN
FOOTAGE = os.path.join(ENGINE_DIR, "footage")
CACHE = os.path.join(ENGINE_DIR, "renders", ".cache.json")

STYLE = {  # kind: (font, size, colour)
    "hook": (DISPLAY, 84, BONE),
    "quote": (QUOTE, 64, BONE),
    "body": (BODY_M, 60, BONE),
    "cite": (BODY_M, 32, ASH),
    "cta": (BODY_SB, 50, BONE),
}
PD_TRANSLATIONS = ("Long", "Gummere", "Trotter", "Garnett", "Common", "Jowett", "Ross", "Higginson", "Basore")
BANNED = ["studies show", "science proves", "guaranteed", "cure", "alpha", "high value", "high-value",
          "grindset", "sigma", "level up", "unlock", "game-changer", "game changer", "dive into",
          "embrace your", "in today's world", "journey", "manifest", "hustle", "king"]


# ---------- citation registry ----------
CITE_RE = re.compile(r"(Meditations|Enchiridion|Ench\.|Discourses|Letters?|On Anger|Pensées|Gay Science|"
                     r"Nicomachean Ethics|Republic|Phaedrus|Twilight of the Idols|Brothers Karamazov)"
                     r"[ ,]*(?:Book\s*)?([IVX]+\.\d+|\d+(?:\.\d+)?)")


def norm(work, sec):
    work = {"Ench.": "Enchiridion", "Letter": "Letters"}.get(work, work)
    return f"{work} {sec}"


def registry(exclude_engine=True):
    """Every work+section cited anywhere in the project's text files (manifests, calendars, docs)."""
    used = {}
    for path in glob.glob(os.path.join(PROJECT, "**", "*.*"), recursive=True):
        if not path.endswith((".json", ".md", ".csv", ".txt")):
            continue
        if exclude_engine and path.startswith(ENGINE_DIR):
            continue
        try:
            text = open(path, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        for line in text.splitlines():
            for work, sec in CITE_RE.findall(line):
                used.setdefault(norm(work, sec), {}).setdefault(os.path.relpath(path, PROJECT), []).append(line)
    return used


# ---------- quality gate ----------
def words(s):
    return len(re.findall(r"[\w’']+", s))


def qc(script, used):
    """Return (errors, warnings). Errors block rendering."""
    err, warn = [], []
    cards = script["cards"]
    total = sum(d for _, d, _ in cards)
    if not 7 <= total <= 20.5:
        (warn if total <= 40 else err).append(f"length {total:.1f}s outside 7-20s")
    text0, d0, k0 = cards[0]
    if k0 != "hook":
        err.append("first card must be the hook")
    for label, h in (("hook", text0), ("hook_b", script.get("hook_b", ""))):
        if words(h) > 14 if label == "hook_b" else words(h) > 12:
            err.append(f"{label} has {words(h)} words (max {14 if label == 'hook_b' else 12})")
    if d0 > 2.6:
        warn.append("hook card longer than 2.6s")
    for i, (t, d, k) in enumerate(cards):
        need = 0.4 + words(t) / 4.5   # ~270 wpm for short lines; viewers also loop
        if k not in ("cite",) and d < need - 0.2:
            err.append(f"card {i + 1} too fast to read ({d}s for {words(t)} words, needs ~{need:.1f}s)")
        if k == "quote" and (i + 1 >= len(cards) or cards[i + 1][2] != "cite"):
            err.append(f"card {i + 1} is a quote without a cite card after it")
    src = script["source"]
    has_quote = any(k == "quote" for _, _, k in cards)
    if has_quote:
        if src["type"] != "quote":
            err.append("quote card but source.type is not 'quote'")
        if not any(p in src.get("translation", "") for p in PD_TRANSLATIONS):
            err.append(f"translation '{src.get('translation')}' is not on the public-domain list")
        key = norm(src["work"].replace("Moral Letters to Lucilius", "Letters").split(":")[0],
                   src["section"].split()[0])
        # a calendar row that books this very script (mentions its id) is not a repeat
        clash = sorted(f for f, lines in used.get(key, {}).items()
                       if not all(script["id"] in ln for ln in lines))
        if clash:
            err.append(f"{key} already used in: {', '.join(clash[:3])}")
    if src["type"] == "idea" and not any(k == "cite" and "Idea:" in t for t, _, k in cards):
        err.append("idea from a book needs an 'Idea: … · Moodius words' cite card")
    cap = script["caption"]
    if len(cap) > 2200:
        err.append("caption over 2,200 characters")
    if "?" not in cap:
        warn.append("caption has no question")
    if len(script.get("hashtags", [])) > 5:
        err.append("more than 5 hashtags")
    if not script.get("first_comment"):
        err.append("no first comment")
    blob = " ".join([t for t, _, _ in cards] + [cap, script.get("first_comment", "")]).lower()
    for b in BANNED:
        if re.search(r"\b" + re.escape(b) + r"\b", blob):
            err.append(f"banned phrase: '{b}'")
    return err, warn


# ---------- rendering ----------
def wrap(text, font, fs):
    from PIL import ImageFont
    width = ImageFont.truetype(font, fs).getlength
    out = []
    for ln in text.split("\n"):
        cur = ""
        for word in ln.split(" "):
            cand = f"{cur} {word}".strip()
            if cur and width(cand) > MAX_W:
                out.append(cur)
                cur = word
            else:
                cur = cand
        out.append(cur)
    return out


def card_layout(text, kind):
    font, fs, col = STYLE[kind]
    if kind == "cite":
        text = text.upper()
    lines = wrap(text, font, fs)
    while kind in ("quote", "body", "hook") and len(lines) > 6 and fs > 44:
        fs -= 4
        lines = wrap(text, font, fs)
    return font, fs, col, lines


def footage_for(tag):
    if not tag:
        return None
    hits = sorted(glob.glob(os.path.join(FOOTAGE, f"{tag}*.mp4")) + glob.glob(os.path.join(FOOTAGE, f"{tag}*.mov")))
    return hits[0] if hits else None


def build_filter(script, total, layout, clip, tmp):
    centre_y = 880 if layout == "upper" else 960
    f = []
    if clip:
        f.append(f"[1:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                 f"hue=s=0.25,eq=brightness=-0.06:contrast=0.95,setsar=1,fps=30,trim=0:{total:.2f},setpts=PTS-STARTPTS[foot];"
                 f"color=c={hexc(SLATE)}@0.72:s={W}x{H}:d={total:.2f},format=rgba[tint];"
                 f"[foot][tint]overlay=0:0,format=yuv420p[bg]")
    else:
        f.append(f"color=c={hexc(SLATE)}:s={W}x{H}:d={total:.2f},format=yuv420p[bg]")
    chain, n, t = "[bg]", 0, 0.2
    for ci, (text, d, kind) in enumerate(script["cards"]):
        font, fs, col, lines = card_layout(text, kind)
        lh = fs * 1.28
        y0 = centre_y - lh * len(lines) / 2
        a = (f"if(lt(t-{t:.2f},0.3),(t-{t:.2f})/0.3,"
             f"if(gt(t-{t:.2f},{d - 0.3:.2f}),({t + d:.2f}-t)/0.3,1))")
        rise = f"14*max(0,1-(t-{t:.2f})/0.35)"
        for j, ln in enumerate(lines):
            tf = os.path.join(tmp, f"c{ci}_{j}.txt")
            with open(tf, "w", encoding="utf-8") as fh:
                fh.write(ln)
            nxt = f"[v{n}]"
            f.append(f"{chain}drawtext=fontfile={font}:textfile={tf}:expansion=none:fontsize={fs}:"
                     f"fontcolor={hexc(col)}:x={MARGIN}:y='{y0 + j * lh:.0f}+{rise}':alpha='{a}':"
                     f"enable='between(t,{t:.2f},{t + d:.2f})'{nxt}")
            chain, n = nxt, n + 1
        if kind == "hook":  # the single Ember accent: a short rule under hook cards
            nxt = f"[v{n}]"
            f.append(f"{chain}drawbox=x={MARGIN}:y={y0 + lh * len(lines) + 18:.0f}:w=120:h=5:"
                     f"color={hexc(EMBER)}:t=fill:enable='between(t,{t + 0.25:.2f},{t + d - 0.2:.2f})'{nxt}")
            chain, n = nxt, n + 1
        t += d
    f.append(f"{chain}drawbox=x={MARGIN}:y={MARGIN + 196}:w=14:h=14:color={hexc(EMBER)}:t=fill,"
             f"drawtext=fontfile={BODY_SB}:text='M O O D I U S':fontsize=28:fontcolor={hexc(BONE)}:x={MARGIN + 30}:y={MARGIN + 190},"
             f"drawtext=fontfile={BODY}:text='{HANDLE}':fontsize=32:fontcolor={hexc(ASH)}:x={MARGIN}:y=1560[vout]")
    return ";".join(f)


def audio(script, total, wav):
    a = script["audio"]
    if a.get("engine", "ambient") == "ambient":
        cmd = [sys.executable, os.path.join(ENGINE_TOOLS, "ambient.py"), a["mood"], f"{total:.2f}", str(a["seed"]), wav]
    else:
        cmd = [sys.executable, os.path.join(PROJECT, "tools", "score.py"), a["style"], f"{total:.2f}", str(a["seed"]), wav]
    subprocess.run(cmd, check=True, capture_output=True)


def render(script, out_dir, layout="upper", variant="a"):
    s = json.loads(json.dumps(script))
    if variant == "b" and s.get("hook_b"):
        s["cards"][0][0] = s["hook_b"]
        s["cards"][0][1] = max(s["cards"][0][1], round(0.45 + words(s["hook_b"]) / 4.5, 1))
    total = sum(d for _, d, _ in s["cards"]) + 0.4
    name = f"{s['id']}-{s['slug']}" + ("" if variant == "a" else f"-{variant}")
    clip = footage_for(s.get("footage"))
    out = os.path.join(out_dir, f"{name}.mp4")
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "bed.wav")
        audio(s, total, wav)
        inputs = ["-i", wav] + (["-stream_loop", "-1", "-i", clip] if clip else [])
        filt = build_filter(s, total, layout, clip, tmp) + ";[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[aout]"
        cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", filt,
               "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.2f}", "-r", "30",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out]
        r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        return name, False, r.stderr[-800:]
    hook_mid = 0.2 + s["cards"][0][1] * 0.6
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{hook_mid:.2f}", "-i", out, "-frames:v", "1",
                    "-q:v", "3", os.path.join(out_dir, f"{name}-cover.jpg")], check=False)
    with open(os.path.join(out_dir, f"{name}.txt"), "w", encoding="utf-8") as fh:
        fh.write(s["caption"] + "\n\n" + " ".join(s.get("hashtags", [])) + "\n\n---\nFirst comment:\n" + s["first_comment"] + "\n")
    return name, True, f"{total:.1f}s" + (" footage" if clip else " flat")


def digest(script, layout, variant):
    blob = json.dumps([script, layout, variant, VERSION, footage_for(script.get("footage"))], sort_keys=True)
    return hashlib.sha1(blob.encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check", "render", "registry"])
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--only")
    ap.add_argument("--variant", default="a", choices=["a", "b"])
    ap.add_argument("--layout", default="upper", choices=["upper", "centre"])
    ap.add_argument("--out", default=os.path.join(ENGINE_DIR, "renders"))
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    used = registry()
    if args.cmd == "registry":
        for k in sorted(used):
            print(f"{k:32s} {len(used[k])} file(s)")
        return
    batch = json.load(open(args.spec, encoding="utf-8"))
    scripts = [s for s in batch["scripts"] if not args.only or s["id"] in args.only.split(",")]
    # within-batch duplicates count too
    seen = {}
    for s in scripts:
        src = s["source"]
        if src["type"] == "quote":
            seen.setdefault((src["work"], src["section"]), []).append(s["id"])
    dupes = {k: v for k, v in seen.items() if len(v) > 1}

    os.makedirs(args.out, exist_ok=True)
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    bad = 0
    for s in scripts:
        err, warn = qc(s, used)
        for k, v in dupes.items():
            if s["id"] in v:
                err.append(f"source {k} used twice in this batch: {v}")
        status = "FAIL" if err else "pass"
        print(f"{s['id']} {s['slug']:26s} {status}" + "".join(f"\n   ✗ {e}" for e in err) + "".join(f"\n   ! {w}" for w in warn))
        if err:
            bad += 1
            continue
        if args.cmd == "render":
            key = f"{s['id']}:{args.variant}:{args.layout}"
            h = digest(s, args.layout, args.variant)
            if not args.force and cache.get(key) == h:
                print("   = unchanged, skipped")
                continue
            name, ok, msg = render(s, args.out, args.layout, args.variant)
            print(f"   → {name}.mp4 {msg if ok else 'ERROR ' + msg}")
            if ok:
                cache[key] = h
    if args.cmd == "render":
        with open(CACHE, "w") as fh:
            json.dump(cache, fh, indent=1)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
