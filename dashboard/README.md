# GAC Counter Lookup Dashboard

A local Vue + Vite + Tailwind dashboard over the scraped GAC history. Pick an
enemy team and see which of **your** teams beat it historically, ranked by
win-rate and average banners.

## Data pipeline

The dashboard reads two JSON files in `public/data/`, both produced from the
scraper's `output/` by build scripts in the repo's `scripts/` folder:

| File             | Built by                     | Contents                                  |
| ---------------- | ---------------------------- | ----------------------------------------- |
| `battles.json`   | `scripts/build_dataset.py`   | Every battle, unioned from all event files (no dedupe), with a derived `mode` (`squad_5v5`/`squad_3v3`/`fleet`) |
| `units.json`     | `scripts/fetch_units.py`     | `base_id → display name` map (characters + ships) from swgoh.gg |

Regenerate after each scrape (run from the **repo root**, venv active):

```bash
python scripts/build_dataset.py     # always; offline
python scripts/fetch_units.py       # only when new units appear (uses Playwright)
```

`fetch_units.py` reuses the scraper's Cloudflare-cleared Chrome session
(`user_data/`); if clearance expired, solve the one-time challenge in the window.

## Run the dashboard

```bash
cd dashboard
npm install
npm run dev        # open the printed localhost URL
```

## Using it

- **Match by leader** (default) groups by the enemy leader; **Match exact team**
  groups by the exact 5/3-char composition.
- **5v5 / 3v3 / Fleet** facets filter by game mode.
- Results rank your teams by win-rate, then avg banners. The `W-L-R-D` column is
  Wins-Losses-Retreats-Draws; win-rate counts only clean **Wins** over all
  attempts. A small `n=` badge flags low-sample matchups.
- Expand any row to see the individual past battles.

## Scope

v1 is **offense only** (`your_attack`). Defense analysis and portraits are
possible future work. The dashboard uses only data the scraper produces
(`output/*.json`) — no external/legacy data sources.
