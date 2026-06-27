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
.venv\Scripts\activate   # Windows
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

Example:

```bash
swgoh-scraper --url https://swgoh.gg/p/887623583/gac-history/ --output output
```

A logged-in `swgoh_cookies.json` is required to access GAC history. The scraper
launches a visible Chromium window via Playwright.

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
