#!/usr/bin/env python3
"""Moodius reels engine: quality gate + deterministic batch renderer (Phase 1 design system).

    python3 engine.py check   scripts/batch-01.json            # QC only, no rendering
    python3 engine.py render  scripts/batch-01.json [--only R001,R002] [--variant b]
                              [--layout upper|centre] [--force] [--out ../renders]
    python3 engine.py registry                                  # every citation already used on the account
    python3 engine.py doctor  scripts/batch-02.json [--only …]  # Script Doctor brief (prompts/script-doctor.md)

1.3 (22 Oct 2026, beat grammar, opt-in with "grammar": "beat" on the batch or a script): the hook is on
screen at frame 0 (no fade from blank), "quiz" pause cards with a draining Ember timer, "reveal" cards that
build line by line, a loop ending whose last frame is frame 0, a phone-size QA sheet per render with a
safe-zone and loop check, a Script Doctor score in QC, and a word-for-word quote check (quotes.py, all
scripts). Beat grammar adapted from hassancs91/claude-faceless-shorts-creator (MIT, Hasan Aboul Hasan);
Script Doctor from Purffle Studios' purffle-shorts (MIT). Classic scripts render exactly as before.

1.2 (21 Oct 2026, formats A-F): question / labelled / pause cards, still-photo backgrounds with a slow
drift, optional film grain ("texture": "grain"), "max_s" for longer essays, data sources need a dated cite.

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
sys.path.insert(0, ENGINE_TOOLS)
import quotes  # noqa: E402  (1.3)

VERSION = "1.1"  # 1.1 (20 Oct 2026): no one-word last lines
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
    "question": (DISPLAY, 88, BONE),   # 1.2: format A hook
    "labelled": (BODY_M, 60, BONE),    # 1.2: first line is an Ember label (format C)
    "pause": (BODY_M, 60, BONE),       # 1.2: an empty beat
    "quiz": (DISPLAY, 76, BONE),       # 1.3: a question held on screen with a draining timer
    "reveal": (BODY_M, 60, BONE),      # 1.3: one line per step ("\n"), each appearing in turn
}
LOOP_S = 0.6                           # 1.3: the hook fades back in over the last 0.6 s
SAFE_BOTTOM, SAFE_RIGHT, SAFE_RIGHT_FROM = H - 340, W - 160, 1100   # Instagram caption and button column
DOCTOR_MIN = 70
STOP = set("the a an and or but of to in on at for with you your you're it its it's is are was be this that "
           "they them their what when who how why not no do does did i me my we our than then just".split())
LABEL = (BODY_SB, 30, EMBER)
PD_TRANSLATIONS = ("Long", "Gummere", "Trotter", "Garnett", "Common", "Jowett", "Ross", "Higginson", "Basore")
BANNED = ["studies show", "science proves", "guaranteed", "cure", "alpha", "high value", "high-value",
          "grindset", "sigma", "level up", "unlock", "game-changer", "game changer", "dive into",
          "embrace your", "in today's world", "journey", "manifest", "hustle", "king",
          # 1.2: format E guardrails (masculinity without the manosphere)
          "smv", "hypergamy", "simp", "beta male", "female nature", "red pill", "redpill", "alpha male"]


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
        if os.sep + "upload-pack" + os.sep in path:   # copies of already-scheduled posts
            continue
        if path.endswith("research-library.csv"):     # libraries list candidates, not uses
            continue
        if os.sep + "hook-intel" + os.sep in path and os.sep + "data" + os.sep + "scripts" + os.sep not in path:
            continue                                   # 1.3: hook-intel mirrors posts (ours and others'), not plans
        if os.sep + "renders" + os.sep in path:        # 1.3: caption files beside renders repeat their script
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
    max_s = script.get("max_s", 20.5)   # format D may set up to 45
    if not 7 <= total <= max_s:
        (warn if total <= max(40, max_s + 5) else err).append(f"length {total:.1f}s outside 7-{max_s:g}s")
    text0, d0, k0 = cards[0]
    if k0 not in ("hook", "question"):
        err.append("first card must be the hook")
    for label, h in (("hook", text0), ("hook_b", script.get("hook_b", ""))):
        if words(h) > 14 if label == "hook_b" else words(h) > 12:
            err.append(f"{label} has {words(h)} words (max {14 if label == 'hook_b' else 12})")
    if d0 > (3.0 if k0 == "question" else 2.6):
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
    if src["type"] == "data" and not any(k == "cite" and re.search(r"\b(19|20)\d{2}\b", t) for t, _, k in cards):
        err.append("a study or survey needs a cite card with its year")
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
    # 1.3: every quote card checked word for word against the public-domain text
    for t, _, k in cards:
        if k == "quote":
            status, detail = quotes.check(src.get("work", ""), src.get("section", ""), src.get("translation", ""), t)
            if status == "missing":
                err.append(f"quote does not match {src.get('translation')}: {detail}")
            elif status == "manual" and not src.get("verified_at"):
                warn.append(f"quote not machine-checked ({detail}); add source.verified_at once checked")
    for seg in plan(script)[0]:
        if seg["role"] == "text" and (seg["y"] + seg["fs"] > SAFE_BOTTOM or
                                      (seg["x"] + seg["w"] > SAFE_RIGHT and seg["y"] + seg["fs"] > SAFE_RIGHT_FROM)):
            warn.append(f"card {seg['card'] + 1} line '{seg['text'][:24]}…' sits under Instagram's buttons or caption")
            break
    if script.get("grammar") == "beat":
        err += beat_qc(script, warn)
    return err, warn


def beat_qc(script, warn):
    """1.3 beat grammar: hook at frame 0 → setup → optional quiz → reveal → payoff → loop."""
    err, cards = [], script["cards"]
    kinds = [k for _, _, k in cards]
    starts = [sum(d for _, d, _ in cards[:i]) for i in range(len(cards))]
    quiz = [i for i, k in enumerate(kinds) if k == "quiz"]
    if len(quiz) > 1:
        err.append("more than one quiz card")
    for i in quiz:
        t, d, _ = cards[i]
        if i in (0, len(cards) - 1) or kinds[i + 1] in ("cta", "cite"):
            err.append(f"quiz card {i + 1} must sit mid-reel and be answered by the next card")
        if not t.rstrip().endswith("?"):
            err.append(f"quiz card {i + 1} must be a question")
        if not 2.0 <= d <= 3.5:
            err.append(f"quiz card {i + 1} lasts {d}s (2.0-3.5s)")
    for i, (t, d, k) in enumerate(cards):
        if k == "reveal":
            steps = [s for s in t.split("\n") if s.strip()]
            if not 2 <= len(steps) <= 4:
                err.append(f"reveal card {i + 1} has {len(steps)} steps (2-4)")
            if d < reveal_gap(d, len(steps)) * (len(steps) - 1) + 0.4 + words(steps[-1]) / 4.5:
                err.append(f"reveal card {i + 1} too short for its last step to be read")
    if not any(k in ("quiz", "labelled", "question", "reveal") and 5 <= starts[i] <= 10
               for i, k in enumerate(kinds) if i):
        warn.append("no pattern change between 5 and 10s (hook-system rule 6: quiz, label, question or reveal)")
    body = [i for i, k in enumerate(kinds) if k not in ("cta", "cite", "pause")]
    if len(body) > 2:
        key = lambda s: {w for w in re.findall(r"[a-z’']+", s.lower()) if len(w) > 3 and w not in STOP}
        if not key(cards[0][0]) & key(cards[body[-1]][0]):
            warn.append("payoff card doesn't reuse a word from the hook (hook-system rule 7)")
    doc = script.get("doctor")
    if not doc:
        warn.append("no Script Doctor score yet (engine.py doctor; prompts/script-doctor.md)")
    elif doc.get("score", 0) < DOCTOR_MIN:
        err.append(f"Script Doctor score {doc.get('score')} is under {DOCTOR_MIN}: {'; '.join(doc.get('issues', [])[:2])}")
    return err


# ---------- rendering ----------
def wrap(text, font, fs):
    """Greedy wrap; if the last line is a single word, balance the lines instead (no runts)."""
    from PIL import ImageFont
    width = ImageFont.truetype(font, fs).getlength

    def greedy(ln, max_w):
        out, cur = [], ""
        for word in ln.split(" "):
            cand = f"{cur} {word}".strip()
            if cur and width(cand) > max_w:
                out.append(cur)
                cur = word
            else:
                cur = cand
        return out + [cur]

    out = []
    for ln in text.split("\n"):
        lines = greedy(ln, MAX_W)
        if len(lines) > 1 and " " not in lines[-1]:
            lo, hi = MAX_W * 0.5, MAX_W
            for _ in range(14):
                mid = (lo + hi) / 2
                lo, hi = (lo, mid) if len(greedy(ln, mid)) == len(lines) else (mid, hi)
            lines = greedy(ln, hi)
        out += lines
    return out


def card_layout(text, kind):
    font, fs, col = STYLE[kind]
    if kind == "cite":
        text = text.upper()
    lines = wrap(text, font, fs)
    while kind in ("quote", "body", "hook", "question") and len(lines) > 6 and fs > 44:
        fs -= 4
        lines = wrap(text, font, fs)
    return font, fs, col, lines


def footage_for(tag):
    if not tag:
        return None
    hits = sorted(sum((glob.glob(os.path.join(FOOTAGE, f"{tag}*.{e}")) for e in ("mp4", "mov", "jpg", "jpeg", "png")), []))
    return hits[0] if hits else None


def is_still(path):
    return bool(path) and path.lower().endswith((".jpg", ".jpeg", ".png"))


def reveal_gap(d, n):
    return min(1.0, max(0.5, (d - 1.2) / max(n, 1)))


def timing(script):
    """(first card start, total length). Beat grammar starts at frame 0 and ends on the loop."""
    body = sum(d for _, d, _ in script["cards"])
    return (0.0, body + LOOP_S) if script.get("grammar") == "beat" else (0.2, body + 0.4)


def plan(script, layout="upper"):
    """Every drawn element with its time window: (segments, total). Shared by the renderer and QC."""
    beat = script.get("grammar") == "beat"
    centre_y = 880 if layout == "upper" else 960
    t, total = timing(script)
    segs = []

    def fade(t0, d, fade_in=True):   # same expression as 1.2 so classic renders are unchanged
        out = f"if(gt(t-{t0:.2f},{d - 0.3:.2f}),({t0 + d:.2f}-t)/0.3,1)"
        return f"if(lt(t-{t0:.2f},0.3),(t-{t0:.2f})/0.3,{out})" if fade_in else out

    for ci, (text, d, kind) in enumerate(script["cards"]):
        if kind == "pause":
            t += d
            continue
        first = beat and ci == 0                      # frame-0 rule: fully composed, no rise, no fade-in
        rise = "0" if first else f"14*max(0,1-(t-{t:.2f})/0.35)"
        if kind == "labelled":  # Ember label line, then the body lines
            label, _, body = text.partition("\n")
            font, fs, col, lines = card_layout(body, "body")
            lh = fs * 1.28
            y0 = centre_y - (lh * len(lines) + 62) / 2 + 62
            rows = [(LABEL[0], LABEL[1], LABEL[2], label.upper(), y0 - 62, t)] + \
                   [(font, fs, col, ln, y0 + j * lh, t) for j, ln in enumerate(lines)]
        elif kind == "reveal":  # each step's lines appear in turn and stay until the card ends
            steps = [s for s in text.split("\n") if s.strip()]
            font, fs, col = STYLE["reveal"]
            wrapped = [wrap(s, font, fs) for s in steps]
            lh, gap_y = fs * 1.28, fs * 0.5
            height = sum(lh * len(w) for w in wrapped) + gap_y * (len(steps) - 1)
            y, rows, g = centre_y - height / 2, [], reveal_gap(d, len(steps))
            for si, w in enumerate(wrapped):
                for ln in w:
                    rows.append((font, fs, col, ln, y, t + si * g))
                    y += lh
                y += gap_y
            lines = [r[3] for r in rows]
            y0 = rows[0][4]
        else:
            font, fs, col, lines = card_layout(text, kind)
            lh = fs * 1.28
            y0 = centre_y - lh * len(lines) / 2
            rows = [(font, fs, col, ln, y0 + j * lh, t) for j, ln in enumerate(lines)]
        for sfont, sfs, scol, ln, y, ts in rows:
            segs.append({"role": "text", "card": ci, "font": sfont, "fs": sfs, "col": scol, "text": ln,
                         "x": MARGIN, "y": y, "w": text_width(ln, sfont, sfs), "t0": ts, "t1": t + d,
                         "rise": rise if ts == t else f"14*max(0,1-(t-{ts:.2f})/0.35)",
                         "alpha": fade(ts, t + d - ts, fade_in=not first)})
        if kind in ("hook", "question"):  # the single Ember accent: a short rule under hook cards
            segs.append({"role": "rule", "card": ci, "x": MARGIN, "y": y0 + lh * len(lines) + 18, "w": 120, "h": 5,
                         "t0": t if first else t + 0.25, "t1": t + d - 0.2})
        if kind == "quiz":  # a timer that drains right to left while the question is held
            n, bw = 30, MAX_W / 30
            for k in range(n):
                segs.append({"role": "rule", "card": ci, "x": MARGIN + k * bw, "y": y0 + lh * len(lines) + 34,
                             "w": bw + 1, "h": 6, "t0": t + 0.3, "t1": t + 0.3 + (d - 0.6) * (n - k) / n})
        t += d
    if beat:  # loop: the hook fades back in so the last frame is frame 0
        ls = total - LOOP_S
        for s in [s for s in segs if s["card"] == 0]:
            s2 = dict(s, card=-1, t0=ls, t1=total + 1)
            if s["role"] == "text":
                s2.update(rise="0", alpha=f"min(1,(t-{ls:.2f})/{LOOP_S - 0.15:.2f})")
            else:
                s2.update(t0=ls + 0.15)
            segs.append(s2)
    return segs, total


def text_width(text, font, fs):
    from PIL import ImageFont
    return ImageFont.truetype(font, fs).getlength(text)


def build_filter(script, total, layout, clip, tmp):
    f = []
    beat = script.get("grammar") == "beat"
    grain = ",noise=alls=7:allf=t" if script.get("texture") == "grain" else ""
    # 1.2: a photograph drifting ~5% over the reel; 1.3 beat: there and back, so the loop lands on frame 0
    drift = (lambda a: f"{a:.0f}*sin(PI*t/{total:.2f})") if beat else (lambda a: f"{a:.0f}*t/{total:.2f}")
    if is_still(clip):
        f.append(f"[1:v]scale={int(W * 1.1)}:{int(H * 1.1)}:force_original_aspect_ratio=increase,crop={int(W * 1.1)}:{int(H * 1.1)},"
                 f"crop={W}:{H}:x='{drift(W * 0.1)}':y='{drift(H * 0.05)}',"
                 f"hue=s=0.25,eq=brightness=-0.06:contrast=0.95,setsar=1,fps=30,trim=0:{total:.2f},setpts=PTS-STARTPTS[foot];"
                 f"color=c={hexc(SLATE)}@0.72:s={W}x{H}:d={total:.2f},format=rgba[tint];"
                 f"[foot][tint]overlay=0:0{grain},format=yuv420p[bg]")
    elif clip:
        f.append(f"[1:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                 f"hue=s=0.25,eq=brightness=-0.06:contrast=0.95,setsar=1,fps=30,trim=0:{total:.2f},setpts=PTS-STARTPTS[foot];"
                 f"color=c={hexc(SLATE)}@0.72:s={W}x{H}:d={total:.2f},format=rgba[tint];"
                 f"[foot][tint]overlay=0:0{grain},format=yuv420p[bg]")
    else:
        f.append(f"color=c={hexc(SLATE)}:s={W}x{H}:d={total:.2f}{grain},format=yuv420p[bg]")
    chain, n = "[bg]", 0
    segs, _ = plan(script, layout)
    for j, s in enumerate(segs):
        nxt = f"[v{n}]"
        if s["role"] == "text":
            tf = os.path.join(tmp, f"s{j}.txt")
            with open(tf, "w", encoding="utf-8") as fh:
                fh.write(s["text"])
            f.append(f"{chain}drawtext=fontfile={s['font']}:textfile={tf}:expansion=none:fontsize={s['fs']}:"
                     f"fontcolor={hexc(s['col'])}:x={s['x']}:y='{s['y']:.0f}+{s['rise']}':alpha='{s['alpha']}':"
                     f"enable='between(t,{s['t0']:.2f},{s['t1']:.2f})'{nxt}")
        else:
            f.append(f"{chain}drawbox=x={s['x']:.0f}:y={s['y']:.0f}:w={s['w']:.0f}:h={s['h']}:"
                     f"color={hexc(EMBER)}:t=fill:enable='between(t,{s['t0']:.2f},{s['t1']:.2f})'{nxt}")
        chain, n = nxt, n + 1
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
    total = timing(s)[1]
    name = f"{s['id']}-{s['slug']}" + ("" if variant == "a" else f"-{variant}")
    clip = footage_for(s.get("footage"))
    out = os.path.join(out_dir, f"{name}.mp4")
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "bed.wav")
        audio(s, total, wav)
        inputs = ["-i", wav] + ((["-loop", "1", "-framerate", "30", "-i", clip] if is_still(clip)
                                 else ["-stream_loop", "-1", "-i", clip]) if clip else [])
        filt = build_filter(s, total, layout, clip, tmp) + ";[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[aout]"
        cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", filt,
               "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.2f}", "-r", "30",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
               *(["-maxrate", "8M", "-bufsize", "16M"] if s.get("texture") == "grain" else []),  # grain is incompressible
               "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out]
        r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        return name, False, r.stderr[-800:]
    beat = s.get("grammar") == "beat"
    hook_mid = 0.0 if beat else 0.2 + s["cards"][0][1] * 0.6   # beat: frame 0 is thumbnail-grade
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{hook_mid:.2f}", "-i", out, "-frames:v", "1",
                    "-q:v", "3", os.path.join(out_dir, f"{name}-cover.jpg")], check=False)
    qa = qa_sheet(s, out, out_dir, name, total) if beat or s.get("qa") else ""
    with open(os.path.join(out_dir, f"{name}.txt"), "w", encoding="utf-8") as fh:
        fh.write(s["caption"] + "\n\n" + " ".join(s.get("hashtags", [])) + "\n\n---\nFirst comment:\n" + s["first_comment"] + "\n")
    return name, True, f"{total:.1f}s" + (" still" if is_still(clip) else " footage" if clip else " flat") + \
        (" +grain" if s.get("texture") == "grain" else "") + qa


def grab(video, t, path):
    """One frame at t seconds; t=None is the video's very last frame."""
    seek = ["-sseof", "-0.4", "-i", video, "-update", "1"] if t is None else \
        ["-ss", f"{max(t, 0):.3f}", "-i", video, "-frames:v", "1"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *seek, path], check=True)
    from PIL import Image
    return Image.open(path).convert("RGB")


def qa_sheet(script, video, out_dir, name, total):
    """1.3 phone-size QA: frame 0, the middle of every card and the last frame at 1/3 size, Instagram's
    caption and button zones shaded, plus two automatic checks. Writes <name>-qa.png and -qa.json."""
    from PIL import Image, ImageDraw, ImageChops, ImageStat, ImageFont
    t, _ = timing(script)
    stops = [("frame 0", 0.0)]
    for i, (_, d, k) in enumerate(script["cards"]):
        if i and k != "pause":
            stops.append((f"card {i + 1}", t + d * (0.85 if k == "reveal" else 0.5)))
        t += d
    stops.append(("last frame", total - 1 / 30))
    with tempfile.TemporaryDirectory() as tmp:
        frames = [(lab, ts, grab(video, None if lab == "last frame" else ts, os.path.join(tmp, f"{j}.png")))
                  for j, (lab, ts) in enumerate(stops)]
    first, last = frames[0][2], frames[-1][2]
    # text on frame 0: share of pixels far brighter than the Slate ground
    lum = first.convert("L")
    bright = sum(lum.histogram()[150:]) / (W * H)
    loop_diff = sum(ImageStat.Stat(ImageChops.difference(first, last)).mean) / 3
    checks = {"frame0_has_text": bright > 0.004, "frame0_bright_share": round(bright, 4),
              "loop_matches_frame0": loop_diff < 4.0, "loop_mean_abs_diff": round(loop_diff, 2)}
    sw, sh, cols = W // 3, H // 3, 5
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (sw + 16) + 16, rows * (sh + 52) + 16), SLATE)
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(BODY_M, 22)
    for j, (lab, ts, im) in enumerate(frames):
        x, y = 16 + (j % cols) * (sw + 16), 16 + (j // cols) * (sh + 52)
        thumb = im.resize((sw, sh)).convert("RGBA")
        zone = Image.new("RGBA", thumb.size, (0, 0, 0, 0))
        zd = ImageDraw.Draw(zone)
        zd.rectangle([0, SAFE_BOTTOM // 3, sw, sh], fill=(220, 60, 60, 60))
        zd.rectangle([SAFE_RIGHT // 3, SAFE_RIGHT_FROM // 3, sw, SAFE_BOTTOM // 3], fill=(220, 60, 60, 60))
        sheet.paste(Image.alpha_composite(thumb, zone).convert("RGB"), (x, y))
        draw.text((x, y + sh + 10), f"{lab} · {ts:.1f}s", font=label_font, fill=ASH)
    sheet.save(os.path.join(out_dir, f"{name}-qa.png"))
    json.dump(checks, open(os.path.join(out_dir, f"{name}-qa.json"), "w"), indent=1)
    bad = [k for k in ("frame0_has_text", "loop_matches_frame0") if not checks[k]]
    return " QA " + ("ok" if not bad else "CHECK " + ", ".join(bad))


def digest(script, layout, variant):
    blob = json.dumps([script, layout, variant, VERSION, footage_for(script.get("footage"))], sort_keys=True)
    # (1.2 features are opt-in per script, so VERSION stays 1.1 and scheduled reels aren't re-rendered)
    return hashlib.sha1(blob.encode()).hexdigest()


def doctor_brief(scripts):
    """The Script Doctor's input: the rubric once, then each draft with its timings. Claude scores it,
    rewrites below 70, and stores {"score", "issues", "rewritten", "by"} as the script's "doctor" field."""
    rubric = open(os.path.join(ENGINE_DIR, "prompts", "script-doctor.md"), encoding="utf-8").read()
    out = [rubric, "\n---\n# Drafts"]
    for s in scripts:
        t, rows = timing(s)[0], []
        for text, d, k in s["cards"]:
            rows.append(f"  {t:5.1f}s  {k:9s} {text.replace(chr(10), ' / ')}")
            t += d
        src = s.get("source", {})
        out.append(f"\n## {s['id']} {s.get('slug', '')} ({s.get('format', '')})\n" + "\n".join(rows) +
                   f"\n  source: {src.get('type')} {src.get('work', '')} {src.get('section', '')} {src.get('translation', '')}"
                   f"\n  caption last line: {s.get('caption', '').strip().splitlines()[-1] if s.get('caption') else ''}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check", "render", "registry", "doctor"])
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
    for s in scripts:   # 1.3: a batch-level "grammar" applies to every script that doesn't set its own
        if batch.get("grammar") and "grammar" not in s:
            s["grammar"] = batch["grammar"]
    if args.cmd == "doctor":
        print(doctor_brief(scripts))
        return
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
