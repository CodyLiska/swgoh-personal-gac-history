from swgoh_scraper.validate import check_roster, check_rounds


def battle(**overrides):
    b = {"outcome": "Win", "date": "2026-05-19T00:00:00", "attacker": "Me",
         "defender": "Them", "attacker_chars": ["A"], "defender_chars": ["B"],
         "league": None, "zone": None}
    return {**b, **overrides}


def round_(n, event="1", **overrides):
    r = {"_id": f"{event}_R{n}", "event_id": event, "season_number": 79,
         "date": "2026-05-19T00:00:00", "matchup": "Me vs Them",
         "points": {"player": 10, "opponent": 5}, "battles": [battle()]}
    return {**r, **overrides}


def healthy():
    return [round_(1), round_(2), round_(3)]


def test_healthy_rounds_pass():
    assert check_rounds(healthy()) == []


def test_empty_headers_flagged():
    # The 2026-11 redesign: every header field came back None.
    rounds = [round_(n, season_number=None, matchup=None) for n in (1, 2, 3)]
    problems = check_rounds(rounds)
    assert any(p.startswith("season_number empty in 3/3") for p in problems)
    assert any(p.startswith("matchup empty in 3/3") for p in problems)


def test_points_without_battles_flagged():
    rounds = healthy()
    rounds[1]["battles"] = []
    assert any("points but no battles" in p for p in check_rounds(rounds))


def test_zero_zero_round_without_battles_ok():
    rounds = healthy()
    rounds[1].update(battles=[], points={"player": 0, "opponent": 0})
    assert check_rounds(rounds) == []


def test_skipped_round_flagged():
    assert any("missing rounds" in p for p in check_rounds(healthy()[:2]))


def test_empty_battle_fields_flagged():
    rounds = healthy()
    rounds[0]["battles"] = [battle(attacker_chars=[])]
    assert any(p.startswith("attacker_chars empty in 1/3") for p in check_rounds(rounds))


def test_no_rounds_flagged():
    assert check_rounds([]) == ["No rounds scraped."]


def unit(**overrides):
    d = {"base_id": "4LOM", "name": "4-LOM", "rarity": 7, "level": 85,
         "power": 22327, "gear_level": 13, "relic_tier": None}
    return {"data": {**d, **overrides}}


def test_healthy_roster_passes():
    assert check_roster({"units": [unit()], "mods": [{}]}) == []


def test_roster_problems_flagged():
    problems = check_roster({"units": [unit(gear_level=None)], "mods": []})
    assert any(p.startswith("gear_level empty in 1/1") for p in problems)
    assert "No mods in roster." in problems
    assert check_roster({}) == ["No units in roster."]
