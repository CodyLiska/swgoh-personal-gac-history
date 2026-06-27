import argparse

from .config import BASE_HISTORY_URL, OUTPUT_DIR
from .scraper import scrape_all_events


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
    args = parser.parse_args(argv)

    scrape_all_events(
        base_url=args.url, output_dir=args.output, headless=args.headless)


if __name__ == "__main__":
    main()
