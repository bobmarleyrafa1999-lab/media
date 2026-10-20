#!/usr/bin/env python3
"""Build strategy/upload-pack/<date>/ folders: final media + caption.txt per day, plus manifest.json.

    python3 build.py            # everything
    python3 build.py --no-reels # skip the slow reel re-renders
"""
import datetime as dt, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PACK))            # moodius-aurelius/
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import stills_v3, reels_v2                                # noqa: E402
from content import *                                     # noqa: E402

QUEUE = json.load(open(os.path.join(HERE, "metricool-queue-2026-10-20.json")))
DAYS = [dt.date(2026, 10, 20) + dt.timedelta(d) for d in range(13)]
SEP = "-" * 60


def mc(date, kind):
    t = {"carousel": "POST", "reel": "REEL"}[kind]
    for p in QUEUE:
        if p["publicationDate"]["dateTime"].startswith(date) and p["instagramData"]["type"] == t:
            return p
    return None


def caption_for(date, kind):
    if CAPTIONS.get((date, kind)):
        text, first, alt = CAPTIONS[(date, kind)]
    else:
        p = mc(date, kind)
        text, first, alt = p["text"], p.get("firstCommentText", ""), (p.get("mediaAltText") or [""])[0]
        text = re.sub(r"\n\n(#\S+\s*)+$", "", text.strip())      # strip the old hashtag line
        if (date, kind) not in TAGS:
            TAGS[(date, kind)] = " ".join(re.findall(r"#\w+", p["text"])[:5])
    tags = TAGS[(date, kind)]
    assert len(tags.split()) <= 5, (date, kind, tags)
    return f"{text}\n\n{tags}", first, alt


def save(img, path):
    img.save(path, quality=94)


def reel_cover(mp4, out, t=1.4):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", mp4, "-frames:v", "1", "-q:v", "2", out], check=True)


def main(do_reels=True):
    manifest = []
    for day in DAYS:
        date = day.isoformat()
        out = os.path.join(PACK, date)
        os.makedirs(out, exist_ok=True)
        tz = "+02:00" if day < dt.date(2026, 10, 25) else "+01:00"
        items = []

        if date == "2026-10-20":
            spec = json.load(open(os.path.join(ROOT, "strategy", "manifesto-stories", "manifesto-stories.json")))
            for i, (name, s) in enumerate(spec.items(), 1):
                f = f"2000-story-manifesto-{i}.jpg"
                save(stills_v3.render(s), os.path.join(out, f))
                items.append({"time": f"20:0{i - 1}", "type": "STORY", "files": [f], "highlight": "Manifesto"})
            manifest.append({"date": date, "tz": tz, "items": items})
            continue

        d_story, j_story = STORIES[date]
        save(stills_v3.render(d_story), os.path.join(out, "0900-story-daily.jpg"))
        items.append({"time": "09:00", "type": "STORY", "files": ["0900-story-daily.jpg"], "highlight": d_story["label"]})

        if date in NEW_CAROUSELS:
            slides = NEW_CAROUSELS[date]
        else:
            allc = json.load(open(os.path.join(ROOT, "strategy", "phase1-first-five", "carousels.json")))
            pre = OLD_CAROUSELS[date] + "-"
            slides = {k[len(pre):]: dict(v, **OLD_OVERRIDES.get(k, {})) for k, v in allc.items() if k.startswith(pre)}
        files = []
        n = len(slides)
        for i, (k, s) in enumerate(sorted(slides.items()), 1):
            s = dict(s, page=f"{i}/{n}")
            f = f"1200-carousel-{i:02d}.jpg"
            save(stills_v3.render(s), os.path.join(out, f))
            files.append(f)
        cap, first, alt = caption_for(date, "carousel")
        items.append({"time": "12:00", "type": "CAROUSEL", "files": files, "caption": cap, "first_comment": first, "alt": alt})

        rtime = "17:00" if day.weekday() == 4 else "18:00"
        rt = rtime.replace(":", "")
        mp4, cover = f"{rt}-reel.mp4", f"{rt}-reel-cover.jpg"
        if date in REELS_V2:
            name, spec = REELS_V2[date]
            if do_reels or not os.path.exists(os.path.join(out, mp4)):
                reels_v2.render(name, spec, out)
                os.replace(os.path.join(out, f"{name}.mp4"), os.path.join(out, mp4))
            reel_cover(os.path.join(out, mp4), os.path.join(out, cover))
        else:
            src = os.path.join(ROOT, "reels-engine", "renders", ENGINE_REELS[date])
            shutil.copyfile(src + ".mp4", os.path.join(out, mp4))
            shutil.copyfile(src + "-cover.jpg", os.path.join(out, cover))
        cap, first, alt = caption_for(date, "reel")
        items.append({"time": rtime, "type": "REEL", "files": [mp4, cover], "caption": cap, "first_comment": first, "alt": alt})

        save(stills_v3.render(j_story), os.path.join(out, "2100-story-journal.jpg"))
        items.append({"time": "21:00", "type": "STORY", "files": ["2100-story-journal.jpg"], "highlight": "Journal"})
        manifest.append({"date": date, "tz": tz, "items": items})

    for day in manifest:
        write_caption_txt(day)
    json.dump(manifest, open(os.path.join(PACK, "manifest.json"), "w"), indent=1, ensure_ascii=False)


def write_caption_txt(day):
    d = dt.date.fromisoformat(day["date"])
    lines = [f"MOODIUS AURELIUS · {d.strftime('%A %d %B %Y')} · Madrid time (UTC{day['tz']})", ""]
    if day["date"] == "2026-10-20":
        lines += ["Tonight, or any time this week: the 4 Manifesto stories. Post them in order, 1 to 4,",
                  "then add all four to the Manifesto highlight (it should be the first highlight).", ""]
    for it in day["items"]:
        head = f"== {it['time']} · {it['type']}"
        if it["type"] == "CAROUSEL":
            head += f" ({len(it['files'])} slides)"
        lines += [head + " " + "=" * max(4, 56 - len(head)), ""]
        if it["type"] == "STORY":
            lines += [f"File: {it['files'][0]}", f"After it's live: add it to the \"{it['highlight']}\" highlight.", "No caption."]
            if it["highlight"] == "Journal":
                lines += ["Optional (app only): add a Question sticker in the empty space under the text."]
        else:
            if it["type"] == "CAROUSEL":
                lines += [f"Files, in this order: {it['files'][0]} to {it['files'][-1]}"]
            else:
                lines += [f"Video: {it['files'][0]}", f"Cover: {it['files'][1]} (Edit cover > Add from camera roll / Upload)",
                          "Turn ON \"Also share to feed\"."]
            lines += ["", "Caption (copy everything between the lines):", SEP, it["caption"], SEP, "",
                      "First comment (post it yourself as soon as the post is live):", SEP, it["first_comment"], SEP, "",
                      f"Alt text (Advanced settings > Accessibility): {it['alt']}"]
        lines.append("")
    open(os.path.join(PACK, day["date"], "caption.txt"), "w").write("\n".join(lines))


if __name__ == "__main__":
    main(do_reels="--no-reels" not in sys.argv)
