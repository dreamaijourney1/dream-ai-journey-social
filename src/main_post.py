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
