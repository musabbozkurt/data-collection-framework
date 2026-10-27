import json
from datetime import datetime
from pathlib import Path

import tweepy

from data_collection_framework.logger import get_logger
from data_collection_framework.storage.mongo import MongoRepository
from data_collection_framework.twitter.client import TWEET_FIELDS, USER_FIELDS, normalize_tweet

log = get_logger(__name__)


class StreamCollector(tweepy.StreamingClient):
    """Streams matching tweets (Twitter API v2 filtered stream) into a text file and MongoDB until the end time."""

    def __init__(self, bearer_token: str, repository: MongoRepository, output_file: Path, end_time: datetime):
        super().__init__(bearer_token, wait_on_rate_limit=True)
        self._repository = repository
        self._output_file = Path(output_file)
        self._end_time = end_time

    def stream(self, keywords) -> None:
        """Replaces this app's stream rules with one rule matching any keyword, then starts streaming."""
        existing = self.get_rules().data or []
        if existing:
            self.delete_rules([rule.id for rule in existing])
        query = " OR ".join(f'"{word}"' if " " in word else word for word in keywords)
        self.add_rules(tweepy.StreamRule(query))
        self.filter(tweet_fields=TWEET_FIELDS, user_fields=USER_FIELDS, expansions=["author_id"])

    def on_data(self, raw_data):
        if datetime.now() >= self._end_time:
            log.info("Streaming finished")
            self.disconnect()
            return
        text = raw_data.decode("utf-8") if isinstance(raw_data, bytes) else raw_data
        document = json.loads(text)
        if "data" not in document:
            return
        with open(self._output_file, "a", encoding="utf-8") as handle:
            handle.write(text.strip() + "\n")
        users = {user["id"]: user for user in document.get("includes", {}).get("users", [])}
        self._repository.insert_one(normalize_tweet(document["data"], users))

    def on_request_error(self, status_code):
        log.error("Streaming request error: %s", status_code)

    def on_connection_error(self):
        log.warning("Stream disconnected; reconnecting")
