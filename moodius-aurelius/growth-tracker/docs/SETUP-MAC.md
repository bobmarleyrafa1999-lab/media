# Set up on your Mac (once, about 15 minutes, £0)

You'll copy and paste a few lines into Terminal. Each step says what you should see.

## 1. Install Python 3.13 (free, from the official site)
1. Go to **python.org** > **Downloads** > **macOS**.
2. Click the newest **Python 3.13.x** "macOS 64-bit universal2 installer".
3. Open the downloaded `.pkg` and click **Continue** until **Install**. Enter your Mac password when asked (that's your Mac's, never Instagram's).
4. When the installer finishes, a Finder window opens: double-click **Install Certificates.command**.

Your Mac's built-in Python is too old for these tools, which is why this step is needed.

## 2. Download the tracker
1. Open **github.com/bobmarleyrafa1999-lab/media**.
2. Click the green **Code** button > **Download ZIP**.
3. Open the ZIP in Downloads, then drag the folder `moodius-aurelius/growth-tracker` into your **Documents** folder.

## 3. Create a private environment and install the pinned libraries
Open **Terminal** (Cmd+Space, type Terminal, Enter) and paste these lines one at a time:

```
cd ~/Documents/growth-tracker
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt
```

You should see "Successfully installed ..." at the end. `.venv` keeps these libraries separate from everything else on your Mac. Delete the folder and they're gone.

## 4. Check it works
```
python -m unittest discover -s tests
python -m moodius_growth demo
python -m moodius_growth --demo report
```
You should see `OK`, then "Demo database rebuilt", then "Report written to ...". That report is SYNTHETIC: it only shows that everything runs.

## 5. Load your real data
* If Claude gave you `metricool-pull-2026-10-27.json`, move it into the growth-tracker folder and run
  `python -m moodius_growth import-metricool-json metricool-pull-2026-10-27.json`
* Then follow docs/IMPORT-GUIDE.md each week.
* Run `python -m moodius_growth import-experiments templates/experiments.csv` once to load E1-E3.

## 6. Open the dashboard
```
streamlit run app.py
```
Your browser opens **http://localhost:8501**. Only your Mac can see it. Close the Terminal window to stop it.

## Every time after
```
cd ~/Documents/growth-tracker
source .venv/bin/activate
```
then the command you need (`report`, `streamlit run app.py`, an import).

## If something goes wrong
Copy the last 10 lines of Terminal into the Claude thread. Never paste a token or password.
