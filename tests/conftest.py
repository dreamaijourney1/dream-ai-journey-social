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
