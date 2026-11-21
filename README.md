# SWGOH Scraper

A Python-based command-line tool for scraping Star Wars: Galaxy of Heroes (SWGOH) data.
This project is packaged as a Python module and includes a CLI for interacting with the scraper.

## Features
- Command-line interface for scraping SWGOH data
- Configurable via `config.py`
- Utility helpers for parsing and data handling
- Includes unit tests for core functionality

## Requirements
- Python 3.10 or later
- pip

## Installation

It is recommended to use a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\Activate.ps1   # Windows
```

Install dependencies from `pyproject.toml`:

```bash
pip install -e .
```

This will install the package in editable/development mode.

## Usage

After `pip install -e .`, the `swgoh-scraper` command is available:

```bash
swgoh-scraper --help
```

Equivalently, run it as a module:

```bash
python -m swgoh_scraper --help
```

Options:

- `--url` — GAC history page URL to scrape (defaults to the value in `config.py`)
- `--output` — directory to write JSON output to (default: `output`)
- `--roster` — capture your roster (swgoh.gg player API: units, mods, datacrons) to `output/roster.json` instead of GAC history

Example:

```bash
swgoh-scraper --url https://swgoh.gg/p/887623583/gac-history/ --output output
```

The scraper launches your installed Google Chrome (headed) via Playwright with a
persistent profile in `user_data/`. No cookie file is needed: the first run may
show a Cloudflare check to solve by hand, and the `cf_clearance` cookie it earns
stays in `user_data/` for later runs. Don't delete `user_data/`.
`swgoh_cookies.json` is optional and only loaded if present.

After every run the output is checked (`swgoh_scraper/validate.py`). If key
fields came back empty (usually a swgoh.gg markup change or a Cloudflare block),
it prints `❌ Data check FAILED` with the affected fields and exits with code 1.
The output is still saved.

## Project Structure
```
swgoh_scraper/
├── cli.py          # Command-line interface
├── config.py       # Configuration handling
├── scraper.py      # Core scraping logic
├── utils.py        # Utility functions
├── __init__.py
tests/
├── test_scraper.py # Unit tests for scraper
pyproject.toml      # Project configuration
swgoh_cookies.json  # Local cookies file (ignored in git)
user_data/          # Local browser/user data (ignored in git)
```

## Notes
- `swgoh_cookies.json` contains local authentication cookies and must not be committed.
- The `user_data/` folder contains browser/user session data and must not be committed.
- `__pycache__/`, `.egg-info/`, build outputs, and other generated files are ignored.
- To contribute, add new tests under the `tests/` directory.
