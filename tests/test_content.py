import json
import pytest
from unittest.mock import patch, MagicMock


SERVICES = [
    "AI Chatbots", "Follow-up Emails", "Marketing Automation",
    "Data Entry Automation", "Invoicing & Billing", "Inventory Alerts",
    "General Brand Story",
]


def _make_sample_days(n=7):
    return [
        {
            "service": SERVICES[i],
            "angle": "client_win",
            "image_prompt": f"Friendly image for {SERVICES[i]}",
            "posts": {
                "facebook": f"Facebook post about {SERVICES[i]} dream-page.com",
                "instagram": f"Instagram post about {SERVICES[i]} dream-page.com",
                "twitter": f"Twitter post {SERVICES[i]} dream-page.com",
            },
        }
        for i in range(n)
    ]


def _mock_claude(sample_days):
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text=json.dumps({"days": sample_days}))]
    return mock_msg


@patch("src.content.client")
def test_generate_weekly_content_returns_seven_days(mock_client):
    mock_client.messages.create.return_value = _mock_claude(_make_sample_days())
    from src.content import generate_weekly_content
    result = generate_weekly_content({"weeks": []}, week_of="2026-07-07")
    assert len(result["days"]) == 7


@patch("src.content.client")
def test_generate_weekly_content_assigns_correct_dates(mock_client):
    mock_client.messages.create.return_value = _mock_claude(_make_sample_days())
    from src.content import generate_weekly_content
    result = generate_weekly_content({"weeks": []}, week_of="2026-07-07")
    assert result["days"][0]["date"] == "2026-07-07"
    assert result["days"][1]["date"] == "2026-07-08"
    assert result["days"][6]["date"] == "2026-07-13"


@patch("src.content.client")
def test_generate_weekly_content_includes_week_of(mock_client):
    mock_client.messages.create.return_value = _mock_claude(_make_sample_days())
    from src.content import generate_weekly_content
    result = generate_weekly_content({"weeks": []}, week_of="2026-07-07")
    assert result["week_of"] == "2026-07-07"


@patch("src.content.client")
def test_generate_weekly_content_each_day_has_required_keys(mock_client):
    mock_client.messages.create.return_value = _mock_claude(_make_sample_days())
    from src.content import generate_weekly_content
    result = generate_weekly_content({"weeks": []}, week_of="2026-07-07")
    for day in result["days"]:
        assert "date" in day
        assert "service" in day
        assert "angle" in day
        assert "image_prompt" in day
        assert "facebook" in day["posts"]
        assert "instagram" in day["posts"]
        assert "twitter" in day["posts"]


@patch("src.content.client")
def test_generate_weekly_content_passes_history_to_prompt(mock_client):
    mock_client.messages.create.return_value = _mock_claude(_make_sample_days())
    from src.content import generate_weekly_content
    history = {
        "weeks": [
            {"week_of": "2026-06-30", "days": [{"service": "AI Chatbots", "angle": "myth_busting"}]}
        ]
    }
    generate_weekly_content(history, week_of="2026-07-07")
    call_kwargs = mock_client.messages.create.call_args[1]
    user_content = call_kwargs["messages"][0]["content"]
    assert "myth_busting" in user_content
    assert "2026-06-30" in user_content


@patch("src.content.client")
def test_generate_weekly_content_uses_today_as_default_week_of(mock_client):
    mock_client.messages.create.return_value = _mock_claude(_make_sample_days())
    from src.content import generate_weekly_content
    from datetime import date
    result = generate_weekly_content({"weeks": []})
    assert result["week_of"] == date.today().isoformat()
