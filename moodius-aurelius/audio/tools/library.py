#!/usr/bin/env python3
"""Moodius music library: one catalogue, licence log, analysis and soundtrack candidates.

    python3 library.py build                         # originals.json + external.csv -> ../library/tracks.csv
    python3 library.py ingest                        # analyse files you dropped in ../library/external/<id>.<ext>
    python3 library.py candidates <batch.json> [--only D01] [--json out.json]
    python3 library.py credits <track_id>            # the exact attribution line for a caption

tracks.csv is the single source of truth for licence, attribution, source and usage rights.
A track is only mixed if status == in_library and commercial_ok == yes.
"""
import argparse, csv, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.dirname(HERE)
LIB = os.path.join(AUDIO, "library")
TRACKS = os.path.join(LIB, "tracks.csv")
USAGE = os.path.join(AUDIO, "usage-log.csv")
FIELDS = ["id", "title", "artist", "source", "source_url", "licence", "licence_url", "attribution", "commercial_ok",
          "platform_lock", "verification", "category", "mood", "energy", "bpm", "key", "instrumentation", "seconds",
          "lufs", "why", "file", "status"]
VARIANT_MOOD = {1: "sparse still", 2: "warm tender glowing", 3: "dark grave low", 4: "light hopeful airy"}
CATS = ["stoicism", "psychology", "masculinity", "existentialism", "relationships", "discipline", "refined"]

FORMAT_CAT = {"A": "psychology", "B": "stoicism", "C": "discipline", "D": "existentialism", "E": "masculinity",
              "F": "stoicism", "R1": "stoicism", "R2": "stoicism", "R3": "psychology", "R4": "refined", "R5": "psychology"}
KEYWORDS = {
    "relationships": r"\b(love|partner|friend|friends|intima|attach|text one|wedding|together|lonely)\w*",
    "existentialism": r"\b(meaning|absurd|death|grief|nostalg|past|used to|camus|kierkegaard|nietzsche|bench)\w*",
    "discipline": r"\b(discipline|habit|alarm|gym|grind|routine|monday|promise|word to yourself)\w*",
    "masculinity": r"\b(men|man|masculin|brother|father|self-reliance|strong)\b",
    "psychology": r"\b(brain|anxiety|feel|felt|feeling|psycholog|study|research|words)\w*",
    "stoicism": r"\b(seneca|marcus|epictetus|stoic|letters|meditations)\w*",
    "refined": r"\b(slow|coffee|morning|home|quiet|song|sit)\w*",
}
MOOD_WORDS = {"night": "dark introspective still slow", "warm": "tender warm elegant glowing", "low": "heavy grave low sparse",
              "dawn": "hopeful luminous light airy", "room": "still resting sparse weightless", "dry": "light curious unhurried"}
FORMAT_ENERGY = {"A": 1.5, "B": 1.5, "C": 2.5, "D": 1.5, "E": 2, "F": 2, "R1": 1.5, "R2": 2, "R3": 2.5, "R4": 2, "R5": 2}


def load():
    with open(TRACKS, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def save(rows):
    with open(TRACKS, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})


def build(_):
    old = {r["id"]: r for r in load()} if os.path.exists(TRACKS) else {}
    rows = []
    for m in json.load(open(os.path.join(LIB, "originals", "originals.json"))):
        rows.append(dict(id=m["id"], title=f"Moodius {m['category'].title()} {m['variant']}", artist="Moodius (original)",
                         source="audio/tools/compose.py", source_url="", licence="Owned (original composition)",
                         attribution="none needed", commercial_ok="yes", platform_lock="none",
                         verification="synthesised in-house, no samples or models", category=m["category"], mood=f"{m['mood']}, {VARIANT_MOOD[m['variant']]}",
                         energy=m["energy"], bpm=m["bpm"], key=m["key"], instrumentation=m["voices"], seconds=m["seconds"],
                         why="Scored to picture: re-rendered per reel so the harmony turns on the statement card",
                         file=f"originals/{m['id']}.m4a", status="in_library"))
    with open(os.path.join(LIB, "external.csv"), newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            prev = old.get(r["id"], {})
            for k in ("file", "status", "seconds", "lufs", "bpm"):
                if prev.get(k):
                    r[k] = prev[k]
            rows.append(r)
    save(rows)
    print(f"{len(rows)} tracks: {sum(r['status'] == 'in_library' for r in rows)} in library, "
          f"{sum(r['status'] != 'in_library' for r in rows)} to download")


def probe_seconds(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return round(float(out), 1) if out else ""


def lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    m = re.search(r'"input_i"\s*:\s*"([-\d.]+)"', r)
    return m.group(1) if m else ""


def ingest(_):
    rows = load()
    ext = os.path.join(LIB, "external")
    files = {os.path.splitext(f)[0]: f for f in os.listdir(ext)}
    for r in rows:
        if r["id"].startswith("EX-") and r["id"] in files:
            p = os.path.join(ext, files[r["id"]])
            r["file"], r["status"] = f"external/{files[r['id']]}", "in_library"
            r["seconds"], r["lufs"] = probe_seconds(p), lufs(p)
            print(f"{r['id']}  {r['title']:40s} {r['seconds']}s  {r['lufs']} LUFS")
    save(rows)


def usage_counts(last=7):
    if not os.path.exists(USAGE):
        return {}
    rows = list(csv.DictReader(open(USAGE, newline="")))[-last:]
    c = {}
    for r in rows:
        c[r["track_id"]] = c.get(r["track_id"], 0) + 1
    return c


def profile(script):
    text = " ".join([c[0] for c in script["cards"]] + [script.get("caption", "")]).lower()
    fmt = script.get("format", "B")
    primary = FORMAT_CAT.get(fmt, "stoicism")
    hits = {cat: len(re.findall(rx, text)) for cat, rx in KEYWORDS.items()}
    secondary = max((c for c in hits if c != primary), key=lambda c: hits[c])
    mood = MOOD_WORDS.get(script.get("audio", {}).get("mood", "night"), "")
    return primary, secondary if hits[secondary] else None, mood, FORMAT_ENERGY.get(fmt, 2)


def score(track, primary, secondary, mood, energy, used):
    s, why = 0.0, []
    if track["category"] == primary:
        s += 3; why.append(f"{primary} category")
    elif track["category"] == secondary:
        s += 1.8; why.append(f"matches the {secondary} theme in the text")
    overlap = set(mood.split()) & set(re.findall(r"\w+", track["mood"].lower()))
    s += min(2, len(overlap)); why += [f"mood: {', '.join(sorted(overlap))}"] if overlap else []
    try:
        e = float(track["energy"]); s -= 0.7 * abs(e - energy)
    except ValueError:
        pass
    if track["licence"].startswith("Owned"):
        s += 0.6; why.append("owned, scored to this reel's cuts")
    elif "Public domain" in track["licence"]:
        s += 0.2
    if track["status"] != "in_library":
        s -= 0.8; why.append("needs download first")
    if track["commercial_ok"] != "yes":
        s -= 99
    if used.get(track["id"]):
        s -= 1.5 * used[track["id"]]; why.append(f"used {used[track['id']]}x in the last 7 reels")
    return round(s, 2), why


def candidates(a):
    rows = [r for r in load() if r["commercial_ok"] == "yes"]
    batch = json.load(open(a.batch, encoding="utf-8"))
    used, out = usage_counts(), {}
    for sc in batch["scripts"]:
        if a.only and sc["id"] not in a.only.split(","):
            continue
        primary, secondary, mood, energy = profile(sc)
        ranked = sorted(((*score(t, primary, secondary, mood, energy, used), t) for t in rows), key=lambda x: -x[0])
        picks, cats = [], {}
        for sc_, why, t in ranked:                 # three genuinely different candidates: one per category
            if cats.get(t["category"], 0) >= 1:
                continue
            picks.append({"id": t["id"], "title": t["title"], "artist": t["artist"], "score": sc_, "why": why,
                          "status": t["status"], "attribution": t["attribution"]})
            cats[t["category"]] = cats.get(t["category"], 0) + 1
            if len(picks) == 3:
                break
        ext = next(((sc_, why, t) for sc_, why, t in ranked if t["id"].startswith("EX-")), None)
        if ext and not any(p["id"].startswith("EX-") for p in picks) and ext[0] >= picks[-1]["score"] - 1.5:
            sc_, why, t = ext                       # keep one real recording in view as the third option
            picks[-1] = {"id": t["id"], "title": t["title"], "artist": t["artist"], "score": sc_, "why": why,
                         "status": t["status"], "attribution": t["attribution"]}
        rec = next((p for p in picks if p["status"] == "in_library"), picks[0])
        out[sc["id"]] = {"profile": {"primary": primary, "secondary": secondary, "mood": mood, "energy": energy},
                         "candidates": picks, "recommended": rec["id"]}
        print(f"\n{sc['id']} {sc.get('slug', '')}  [{primary}{' + ' + secondary if secondary else ''} · {mood} · energy {energy}]")
        for p in picks:
            star = "★" if p["id"] == rec["id"] else " "
            print(f" {star} {p['id']:10s} {p['title'][:38]:38s} {p['score']:5.2f}  {'; '.join(p['why'])}")
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1, ensure_ascii=False)
    return out


def credits(a):
    t = next(r for r in load() if r["id"] == a.track_id)
    print(t["attribution"] if t["attribution"] != "none needed" else "")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("build"); sp.add_parser("ingest")
    c = sp.add_parser("candidates"); c.add_argument("batch"); c.add_argument("--only"); c.add_argument("--json")
    cr = sp.add_parser("credits"); cr.add_argument("track_id")
    a = ap.parse_args()
    {"build": build, "ingest": ingest, "candidates": candidates, "credits": credits}[a.cmd](a)


if __name__ == "__main__":
    main()
