"""
Main scraper logic for SWGOH.gg GAC history.
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from pathlib import Path
import json
import re
from datetime import datetime
from dateutil import parser

from .config import BASE_HISTORY_URL, OUTPUT_DIR
from .utils import save_json, clean_name


def get_event_links(page):
    page.goto(BASE_HISTORY_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    soup = BeautifulSoup(page.content(), "lxml")
    links = []
    for a in soup.select("a[href*='/gac-history/O']"):
        full_url = "https://swgoh.gg" + a["href"]
        clean_url = re.sub(r"/[123]/?$", "/", full_url)
        links.append(clean_url)
    return sorted(set(links))


def scrape_battles_from_section(soup, section_id, battle_type):
    """Scrape all battles from a given tab section (attacks or defenses)."""
    battles = []
    section = soup.select_one(f"#{section_id}")
    if not section:
        return battles

    for card in section.select(".gac-counters-battle-summary"):
        stats = {}
        for stat in card.select(".gac-counters-battle-summary__stat"):
            label = stat.select_one(
                ".gac-counters-battle-summary__stat-label").get_text(strip=True)
            value = stat.select_one(
                ".gac-counters-battle-summary__stat-value").get_text(strip=True)
            stats[label] = value

        attacker = card.select_one(
            ".gac-counters-battle-summary__side--attacker .gac-counters-battle-summary__side-name div"
        )
        defender = card.select_one(
            ".gac-counters-battle-summary__side--defense .gac-counters-battle-summary__side-name div"
        )

        attacker_chars = [
            u["data-unit-def-tooltip-app"]
            for u in card.select(
                ".gac-counters-battle-summary__side--attacker "
                ".character-portrait[data-unit-def-tooltip-app], "
                ".gac-counters-battle-summary__side--attacker "
                ".ship-portrait[data-unit-def-tooltip-app]"
            )
        ]
        defender_chars = [
            u["data-unit-def-tooltip-app"]
            for u in card.select(
                ".gac-counters-battle-summary__side--defense "
                ".character-portrait[data-unit-def-tooltip-app], "
                ".gac-counters-battle-summary__side--defense "
                ".ship-portrait[data-unit-def-tooltip-app]"
            )
        ]

        # Parse battle date into ISO format if possible
        raw_date = stats.get("Date")
        try:
            iso_date = parser.parse(raw_date).isoformat()
        except Exception:
            iso_date = None

        # Duration to seconds if possible
        raw_duration = stats.get("Duration")
        duration_sec = None
        if raw_duration:
            match = re.match(r"(\d+)m\s*(\d+)s", raw_duration)
            if match:
                duration_sec = int(match.group(1)) * 60 + int(match.group(2))
            else:
                match = re.match(r"(\d+)s", raw_duration)
                if match:
                    duration_sec = int(match.group(1))

        battles.append({
            "banners": int(stats.get("Banners")) if stats.get("Banners") and stats.get("Banners").isdigit() else stats.get("Banners"),
            "attempt": int(stats.get("Attempt")) if stats.get("Attempt") and stats.get("Attempt").isdigit() else stats.get("Attempt"),
            "outcome": stats.get("Outcome"),
            "league": stats.get("League"),
            "zone": stats.get("Zone"),
            "duration": raw_duration,
            "duration_sec": duration_sec,
            "date": iso_date,
            "date_display": raw_date,
            "attacker": clean_name(attacker.get_text(strip=True)) if attacker else None,
            "defender": clean_name(defender.get_text(strip=True)) if defender else None,
            "attacker_chars": attacker_chars,
            "defender_chars": defender_chars,
            "battle_type": battle_type
        })
    return battles


def scrape_round(page, event_url, round_num):
    """Scrape a single round within a given event."""
    url = f"{event_url.rstrip('/')}/{round_num}/"
    print(f"Visiting {url}")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    soup = BeautifulSoup(page.content(), "lxml")

    # --- Top summary ---
    season_block = soup.select_one("h2.mb-0")
    season_raw = season_block.get_text(
        " ", strip=True) if season_block else None

    season_number_match = re.search(r"Season (\d+)", season_raw or "")
    season_number = int(season_number_match.group(
        1)) if season_number_match else None

    event_type_match = re.search(r"\((.*?)\)", season_raw or "")
    event_type = event_type_match.group(1) if event_type_match else None

    date_block = soup.select_one("div.fs-2 span.smaller.text-muted")
    raw_date = date_block.get_text(strip=True) if date_block else None
    try:
        iso_date = parser.parse(raw_date).isoformat()
    except Exception:
        iso_date = None

    season = f"{season_raw}, {raw_date}" if season_raw and raw_date else season_raw or raw_date

    vs_block = soup.select("div.fs-2")
    if len(vs_block) > 1:
        parts = vs_block[1].get_text(strip=True).split("vs")
        if len(parts) == 2:
            matchup = f"{parts[0].strip()} vs {parts[1].strip()}"
        else:
            matchup = vs_block[1].get_text(strip=True)
    else:
        matchup = None

    points = None
    points_block = soup.select_one("div.text-muted")
    points_text = points_block.get_text(strip=True) if points_block else None
    if points_text and "-" in points_text:
        try:
            p1, p2 = [int(p.strip()) for p in points_text.split("-")]
            points = {"player": p1, "opponent": p2}
        except Exception:
            points = None

    # --- Battles from both sections ---
    your_attacks = scrape_battles_from_section(
        soup, "battles-attack", "your_attack")
    opponent_attacks = scrape_battles_from_section(
        soup, "battles-defense", "opponent_attack")
    all_battles = your_attacks + opponent_attacks

    # Extract event_id from URL
    event_id_match = re.search(r"/O(\d+)/", event_url)
    event_id = event_id_match.group(1) if event_id_match else "unknown"

    return {
        "_id": f"{event_id}_R{round_num}",
        "event_id": event_id,
        "event_url": event_url,
        "season_number": season_number,
        "event_type": event_type,
        "round_number": round_num,
        "season": season,
        "date": iso_date,
        "date_display": raw_date,
        "matchup": matchup,
        "points": points,
        "battles": all_battles,
        "scrape_timestamp": datetime.utcnow().isoformat()
    }


def scrape_all_events():
    """Scrape all events and their rounds from the GAC history page."""
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="user_data",
            headless=False,
            slow_mo=250
        )
        page = context.new_page()

        try:
            with open("swgoh_cookies.json", "r") as f:
                cookies = json.load(f)
            context.add_cookies(cookies)
            print("✅ Cookies loaded successfully.")
        except FileNotFoundError:
            print("⚠️ No swgoh_cookies.json found — you may not be logged in.")

        event_links = get_event_links(page)
        print(f"Found {len(event_links)} event links")

        all_results = []

        for event_url in event_links:
            print(f"Scraping event: {event_url}")
            event_results = []
            for round_num in range(1, 4):
                try:
                    data = scrape_round(page, event_url, round_num)
                    event_results.append(data)
                except Exception as e:
                    print(f"⚠️ Skipping round {round_num} of {event_url}: {e}")

            if event_results:
                event_id_match = re.search(r"/O(\d+)/", event_url)
                event_id = event_id_match.group(
                    1) if event_id_match else "unknown"
                filename = Path(OUTPUT_DIR) / \
                    f"gac_history_event_{event_id}.json"
                save_json(event_results, filename)
                all_results.extend(event_results)

        context.close()

    master_file = Path(OUTPUT_DIR) / "gac_history_all.json"
    save_json(all_results, master_file)
    print("✅ Scraping complete! Master data saved.")
    return all_results
