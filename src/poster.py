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
