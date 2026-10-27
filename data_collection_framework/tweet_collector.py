import json
from pathlib import Path

from data_collection_framework.logger import get_logger
from data_collection_framework.storage.mongo import MongoRepository
from data_collection_framework.twitter.client import TWEET_FIELDS, USER_FIELDS, normalize_tweet

log = get_logger(__name__)
MIN_PAGE, MAX_PAGE = 5, 100  # page sizes allowed by the v2 user tweets endpoint


class TweetCollector:
    """Collects a user's timeline (Twitter API v2) into a text file (one JSON per line) and MongoDB."""

    def __init__(self, client, output_dir: Path, repository_factory=MongoRepository):
        self._client = client
        self._output_dir = Path(output_dir)
        self._repository_factory = repository_factory

    def get_all_tweets(self, screen_name: str, limit: int, database: str) -> int:
        user_id = self._client.get_user(username=screen_name).data.id
        documents = []
        token = None
        while len(documents) < limit:
            response = self._client.get_users_tweets(
                user_id, max_results=max(MIN_PAGE, min(MAX_PAGE, limit - len(documents))),
                pagination_token=token, tweet_fields=TWEET_FIELDS, user_fields=USER_FIELDS,
                expansions=["author_id"])
            users = {str(user.id): dict(user.data) for user in (response.includes or {}).get("users", [])}
            documents.extend(normalize_tweet(dict(tweet.data), users) for tweet in response.data or [])
            token = (response.meta or {}).get("next_token")
            log.debug("%s tweets downloaded so far for %s", len(documents), screen_name)
            if not token:
                break
        documents = documents[:limit]

        with open(self._output_dir / f"{screen_name}.txt", "a", encoding="utf-8") as handle:
            handle.writelines(json.dumps(doc) + "\n" for doc in documents)
        self._repository_factory(database, screen_name).insert_many(documents)
        log.info("Collected %s tweets from %s", len(documents), screen_name)
        return len(documents)
