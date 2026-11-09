# pavo-engine-py: assessment (21 Oct 2026)

Repo: https://github.com/sonnhfit/pavo-engine-py. Cloned and run today in an isolated folder. It wasn't added to the project.

**Verdict: don't adopt it.** Our FFmpeg engine (`reels-engine/tools/engine.py`) already does more for our kind of reel, about twice as fast.

| Check | Finding |
|---|---|
| What it is | A Python timeline renderer (JSON or the "Pavo Lang" DSL to MP4) with text animations, transitions and subtitles. Perception modules (Whisper, YOLO, scene detection) are optional extras. |
| "AI video editing agent" | Not built yet. The planner that turns a prompt into a timeline is still an open item in its own todo list (Issue 004). |
| Maintenance | 76 commits since Dec 2022, active in May 2026. Around 40% of commits come from GitHub's Copilot agent. It's a single maintainer. |
| Licence | The README and setup.py say MIT, but the repo has **no LICENSE file**. That's usable for testing, but it's an ambiguity to avoid for a business. |
| Dependencies | ffmpeg-python, Pillow, pydantic, plus boto3/requests for remote media. The full extras pull in torch, Whisper and ultralytics (several GB). |
| Actual test | It rendered a 5 s, 1080×1920 text reel in Playfair on Slate in 11.4 s, which works. But the long line **wasn't wrapped and ran off the screen**, there was **no audio track**, and it renders frame by frame in Pillow, at roughly 2.3× real time vs our engine's ~1×. |
| What we'd lose | Line wrapping without one-word last lines, the quality gate, the citation registry, ambient audio, cover and caption files, the render cache, the A–F card kinds. |

**Where it could help later:** its scene-detection module (built on PySceneDetect) could cut long phone clips into usable 10–15 s shots. If you ever shoot longer footage, we'd use PySceneDetect directly instead.
