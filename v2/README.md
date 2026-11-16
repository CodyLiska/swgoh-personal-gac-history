# GAC Archive v2

A separate local browser dashboard for exploring captured GAC history and starting a fresh scrape. The original `dashboard/` files are untouched.

## Run

Use the same Python environment that runs the scraper (the project's `.venv` in WSL):

```bash
source .venv/bin/activate
python v2/server.py
```

Open **http://127.0.0.1:8765**. Use `python v2/server.py --port 8766` if that port is occupied.

No npm install or dataset build is needed. V2 reads every `output/gac_history_event_*.json` file directly and uses the existing unit name map when available. It never writes to the original dashboard or rewrites the event files itself.

## Capture flow

Open **Capture data**, confirm the swgoh.gg GAC history URL, and select **Start capture**. The server launches the existing `swgoh_scraper` module from the repository root with the current Python interpreter. The default visible Chrome mode lets you solve a Cloudflare challenge if needed. Watch the activity log; after completion, v2 reloads the event files automatically. Stop capture is available while the process is running.

The scraper still needs the project's existing Chrome/Playwright setup and a logged-in `swgoh_cookies.json` or persistent `user_data/` session. A full archive scrape can take a while because each event has three rounds.

The local HTTP server listens only on `127.0.0.1`. Its scrape endpoint accepts only HTTPS `swgoh.gg/p/<player-id>/gac-history/` URLs.

