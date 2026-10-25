# Pinterest: Metricool first, direct API as backup

**Recommendation (21 Oct 2026):** connect Pinterest in Metricool. It's already paid for, needs no app review, and Claude can schedule pins from this project the same way it schedules Instagram. Keep the direct API (Pinterest's api-quickstart) as a backup only.

Why not the API first:
- A new developer app starts on **Trial access**. Pins and boards made with Trial are visible only to you (sandbox), so nobody else sees them.
- Public pins need **Standard access**: you apply with a screen recording that shows the full OAuth sign-in plus one pin being created. Reviews take days to weeks and get refused if the OAuth part is missing.
- The API has no scheduling for organic pins, so a script has to run every day from somewhere with your token. Metricool already does that.

## Surafel, if we go Metricool (10 min, once)
1. Make a free Pinterest **business** account, "Moodius Aurelius".
2. Metricool > Settings > Connections > Pinterest > connect.
Then Claude creates the 5 boards' pins from `pins-plan.json` on the schedule in strategy/13-distribution-channels.md.

## Surafel, if we also want the API (≈40 min plus waiting)
1. developers.pinterest.com > sign in with the business account > Apps > **Connect app** (accept terms, describe it as "personal publishing tool for my own account").
2. In the app's Manage page add redirect `http://localhost:8085/`.
3. On your computer: clone https://github.com/pinterest/api-quickstart, put App ID and secret in `common/scripts/api_app_credentials`, then `cd python && pip install -r requirements.txt` and
   `python scripts/get_access_token.py -w -s boards:read boards:write pins:read pins:write`
   (a browser opens, you click Allow, the token is saved to `common/oauth_tokens/access_token.json`).
4. Test in sandbox: `PINTEREST_TOKEN_FILE=<that file> python3 pins.py post --limit 1 --sandbox`.
5. Record steps 3-4 on screen and request **Standard access** in the app dashboard.
Never paste the secret or token into the chat or project files.

## Files
- `pins.py plan` turns each carousel in strategy/upload-pack/manifest.json into 2 pins (cover + slide 2) at 1000x1500 in `out/`, with board, search-phrase title, cited description and link, into `pins-plan.json` (edit freely).
- `pins.py post --limit 2` creates missing boards and posts the next unposted pins, logged in `pins-log.csv`.
- Link defaults to the Instagram profile. Re-run `plan --link <Kit page URL>` once the free-guide page exists (doc 13 says all outbound links go to Kit).
