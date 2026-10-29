import pytest

from data_collection_framework.analytics import analyze, tweet_authors


def tweet(user, likes, **extra):
    return {"user": {"username": user}, "metrics": {"favorite_count": likes, "retweet_count": 1},
            "text": f"hello world from {user}", "hashtags": ["Py"], "media": [], "is_reply": False, **extra}


class FakeCollection:
    def __init__(self, documents):
        self.documents = documents

    def find(self, query, _projection):
        name = query.get("$or", [{}])[0].get("user.username")
        return [d for d in self.documents if not name or d["user"]["username"] == name]

    def aggregate(self, _pipeline):
        return [{"_id": n} for n in sorted({d["user"]["username"] for d in self.documents})]


class FakeClient:
    def __init__(self, documents):
        self.collection = FakeCollection(documents)

    def __getitem__(self, _name):
        return {"c": self.collection}


CLIENT = FakeClient([tweet("a", 5), tweet("a", 1, media=[{"type": "photo"}]), tweet("b", 9, is_reply=True)])


def run(metric, user=""):
    return analyze(metric, 5, user, 2, "d", "c", CLIENT)


def test_tweets_and_likes_per_profile():
    assert run("tweets_per_profile")["items"][0] == {"label": "a", "value": 2}
    assert run("likes_per_profile")["items"][0] == {"label": "b", "value": 9}


def test_filter_by_profile_and_types():
    result = run("tweet_type", "a")
    assert result["tweets"] == 2
    assert {i["label"] for i in result["items"]} == {"text only", "with media"}


def test_most_liked_and_terms():
    assert run("most_liked")["items"][0]["value"] == 9
    assert run("top_terms")["items"][0]["label"] == "hello"


def test_ngrams_and_char_ngrams():
    assert run("word_ngrams")["items"][0] == {"label": "hello world", "value": 3}
    assert run("char_ngrams")["items"][0]["value"] >= 3


def test_unknown_metric_and_authors():
    with pytest.raises(ValueError):
        run("nope")
    assert tweet_authors("d", "c", CLIENT) == ["a", "b"]


class SamplingCollection:
    def __init__(self, documents):
        self.documents = documents

    def find(self, query=None, projection=None):
        return FakeCursor(self.documents)


class FakeCursor(list):
    def limit(self, count):
        return self[:count]


class SamplingClient:
    def __init__(self, documents):
        self.collection = SamplingCollection(documents)

    def __getitem__(self, _name):
        return {"c": self.collection}


def test_available_metrics_follow_the_collection_content():
    from data_collection_framework.analytics import available_metrics
    tweets = [tweet("a", 1), tweet("b", 2)]
    keys = [m["key"] for m in available_metrics("d", "c", SamplingClient(tweets))]
    assert {"tweets_per_profile", "likes_per_profile", "most_liked", "top_terms", "hashtags"} <= set(keys)
    assert "views_per_profile" not in keys  # no view_count in the sample

    plain = [{"city": "Rome", "price": 3}, {"city": "Oslo", "price": 3}, {"city": "Rome", "price": 5}]
    metrics = available_metrics("d", "c", SamplingClient(plain))
    assert [m["key"] for m in metrics] == ["field:city", "field:price"]
    assert all(m["description"] for m in metrics)


def test_field_metric_counts_values_of_any_collection():
    docs = [{"city": "Rome", "tags": ["x", "y"]}, {"city": "Rome", "tags": ["x"]}, {"city": "Oslo"}]
    result = analyze("field:city", 5, database="d", collection="c", client=SamplingClient(docs))
    assert result["items"][0] == {"label": "Rome", "value": 2}
    assert result["description"]
    tags = analyze("field:tags", 5, database="d", collection="c", client=SamplingClient(docs))
    assert tags["items"][0] == {"label": "x", "value": 2}
