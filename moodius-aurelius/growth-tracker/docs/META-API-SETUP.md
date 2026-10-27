# Optional: connect Meta's official Instagram API (about 30 minutes, £0)

**Do you need this?** No. The CSV route works. This only saves you copying numbers, and it captures story numbers before they disappear after 24 hours. Decide after a couple of weeks of the CSV route.

**What it uses:** the "Instagram API with Facebook Login" (your Instagram is a professional account linked to the Moodius Facebook Page, which qualifies). It never asks for your Instagram password or cookies. It reads only, and can't post or delete anything.

**Anonymity:** the developer app sits in your own Meta developer account and stays in *Development mode*, which is never shown to the public. Give it a plain name like "Page stats". Don't publish it or submit it for App Review; you don't need to for your own accounts.

**Security:** the token is stored in your Mac's Keychain, not in a file, not in git and not in any log (logs show `[TOKEN]`).

## Steps
Meta changes labels in this flow often. If a screen doesn't match, tell Claude what you see.

1. Go to **developers.facebook.com**, log in with the Facebook account that manages the Moodius Page, and accept the developer terms if asked (free).
2. **My Apps** > **Create app**. Choose the option for business / "Other", then type **Business**. Name: `Page stats`. Contact email: hello@moodius.co.uk.
3. In the app dashboard, add the product **Instagram** and pick **API setup with Facebook login**.
4. Open **Tools** > **Graph API Explorer**. Pick your app at the top right. Under **Permissions** add:
   `instagram_basic`, `instagram_manage_insights`, `pages_show_list`, `pages_read_engagement`.
   Click **Generate Access Token**, and in the pop-up allow **only** the Moodius Page and @moodiusaurelius.
5. In the Explorer's query box, run: `me/accounts?fields=name,instagram_business_account`
   Copy the number shown under `instagram_business_account` > `id`. That's your Instagram user ID (not secret).
6. **Make the token last ~60 days:** open **Tools** > **Access Token Debugger**, paste the token, click **Debug**, then **Extend Access Token**. Copy the new long token.
   Then store it in your Keychain. In Terminal paste this line, press Enter, then paste the token when it asks for a password (nothing shows while you paste; that's normal):
   ```
   security add-generic-password -s moodius-ig-token -a moodius -w
   ```
7. Save the Instagram user ID (from step 5) in the growth-tracker folder:
   ```
   cd ~/Documents/growth-tracker
   echo "PASTE_THE_ID" > ig_user_id.txt
   ```
8. Test it:
   ```
   source .venv/bin/activate
   python -m moodius_growth collect-meta --ig-user-id "$(cat ig_user_id.txt)" --days-back 3
   python -m moodius_growth status
   ```
   You should see `('ok', N)` and a `meta_api` row marked fresh. If you see `partial` or `failed`, open `logs/collect.log` and send Claude the lines (the token is already blanked out).
9. **Optional daily schedule (08:30 on your Mac):**
   ```
   sed "s#FOLDER#$HOME/Documents/growth-tracker#g" schedule/com.moodius.growth.plist.template > ~/Library/LaunchAgents/com.moodius.growth.plist
   launchctl load ~/Library/LaunchAgents/com.moodius.growth.plist
   ```
   Check it the next day with `python -m moodius_growth status`. It only counts as running once a `meta_api` row appears with that day's time.
   To stop it: `launchctl unload ~/Library/LaunchAgents/com.moodius.growth.plist`.

## Things to know
* **Your Mac must be on.** If it's asleep at 08:30, macOS runs the job when it wakes. If it's switched off for days, those days are missed. Instagram keeps account Insights for a while, so the 3-day look-back fills short gaps. Stories older than 24 hours are lost for good.
* **The token expires after about 60 days.** Repeat steps 4 and 6, then update the Keychain entry with
  `security add-generic-password -U -s moodius-ig-token -a moodius -w`.
  A failed run will show `Meta API error 190` in the log when it has expired.
* **Retries:** each request retries 3 more times (2, 4, 8 seconds) on network errors, server errors and rate limits; the whole run retries once after 10 minutes.
* **Graph API version** is `v26.0` (set `MOODIUS_GRAPH_VERSION` to change it). Meta retires versions about two years after release.
* **To verify on the first real run:** that Meta returns watch time in milliseconds (the collector divides by 1,000) and that the `follow_type` breakdown uses FOLLOWER / NON_FOLLOWER. Both are from Meta's docs but haven't been seen on your account yet, because Meta's servers can't be reached from Claude's side.
* **To remove access completely:** Facebook > Settings > Business integrations > remove "Page stats", then `security delete-generic-password -s moodius-ig-token`.
