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


def test_write_files_loads_selected_files_and_rejects_bad_json(tmp_path):
    good = tmp_path / "a.txt"
    good.write_text('{"id": 1}\n\n{"id": 2}\n', encoding="utf-8")
    bad = tmp_path / "b.txt"
    bad.write_text('{"id": 3}\nnot json\n', encoding="utf-8")
    writer = MongoWriter(FakeRepository)
    assert writer.write_files([good], "d", "c") == 2
    with pytest.raises(ValueError, match="b.txt, line 2"):
        writer.write_files([bad], "d", "c")


def test_write_lines_and_json_files(tmp_path):
    writer = MongoWriter(FakeRepository)
    assert writer.write_lines(['{"a": 1}', "", '{"a": 2}'], "d", "c") == 2
    with pytest.raises(ValueError, match="line 1"):
        writer.write_lines(["nope"], "d", "c")
    with pytest.raises(ValueError, match="JSON object"):
        writer.write_lines(["[1]"], "d", "c")
    data = tmp_path / "a.json"
    data.write_text('[{"id": 1}, {"id": 2}]', encoding="utf-8")
    assert MongoWriter(FakeRepository).write_files([data], "d", "c") == 2


def test_read_usernames_template_comments_and_validation(tmp_path):
    from data_collection_framework.storage.files import read_usernames
    folder = tmp_path / "users"
    assert read_usernames(folder) == ["NASA", "elonmusk"]  # copied from the template
    (folder / "usernames.txt").write_text("# team\n@Alice bob # note\nalice\n", encoding="utf-8")
    assert read_usernames(folder) == ["Alice", "bob"]
    (folder / "usernames.txt").write_text("fine\nnot a name!\n", encoding="utf-8")
    with pytest.raises(ValueError, match="line 2"):
        read_usernames(folder)


def test_save_usernames_replaces_list(tmp_path):
    from data_collection_framework.storage.files import read_usernames, save_usernames
    (tmp_path / "old.txt").write_text("old_user\n", encoding="utf-8")
    assert save_usernames(tmp_path, "# list\n@new_one two\n") == 2
    assert read_usernames(tmp_path) == ["new_one", "two"]
    assert (tmp_path / "old.txt.bak").exists()
    with pytest.raises(ValueError, match="line 1"):
        save_usernames(tmp_path, "bad name!\n")
    assert read_usernames(tmp_path) == ["new_one", "two"]
