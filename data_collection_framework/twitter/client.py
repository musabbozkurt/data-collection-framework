"""Factory and helpers for the Twitter API v2 client. tweepy is imported lazily so it is only needed when used."""
import tweepy

from data_collection_framework.config.settings import Settings, get_settings

TWEET_FIELDS = ["created_at", "author_id", "lang", "public_metrics", "entities", "geo"]
USER_FIELDS = ["created_at", "public_metrics", "name", "username"]


def build_client(settings: Settings = None) -> "tweepy.Client":
    """Builds a tweepy.Client with the credentials in the config.ini or environment variables."""
    import tweepy
    settings = settings or get_settings()
    has_user_keys = all((settings.consumer_key, settings.consumer_secret, settings.access_key, settings.access_secret))
    if not settings.bearer_token and not has_user_keys:
        raise RuntimeError("Twitter credentials are missing. Set TWITTER_BEARER_TOKEN (or the TWITTER_CONSUMER_* and "
                           "TWITTER_ACCESS_* variables) or fill them in config/config.ini.")
    return tweepy.Client(
        bearer_token=settings.bearer_token or None,
        consumer_key=settings.consumer_key or None,
        consumer_secret=settings.consumer_secret or None,
        access_token=settings.access_key or None,
        access_token_secret=settings.access_secret or None,
        wait_on_rate_limit=True,
    )


def normalize_tweet(tweet: dict, users: dict = None) -> dict:
    """Maps a v2 tweet to the v1.1-like document shape used by the analysis and term-frequency code."""
    metrics = tweet.get("public_metrics") or {}
    user = (users or {}).get(tweet.get("author_id")) or {}
    user_metrics = user.get("public_metrics") or {}
    return {
        "id": tweet.get("id"),
        "text": tweet.get("text"),
        "created_at": tweet.get("created_at"),
        "lang": tweet.get("lang"),
        "retweet_count": metrics.get("retweet_count"),
        "favorite_count": metrics.get("like_count"),
        "place": {"country": (tweet.get("geo") or {}).get("country")} if tweet.get("geo") else None,
        "user": {
            "id": tweet.get("author_id"),
            "id_str": tweet.get("author_id"),
            "name": user.get("name"),
            "screen_name": user.get("username"),
            "lang": tweet.get("lang"),
            "followers_count": user_metrics.get("followers_count"),
            "friends_count": user_metrics.get("following_count"),
        },
    }
