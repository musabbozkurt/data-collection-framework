"""Charts and statistics computed from the documents of any MongoDB collection (tweets by default)."""
import re
from collections import Counter
from typing import Callable, Dict, Iterable, List, Tuple

from data_collection_framework.nlp.char_ngrams import char_ngrams
from data_collection_framework.nlp.ngrams import ngrams
from data_collection_framework.nlp.term_frequency import count_pairs, count_terms
from data_collection_framework.storage.mongo import AUTHOR_PATH, get_client

DEFAULT_DATABASE = "x_profile_db"
DEFAULT_COLLECTION = "profile_tweets"
UNKNOWN = "unknown"
FIELD_PREFIX = "field:"
FIELD_PATTERN = r"field:[A-Za-z0-9_.\-]{1,100}"
SAMPLE_SIZE = 300
MAX_FIELDS = 30
LONG_TEXT = 60


def _author(tweet: dict) -> str:
    return (tweet.get("user") or {}).get("username") or tweet.get("username") or UNKNOWN


def _metric(name: str) -> Callable[[dict], int]:
    return lambda tweet: int((tweet.get("metrics") or {}).get(name) or 0)


def _tweet_type(tweet: dict) -> str:
    if tweet.get("is_reply"):
        return "reply"
    return "with media" if tweet.get("media") else "text only"


def _media_types(tweet: dict) -> List[str]:
    return [item.get("type", UNKNOWN) for item in tweet.get("media") or []]


# metric -> (title, label of the value axis, how a tweet contributes: list of (label, amount))
def _count(key: Callable[[dict], Iterable[str]]) -> Callable[[dict], List[Tuple[str, int]]]:
    return lambda tweet: [(label, 1) for label in key(tweet)]


def _sum(metric: str) -> Callable[[dict], List[Tuple[str, int]]]:
    read = _metric(metric)
    return lambda tweet: [(_author(tweet), read(tweet))]


METRICS: Dict[str, Tuple[str, str, Callable[[dict], List[Tuple[str, int]]]]] = {
    "tweets_per_profile": ("Tweets per profile", "tweets", _count(lambda t: [_author(t)])),
    "likes_per_profile": ("Likes per profile", "likes", _sum("favorite_count")),
    "retweets_per_profile": ("Retweets per profile", "retweets", _sum("retweet_count")),
    "views_per_profile": ("Views per profile", "views", _sum("view_count")),
    "replies_per_profile": ("Replies per profile", "replies", _sum("reply_count")),
    "hashtags": ("Top hashtags", "tweets", _count(lambda t: [h.lower() for h in t.get("hashtags") or []])),
    "tweet_type": ("Tweet types", "tweets", _count(lambda t: [_tweet_type(t)])),
    "media_type": ("Media types", "attachments", _count(_media_types)),
    "posts_by_date": ("Tweets by date", "tweets", _count(lambda t: [t.get("created_at") or UNKNOWN])),
}
TEXT_METRICS = {
    "top_terms": "Most frequent terms",
    "top_pairs": "Terms that appear together",
    "word_ngrams": "Word n-grams",
    "char_ngrams": "Character n-grams",
}
LINKS_AND_MENTIONS = re.compile(r"https?://\S+|@\w+")
CHOICES = {**{key: spec[0] for key, spec in METRICS.items()}, "most_liked": "Most liked tweets", **TEXT_METRICS}


def _tweets(database: str, collection: str, username: str, client=None, metric: str = "") -> Iterable[dict]:
    target = (client or get_client())[database][collection]
    query = {"$or": [{AUTHOR_PATH: username}, {"username": username}]} if username else {}
    if metric.startswith(FIELD_PREFIX):
        return target.find(query, {metric[len(FIELD_PREFIX):]: 1})
    projection = {AUTHOR_PATH: 1, "username": 1, "metrics": 1, "hashtags": 1, "media.type": 1,
                  "is_reply": 1, "created_at": 1, "text": 1}
    return target.find(query, projection)


def _result(title: str, unit: str, items: List[Tuple[str, int]], total: int, **extra) -> dict:
    return {"title": title, "unit": unit, "tweets": total,
            "items": [{"label": str(label), "value": value} for label, value in items], **extra}


def _scoped(title: str, username: str) -> str:
    return f"{title} of @{username}" if username else title


def _sum_metric(metric: str, tweets: List[dict], top: int, scope: str) -> dict:
    title, unit, contribution = METRICS[metric]
    totals: Counter = Counter()
    for tweet in tweets:
        for label, amount in contribution(tweet):
            totals[label] += amount
    return _result(_scoped(title, scope), unit, totals.most_common(top), len(tweets))


def _most_liked(tweets: List[dict], top: int, scope: str) -> dict:
    likes = _metric("favorite_count")
    ranked = sorted(tweets, key=likes, reverse=True)[:top]
    items = [(f"@{_author(t)}: {(t.get('text') or '')[:90]}", likes(t)) for t in ranked]
    return _result(_scoped(CHOICES["most_liked"], scope), "likes", items, len(tweets))


def _ngram_metric(metric: str, tweets: List[dict], top: int, scope: str, n: int) -> dict:
    count = ngrams if metric == "word_ngrams" else char_ngrams
    totals: Counter = Counter()
    for tweet in tweets:
        totals.update(count(LINKS_AND_MENTIONS.sub(" ", (tweet.get("text") or "").lower()), n))
    return _result(_scoped(f"{CHOICES[metric]} (n={n})", scope), "occurrences", totals.most_common(top), len(tweets))


def _term_metric(metric: str, tweets: List[dict], top: int, scope: str) -> dict:
    texts = [tweet.get("text") or "" for tweet in tweets]
    title = _scoped(CHOICES[metric], scope)
    if metric == "top_pairs":
        pairs = count_pairs(texts, "", top, top)["pairs"]
        return _result(title, "tweets", [(" + ".join(pair), count) for pair, count in pairs], len(tweets))
    return _result(title, "occurrences", count_terms(texts, top)["terms"], len(tweets))


def _as_list(node) -> list:
    return node if isinstance(node, list) else [node]


def _values(document: dict, path: str) -> List[str]:
    """The scalar values at a dotted path; lists are flattened and missing paths give nothing."""
    found = [document]
    for part in path.split("."):
        found = [node[part] for item in found for node in _as_list(item)
                 if isinstance(node, dict) and node.get(part) is not None]
    return [str(node) for item in found for node in _as_list(item) if isinstance(node, (str, int, float, bool))]


def _field_metric(path: str, documents: List[dict], top: int, scope: str) -> dict:
    totals: Counter = Counter()
    for document in documents:
        totals.update(_values(document, path))
    return _result(_scoped(f"Values of {path}", scope), "documents", totals.most_common(top), len(documents))


def analyze(metric: str, top: int, username: str = "", n: int = 2, database: str = DEFAULT_DATABASE,
            collection: str = DEFAULT_COLLECTION, client=None) -> dict:
    """Returns {title, unit, tweets, description, items:[{label, value}]} for one metric, optionally for one profile."""
    result = _compute(metric, top, username, n, database, collection, client)
    return {**result, "description": describe(metric)}


def _compute(metric: str, top: int, username: str, n: int, database: str, collection: str, client) -> dict:
    is_field = metric.startswith(FIELD_PREFIX)
    if metric not in CHOICES and not is_field:
        raise ValueError(f"Unknown metric {metric}")
    tweets = list(_tweets(database, collection, username, client, metric))
    if is_field:
        return _field_metric(metric[len(FIELD_PREFIX):], tweets, top, username)
    if metric in METRICS:
        return _sum_metric(metric, tweets, top, username)
    if metric == "most_liked":
        return _most_liked(tweets, top, username)
    if metric in ("word_ngrams", "char_ngrams"):
        return _ngram_metric(metric, tweets, top, username, n)
    return _term_metric(metric, tweets, top, username)


DESCRIPTIONS = {
    "tweets_per_profile": "How many tweets each profile has in this collection.",
    "likes_per_profile": "Total likes of each profile's tweets.",
    "retweets_per_profile": "Total retweets of each profile's tweets.",
    "views_per_profile": "Total views of each profile's tweets.",
    "replies_per_profile": "Total replies to each profile's tweets.",
    "most_liked": "The individual tweets with the most likes.",
    "hashtags": "The hashtags used most often (each tweet counts once per hashtag).",
    "top_terms": "The words used most often in the tweet texts (common stop words are ignored).",
    "top_pairs": "Pairs of words that appear together in the same tweet most often.",
    "word_ngrams": "The most common sequences of n consecutive words (n=2 gives word pairs).",
    "char_ngrams": "The most common sequences of n consecutive characters (n=3 gives trigrams).",
    "tweet_type": "How many tweets are text only, have media (photo, video), or are replies.",
    "media_type": "How many photos, videos and other attachments the tweets contain.",
    "posts_by_date": "How many tweets were posted on each date.",
}
LABELS = {**{key: spec[0] for key, spec in METRICS.items()}, "most_liked": "Most liked tweets",
          "top_terms": "Most frequent terms", "top_pairs": "Terms that appear together",
          "word_ngrams": "Word n-grams", "char_ngrams": "Character n-grams"}
TWEET_GROUP = "Tweet analyses"
FIELD_GROUP = "Fields of this collection"
AUTHOR_PATHS = (AUTHOR_PATH, "username")
SUMS = {"likes_per_profile": "metrics.favorite_count", "retweets_per_profile": "metrics.retweet_count",
        "views_per_profile": "metrics.view_count", "replies_per_profile": "metrics.reply_count"}
REQUIRES = {"hashtags": "hashtags", "media_type": "media", "posts_by_date": "created_at", "tweet_type": "created_at",
            "top_terms": "text", "top_pairs": "text", "word_ngrams": "text", "char_ngrams": "text"}


def describe(metric: str) -> str:
    if metric.startswith(FIELD_PREFIX):
        return (f"How many documents have each value of the field '{metric[len(FIELD_PREFIX):]}'. "
                "Arrays are counted value by value.")
    return DESCRIPTIONS.get(metric, "")


def _paths(document: dict, prefix: str = "", depth: int = 0) -> Iterable[Tuple[str, List[str]]]:
    for key, value in document.items():
        path = f"{prefix}{key}"
        if isinstance(value, dict) and depth < 2:
            yield from _paths(value, path + ".", depth + 1)
        elif isinstance(value, (str, int, float, bool)) or (
                isinstance(value, list) and value and all(isinstance(v, (str, int, float, bool)) for v in value)):
            yield path, [str(v) for v in _as_list(value)]


def _field_candidates(documents: List[dict]) -> List[str]:
    """Fields with few distinct short values, which make a readable chart."""
    seen: Dict[str, List[str]] = {}
    for document in documents:
        for path, values in _paths(document):
            seen.setdefault(path, []).extend(values)
    fields = []
    for path, values in seen.items():
        distinct = len(set(values))
        too_varied = len(documents) > 20 and distinct > len(documents) / 2
        too_long = sum(len(v) for v in values) / len(values) > LONG_TEXT
        if path != "_id" and distinct > 1 and not too_varied and not too_long:
            fields.append(path)
    return sorted(fields)[:MAX_FIELDS]


def available_metrics(database: str = DEFAULT_DATABASE, collection: str = DEFAULT_COLLECTION,
                      client=None) -> List[dict]:
    """The analyses that make sense for this collection, worked out from a sample of its documents."""
    target = (client or get_client())[database][collection]
    documents = list(target.find({}).limit(SAMPLE_SIZE))
    keys = {key for document in documents for key in document}
    paths = {path for document in documents for path, _ in _paths(document)}
    metrics = []

    def add(key: str, label: str, description: str, group: str) -> None:
        metrics.append({"key": key, "label": label, "description": description, "group": group})

    if paths & set(AUTHOR_PATHS):
        add("tweets_per_profile", LABELS["tweets_per_profile"], DESCRIPTIONS["tweets_per_profile"], TWEET_GROUP)
    for key, path in SUMS.items():
        if path in paths:
            add(key, LABELS[key], DESCRIPTIONS[key], TWEET_GROUP)
    if "metrics.favorite_count" in paths and "text" in keys:
        add("most_liked", LABELS["most_liked"], DESCRIPTIONS["most_liked"], TWEET_GROUP)
    for key, needed in REQUIRES.items():
        if needed in keys:
            add(key, LABELS[key], DESCRIPTIONS[key], TWEET_GROUP)
    for path in _field_candidates(documents):
        add(FIELD_PREFIX + path, f"Values of {path}", describe(FIELD_PREFIX + path), FIELD_GROUP)
    return metrics


def tweet_authors(database: str = DEFAULT_DATABASE, collection: str = DEFAULT_COLLECTION,
                  client=None) -> List[str]:
    target = (client or get_client())[database][collection]
    rows = target.aggregate([{"$group": {"_id": {"$ifNull": ["$user.username", "$username"]}}}, {"$sort": {"_id": 1}}])
    return [row["_id"] for row in rows if isinstance(row["_id"], str) and row["_id"]]


DEFAULT_TEXT_FIELD = "text"
TEXT_LENGTH = 20


def _documents(database: str, collection: str, fields: List[str], client=None) -> Iterable[dict]:
    target = (client or get_client())[database][collection]
    projection = {field: 1 for field in [*fields, *AUTHOR_PATHS] if field}
    return target.find({}, projection)


def collection_fields(database: str = DEFAULT_DATABASE, collection: str = DEFAULT_COLLECTION, client=None) -> dict:
    """Fields of a collection that can be analysed as text, and fields that can label (classify) its documents."""
    documents = list(((client or get_client())[database][collection]).find({}).limit(SAMPLE_SIZE))
    lengths: Dict[str, List[int]] = {}
    for document in documents:
        for path, values in _paths(document):
            lengths.setdefault(path, []).extend(len(value) for value in values)
    texts = [path for path, sizes in lengths.items() if sum(sizes) / len(sizes) >= TEXT_LENGTH]
    labels = _field_candidates(documents)
    labels.sort(key=lambda path: (path not in AUTHOR_PATHS, path))
    return {"text": sorted(texts, key=lambda path: (path != DEFAULT_TEXT_FIELD, path)), "labels": labels}


def labelled_texts(database: str = DEFAULT_DATABASE, collection: str = DEFAULT_COLLECTION, client=None,
                   text_field: str = DEFAULT_TEXT_FIELD, label_field: str = ""):
    """Returns (texts, labels): the text of every document with its label, which is the value of label_field
    (by default the profile that wrote the tweet)."""
    texts, labels = [], []
    for document in _documents(database, collection, [text_field, label_field], client):
        text = LINKS_AND_MENTIONS.sub(" ", " ".join(_values(document, text_field))).strip()
        label = (_values(document, label_field) or [UNKNOWN])[0] if label_field else _author(document)
        if text:
            texts.append(text)
            labels.append(label)
    return texts, labels


def collection_texts(database: str, collection: str, text_field: str, client=None) -> List[str]:
    return [" ".join(_values(document, text_field)) for document in
            _documents(database, collection, [text_field], client)]
