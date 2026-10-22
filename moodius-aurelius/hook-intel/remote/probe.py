"""Reachability probe #2 for the hook-intel remote fetcher (runs on GitHub Actions)."""
import json, subprocess, urllib.request

def ytdlp(args):
    p = subprocess.run(["yt-dlp", "--no-warnings", *args], capture_output=True, text=True, timeout=240)
    return p.returncode, p.stdout, p.stderr[-400:]

rc, out, err = ytdlp(["--flat-playlist", "-J", "ytsearch3:stoicism shorts"])
if rc == 0: print("SEARCH ENTRY KEYS:", json.dumps(json.loads(out)["entries"][0])[:1500])
rc, out, err = ytdlp(["--flat-playlist", "-J", "--playlist-end", "3", "https://www.youtube.com/@DailyStoic/shorts"])
if rc == 0: print("SHORTS ENTRY:", json.dumps(json.loads(out)["entries"][0])[:1500])
for client in ["tv", "web_embedded", "mweb", "android_vr", "web_safari", "tv_simply"]:
    rc, out, err = ytdlp(["-J", "--skip-download", "--extractor-args", f"youtube:player_client={client}", "https://www.youtube.com/shorts/5_06_YawRhs"])
    keys = {}
    if rc == 0 and out.strip() and out.strip() != "null":
        d = json.loads(out); keys = {k: d.get(k) for k in ["upload_date", "view_count", "like_count", "comment_count", "duration"]}
        keys["subs"] = list((d.get("automatic_captions") or {}).keys())[:3]
    print(f"CLIENT {client} rc={rc} {keys} {err[-200:] if rc else ''}", flush=True)
for u in ["https://www.tiktok.com/@withmindful/video/7653749995597794574", "https://www.tiktok.com/@xmentality.10/video/7627968887551692064"]:
    rc, out, err = ytdlp(["-J", "--skip-download", u])
    if rc == 0:
        d = json.loads(out); print("TIKTOK", {k: d.get(k) for k in ["upload_date", "view_count", "like_count", "comment_count", "duration", "uploader", "channel_follower_count", "title"]}, list((d.get("subtitles") or {}).keys()))
    else: print("TIKTOK FAIL", err)
rc, out, err = ytdlp(["--flat-playlist", "-J", "--playlist-end", "5", "https://www.tiktok.com/@withmindful"])
print("TIKTOK USER rc", rc, out[:600], err)
for url in ["https://www.youtube.com/feeds/videos.xml?channel_id=UCkUaT0T03TJvafYkfATM2Ag"]:
    try: print("RSS", urllib.request.urlopen(url, timeout=20).read()[:2500])
    except Exception as e: print("RSS FAIL", e)
