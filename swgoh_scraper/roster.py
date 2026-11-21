"""
Roster capture: the swgoh.gg player API (units, mods, datacrons) saved as-is.

The API sits behind the same Cloudflare check as the site, so it is fetched in
the scraper's persistent Chrome context, which reuses the banked cf_clearance.
"""

import json
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

from .config import OUTPUT_DIR, PLAYER_API_URL
from .scraper import launch_context
from .utils import save_json


def _is_challenge(page):
    return "just a moment" in (page.title() or "").lower()


def scrape_roster(api_url=PLAYER_API_URL, output_dir=OUTPUT_DIR,
                  headless=False, challenge_timeout=120000):
    """Fetch the player API and save it to <output_dir>/roster.json."""
    with sync_playwright() as p:
        context = launch_context(p, headless)
        page = context.new_page()
        resp = page.goto(api_url, wait_until="domcontentloaded")
        if _is_challenge(page):
            print("🛑 Cloudflare check showing — solve it in the browser window.")
            page.wait_for_function(
                "!document.title.toLowerCase().includes('just a moment')",
                timeout=challenge_timeout)
            resp = page.goto(api_url, wait_until="domcontentloaded")
        status = resp.status if resp else None
        body = page.inner_text("body")
        context.close()

    if status != 200 or not body.lstrip().startswith("{"):
        raise RuntimeError(
            f"Unexpected response from {api_url}: status={status} "
            f"body starts {body[:80]!r}")

    payload = json.loads(body)
    if not payload.get("units"):
        raise RuntimeError(f"No units in response from {api_url}")

    save_json({"scrape_timestamp": datetime.utcnow().isoformat(), **payload},
              Path(output_dir) / "roster.json")
    print(f"✅ Roster saved: {len(payload['units'])} units.")
    return payload
