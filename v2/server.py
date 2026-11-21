"""Local v2 dashboard and scrape control. Run: python v2/server.py"""
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import argparse
import json
import re
import subprocess
import sys
import threading

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from swgoh_scraper import mongo  # noqa: E402
from swgoh_scraper.validate import check_roster, check_rounds  # noqa: E402

HERE = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
ROSTER = OUTPUT / "roster.json"
PUSH_LOCK = threading.Lock()
UNITS = ROOT / "dashboard/public/data/units.json"
DEFAULT_URL = "https://swgoh.gg/p/887623583/gac-history/"
HISTORY_PATH = re.compile(r"^/p/\d+/gac-history/?$")


def now():
    return datetime.now(timezone.utc).isoformat()


def history():
    rounds, errors, latest = [], [], None
    files = sorted(OUTPUT.glob("gac_history_event_*.json"))
    for file in files:
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                raise ValueError("Expected a list of rounds")
            rounds.extend(row for row in data if isinstance(row, dict))
            latest = max(latest or 0, file.stat().st_mtime)
        except (OSError, ValueError) as exc:
            errors.append(f"{file.name}: {exc}")
    # Same post-scrape check the CLI runs, re-run on what's on disk so the alert
    # stays up until a clean capture replaces the bad files.
    problems = check_rounds(rounds) if files else []
    if ROSTER.exists():
        try:
            problems += [f"Roster: {p}" for p in
                         check_roster(json.loads(ROSTER.read_text(encoding="utf-8")))]
        except (OSError, ValueError) as exc:
            errors.append(f"{ROSTER.name}: {exc}")
    return {"rounds": rounds, "event_files": len(files),
            "updated_at": datetime.fromtimestamp(latest, timezone.utc).isoformat() if latest else None,
            "errors": errors, "problems": problems}


def push_to_mongo():
    db = mongo.connect()
    try:
        rounds, roster = mongo.push(db, OUTPUT)
    finally:
        db.client.close()
    return {"ok": True, "rounds": rounds, "roster": roster, "pushed_at": now()}


class Job:
    def __init__(self):
        self.lock = threading.Lock()
        self.process = None
        self.state = "idle"
        self.started_at = self.finished_at = self.error = self.current_event = self.event_count = None
        self.url = DEFAULT_URL
        self.headless = False
        self.lines = deque(maxlen=120)

    def snapshot(self):
        with self.lock:
            return {"state": self.state, "started_at": self.started_at,
                    "finished_at": self.finished_at, "error": self.error,
                    "current_event": self.current_event, "event_count": self.event_count,
                    "url": self.url, "headless": self.headless, "lines": list(self.lines)}

    def start(self, url, headless):
        with self.lock:
            if self.state in ("running", "stopping"):
                return False
            self.state = "running"
            self.started_at, self.finished_at = now(), None
            self.error = self.current_event = self.event_count = None
            self.url, self.headless = url, headless
            self.lines.clear()
            self.lines.append("Starting the scraper…")
        threading.Thread(target=self.run, daemon=True).start()
        return True

    def stop(self):
        with self.lock:
            if self.state != "running":
                return False
            self.state = "stopping"
            self.lines.append("Stopping the scraper…")
            process = self.process
        if process:
            process.terminate()
        return True

    def run(self):
        command = [sys.executable, "-u", "-m", "swgoh_scraper", "--url", self.url,
                   "--output", str(OUTPUT), "--headless" if self.headless else "--no-headless"]
        try:
            process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                       errors="replace", bufsize=1)
            with self.lock:
                self.process = process
                stopping = self.state == "stopping"
            if stopping:
                process.terminate()
            for raw in process.stdout:
                line = raw.rstrip()
                if not line:
                    continue
                with self.lock:
                    self.lines.append(line)
                    count = re.search(r"Found (\d+) event links", line)
                    event = re.search(r"Scraping event: (\S+)", line)
                    if count:
                        self.event_count = int(count.group(1))
                    if event:
                        self.current_event = event.group(1)
            code = process.wait()
            with self.lock:
                self.state = "stopped" if self.state == "stopping" else "complete" if code == 0 else "failed"
                if self.state != "failed":
                    self.error = None
                elif any("Data check FAILED" in line for line in self.lines):
                    self.error = "Data check failed: some fields came back empty. See the alert above."
                else:
                    self.error = f"Scraper exited with code {code}. Check the log."
                self.finished_at, self.process = now(), None
        except Exception as exc:
            with self.lock:
                self.state, self.error = "failed", str(exc)
                self.lines.append(f"Failed to start: {exc}")
                self.finished_at, self.process = now(), None


JOB = Job()


class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = self.path.split("?", 1)[0]
        if route == "/api/history":
            return self.send_json(history())
        if route == "/api/status":
            return self.send_json(JOB.snapshot())
        if route == "/api/units":
            try:
                return self.send_json(json.loads(UNITS.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                return self.send_json({})
        files = {"/": "index.html", "/index.html": "index.html", "/app.js": "app.js", "/styles.css": "styles.css"}
        name = files.get(route)
        if not name:
            return self.send_error(404)
        body = (HERE / name).read_bytes()
        mime = {"index.html": "text/html", "app.js": "text/javascript", "styles.css": "text/css"}[name]
        self.send_response(200)
        self.send_header("Content-Type", f"{mime}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        origin = self.headers.get("Origin")
        if origin and urlparse(origin).hostname not in ("localhost", "127.0.0.1"):
            return self.send_json({"error": "Invalid origin."}, 403)
        if self.headers.get("Content-Type", "").split(";", 1)[0] != "application/json":
            return self.send_json({"error": "Expected JSON."}, 415)
        route = self.path.split("?", 1)[0]
        if route == "/api/scrape/stop":
            return self.send_json({"ok": JOB.stop(), "status": JOB.snapshot()})
        if route == "/api/push":
            if JOB.snapshot()["state"] in ("running", "stopping"):
                return self.send_json({"error": "Wait for the capture to finish before pushing."}, 409)
            if not PUSH_LOCK.acquire(blocking=False):
                return self.send_json({"error": "A push is already running."}, 409)
            try:
                return self.send_json(push_to_mongo())
            except Exception as exc:  # surface any connect/write failure to the UI
                return self.send_json({"error": f"Push failed: {exc}"}, 502)
            finally:
                PUSH_LOCK.release()
        if route != "/api/scrape/start":
            return self.send_json({"error": "Unknown endpoint."}, 404)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 1 <= length <= 4096:
                raise ValueError("Invalid request size")
            body = json.loads(self.rfile.read(length))
            url = body.get("url", DEFAULT_URL).strip()
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.hostname != "swgoh.gg" or not HISTORY_PATH.fullmatch(parsed.path) or parsed.query or parsed.fragment:
                raise ValueError("Enter a swgoh.gg player GAC history URL.")
            headless = body.get("headless", False)
            if not isinstance(headless, bool):
                raise ValueError("Invalid browser mode")
            if not JOB.start(url, headless):
                return self.send_json({"error": "A scrape is already running."}, 409)
            return self.send_json({"ok": True, "status": JOB.snapshot()}, 202)
        except (ValueError, AttributeError, TypeError) as exc:
            return self.send_json({"error": str(exc)}, 400)


def main():
    parser = argparse.ArgumentParser(description="Run the local GAC v2 dashboard")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"GAC v2 dashboard: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        JOB.stop()
        server.server_close()


if __name__ == "__main__":
    main()
