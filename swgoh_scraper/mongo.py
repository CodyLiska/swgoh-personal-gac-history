"""
Load scraped JSON from output/ into MongoDB.

GAC rounds go to `gac_rounds`, upserted on the scraper's `_id`
(<event_id>_R<round>), so re-running the load never duplicates a round.
The roster goes to `rosters`, one doc per ally code, replaced on each load.

Connection comes from MONGO_URI (and optional MONGO_DB, default "swgoh"),
read from the environment or a .env file in the working directory.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient, ReplaceOne

from .config import OUTPUT_DIR


def connect():
    load_dotenv()
    uri = os.environ.get("MONGO_URI")
    if not uri:
        raise RuntimeError("MONGO_URI is not set — add it to .env.")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")  # fail now, not halfway through the load
    return client[os.environ.get("MONGO_DB", "swgoh")]


def push(db, output_dir=OUTPUT_DIR):
    """Upsert every round and the roster from output_dir into db."""
    out = Path(output_dir)
    rounds = []
    for f in sorted(out.glob("gac_history_event_*.json")):
        rounds.extend(json.loads(f.read_text(encoding="utf-8")))

    roster_file = out / "roster.json"
    roster = json.loads(roster_file.read_text(encoding="utf-8")) \
        if roster_file.exists() else None

    if not rounds and roster is None:
        raise RuntimeError(f"Nothing to push: no event files or roster.json in {out}")

    if rounds:
        db.gac_rounds.bulk_write(
            [ReplaceOne({"_id": r["_id"]}, r, upsert=True) for r in rounds])
    if roster is not None:
        db.rosters.replace_one(
            {"_id": roster["data"]["ally_code"]}, roster, upsert=True)

    print(f"✅ Pushed {len(rounds)} rounds"
          f"{' and roster' if roster is not None else ''} to MongoDB.")
    return len(rounds), roster is not None
