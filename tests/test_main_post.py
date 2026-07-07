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
    mock_save.assert_called_once()


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


@patch("src.main_post.subprocess.run")
@patch("src.main_post.post_instagram")
@patch("src.main_post.post_facebook")
@patch("src.main_post.post_twitter")
@patch("src.main_post.save_queue")
@patch("src.main_post.get_todays_entry")
@patch("src.main_post.load_queue")
def test_run_skips_commit_when_all_platforms_fail(
    mock_load, mock_today, mock_save, mock_twitter, mock_facebook, mock_instagram, mock_sub
):
    mock_load.return_value = SAMPLE_QUEUE
    mock_today.return_value = SAMPLE_TODAY_ENTRY
    mock_twitter.return_value = False
    mock_facebook.return_value = False
    mock_instagram.return_value = False

    from src.main_post import run
    run()

    mock_save.assert_not_called()
    mock_sub.assert_not_called()
