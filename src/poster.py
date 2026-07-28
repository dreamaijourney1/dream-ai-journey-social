import os
import time

import requests
import tweepy


GRAPH_API_VERSION = "v19.0"
REQUEST_TIMEOUT = 60


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


def _print_response_error(platform: str, response: requests.Response) -> None:
    print(f"{platform} response status: {response.status_code}")
    print(f"{platform} response body: {response.text}")


def post_twitter(text: str, image_path: str) -> bool:
    try:
        api = _twitter_api()
        client = _twitter_client()

        print("Uploading image to X...")
        media = api.media_upload(filename=image_path)

        print(f"X media uploaded. Media ID: {media.media_id}")

        response = client.create_tweet(
            text=text,
            media_ids=[media.media_id],
            user_auth=True,
        )

        tweet_id = None
        if response and response.data:
            tweet_id = response.data.get("id")

        print(f"X post published successfully. Post ID: {tweet_id}")
        return True

    except tweepy.TweepyException as error:
        print(f"Twitter post failed: {error}")

        if getattr(error, "response", None) is not None:
            print(f"Twitter status: {error.response.status_code}")
            print(f"Twitter response: {error.response.text}")

        return False

    except Exception as error:
        print(f"Twitter unexpected error: {error}")
        return False


def post_facebook(text: str, image_url: str) -> bool:
    try:
        page_id = os.environ["FACEBOOK_PAGE_ID"]
        token = os.environ["FACEBOOK_PAGE_TOKEN"]

        url = (
            f"https://graph.facebook.com/"
            f"{GRAPH_API_VERSION}/{page_id}/photos"
        )

        print(f"Facebook image URL: {image_url}")

        response = requests.post(
            url,
            data={
                "caption": text,
                "url": image_url,
                "access_token": token,
            },
            timeout=REQUEST_TIMEOUT,
        )

        if not response.ok:
            _print_response_error("Facebook", response)
            return False

        response_data = response.json()
        post_id = response_data.get("post_id") or response_data.get("id")

        print(f"Facebook post published successfully. Post ID: {post_id}")
        return True

    except requests.RequestException as error:
        print(f"Facebook request failed: {error}")
        return False

    except Exception as error:
        print(f"Facebook unexpected error: {error}")
        return False


def _wait_for_instagram_container(
    creation_id: str,
    token: str,
    max_attempts: int = 12,
    wait_seconds: int = 5,
) -> bool:
    status_url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_API_VERSION}/{creation_id}"
    )

    for attempt in range(1, max_attempts + 1):
        response = requests.get(
            status_url,
            params={
                "fields": "status_code,status",
                "access_token": token,
            },
            timeout=REQUEST_TIMEOUT,
        )

        if not response.ok:
            _print_response_error("Instagram container status", response)
            return False

        status_data = response.json()
        status_code = status_data.get("status_code")
        status_message = status_data.get("status")

        print(
            f"Instagram container check {attempt}/{max_attempts}: "
            f"{status_code} - {status_message}"
        )

        if status_code == "FINISHED":
            return True

        if status_code in {"ERROR", "EXPIRED"}:
            print(
                "Instagram container could not be published: "
                f"{status_data}"
            )
            return False

        time.sleep(wait_seconds)

    print("Instagram container did not finish processing in time.")
    return False


def post_instagram(caption: str, image_url: str) -> bool:
    try:
        ig_id = os.environ["INSTAGRAM_USER_ID"]
        token = os.environ["FACEBOOK_PAGE_TOKEN"]
        base = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

        print(f"Instagram image URL: {image_url}")

        container = requests.post(
            f"{base}/{ig_id}/media",
            data={
                "image_url": image_url,
                "caption": caption,
                "access_token": token,
            },
            timeout=REQUEST_TIMEOUT,
        )

        if not container.ok:
            _print_response_error(
                "Instagram container creation",
                container,
            )
            return False

        container_data = container.json()
        creation_id = container_data.get("id")

        if not creation_id:
            print(
                "Instagram did not return a creation ID: "
                f"{container_data}"
            )
            return False

        print(f"Instagram container created. ID: {creation_id}")

        if not _wait_for_instagram_container(creation_id, token):
            return False

        publish = requests.post(
            f"{base}/{ig_id}/media_publish",
            data={
                "creation_id": creation_id,
                "access_token": token,
            },
            timeout=REQUEST_TIMEOUT,
        )

        if not publish.ok:
            _print_response_error("Instagram publish", publish)
            return False

        publish_data = publish.json()
        media_id = publish_data.get("id")

        print(
            "Instagram post published successfully. "
            f"Media ID: {media_id}"
        )
        return True

    except requests.RequestException as error:
        print(f"Instagram request failed: {error}")
        return False

    except Exception as error:
        print(f"Instagram unexpected error: {error}")
        return False
