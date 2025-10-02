"""
CLI entrypoint for SWGOH scraper.
"""

from swgoh_scraper.scraper import scrape_all_events

def main():
    scrape_all_events()

if __name__ == "__main__":
    main()
