from swgoh_scraper.scraper import scrape_round

# Header panel copied from a real round page (swgoh.gg, captured 2026-11-20).
ROUND_HTML = """
<html><body>
<div class="panel my-2 text-center font-bold">
 <div class="text-3xl">Season 79
  <span class="text-xs text-gg-gray-300">
   <time class="js-local-time-app whitespace-nowrap" data-mode="date" datetime="2026-05-19T21:00:00+00:00">
    <span class="whitespace-nowrap">May 19, 2026</span>
   </time>
  </span>
 </div>
 <div class="flex gap-x-1 justify-center my-2">
  <a class="btn btn-sm btn-primary" href="/p/887623583/gac-history/O1779224400000/1/">Round 1</a>
 </div>
 <div class="text-3xl">
  <span class="text-gg-negative">Hxchillbilly</span> vs
  <a class="text-gg-positive" href="/p/668774563/">Dart MeloN</a>
 </div>
 <div class="text-gg-gray-300">1,707 - 1,787</div>
</div>
</body></html>
"""


class FakePage:
    def __init__(self, html):
        self.html = html

    def goto(self, url, wait_until=None):
        pass

    def wait_for_timeout(self, ms):
        pass

    def title(self):
        return "Hxchillbilly's GAC on Star Wars Galaxy of Heroes - SWGOH.GG"

    def content(self):
        return self.html


def test_round_header_fields():
    event_url = "https://swgoh.gg/p/887623583/gac-history/O1779224400000/"
    r = scrape_round(FakePage(ROUND_HTML), event_url, 1)
    assert r["season_number"] == 79
    assert r["date_display"] == "May 19, 2026"
    assert r["date"] == "2026-05-19T00:00:00"
    assert r["season"] == "Season 79, May 19, 2026"
    assert r["matchup"] == "Hxchillbilly vs Dart MeloN"
    assert r["points"] == {"player": 1707, "opponent": 1787}
    assert r["_id"] == "1779224400000_R1"
