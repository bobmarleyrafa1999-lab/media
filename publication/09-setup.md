# 9. Setup instructions

About an hour in total, once. Menu names are Substack's as of late 2026 and may move slightly; if something isn't where this says, search Substack's settings page for the bold word.

## 1. Create the publication (15 minutes, Surafel)
1. Go to substack.com, sign up with an email you're happy to keep private from readers (it isn't shown publicly), and choose **Create a publication**.
2. **Name:** `Moodius Aurelius`. **Short description (tagline):** `Psychology and philosophy for people who feel things. Every claim labelled. A practice in every essay.`
3. **URL:** `moodiusaurelius.substack.com`. A custom domain is optional and can wait; Substack has historically charged a one-time fee for it, plus the domain itself (≈€12/year).
4. **Your profile:** name `Moodius`, no photo of you. Use `strategy/highlight-covers/` Manifesto cover or the Threads monogram (`threads/profile/avatar-A-monogram.png`) as the avatar. Bio: `Writes Moodius Aurelius. Anonymous on purpose: the sources are the authority, not the author.`
5. **Logo / cover:** the same monogram; publication accent colour Ember `#C9742E`, background light.
6. **Payments:** leave **off** for the first 90 days (strategy §Metrics). Turning them on later needs Stripe, which needs your legal identity, but that is never shown to readers.

## 2. Configure it (15 minutes, Surafel)
1. **Sections** (Settings → Sections): create *The Evening Review*, *What We Disown*, *Masculinity, Reconsidered*, *Old Answers*, *The Distance Between Us*, *After the Goal*, *The Loud Room*, *Memento*. Each essay's `meta.txt` says which section it belongs to.
2. **Welcome email** (Settings → Emails → Welcome email): paste the text below and attach or link the free guide `lead-magnet/7-stoic-tools-for-loud-emotions.pdf` (host it as a Substack file or keep the existing GitHub link).
   > Welcome to Moodius Aurelius. Every Thursday you'll get one essay on the inner life, written with the evidence labelled (study, philosophy or opinion) and a practice at the end. As promised, here's the free guide: *7 Stoic tools for when emotions are loud*. Start with tool 3 tonight. If you ever want to tell me what you'd like me to write about, reply to this email. I read every one. — Moodius
3. **About page:** paste the "one-line idea" and "five promises" from `01-editorial-strategy.md`.
4. **Recommendations:** leave empty until 4 essays are live; then Claude will suggest 3–5 aligned publications from `02-market-research.md` for you to recommend and approach.
5. **Import your Kit list (decision):** Settings → Import → Subscribers (CSV). Only after you decide to move to one list. Export from Kit first: Subscribers → Export.

## 3. Publishing one essay (10 minutes, Thursday, Surafel)
1. Open `exports/<slug>/preview.html` in your browser (download it from the project files or the repo).
2. In Substack: **New post** → paste **Title** and **Subtitle** from `meta.txt` into their own fields.
3. In the preview page, select from the first paragraph to the end of the Sources list, copy, and paste into the body. Headings, bold evidence labels, block quotes and links come across as rich text. Check that the block quotes kept their quote style.
4. Settings panel: **Section** from `meta.txt`, **URL slug** from `meta.txt`, **SEO description** from `meta.txt`. Audience: Everyone. Comments: Everyone.
5. **Preview → Send test email to yourself**, skim on your phone, then **Schedule** for 07:30 or publish.
6. Tell Claude it's live (or paste the URL), so the Notes, story link and pins can point to it.

## 4. Notes (2 minutes each)
Copy the Note text from `packages/NN-slug.md` §6, start a new Note in the Substack app, paste, and add the essay as an embed (paste the post URL on its own line; Substack turns it into a card). Embeds tend to convert better than outside links (see research §5).

## 5. Obsidian (10 minutes, optional)
1. Install Obsidian (free for personal use) and clone this repo with GitHub Desktop, or download the `publication/` folder.
2. **Open folder as vault** → choose `publication/vault/` (or `publication/` to see everything).
3. Settings → Community plugins → turn off Restricted mode → install **Dataview** and **Obsidian Git**. In Obsidian Git, set auto-pull on open.
4. Browse `20-ideas/` (backlog) and `10-sources/` (library). Tick items in `00-inbox/` that look worth using.

## 6. GitHub (5 minutes, optional)
1. Repository → Settings → Secrets and variables → Actions → **New repository secret**:
   - `CROSSREF_MAILTO` = any address you check (Crossref asks for one; it is not published).
   - `OPENALEX_API_KEY` = free key from openalex.org (optional).
2. Actions tab → enable workflows. *Weekly research feed* runs Mondays and opens a pull request; *Editorial QC* checks every change. Both live on the `claude/project-thread-8laot0` branch until merged into `main`.

## 7. Claude Code commands
Open the repo in Claude Code (web or terminal) and type `/` to see: `/research-topic`, `/verify-sources`, `/draft-essay`, `/repurpose`, `/export-substack`, `/weekly-plan`, `/metrics-review`, `/add-idea`. In this project you can also just ask in the thread ("draft MA-005"); Claude follows the same steps.

## 8. Analytics hand-off (2 minutes, weekly, Surafel)
Substack dashboard → **Stats** → export the post and subscriber CSVs (Settings → Exports) and drop them into `data/imports/` (or upload them in the thread). Instagram numbers come through Metricool automatically.

## Claude does / You do
**Claude:** everything in the repo, the exports, the approval queue, Instagram/Pinterest scheduling for approved items via the account thread, and the reviews.
**You:** sections 1–4 and 8. Sections 5–6 are optional.
