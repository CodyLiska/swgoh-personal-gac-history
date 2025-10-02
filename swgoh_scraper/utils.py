"""
Utility functions for SWGOH scraper.
"""
import json
from pathlib import Path


def save_json(data, filename):
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved JSON to {filename}")


def clean_name(name: str) -> str:
    """Remove unwanted suffixes like 'Insight' or 'CountersInsight' from names."""
    if not name:
        return name
    return (
        name.replace("CountersInsight", "")
            .replace("Insight", "")
            .strip()
    )
