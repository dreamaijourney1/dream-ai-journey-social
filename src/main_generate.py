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
