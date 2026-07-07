import json
import pytest
from datetime import date
from src.queue_manager import (
    load_history, save_history, load_queue, save_queue,
    get_todays_entry, mark_posted, update_history,
)


def test_load_history_returns_empty_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert load_history() == {"weeks": []}


def test_load_history_returns_data_when_file_exists(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    data = {"weeks": [{"week_of": "2026-07-07", "days": []}]}
    (tmp_path / "history.json").write_text(json.dumps(data))
    assert load_history() == data


def test_save_and_load_history_roundtrip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    data = {"weeks": [{"week_of": "2026-07-07", "days": [{"service": "AI Chatbots", "angle": "client_win"}]}]}
    save_history(data)
    assert load_history() == data


def test_load_queue_returns_empty_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert load_queue() == {"week_of": "", "days": []}


def test_save_and_load_queue_roundtrip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    data = {"week_of": "2026-07-07", "days": [{"date": "2026-07-07", "posts": {}}]}
    save_queue(data)
    assert load_queue() == data


def test_get_todays_entry_returns_matching_day():
    today = date.today().isoformat()
    queue = {
        "week_of": today,
        "days": [
            {"date": "2020-01-01", "service": "Old"},
            {"date": today, "service": "AI Chatbots", "posts": {}, "posted": {"facebook": False, "instagram": False, "twitter": False}, "image_path": "images/test/day-1.png"},
        ],
    }
    result = get_todays_entry(queue)
    assert result is not None
    assert result["date"] == today
    assert result["service"] == "AI Chatbots"


def test_get_todays_entry_returns_none_when_no_match():
    queue = {"week_of": "2020-01-01", "days": [{"date": "2020-01-01", "service": "Old"}]}
    assert get_todays_entry(queue) is None


def test_get_todays_entry_returns_none_for_empty_queue():
    assert get_todays_entry({"week_of": "", "days": []}) is None


def test_mark_posted_sets_platform_to_true():
    queue = {"days": [{"date": "2026-07-07", "posted": {"twitter": False, "facebook": False, "instagram": False}}]}
    result = mark_posted(queue, "2026-07-07", "twitter")
    assert result["days"][0]["posted"]["twitter"] is True
    assert result["days"][0]["posted"]["facebook"] is False


def test_mark_posted_does_not_affect_other_dates():
    queue = {
        "days": [
            {"date": "2026-07-07", "posted": {"twitter": False, "facebook": False, "instagram": False}},
            {"date": "2026-07-08", "posted": {"twitter": False, "facebook": False, "instagram": False}},
        ]
    }
    result = mark_posted(queue, "2026-07-07", "facebook")
    assert result["days"][0]["posted"]["facebook"] is True
    assert result["days"][1]["posted"]["facebook"] is False


def test_update_history_prepends_new_week():
    history = {"weeks": [{"week_of": "2026-06-30", "days": []}]}
    week_data = {"week_of": "2026-07-07", "days": [{"service": "AI Chatbots", "angle": "client_win"}]}
    result = update_history(history, week_data)
    assert result["weeks"][0]["week_of"] == "2026-07-07"
    assert result["weeks"][1]["week_of"] == "2026-06-30"


def test_update_history_trims_to_four_weeks():
    history = {
        "weeks": [
            {"week_of": "2026-06-09", "days": []},
            {"week_of": "2026-06-16", "days": []},
            {"week_of": "2026-06-23", "days": []},
            {"week_of": "2026-06-30", "days": []},
        ]
    }
    week_data = {"week_of": "2026-07-07", "days": [{"service": "AI Chatbots", "angle": "client_win"}]}
    result = update_history(history, week_data)
    assert len(result["weeks"]) == 4
    assert result["weeks"][0]["week_of"] == "2026-07-07"
    assert result["weeks"][-1]["week_of"] == "2026-06-16"


def test_update_history_stores_only_service_and_angle():
    history = {"weeks": []}
    week_data = {
        "week_of": "2026-07-07",
        "days": [{"service": "AI Chatbots", "angle": "client_win", "posts": {"twitter": "..."}, "image_path": "..."}],
    }
    result = update_history(history, week_data)
    assert list(result["weeks"][0]["days"][0].keys()) == ["service", "angle"]
