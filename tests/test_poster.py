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
