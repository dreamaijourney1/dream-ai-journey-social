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

raw_response = message.content[0].text.strip()

print("Claude raw response:")
print(raw_response)

if not raw_response:
    raise ValueError("Claude returned an empty response.")

if raw_response.startswith("```"):
    raw_response = raw_response.removeprefix("```json")
    raw_response = raw_response.removeprefix("```")
    raw_response = raw_response.removesuffix("```")
    raw_response = raw_response.strip()

data = json.loads(raw_response)
    return {
        "week_of": week_of,
        "days": [
            {**day, "date": day_dates[i]}
            for i, day in enumerate(data["days"])
        ],
    }
