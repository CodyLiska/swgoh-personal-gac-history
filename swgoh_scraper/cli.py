import argparse
import sys

from .config import BASE_HISTORY_URL, OUTPUT_DIR
from .roster import scrape_roster
from .scraper import scrape_all_events
from .validate import check_roster, check_rounds, report


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="swgoh-scraper",
        description="Scrape SWGOH.gg GAC history for a player profile.",
    )
    parser.add_argument(
        "--url",
        default=BASE_HISTORY_URL,
        help="GAC history page URL to scrape (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        default=OUTPUT_DIR,
        help="Directory to write JSON output to (default: %(default)s)",
    )
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Run the browser headless. Default is headed (--no-headless), "
             "which is needed to clear swgoh.gg's Cloudflare challenge.",
    )
    parser.add_argument(
        "--roster",
        action="store_true",
        help="Capture your roster (output/roster.json) instead of GAC history.",
    )
    args = parser.parse_args(argv)

    if args.roster:
        data = scrape_roster(output_dir=args.output, headless=args.headless)
        ok = report(check_roster(data))
    else:
        data = scrape_all_events(
            base_url=args.url, output_dir=args.output, headless=args.headless)
        ok = report(check_rounds(data))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
