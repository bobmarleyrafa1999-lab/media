# Moodius audio system (21 Oct 2026)

Background music for reels, stories and photo dumps: a licence-tracked library, three soundtrack candidates per reel, and a mixer that cuts the music to the picture at Instagram loudness. It's all local and free, with no API calls.

```
audio/
  tools/compose.py     original Moodius score (synthesised in-house, owned outright, scored to picture)
  tools/library.py     catalogue, licence log, ingest/analysis, 3 candidates per reel, credit lines
  tools/mix.py         alignment, fades, reading dips, voice ducking, -14 LUFS, mux, usage log
  library/tracks.csv   THE licence log: source, licence, attribution, commercial use, platform lock, verification
  library/originals/   28 Moodius originals (7 categories × 4), 48 s, AAC 256k
  library/external/    drop downloaded CC/PD tracks here as <id>.mp3/.wav/.ogg
  library/external.csv the 15 curated third-party tracks (source of tracks.csv's EX- rows)
  renders/             mixed reels (+ caption file with the credit line)
  usage-log.csv        every mix: reel, track, offset, loudness (stops repeats)
  01-sonic-identity.md the Moodius sound, rules and audit of the four repos
```

## Setup (once, ~2 min)
```
pip install numpy scipy        # compose.py; FFmpeg ≥ 5 must be on PATH (it already is here)
cd audio/tools
python3 compose.py library     # renders the 28 originals (~2 min)
python3 library.py build       # writes library/tracks.csv
```

## Every reel
```
python3 library.py candidates ../../reels-engine/scripts/formats-AF.json --only D01   # three candidates, ★ = recommended
python3 mix.py ../../reels-engine/scripts/formats-AF.json D01 --video ../../reels-engine/renders/D01-the-bench.mp4 --candidates 3
python3 mix.py … D01 --video … --track MO-EXI-2            # or force one track
python3 mix.py … D01 --video … --track MO-EXI-2 --vo vo.wav   # with a voice-over: music ducks under it
```

## Adding the curated third-party tracks (Surafel, ~15 min once, on your computer)
This container can't reach music sites, so they have to be downloaded by hand. Open each `source_url` in `library/external.csv`. **Confirm the licence on the track's own page** (the `verification` column says what's still unconfirmed), download it, and save it as `library/external/<id>.<ext>` (e.g. `EX-SB-01.mp3`). Upload the files to the project, and Claude runs `library.py ingest`. From then on the mixer can use them, and their credit line goes into the caption automatically.

## Claude does / You do
**Claude, automatically:** composes and renders the originals, ranks three candidates per reel, mixes the recommended one (or all three for you to compare), adds credit lines to captions, logs usage so no track repeats within 7 reels, and checks loudness on every export.
**You, by hand:** download the 15 curated tracks once, confirming each licence on its page. Optionally, listen to the three versions of a reel and say which one wins; that teaches the ranking.
