# Dream AI Journey Social Media Automation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fully automated pipeline that generates 21 social media posts per week for Dream AI Journey and publishes them to Twitter/X, Facebook, and Instagram via their native APIs, running on GitHub Actions at near-zero cost.

**Architecture:** A Python project with two GitHub Actions workflows — a Monday generator that calls Claude + DALL-E to write posts and create images (committing results to the repo), and a daily poster that reads the committed queue and publishes to all three platforms. A rolling `history.json` prevents repeated content angles week-over-week.

**Tech Stack:** Python 3.11, `anthropic>=0.40.0`, `openai>=1.50.0`, `tweepy>=4.14.0`, `requests>=2.31.0`, `python-dotenv>=1.0.0`, `pytest>=7.4.0`, `pytest-mock>=3.12.0`

## Global Constraints

- All file paths are relative to the repo root (`dream-ai-journey-social/`)
- Run commands from the repo root
- `queue.json` and `history.json` live at repo root
- Images saved to `images/{YYYY-MM-DD}/day-N.png` at repo root
- Claude model: `claude-sonnet-4-6`
- DALL-E model: `dall-e-3`, size `1024x1024`, quality `standard`
- Twitter: OAuth 1.0a for media upload (v1.1), OAuth 2.0 client for tweet creation (v2)
- Meta Graph API version: `v19.0`
- CTA URL in every post: `dream-page.com`
- GitHub Actions cron times are UTC: Monday generator = `0 13 * * 1`, daily poster = `0 15 * * *`
- Never commit `.env` — secrets live in GitHub Actions Secrets only

---

## File Map

| File | Responsibility |
|------|---------------|
| `src/__init__.py` | Makes `src` a Python package |
| `src/queue_manager.py` | Read/write `queue.json` and `history.json`; date-based lookups |
| `src/content.py` | Call Claude API; return structured week of posts + image prompts |
| `src/images.py` | Call DALL-E API; download and save images to `images/` |
| `src/poster.py` | Post to Twitter, Facebook, Instagram via their native APIs |
| `src/main_generate.py` | Monday orchestrator: read history → generate content → generate images → commit |
| `src/main_post.py` | Daily orchestrator: read queue → post today → update queue → commit |
| `tests/conftest.py` | Shared fixtures: env vars, sample data |
| `tests/test_queue_manager.py` | Unit tests for queue_manager |
| `tests/test_content.py` | Unit tests for content with mocked Claude client |
| `tests/test_images.py` | Unit tests for images with mocked OpenAI client |
| `tests/test_poster.py` | Unit tests for poster with mocked tweepy + requests |
| `tests/test_main_generate.py` | Integration tests for Monday orchestrator (all deps mocked) |
| `tests/test_main_post.py` | Integration tests for daily poster (all deps mocked) |
| `.github/workflows/generate.yml` | Monday 8am EST GitHub Actions workflow |
| `.github/workflows/post_daily.yml` | Daily 10am EST GitHub Actions workflow |
| `requirements.txt` | Python dependencies |
| `pytest.ini` | Test configuration |
| `.env.example` | Secrets template |
| `.gitignore` | Excludes `.env`, `__pycache__`, `.venv` |
| `queue.json` | Initialized empty; overwritten each Monday |
| `history.json` | Initialized empty; updated each Monday |
| `images/.gitkeep` | Ensures `images/` is tracked in git |

---

## Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `queue.json`
- Create: `history.json`
- Create: `images/.gitkeep`

**Interfaces:**
- Produces: importable `src` package; `pytest` runnable from repo root

- [ ] **Step 1: Create `requirements.txt`**

```
anthropic>=0.40.0
openai>=1.50.0
tweepy>=4.14.0
requests>=2.31.0
python-dotenv>=1.0.0
pytest>=7.4.0
pytest-mock>=3.12.0
```

- [ ] **Step 2: Create `pytest.ini`**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

- [ ] **Step 3: Create `.env.example`**

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_SECRET=your_twitter_access_secret_here
FACEBOOK_PAGE_ID=your_facebook_page_id_here
FACEBOOK_PAGE_TOKEN=your_facebook_long_lived_page_token_here
INSTAGRAM_USER_ID=your_instagram_business_account_id_here
GITHUB_REPOSITORY=your_github_username/dream-ai-journey-social
```

- [ ] **Step 4: Create `.gitignore`**

```
.env
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
.venv/
venv/
```

- [ ] **Step 5: Create empty package init files**

`src/__init__.py` — empty file

`tests/__init__.py` — empty file

- [ ] **Step 6: Create `tests/conftest.py`**

```python
import pytest


@pytest.fixture(autouse=True)
def set_api_env_vars(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("TWITTER_API_KEY", "test_tw_key")
    monkeypatch.setenv("TWITTER_API_SECRET", "test_tw_secret")
    monkeypatch.setenv("TWITTER_ACCESS_TOKEN", "test_tw_token")
    monkeypatch.setenv("TWITTER_ACCESS_SECRET", "test_tw_access_secret")
    monkeypatch.setenv("FACEBOOK_PAGE_ID", "111222333")
    monkeypatch.setenv("FACEBOOK_PAGE_TOKEN", "test_fb_token")
    monkeypatch.setenv("INSTAGRAM_USER_ID", "444555666")
    monkeypatch.setenv("GITHUB_REPOSITORY", "testowner/dream-ai-journey-social")
```

- [ ] **Step 7: Create `queue.json` and `history.json`**

`queue.json`:
```json
{"week_of": "", "days": []}
```

`history.json`:
```json
{"weeks": []}
```

- [ ] **Step 8: Create `images/.gitkeep`**

Empty file at `images/.gitkeep`.

- [ ] **Step 9: Install dependencies**

```bash
pip install -r requirements.txt
```

- [ ] **Step 10: Verify pytest runs**

Run: `pytest`
Expected: `no tests ran` (0 collected, no errors)

- [ ] **Step 11: Commit**

```bash
git add requirements.txt pytest.ini .env.example .gitignore src/__init__.py tests/__init__.py tests/conftest.py queue.json history.json images/.gitkeep
git commit -m "feat: scaffold project structure and dependencies"
```

---

## Task 2: Queue Manager

**Files:**
- Create: `src/queue_manager.py`
- Create: `tests/test_queue_manager.py`

**Interfaces:**
- Produces:
  - `load_history() -> dict`
  - `save_history(history: dict) -> None`
  - `load_queue() -> dict`
  - `save_queue(queue: dict) -> None`
  - `get_todays_entry(queue: dict) -> dict | None`
  - `mark_posted(queue: dict, target_date: str, platform: str) -> dict`
  - `update_history(history: dict, week_data: dict) -> dict`

- [ ] **Step 1: Write failing tests**

Create `tests/test_queue_manager.py`:

```python
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
```

- [ ] **Step 2: Run tests to confirm they fail**

Run: `pytest tests/test_queue_manager.py -v`
Expected: `ImportError: cannot import name 'load_history' from 'src.queue_manager'`

- [ ] **Step 3: Implement `src/queue_manager.py`**

```python
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
```

- [ ] **Step 4: Run tests to confirm they pass**

Run: `pytest tests/test_queue_manager.py -v`
Expected: All 13 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/queue_manager.py tests/test_queue_manager.py
git commit -m "feat: add queue and history file manager"
```

---

## Task 3: Content Generator

**Files:**
- Create: `src/content.py`
- Create: `tests/test_content.py`

**Interfaces:**
- Consumes: `history: dict` (from `load_history()`), optional `week_of: str`
- Produces: `generate_weekly_content(history: dict, week_of: str = None) -> dict`

  Return shape:
  ```python
  {
    "week_of": "2026-07-07",
    "days": [
      {
        "date": "2026-07-07",         # YYYY-MM-DD, Mon through Sun
        "service": "AI Chatbots",
        "angle": "client_win",
        "image_prompt": "...",
        "posts": {
          "facebook": "...",
          "instagram": "...",
          "twitter": "..."
        }
      },
      # ... 7 total
    ]
  }
  ```

- [ ] **Step 1: Write failing tests**

Create `tests/test_content.py`:

```python
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
```

- [ ] **Step 2: Run tests to confirm they fail**

Run: `pytest tests/test_content.py -v`
Expected: `ImportError: cannot import name 'generate_weekly_content' from 'src.content'`

- [ ] **Step 3: Implement `src/content.py`**

```python
import json
import os
from datetime import date, timedelta

import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

_SERVICES = [
    "AI Chatbots",
    "Follow-up Emails",
    "Marketing Automation",
    "Data Entry Automation",
    "Invoicing & Billing",
    "Inventory Alerts",
    "General Brand Story",
]

_SYSTEM_PROMPT = """You are the warm, human voice of Dream AI Journey — a service that helps small businesses get their time back by automating data entry, follow-up emails, AI chatbots, marketing automation, invoicing and billing, and inventory alerts.

You write social media posts that feel like they come from a real person who genuinely cares about small business owners — never generic ads. Your tone is conversational, encouraging, and specific. You talk TO business owners, not AT them.

Every post ends with a call to action to visit dream-page.com.

You respond with valid JSON only — no markdown, no explanation, just the raw JSON object."""


def _build_history_summary(history: dict) -> str:
    if not history.get("weeks"):
        return "No previous content history."
    lines = []
    for week in history["weeks"]:
        lines.append(f"Week of {week['week_of']}:")
        for day in week["days"]:
            lines.append(f"  - {day['service']}: {day['angle']}")
    return "\n".join(lines)


def generate_weekly_content(history: dict, week_of: str = None) -> dict:
    if week_of is None:
        week_of = date.today().isoformat()

    start = date.fromisoformat(week_of)
    day_dates = [(start + timedelta(days=i)).isoformat() for i in range(7)]
    history_summary = _build_history_summary(history)

    schedule_lines = "\n".join(
        f"{i + 1}. {day_dates[i]} — {_SERVICES[i]}" for i in range(7)
    )

    user_prompt = f"""Generate 7 days of social media content for the week starting {week_of}.

Cover one service per day in this exact order:
{schedule_lines}

Recent content history (avoid repeating the same angle for the same service):
{history_summary}

For each day, pick ONE angle not recently used for that service:
- "client_win" — realistic story of a business owner who solved a problem with this service
- "did_you_know" — surprising tip, stat, or little-known fact about the problem this solves
- "myth_busting" — bust a common misconception small businesses have about automation
- "question_led" — start with a relatable question that makes the reader think "that's me"
- "behind_the_scenes" — explain simply how the feature works in plain language
- "pain_point" — name a real pain point vividly, then show the solution
- "before_after" — paint the before (chaos) and after (calm) picture

For each day write:
- facebook: 150-200 words, conversational, warm, ends with CTA to dream-page.com
- instagram: 100-150 words + 5-10 hashtags on a new line, ends with dream-page.com CTA
- twitter: max 240 characters including dream-page.com

Also write a 1-2 sentence DALL-E image prompt: warm, friendly small business scene. No text in the image.

Return this exact JSON (no other text):
{{
  "days": [
    {{
      "service": "AI Chatbots",
      "angle": "client_win",
      "image_prompt": "...",
      "posts": {{
        "facebook": "...",
        "instagram": "...",
        "twitter": "..."
      }}
    }}
  ]
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8096,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    data = json.loads(message.content[0].text)

    return {
        "week_of": week_of,
        "days": [
            {**day, "date": day_dates[i]}
            for i, day in enumerate(data["days"])
        ],
    }
```

- [ ] **Step 4: Run tests to confirm they pass**

Run: `pytest tests/test_content.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/content.py tests/test_content.py
git commit -m "feat: add Claude-powered content generator"
```

---

## Task 4: Image Generator

**Files:**
- Create: `src/images.py`
- Create: `tests/test_images.py`

**Interfaces:**
- Consumes: `week_of: str`, `days: list[dict]` where each dict has `"image_prompt": str`
- Produces: `generate_and_save_images(week_of: str, days: list[dict]) -> list[dict]`

  Returns the same list with `"image_path": str` added to each dict.
  Image path format: `"images/{week_of}/day-{n}.png"` where n starts at 1.

- [ ] **Step 1: Write failing tests**

Create `tests/test_images.py`:

```python
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


SAMPLE_DAYS = [
    {"date": "2026-07-07", "service": "AI Chatbots", "image_prompt": "A friendly small business owner at a laptop"},
    {"date": "2026-07-08", "service": "Follow-up Emails", "image_prompt": "An organized email inbox with plants nearby"},
]


def _mock_openai(mock_client):
    mock_client.images.generate.return_value = MagicMock(
        data=[MagicMock(url="https://example.com/fake-image.png")]
    )


def _mock_requests(mock_get):
    mock_get.return_value = MagicMock(content=b"fake_png_bytes")


@patch("src.images.requests.get")
@patch("src.images.openai_client")
def test_generate_and_save_images_returns_days_with_image_path(mock_openai, mock_requests, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _mock_openai(mock_openai)
    _mock_requests(mock_requests)

    from src.images import generate_and_save_images
    result = generate_and_save_images("2026-07-07", SAMPLE_DAYS)

    assert len(result) == 2
    assert "image_path" in result[0]
    assert "image_path" in result[1]


@patch("src.images.requests.get")
@patch("src.images.openai_client")
def test_generate_and_save_images_names_files_correctly(mock_openai, mock_requests, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _mock_openai(mock_openai)
    _mock_requests(mock_requests)

    from src.images import generate_and_save_images
    result = generate_and_save_images("2026-07-07", SAMPLE_DAYS)

    assert result[0]["image_path"] == "images/2026-07-07/day-1.png"
    assert result[1]["image_path"] == "images/2026-07-07/day-2.png"


@patch("src.images.requests.get")
@patch("src.images.openai_client")
def test_generate_and_save_images_creates_files_on_disk(mock_openai, mock_requests, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _mock_openai(mock_openai)
    _mock_requests(mock_requests)

    from src.images import generate_and_save_images
    result = generate_and_save_images("2026-07-07", SAMPLE_DAYS)

    assert Path(result[0]["image_path"]).exists()
    assert Path(result[1]["image_path"]).exists()


@patch("src.images.requests.get")
@patch("src.images.openai_client")
def test_generate_and_save_images_preserves_existing_day_fields(mock_openai, mock_requests, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _mock_openai(mock_openai)
    _mock_requests(mock_requests)

    from src.images import generate_and_save_images
    result = generate_and_save_images("2026-07-07", SAMPLE_DAYS)

    assert result[0]["service"] == "AI Chatbots"
    assert result[0]["image_prompt"] == SAMPLE_DAYS[0]["image_prompt"]


@patch("src.images.requests.get")
@patch("src.images.openai_client")
def test_generate_and_save_images_calls_dalle_per_day(mock_openai, mock_requests, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _mock_openai(mock_openai)
    _mock_requests(mock_requests)

    from src.images import generate_and_save_images
    generate_and_save_images("2026-07-07", SAMPLE_DAYS)

    assert mock_openai.images.generate.call_count == 2
```

- [ ] **Step 2: Run tests to confirm they fail**

Run: `pytest tests/test_images.py -v`
Expected: `ImportError: cannot import name 'generate_and_save_images' from 'src.images'`

- [ ] **Step 3: Implement `src/images.py`**

```python
import os
from pathlib import Path

import openai
import requests

openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))


def generate_and_save_images(week_of: str, days: list[dict]) -> list[dict]:
    result = []
    image_dir = Path(f"images/{week_of}")
    image_dir.mkdir(parents=True, exist_ok=True)

    for i, day in enumerate(days):
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=day["image_prompt"],
            size="1024x1024",
            quality="standard",
            n=1,
        )
        temp_url = response.data[0].url
        image_bytes = requests.get(temp_url).content

        image_path = image_dir / f"day-{i + 1}.png"
        image_path.write_bytes(image_bytes)

        result.append({**day, "image_path": image_path.as_posix()})

    return result
```

- [ ] **Step 4: Run tests to confirm they pass**

Run: `pytest tests/test_images.py -v`
Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/images.py tests/test_images.py
git commit -m "feat: add DALL-E image generator"
```

---

## Task 5: Platform Poster

**Files:**
- Create: `src/poster.py`
- Create: `tests/test_poster.py`

**Interfaces:**
- Produces:
  - `post_twitter(text: str, image_path: str) -> bool`
  - `post_facebook(text: str, image_url: str) -> bool`
  - `post_instagram(caption: str, image_url: str) -> bool`

  All return `True` on success, `False` on any exception (logged to stdout).

- [ ] **Step 1: Write failing tests**

Create `tests/test_poster.py`:

```python
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call


@patch("src.poster.tweepy.Client")
@patch("src.poster.tweepy.API")
@patch("src.poster.tweepy.OAuth1UserHandler")
def test_post_twitter_returns_true_on_success(mock_auth, mock_api_cls, mock_client_cls, tmp_path):
    mock_api = MagicMock()
    mock_api.media_upload.return_value = MagicMock(media_id=999)
    mock_api_cls.return_value = mock_api
    mock_client_cls.return_value = MagicMock()

    image_file = tmp_path / "day-1.png"
    image_file.write_bytes(b"fake")

    from src.poster import post_twitter
    assert post_twitter("Tweet text dream-page.com", str(image_file)) is True
    mock_api.media_upload.assert_called_once_with(str(image_file))
    mock_client_cls.return_value.create_tweet.assert_called_once_with(
        text="Tweet text dream-page.com", media_ids=[999]
    )


@patch("src.poster.tweepy.Client")
@patch("src.poster.tweepy.API")
@patch("src.poster.tweepy.OAuth1UserHandler")
def test_post_twitter_returns_false_on_exception(mock_auth, mock_api_cls, mock_client_cls):
    mock_api_cls.return_value.media_upload.side_effect = Exception("rate limit")

    from src.poster import post_twitter
    assert post_twitter("Tweet", "nonexistent.png") is False


@patch("src.poster.requests.post")
def test_post_facebook_returns_true_on_success(mock_post):
    mock_post.return_value = MagicMock(status_code=200)
    mock_post.return_value.raise_for_status.return_value = None

    from src.poster import post_facebook
    assert post_facebook("Facebook post text", "https://raw.githubusercontent.com/owner/repo/main/images/2026-07-07/day-1.png") is True


@patch("src.poster.requests.post")
def test_post_facebook_posts_to_correct_endpoint(mock_post, monkeypatch):
    monkeypatch.setenv("FACEBOOK_PAGE_ID", "111222333")
    monkeypatch.setenv("FACEBOOK_PAGE_TOKEN", "fb_token_abc")
    mock_post.return_value = MagicMock(status_code=200)
    mock_post.return_value.raise_for_status.return_value = None

    from src.poster import post_facebook
    post_facebook("Post text", "https://example.com/image.png")

    called_url = mock_post.call_args[0][0]
    assert "111222333" in called_url
    assert "photos" in called_url


@patch("src.poster.requests.post")
def test_post_facebook_returns_false_on_exception(mock_post):
    mock_post.side_effect = Exception("network error")
    from src.poster import post_facebook
    assert post_facebook("text", "https://example.com/img.png") is False


@patch("src.poster.requests.post")
def test_post_instagram_returns_true_on_success(mock_post):
    mock_post.return_value = MagicMock(status_code=200)
    mock_post.return_value.json.return_value = {"id": "container_abc"}
    mock_post.return_value.raise_for_status.return_value = None

    from src.poster import post_instagram
    assert post_instagram("Caption #hashtag dream-page.com", "https://example.com/image.png") is True


@patch("src.poster.requests.post")
def test_post_instagram_makes_two_api_calls(mock_post, monkeypatch):
    monkeypatch.setenv("INSTAGRAM_USER_ID", "444555666")
    mock_post.return_value = MagicMock(status_code=200)
    mock_post.return_value.json.return_value = {"id": "container_xyz"}
    mock_post.return_value.raise_for_status.return_value = None

    from src.poster import post_instagram
    post_instagram("Caption", "https://example.com/image.png")

    assert mock_post.call_count == 2
    first_url = mock_post.call_args_list[0][0][0]
    second_url = mock_post.call_args_list[1][0][0]
    assert "444555666/media" in first_url
    assert "media_publish" in second_url


@patch("src.poster.requests.post")
def test_post_instagram_returns_false_on_exception(mock_post):
    mock_post.side_effect = Exception("API error")
    from src.poster import post_instagram
    assert post_instagram("Caption", "https://example.com/image.png") is False
```

- [ ] **Step 2: Run tests to confirm they fail**

Run: `pytest tests/test_poster.py -v`
Expected: `ImportError: cannot import name 'post_twitter' from 'src.poster'`

- [ ] **Step 3: Implement `src/poster.py`**

```python
import os

import requests
import tweepy


def _twitter_api() -> tweepy.API:
    auth = tweepy.OAuth1UserHandler(
        os.environ["TWITTER_API_KEY"],
        os.environ["TWITTER_API_SECRET"],
        os.environ["TWITTER_ACCESS_TOKEN"],
        os.environ["TWITTER_ACCESS_SECRET"],
    )
    return tweepy.API(auth)


def _twitter_client() -> tweepy.Client:
    return tweepy.Client(
        consumer_key=os.environ["TWITTER_API_KEY"],
        consumer_secret=os.environ["TWITTER_API_SECRET"],
        access_token=os.environ["TWITTER_ACCESS_TOKEN"],
        access_token_secret=os.environ["TWITTER_ACCESS_SECRET"],
    )


def post_twitter(text: str, image_path: str) -> bool:
    try:
        api = _twitter_api()
        client = _twitter_client()
        media = api.media_upload(image_path)
        client.create_tweet(text=text, media_ids=[media.media_id])
        return True
    except Exception as e:
        print(f"Twitter post failed: {e}")
        return False


def post_facebook(text: str, image_url: str) -> bool:
    try:
        url = f"https://graph.facebook.com/v19.0/{os.environ['FACEBOOK_PAGE_ID']}/photos"
        response = requests.post(url, data={
            "caption": text,
            "url": image_url,
            "access_token": os.environ["FACEBOOK_PAGE_TOKEN"],
        })
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Facebook post failed: {e}")
        return False


def post_instagram(caption: str, image_url: str) -> bool:
    try:
        ig_id = os.environ["INSTAGRAM_USER_ID"]
        token = os.environ["FACEBOOK_PAGE_TOKEN"]
        base = "https://graph.facebook.com/v19.0"

        container = requests.post(
            f"{base}/{ig_id}/media",
            data={"image_url": image_url, "caption": caption, "access_token": token},
        )
        container.raise_for_status()
        creation_id = container.json()["id"]

        publish = requests.post(
            f"{base}/{ig_id}/media_publish",
            data={"creation_id": creation_id, "access_token": token},
        )
        publish.raise_for_status()
        return True
    except Exception as e:
        print(f"Instagram post failed: {e}")
        return False
```

- [ ] **Step 4: Run tests to confirm they pass**

Run: `pytest tests/test_poster.py -v`
Expected: All 8 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/poster.py tests/test_poster.py
git commit -m "feat: add Twitter, Facebook, and Instagram posting"
```

---

## Task 6: Monday Generator Orchestrator

**Files:**
- Create: `src/main_generate.py`
- Create: `tests/test_main_generate.py`

**Interfaces:**
- Consumes:
  - `load_history() -> dict` from `src.queue_manager`
  - `save_history(history: dict) -> None` from `src.queue_manager`
  - `save_queue(queue: dict) -> None` from `src.queue_manager`
  - `update_history(history: dict, week_data: dict) -> dict` from `src.queue_manager`
  - `generate_weekly_content(history: dict, week_of: str) -> dict` from `src.content`
  - `generate_and_save_images(week_of: str, days: list[dict]) -> list[dict]` from `src.images`
- Produces: `run() -> None` — orchestrates full Monday pipeline and commits to git

- [ ] **Step 1: Write failing tests**

Create `tests/test_main_generate.py`:

```python
import pytest
from unittest.mock import patch, MagicMock, call


SAMPLE_CONTENT = {
    "week_of": "2026-07-07",
    "days": [
        {
            "date": f"2026-07-{7 + i:02d}",
            "service": "AI Chatbots",
            "angle": "client_win",
            "image_prompt": "Friendly image",
            "posts": {"facebook": "fb", "instagram": "ig", "twitter": "tw"},
        }
        for i in range(7)
    ],
}

SAMPLE_DAYS_WITH_IMAGES = [
    {**day, "image_path": f"images/2026-07-07/day-{i + 1}.png"}
    for i, day in enumerate(SAMPLE_CONTENT["days"])
]


@patch("src.main_generate.subprocess.run")
@patch("src.main_generate.generate_and_save_images")
@patch("src.main_generate.generate_weekly_content")
@patch("src.main_generate.save_history")
@patch("src.main_generate.save_queue")
@patch("src.main_generate.update_history")
@patch("src.main_generate.load_history")
def test_run_calls_all_steps_in_order(
    mock_load_history, mock_update_history, mock_save_queue,
    mock_save_history, mock_generate_content, mock_generate_images, mock_subprocess
):
    mock_load_history.return_value = {"weeks": []}
    mock_generate_content.return_value = SAMPLE_CONTENT
    mock_generate_images.return_value = SAMPLE_DAYS_WITH_IMAGES
    mock_update_history.return_value = {"weeks": [{"week_of": "2026-07-07", "days": []}]}

    from src.main_generate import run
    run()

    mock_load_history.assert_called_once()
    mock_generate_content.assert_called_once_with({"weeks": []})
    mock_generate_images.assert_called_once_with("2026-07-07", SAMPLE_CONTENT["days"])
    mock_save_queue.assert_called_once()
    mock_save_history.assert_called_once()


@patch("src.main_generate.subprocess.run")
@patch("src.main_generate.generate_and_save_images")
@patch("src.main_generate.generate_weekly_content")
@patch("src.main_generate.save_history")
@patch("src.main_generate.save_queue")
@patch("src.main_generate.update_history")
@patch("src.main_generate.load_history")
def test_run_saves_queue_with_posted_false(
    mock_load_history, mock_update_history, mock_save_queue,
    mock_save_history, mock_generate_content, mock_generate_images, mock_subprocess
):
    mock_load_history.return_value = {"weeks": []}
    mock_generate_content.return_value = SAMPLE_CONTENT
    mock_generate_images.return_value = SAMPLE_DAYS_WITH_IMAGES
    mock_update_history.return_value = {"weeks": []}

    from src.main_generate import run
    run()

    saved_queue = mock_save_queue.call_args[0][0]
    for day in saved_queue["days"]:
        assert day["posted"] == {"facebook": False, "instagram": False, "twitter": False}


@patch("src.main_generate.subprocess.run")
@patch("src.main_generate.generate_and_save_images")
@patch("src.main_generate.generate_weekly_content")
@patch("src.main_generate.save_history")
@patch("src.main_generate.save_queue")
@patch("src.main_generate.update_history")
@patch("src.main_generate.load_history")
def test_run_commits_and_pushes(
    mock_load_history, mock_update_history, mock_save_queue,
    mock_save_history, mock_generate_content, mock_generate_images, mock_subprocess
):
    mock_load_history.return_value = {"weeks": []}
    mock_generate_content.return_value = SAMPLE_CONTENT
    mock_generate_images.return_value = SAMPLE_DAYS_WITH_IMAGES
    mock_update_history.return_value = {"weeks": []}

    from src.main_generate import run
    run()

    subprocess_calls = [str(c) for c in mock_subprocess.call_args_list]
    assert any("commit" in c for c in subprocess_calls)
    assert any("push" in c for c in subprocess_calls)
```

- [ ] **Step 2: Run tests to confirm they fail**

Run: `pytest tests/test_main_generate.py -v`
Expected: `ImportError: cannot import name 'run' from 'src.main_generate'`

- [ ] **Step 3: Implement `src/main_generate.py`**

```python
import subprocess

from src.content import generate_weekly_content
from src.images import generate_and_save_images
from src.queue_manager import load_history, save_history, save_queue, update_history


def _git_commit_and_push(week_of: str) -> None:
    subprocess.run(
        ["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"],
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "github-actions[bot]"],
        check=True,
    )
    subprocess.run(["git", "add", f"images/{week_of}/", "queue.json", "history.json"], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"chore: generate content for week of {week_of}"],
        check=True,
    )
    subprocess.run(["git", "push"], check=True)


def run() -> None:
    history = load_history()
    content = generate_weekly_content(history)

    days_with_images = generate_and_save_images(content["week_of"], content["days"])
    content["days"] = days_with_images

    queue = {
        "week_of": content["week_of"],
        "days": [
            {
                "date": day["date"],
                "service": day["service"],
                "angle": day["angle"],
                "image_path": day["image_path"],
                "posts": day["posts"],
                "posted": {"facebook": False, "instagram": False, "twitter": False},
            }
            for day in content["days"]
        ],
    }

    updated_history = update_history(history, content)
    save_queue(queue)
    save_history(updated_history)
    _git_commit_and_push(content["week_of"])


if __name__ == "__main__":
    run()
```

- [ ] **Step 4: Run tests to confirm they pass**

Run: `pytest tests/test_main_generate.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/main_generate.py tests/test_main_generate.py
git commit -m "feat: add Monday generator orchestrator"
```

---

## Task 7: Daily Poster Orchestrator

**Files:**
- Create: `src/main_post.py`
- Create: `tests/test_main_post.py`

**Interfaces:**
- Consumes:
  - `load_queue() -> dict` from `src.queue_manager`
  - `save_queue(queue: dict) -> None` from `src.queue_manager`
  - `get_todays_entry(queue: dict) -> dict | None` from `src.queue_manager`
  - `mark_posted(queue: dict, target_date: str, platform: str) -> dict` from `src.queue_manager`
  - `post_twitter(text: str, image_path: str) -> bool` from `src.poster`
  - `post_facebook(text: str, image_url: str) -> bool` from `src.poster`
  - `post_instagram(caption: str, image_url: str) -> bool` from `src.poster`
  - `GITHUB_REPOSITORY` env var (format: `owner/repo`)
- Produces: `run() -> None`

- [ ] **Step 1: Write failing tests**

Create `tests/test_main_post.py`:

```python
import pytest
from unittest.mock import patch, MagicMock
from datetime import date


TODAY = date.today().isoformat()

SAMPLE_TODAY_ENTRY = {
    "date": TODAY,
    "service": "AI Chatbots",
    "angle": "client_win",
    "image_path": "images/2026-07-07/day-1.png",
    "posts": {
        "facebook": "Facebook post text dream-page.com",
        "instagram": "Instagram post text dream-page.com",
        "twitter": "Twitter post dream-page.com",
    },
    "posted": {"facebook": False, "instagram": False, "twitter": False},
}

SAMPLE_QUEUE = {"week_of": TODAY, "days": [SAMPLE_TODAY_ENTRY]}


@patch("src.main_post.subprocess.run")
@patch("src.main_post.post_instagram")
@patch("src.main_post.post_facebook")
@patch("src.main_post.post_twitter")
@patch("src.main_post.save_queue")
@patch("src.main_post.get_todays_entry")
@patch("src.main_post.load_queue")
def test_run_posts_to_all_three_platforms(
    mock_load, mock_today, mock_save, mock_twitter, mock_facebook, mock_instagram, mock_sub
):
    mock_load.return_value = SAMPLE_QUEUE
    mock_today.return_value = SAMPLE_TODAY_ENTRY
    mock_twitter.return_value = True
    mock_facebook.return_value = True
    mock_instagram.return_value = True

    from src.main_post import run
    run()

    mock_twitter.assert_called_once()
    mock_facebook.assert_called_once()
    mock_instagram.assert_called_once()


@patch("src.main_post.subprocess.run")
@patch("src.main_post.post_instagram")
@patch("src.main_post.post_facebook")
@patch("src.main_post.post_twitter")
@patch("src.main_post.save_queue")
@patch("src.main_post.get_todays_entry")
@patch("src.main_post.load_queue")
def test_run_exits_early_when_no_entry_for_today(
    mock_load, mock_today, mock_save, mock_twitter, mock_facebook, mock_instagram, mock_sub
):
    mock_load.return_value = {"week_of": "2020-01-01", "days": []}
    mock_today.return_value = None

    from src.main_post import run
    run()

    mock_twitter.assert_not_called()
    mock_facebook.assert_not_called()
    mock_instagram.assert_not_called()
    mock_save.assert_not_called()


@patch("src.main_post.subprocess.run")
@patch("src.main_post.post_instagram")
@patch("src.main_post.post_facebook")
@patch("src.main_post.post_twitter")
@patch("src.main_post.save_queue")
@patch("src.main_post.mark_posted")
@patch("src.main_post.get_todays_entry")
@patch("src.main_post.load_queue")
def test_run_marks_successful_platforms_as_posted(
    mock_load, mock_today, mock_mark, mock_save, mock_twitter, mock_facebook, mock_instagram, mock_sub
):
    mock_load.return_value = SAMPLE_QUEUE
    mock_today.return_value = SAMPLE_TODAY_ENTRY
    mock_twitter.return_value = True
    mock_facebook.return_value = False  # Facebook fails
    mock_instagram.return_value = True
    mock_mark.return_value = SAMPLE_QUEUE

    from src.main_post import run
    run()

    marked_platforms = [c[0][2] for c in mock_mark.call_args_list]
    assert "twitter" in marked_platforms
    assert "instagram" in marked_platforms
    assert "facebook" not in marked_platforms


@patch("src.main_post.subprocess.run")
@patch("src.main_post.post_instagram")
@patch("src.main_post.post_facebook")
@patch("src.main_post.post_twitter")
@patch("src.main_post.save_queue")
@patch("src.main_post.get_todays_entry")
@patch("src.main_post.load_queue")
def test_run_passes_github_image_url_to_facebook_and_instagram(
    mock_load, mock_today, mock_save, mock_twitter, mock_facebook, mock_instagram, mock_sub, monkeypatch
):
    monkeypatch.setenv("GITHUB_REPOSITORY", "myowner/dream-ai-journey-social")
    mock_load.return_value = SAMPLE_QUEUE
    mock_today.return_value = SAMPLE_TODAY_ENTRY
    mock_twitter.return_value = True
    mock_facebook.return_value = True
    mock_instagram.return_value = True

    from src.main_post import run
    run()

    expected_url = "https://raw.githubusercontent.com/myowner/dream-ai-journey-social/main/images/2026-07-07/day-1.png"
    fb_image_url = mock_facebook.call_args[0][1]
    ig_image_url = mock_instagram.call_args[0][1]
    assert fb_image_url == expected_url
    assert ig_image_url == expected_url
```

- [ ] **Step 2: Run tests to confirm they fail**

Run: `pytest tests/test_main_post.py -v`
Expected: `ImportError: cannot import name 'run' from 'src.main_post'`

- [ ] **Step 3: Implement `src/main_post.py`**

```python
import os
import subprocess
from datetime import date

from src.poster import post_facebook, post_instagram, post_twitter
from src.queue_manager import get_todays_entry, load_queue, mark_posted, save_queue


def _image_url(image_path: str) -> str:
    repo = os.environ["GITHUB_REPOSITORY"]
    return f"https://raw.githubusercontent.com/{repo}/main/{image_path}"


def _git_commit_and_push(target_date: str) -> None:
    subprocess.run(
        ["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"],
        check=True,
    )
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "pull", "--rebase"], check=True)
    subprocess.run(["git", "add", "queue.json"], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"chore: mark posts published for {target_date}"],
        check=True,
    )
    subprocess.run(["git", "push"], check=True)


def run() -> None:
    queue = load_queue()
    today = get_todays_entry(queue)

    if not today:
        print(f"No posts scheduled for {date.today().isoformat()} — skipping.")
        return

    target_date = today["date"]
    image_url = _image_url(today["image_path"])

    if not today["posted"]["twitter"]:
        if post_twitter(today["posts"]["twitter"], today["image_path"]):
            queue = mark_posted(queue, target_date, "twitter")

    if not today["posted"]["facebook"]:
        if post_facebook(today["posts"]["facebook"], image_url):
            queue = mark_posted(queue, target_date, "facebook")

    if not today["posted"]["instagram"]:
        if post_instagram(today["posts"]["instagram"], image_url):
            queue = mark_posted(queue, target_date, "instagram")

    save_queue(queue)
    _git_commit_and_push(target_date)


if __name__ == "__main__":
    run()
```

- [ ] **Step 4: Run tests to confirm they pass**

Run: `pytest tests/test_main_post.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Run full test suite**

Run: `pytest -v`
Expected: All tests PASS (no failures)

- [ ] **Step 6: Commit**

```bash
git add src/main_post.py tests/test_main_post.py
git commit -m "feat: add daily poster orchestrator"
```

---

## Task 8: GitHub Actions Workflows

**Files:**
- Create: `.github/workflows/generate.yml`
- Create: `.github/workflows/post_daily.yml`

**Interfaces:**
- Consumes: all GitHub Secrets listed below
- Produces: automated weekly content generation + daily posting

- [ ] **Step 1: Create `.github/workflows/generate.yml`**

```yaml
name: Generate Weekly Content

on:
  schedule:
    - cron: '0 13 * * 1'  # Monday 8am EST (13:00 UTC); shifts to 9am EDT in summer
  workflow_dispatch:       # Allows manual trigger from GitHub Actions UI

permissions:
  contents: write

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Generate weekly content
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python -m src.main_generate
```

- [ ] **Step 2: Create `.github/workflows/post_daily.yml`**

```yaml
name: Post Daily Content

on:
  schedule:
    - cron: '0 15 * * *'  # Daily 10am EST (15:00 UTC); shifts to 11am EDT in summer
  workflow_dispatch:

permissions:
  contents: write

jobs:
  post:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Post today's content
        env:
          TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
          TWITTER_API_SECRET: ${{ secrets.TWITTER_API_SECRET }}
          TWITTER_ACCESS_TOKEN: ${{ secrets.TWITTER_ACCESS_TOKEN }}
          TWITTER_ACCESS_SECRET: ${{ secrets.TWITTER_ACCESS_SECRET }}
          FACEBOOK_PAGE_ID: ${{ secrets.FACEBOOK_PAGE_ID }}
          FACEBOOK_PAGE_TOKEN: ${{ secrets.FACEBOOK_PAGE_TOKEN }}
          INSTAGRAM_USER_ID: ${{ secrets.INSTAGRAM_USER_ID }}
          GITHUB_REPOSITORY: ${{ github.repository }}
        run: python -m src.main_post
```

- [ ] **Step 3: Create GitHub repo and push**

On github.com, create a new repository named `dream-ai-journey-social` (public or private — either works).

```bash
git remote add origin https://github.com/YOUR_USERNAME/dream-ai-journey-social.git
git push -u origin master
```

- [ ] **Step 4: Add GitHub Secrets**

In the GitHub repo → Settings → Secrets and variables → Actions → New repository secret. Add each of these:

| Secret Name | Where to get it |
|-------------|----------------|
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys |
| `OPENAI_API_KEY` | platform.openai.com → API Keys |
| `TWITTER_API_KEY` | developer.twitter.com → Your App → Keys and Tokens |
| `TWITTER_API_SECRET` | Same page as above |
| `TWITTER_ACCESS_TOKEN` | Same page — generate under "Access Token and Secret" |
| `TWITTER_ACCESS_SECRET` | Same page |
| `FACEBOOK_PAGE_ID` | Your Facebook Page → About → Page ID (numeric) |
| `FACEBOOK_PAGE_TOKEN` | Meta for Developers → Graph API Explorer → generate a long-lived token |
| `INSTAGRAM_USER_ID` | Meta Graph API: `GET /me/accounts` then `/PAGE_ID?fields=instagram_business_account` |

- [ ] **Step 5: Test manual trigger**

In GitHub → Actions tab → "Generate Weekly Content" → Run workflow.

Watch the run log. Expected: it completes successfully and a new commit appears with `queue.json`, `history.json`, and 7 images in `images/YYYY-MM-DD/`.

- [ ] **Step 6: Verify daily post manually**

In GitHub → Actions → "Post Daily Content" → Run workflow.

Watch the log for each platform. If any fail, check the specific error in the log.

- [ ] **Step 7: Commit workflows**

```bash
git add .github/workflows/generate.yml .github/workflows/post_daily.yml
git commit -m "feat: add GitHub Actions workflows for generation and posting"
git push
```

---

## Platform Setup Checklist (One-Time)

Before the system can post, these platform accounts need to be configured:

### Twitter/X Developer Setup
1. Apply at developer.twitter.com → Create a project and app
2. Set app permissions to "Read and Write"
3. Generate Access Token and Secret (not just API key)
4. Free tier allows 1,500 tweets/month (~31 used per month here)

### Facebook Page + Meta App Setup
1. You need a Facebook Page (not personal profile) for your business
2. Go to developers.facebook.com → Create App → Business type
3. Add "Pages API" product to your app
4. Use Graph API Explorer to generate a User Access Token, then exchange for a long-lived Page Access Token (lasts 60 days — you'll need to refresh it periodically)

### Instagram Business Account Setup
1. Your Instagram account must be an **Instagram Business** or **Creator** account
2. Connect it to your Facebook Page (in Instagram Settings → Linked Accounts)
3. In Graph API Explorer: `GET /me/accounts` → find your page → `GET /{page-id}?fields=instagram_business_account` → note the `id` — this is your `INSTAGRAM_USER_ID`
