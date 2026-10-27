# Music you can legally use, and what sound actually helps (27 Oct 2026)

## 1. Licensing verdict
| Source | Safe for scheduled reels (Metricool)? | Notes |
|---|---|---|
| **Moodius originals** (`reels-engine/tools/sampled.py`) | ✅ Safest | Composed by us, played on PD piano + CC0 strings (MIT soundfont). No credit, no claims, no expiry. |
| **CC0 / public-domain recordings** (e.g. Musopen) | ✅ | Check the licence box on the file page. Credit optional. |
| **CC BY 4.0** (Scott Buckley, Chris Zabriskie) | ✅ with credit | Credit line in caption (mix.py adds it). Small risk a third party registered the track with Meta Rights Manager and the reel gets muted; skip Kevin MacLeod (most often matched). |
| **Instagram's in-app music** | ⚠️ Hand-posted only | Only attaches when posted in the app; Metricool can't add it. Business accounts get only Meta's cleared commercial catalogue; Creator accounts get the wider library but not for paid/branded use. |
| "No copyright" YouTube mixes, sped-up/slowed pop songs | ❌ | Not licensed, regardless of the title. |
| Paid AI music (Suno, Udio) | ❌ for now | Costs money; rights unclear. |

## 2. Evidence check: "frequencies" for learning and comfort
- **Binaural beats.** A 2019 meta-analysis (Garcia-Argibay et al., *Psychological Research*, 22 studies) found small-to-moderate effects on memory, attention, anxiety and pain, with wide variation between studies. They only exist when each ear gets a different tone, so they **need headphones**. On a phone speaker, which is how most reels are heard, there's no effect at all. Verdict: not for reels. [PubMed 30073406](https://pubmed.ncbi.nlm.nih.gov/30073406/)
- **432 Hz tuning.** The evidence is a few small pilot studies, such as Calamassi & Pomponi 2019 (n=33, slightly lower heart rate), and a 2025 crossover trial in cancer patients. That's too thin to claim anything, and a listener can't hear the 2% pitch difference on a phone. Verdict: harmless, no proven benefit; never claim it in captions. [BMC 2025 trial](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11755923/), [Acta Biomedica 2019](https://mattioli1885journals.com/index.php/actabiomedica/article/view/12915)
- **"Solfeggio" (528 Hz etc.)**: I found no controlled evidence at all.
- **What the research does support:**
  - Music with **lyrics hurts reading**. A meta-analysis by Vasilev, Kirkby & Angele (2018) found lyrical background music impairs reading comprehension. Every reel asks people to read, so instrumental only. [Bournemouth eprints](https://eprints.bournemouth.ac.uk/29995/)
  - Background music has **no overall benefit for learning**, and complex or busy music distracts (Kämpfe, Sedlmeier & Renkewitz 2011 meta-analysis).
  - For **comfort**, slow, predictable, soft music with no lyrics and no sudden changes is what music-for-stress studies use. Music interventions show a moderate reduction in stress (de Witte et al. 2020 meta-analysis, *Health Psychology Review*).

## 3. The Moodius reel sound (spec)
- **Instrumental only**, no vocals or choir (reading comes first).
- **60-72 bpm**, one chord per bar, no drops, no risers, no sudden hits.
- **Timbre:** soft felt piano and sustained strings, with a little room reverb; warm, not bright.
- **Mode by lane:** minor or modal for reflective posts; major for appreciation, curiosity and history (matches the 2-in-3 positive rule).
- **Loudness:** -14 LUFS, peaks under -1 dBTP; a -3 dB dip while a quote is on screen.
- **Same three-note sound logo** under the last card, so the account becomes recognisable by ear.

This is already what `sampled.py` does. Nothing new to build.
