import json

import pytest
from pymongo import ReplaceOne

from swgoh_scraper.mongo import push


class FakeCollection:
    def __init__(self):
        self.calls = []

    def bulk_write(self, ops):
        self.calls.append(("bulk_write", ops))

    def replace_one(self, filter, doc, upsert=False):
        self.calls.append(("replace_one", filter, doc, upsert))


class FakeDb:
    def __init__(self):
        self.gac_rounds = FakeCollection()
        self.rosters = FakeCollection()


def write(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def test_upserts_rounds_and_roster(tmp_path):
    rounds = [{"_id": f"1_R{n}", "battles": []} for n in (1, 2, 3)]
    write(tmp_path / "gac_history_event_1.json", rounds)
    write(tmp_path / "gac_history_all.json", rounds)  # derived; must be ignored
    roster = {"data": {"ally_code": 123}, "units": [1]}
    write(tmp_path / "roster.json", roster)

    db = FakeDb()
    assert push(db, tmp_path) == (3, True)
    assert db.gac_rounds.calls == [("bulk_write", [
        ReplaceOne({"_id": r["_id"]}, r, upsert=True) for r in rounds])]
    assert db.rosters.calls == [("replace_one", {"_id": 123}, roster, True)]


def test_rounds_without_roster(tmp_path):
    write(tmp_path / "gac_history_event_1.json", [{"_id": "1_R1"}])
    db = FakeDb()
    assert push(db, tmp_path) == (1, False)
    assert db.rosters.calls == []


def test_empty_output_fails_loud(tmp_path):
    with pytest.raises(RuntimeError, match="Nothing to push"):
        push(FakeDb(), tmp_path)
