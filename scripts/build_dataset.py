"""
Flatten every scraped GAC event file in output/ into a single flat battle list
the dashboard fetches: dashboard/public/data/battles.json.

IMPORTANT (project rule): every output/gac_history_event_*.json is canonical,
append-only history. This script UNIONS all of them and NEVER dedupes, deletes,
or merges-with-loss. It only reads output/ — the scraper's write path is
untouched.

Each output file is a list of 3 rounds; each round has a battles[] list. We emit
one row per battle, carrying event/round context plus a derived `mode`:
  - 3 chars  -> squad_3v3
  - 5 chars  -> squad_5v5
  - 6-8 chars -> fleet   (capital ship + reinforcements)

Run from the repo root:  python scripts/build_dataset.py
"""

import glob
import json
from pathlib import Path

OUTPUT_GLOB = "output/gac_history_event_*.json"
OUT_PATH = Path("dashboard/public/data/battles.json")


def derive_mode(defender_chars, attacker_chars):
    size = max(len(defender_chars or []), len(attacker_chars or []))
    if size <= 3:
        return "squad_3v3"
    if size == 5:
        return "squad_5v5"
    if size >= 6:
        return "fleet"
    return "unknown"  # size 4 — unexpected, surfaced rather than hidden


def build():
    files = sorted(glob.glob(OUTPUT_GLOB))
    battles = []
    for f in files:
        event_id = Path(f).stem.replace("gac_history_event_", "")
        for rnd in json.load(open(f, encoding="utf-8")):
            round_number = rnd.get("round_number")
            for b in rnd.get("battles", []):
                ac = b.get("attacker_chars") or []
                dc = b.get("defender_chars") or []
                battles.append({
                    "event_id": event_id,
                    "round_number": round_number,
                    "battle_type": b.get("battle_type"),
                    "outcome": b.get("outcome"),
                    "banners": b.get("banners"),
                    "attempt": b.get("attempt"),
                    "duration_sec": b.get("duration_sec"),
                    "date": b.get("date"),
                    "attacker": b.get("attacker"),
                    "attacker_chars": ac,
                    "defender": b.get("defender"),
                    "defender_chars": dc,
                    "mode": derive_mode(dc, ac),
                })

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(battles, f, ensure_ascii=False)

    # Summary so a run is self-verifying against expectations.
    from collections import Counter
    bt = Counter(b["battle_type"] for b in battles)
    md = Counter(b["mode"] for b in battles)
    print(f"Event files unioned: {len(files)} (no dedupe)")
    print(f"Total battles: {len(battles)}")
    print(f"battle_type: {dict(bt)}")
    print(f"mode: {dict(md)}")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    build()
