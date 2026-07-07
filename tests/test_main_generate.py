import pytest
from unittest.mock import patch


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
