"""
Post-scrape sanity checks. Each returns a list of problems (empty = OK), so a
swgoh.gg markup change or a Cloudflare block fails the run loudly instead of
saving nulls. league/zone are not checked: the site renders them as icons.
"""

from collections import Counter

ROUND_FIELDS = ["season_number", "date", "matchup", "points"]
BATTLE_FIELDS = ["outcome", "date", "attacker", "defender",
                 "attacker_chars", "defender_chars"]
UNIT_FIELDS = ["base_id", "name", "rarity", "level", "power", "gear_level"]


def _empty_fields(rows, fields, label):
    """rows: [(id, dict)]. One problem line per field that is empty anywhere."""
    problems = []
    for field in fields:
        bad = [row_id for row_id, row in rows if row.get(field) in (None, [], "")]
        if bad:
            problems.append(f"{field} empty in {len(bad)}/{len(rows)} {label} "
                            f"(e.g. {bad[0]})")
    return problems


def check_rounds(rounds):
    if not rounds:
        return ["No rounds scraped."]

    problems = _empty_fields([(r["_id"], r) for r in rounds], ROUND_FIELDS, "rounds")

    no_battles = [r["_id"] for r in rounds
                  if not r["battles"] and r.get("points")
                  and (r["points"]["player"] or r["points"]["opponent"])]
    if no_battles:
        problems.append(f"{len(no_battles)} rounds have points but no battles parsed "
                        f"(e.g. {no_battles[0]})")

    short = [e for e, n in Counter(r["event_id"] for r in rounds).items() if n < 3]
    if short:
        problems.append(f"{len(short)} events are missing rounds — see the "
                        f"'Skipping round' lines above (e.g. event {short[0]})")

    battles = [(r["_id"], b) for r in rounds for b in r["battles"]]
    if battles:
        problems += _empty_fields(battles, BATTLE_FIELDS, "battles")
    return problems


def check_roster(payload):
    units = [(u.get("data", {}).get("base_id"), u.get("data", {}))
             for u in payload.get("units") or []]
    if not units:
        return ["No units in roster."]
    problems = _empty_fields(units, UNIT_FIELDS, "units")
    if not payload.get("mods"):
        problems.append("No mods in roster.")
    return problems


def report(problems):
    """Print problems; return True when the data looks healthy."""
    if not problems:
        print("✅ Data check passed.")
        return True
    print("❌ Data check FAILED — swgoh.gg markup may have changed or the "
          "page was blocked. Output was saved, but these fields are wrong:")
    for p in problems:
        print(f"   - {p}")
    return False
