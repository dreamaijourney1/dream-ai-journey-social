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
