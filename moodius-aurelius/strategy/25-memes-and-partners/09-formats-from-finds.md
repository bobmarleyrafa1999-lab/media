# Formats taken from saved finds (9 Nov 2026)

Seven saved finds came in (6 screenshots and a short video). Every one is **inspiration-only**. We keep the format and write our own joke. Nothing from a find is reposted.

| Find | Format we keep | Why the find itself can't be used |
|---|---|---|
| Cartoon character crying over a sandwich | Late-night small-moment scene | Copyrighted cartoon |
| Man crying in a car | Reaction mood | A real person's face |
| Reply thread joke about "o'clock" | Fake etymology wordplay | Race and politics, real people's faces |
| Hand-drawn "Dopamine culture" whiteboard | Hand-drawn then/now table | Another creator's original work |
| Protest sign | Hand-lettered sign with one line | Politics, a real person's face |
| Text post: "every time I get close to the answer…" | Plain text post | Someone else's words and account |
| Press-conference clip | Deadpan reaction moment | News footage of real people, politics |

## New originals (renders/formats/, built by tools/formats.py)

All six score at most 0.38 text similarity to the finds (limit 0.6). None of them trips an exclusion flag. Their image fingerprints are at least 24 away from every screenshot.

| ID | Format | Text |
|---|---|---|
| MT01 | Text post | Nobody prepares for a conversation quite like someone who is never going to have it. |
| MT02 | Text post | Marcus Aurelius wrote a whole book reminding himself to stay calm, and probably never meant anyone else to read it. Most relatable thing an emperor has ever done. |
| MT03 | Text post | The Stoics practised imagining losing everything. My phone runs the same drill every evening at 3%. |
| MW01 | Whiteboard table | Getting through a bad day: 65 AD / 2009 / Now. Say it, get advice, calm down. |
| MS01 | Hand-lettered sign | I'M NOT OVERTHINKING. I'M DRAFTING. "Nineteen versions. None of them sent." |
| MD01 | Sketch scene | Where every "from Monday" plan is made: the 1 a.m. sandwich. |

The text-post card uses our own name, handle and mark. It doesn't copy any platform's logo or layout.

## Tools checked for these formats

| Tool | Verdict | Why |
|---|---|---|
| google/fonts: Caveat (OFL), Permanent Marker (Apache-2.0) | 🟢 added | Handwriting and marker lettering for the whiteboard and sign formats; licences are in fonts/ |
| Rough.js (already added) | 🟢 | Sketched lines and boxes for the whiteboard, sign and scene |
| Excalidraw (already 🟢) | 🟢 | Lets you sketch a format idea yourself, no account |
| rough-stuff/rough-notation | 🟠 | MIT, but last commit Oct 2020, and Rough.js already does circles and underlines |
| Gsllchb/Handright | 🟠 | BSD-3, imitates handwriting; last commit Dec 2023, and the fonts give us enough |
| jacebrowning/memegen | 🔴 | MIT and active, but it is built around famous reaction templates (faces, film and TV stills) |
| Fake-tweet/screenshot generators | 🔴 | Built to imitate real platforms and accounts; our text-post card does the job honestly |
