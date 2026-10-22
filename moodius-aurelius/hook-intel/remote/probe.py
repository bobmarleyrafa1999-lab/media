"""One-off reachability probe for the hook-intel remote fetcher (runs on GitHub Actions)."""
import json, subprocess, sys, urllib.request

def ytdlp(args):
    p = subprocess.run(["yt-dlp", "--no-warnings", *args], capture_output=True, text=True, timeout=240)
    return p.returncode, p.stdout[:1500], p.stderr[-800:]

tests = {
    "yt_search_flat": ["--flat-playlist", "-J", "ytsearch5:stoicism shorts"],
    "yt_video_full": ["-J", "--skip-download", "https://www.youtube.com/shorts/5_06_YawRhs"],
    "yt_channel_shorts_flat": ["--flat-playlist", "-J", "--playlist-end", "5", "https://www.youtube.com/@DailyStoic/shorts"],
    "yt_subs": ["--skip-download", "--write-auto-subs", "--sub-langs", "en", "--sub-format", "vtt", "-o", "/tmp/sub", "https://www.youtube.com/shorts/5_06_YawRhs"],
    "tiktok_user": ["--flat-playlist", "-J", "--playlist-end", "3", "https://www.tiktok.com/@dailystoic"],
}
for name, args in tests.items():
    rc, out, err = ytdlp(args)
    print(f"### {name} rc={rc}\nOUT: {out[:700]}\nERR: {err}\n", flush=True)
import glob; print("subs files:", glob.glob("/tmp/sub*"))
for f in glob.glob("/tmp/sub*"): print(open(f).read()[:600])
for url in ["https://itunes.apple.com/search?term=philosophy&entity=podcastEpisode&limit=3",
            "https://www.youtube.com/oembed?url=https://www.youtube.com/shorts/5_06_YawRhs&format=json",
            "https://www.tiktok.com/oembed?url=https://www.tiktok.com/@dailystoic"]:
    try:
        print("###", url, urllib.request.urlopen(url, timeout=20).read()[:400])
    except Exception as e:
        print("###", url, "FAIL", e)
