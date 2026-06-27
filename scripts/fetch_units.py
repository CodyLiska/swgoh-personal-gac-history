"""
Fetch a base_id -> display name map for SWGOH units (characters + ships) from
swgoh.gg and write it to dashboard/public/data/units.json.

swgoh.gg sits behind Cloudflare, so a plain HTTP GET 403s. This reuses the same
headed-Chrome + persistent-context approach as the scraper (see
swgoh_scraper/scraper.py): once the scraper has banked a cf_clearance cookie in
user_data/, navigating to the JSON API returns the payload without a manual
challenge. If clearance has expired, solve the one-time Cloudflare check in the
window that opens.

Run from the repo root:  python scripts/fetch_units.py
"""

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

API_URLS = [
    "https://swgoh.gg/api/characters/",
    "https://swgoh.gg/api/ships/",
]
OUT_PATH = Path("dashboard/public/data/units.json")


def _fetch_json(page, url):
    resp = page.goto(url, wait_until="domcontentloaded")
    if "just a moment" in (page.title() or "").lower():
        input(
            "Solve the Cloudflare challenge in the browser window, then press "
            "Enter here to continue..."
        )
        resp = page.goto(url, wait_until="domcontentloaded")
    body = page.inner_text("body")
    if not (resp and resp.status == 200 and body.strip().startswith("[")):
        raise RuntimeError(
            f"Unexpected response from {url}: status="
            f"{resp.status if resp else 'none'} body starts {body[:80]!r}"
        )
    return json.loads(body)


def fetch_units():
    units = {}
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir="user_data",
            channel="chrome",
            headless=False,
            ignore_default_args=["--enable-automation"],
            args=[
                "--ignore-gpu-blocklist",
                "--enable-unsafe-swiftshader",
                "--use-angle=swiftshader",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        page = ctx.new_page()
        for url in API_URLS:
            data = _fetch_json(page, url)
            for u in data:
                base_id = u.get("base_id")
                name = u.get("name")
                if base_id and name:
                    units[base_id] = name
            print(f"  {url} -> {len(data)} units")
        ctx.close()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(units, f, indent=2, ensure_ascii=False, sort_keys=True)
    print(f"Wrote {len(units)} base_id -> name entries to {OUT_PATH}")


if __name__ == "__main__":
    fetch_units()
