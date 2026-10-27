# Library checks (27 Oct 2026)

Checked for each: who publishes it, licence, release history, Python compatibility, and known security advisories (PyPI's vulnerability feed, which is backed by the OSV and GitHub advisory databases). GitHub stars were not used as evidence.

| Library | Owner (official source) | Licence | Version pinned | Released | Known advisories at that version | Verdict |
|---|---|---|---|---|---|---|
| pandas | pandas-dev (NumFOCUS-sponsored), github.com/pandas-dev/pandas | BSD-3-Clause | 3.0.6 | 17 Sep 2026 | none | ✅ Install. 3.1.0 (22 Oct) skipped: only 5 days old. |
| statsmodels | statsmodels project, github.com/statsmodels/statsmodels | BSD-3-Clause | 0.15.0 | 27 Aug 2026 | none | ✅ Install. Only used once 56+ days of history exist. |
| streamlit | Streamlit (Snowflake), github.com/streamlit/streamlit | Apache-2.0 | 1.66.1 | 21 Oct 2026 | none | ✅ Install, local only. See note 1. |
| plotly | Plotly Inc., github.com/plotly/plotly.py | MIT | 6.9.0 | 9 Jul 2026 | none | ✅ Install. 7.x is a new major; 6.9 is the mature line. |
| facebook-business | Meta, github.com/facebook/facebook-python-business-sdk | Facebook Platform licence (free use with Meta's APIs, not an OSI open-source licence) | not installed | 26.0.2, 21 Sep 2026 | none | ❌ Skipped. See note 2. |

All 41 locked packages (requirements-lock.txt) had **0 known advisories** on 27 Oct 2026, and `pip check` reported no conflicts.

## Notes and unresolved concerns
1. **Streamlit and Pillow.** Streamlit 1.65/1.66.0 cap Pillow below 13, and Pillow 12.3 has 40 published advisories (fixed in 13.0.0) about crafted image files. Streamlit 1.66.1 allows Pillow 13, so both are pinned at their newest versions even though they are under two weeks old. Real exposure is low anyway: the dashboard never opens images from strangers. Streamlit also had past advisories (2022, 2024, 2026) that are all fixed in this version. `.streamlit/config.toml` binds it to `localhost`, so nobody else on your Wi-Fi can open it, and usage statistics are switched off.
2. **Meta's Python SDK.** It does include Instagram objects (IGUser, IGMedia), but it's built for the Marketing API. It adds requests, aiohttp, curlify, pycountry and a Conversions API helper, and curlify can print full request URLs (with the token) when debug logging is on. The collector here uses the same documented Graph API endpoints with Python's standard library and redacts the token from every log line. Revisit if ads ever need managing from code.
3. **Under-two-weeks-old pins.** pillow 13.0.0 and streamlit 1.66.1 (security fixes, note 1), certifi 2026.10.23 (fresh CA certificates; the July one has 2 advisories), plus starlette 1.9.0 and wrapt 2.5.1, which are simply the current releases pip resolved (no advisories on them or on the versions before). If you'd rather wait, re-check on 10 Nov.
4. **Isolation.** Everything installs into `.venv` inside the project folder. Nothing touches system Python.

## How to re-check later (2 minutes)
```
source .venv/bin/activate
pip install pip-audit==2.10.1   # optional, from PyPA (the people who maintain pip)
pip-audit -r requirements-lock.txt
```
