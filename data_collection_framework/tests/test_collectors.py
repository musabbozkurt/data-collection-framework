import json
from types import SimpleNamespace

import pytest

from data_collection_framework.analysis import Analysis
from data_collection_framework.mongo_writer import MongoWriter
from data_collection_framework.tweet_collector import TweetCollector


class FakeRepository:
    stored = []

    def __init__(self, database, collection):
        self.target = (database, collection)

    def insert_many(self, documents):
        documents = list(documents)
        FakeRepository.stored.append((self.target, documents))
        return len(documents)


@pytest.fixture(autouse=True)
def fresh_store(monkeypatch):
    monkeypatch.setattr(FakeRepository, "stored", [])


def tweet(id_):
    return SimpleNamespace(data={"id": str(id_), "text": "hi", "author_id": "7", "lang": "en",
                                 "public_metrics": {"retweet_count": 1, "like_count": 2}})


class FakeClient:
    def __init__(self, tweets):
        self.tweets = tweets

    def get_user(self, username):
        return SimpleNamespace(data=SimpleNamespace(id="7"))

    def get_users_tweets(self, user_id, max_results, pagination_token=None, **kwargs):
        start = int(pagination_token or 0)
        page = self.tweets[start:start + max_results]
        more = start + max_results < len(self.tweets)
        return SimpleNamespace(data=page, includes={}, meta={"next_token": str(start + max_results)} if more else {})


def test_tweet_collector_pages_and_batches(tmp_path):
    collector = TweetCollector(FakeClient([tweet(i) for i in range(500)]), tmp_path, FakeRepository)
    assert collector.get_all_tweets("bob", 250, "db") == 250
    assert len((tmp_path / "bob.txt").read_text().splitlines()) == 250
    assert len(FakeRepository.stored) == 1  # one batched insert
    assert FakeRepository.stored[0][1][0]["user"]["lang"] == "en"


def test_mongo_writer_and_analysis(tmp_path):
    lines = [json.dumps({"user": {"lang": lang}}) for lang in ("en", "en", "tr")]
    (tmp_path / "a.txt").write_text("\n".join(lines) + "\n")
    assert MongoWriter(FakeRepository).write_to_mongo(tmp_path, "db", "col") == 3
    assert Analysis(tmp_path).count("language") == {"en": 2, "tr": 1}
