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

Run the CLI with:

```bash
python -m swgoh_scraper.cli --help
```

Example:

```bash
python -m swgoh_scraper.cli --config config.yaml --output output.json
```

Adjust arguments as required based on implemented CLI options.

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
