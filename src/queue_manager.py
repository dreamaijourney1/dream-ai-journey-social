import json
from datetime import date
from pathlib import Path

QUEUE_FILE = Path("queue.json")
HISTORY_FILE = Path("history.json")
_HISTORY_MAX_WEEKS = 4


def load_history() -> dict:
    if not HISTORY_FILE.exists():
        return {"weeks": []}
    return json.loads(HISTORY_FILE.read_text())


def save_history(history: dict) -> None:
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def load_queue() -> dict:
    if not QUEUE_FILE.exists():
        return {"week_of": "", "days": []}
    return json.loads(QUEUE_FILE.read_text())


def save_queue(queue: dict) -> None:
    QUEUE_FILE.write_text(json.dumps(queue, indent=2))


def get_todays_entry(queue: dict) -> dict | None:
    today = date.today().isoformat()
    for day in queue.get("days", []):
        if day["date"] == today:
            return day
    return None


def mark_posted(queue: dict, target_date: str, platform: str) -> dict:
    for day in queue["days"]:
        if day["date"] == target_date:
            day["posted"][platform] = True
    return queue


def update_history(history: dict, week_data: dict) -> dict:
    new_entry = {
        "week_of": week_data["week_of"],
        "days": [
            {"service": day["service"], "angle": day["angle"]}
            for day in week_data["days"]
        ],
    }
    weeks = [new_entry] + history.get("weeks", [])
    return {"weeks": weeks[:_HISTORY_MAX_WEEKS]}
