"""Finds X usernames through web search (no X login or API), keeps them in MongoDB and lists them alphabetically.

Search engines return only a handful of profiles per query, so discovery asks several random two-letter prefixes
per letter. The result is best-effort and neither random nor complete.
"""
import random
import re
import string
import time
from datetime import datetime
from typing import Dict, Iterable, List, Optional
from urllib.parse import urlparse

DATABASE, COLLECTION = "x_profile_db", "discovered_profiles"
RANDOM = random.SystemRandom()  # only varies which search queries run; nothing depends on it
USERNAME = re.compile(r"(?a)\w{1,15}")
X_HOSTS = {"x.com", "www.x.com", "twitter.com", "www.twitter.com", "mobile.twitter.com"}
RESERVED = {"i", "home", "search", "explore", "hashtag", "intent", "share", "login", "signup", "settings", "messages",
            "notifications", "compose", "tos", "privacy", "about", "help", "jobs", "download", "status", "account",
            "personalization", "lists", "topics", "communities", "premium", "verified", "x", "twitter", "support"}
SEARCH_BACKENDS = ("yahoo", "google")  # the "duckduckgo" and "grokipedia" backends fail on macOS's LibreSSL
LETTERS = string.ascii_uppercase


def username_from_url(url: str) -> Optional[str]:
    """'https://x.com/Alice/status/1' -> 'Alice'; None for non-profile pages such as /i/trending or help.x.com."""
    parsed = urlparse(url)
    if parsed.hostname not in X_HOSTS:
        return None
    first = parsed.path.strip("/").split("/")[0]
    if not USERNAME.fullmatch(first) or first.lower() in RESERVED:
        return None
    return first


def extract_usernames(urls: Iterable[str], letter: Optional[str] = None) -> List[str]:
    """Unique usernames (case-insensitive) from result URLs, optionally only those starting with `letter`."""
    seen: Dict[str, str] = {}
    for url in urls:
        name = username_from_url(url)
        if name and (not letter or name[0].upper() == letter.upper()):
            seen.setdefault(name.lower(), name)
    return list(seen.values())


def mentions(result: Dict, words: Iterable[str]) -> bool:
    """True when the result's title or snippet contains any of the words (always True without words)."""
    words = [w.lower() for w in words]
    haystack = f"{result.get('title', '')} {result.get('body', '')}".lower()
    return not words or any(w in haystack for w in words)


def search_urls(query: str, max_results: int = 30, words: Iterable[str] = ()) -> List[str]:
    """Profile/post URLs for a search; with `words`, only results whose title or snippet mention one of them."""
    from ddgs import DDGS
    words = list(words)
    for backend in SEARCH_BACKENDS:
        try:
            results = DDGS().text(query, max_results=max_results, backend=backend)
        except Exception as error:  # a backend may be blocked or empty; try the next one
            print(f"⚠️ '{backend}' search failed for {query!r}: {str(error)[:80]}")
            continue
        urls = [r.get("href", "") for r in results if mentions(r, words)]
        if extract_usernames(urls):
            return urls
    return []


def discover_letter(letter: str, rounds: int = 4, pause: float = 1.0, keyword: str = "") -> List[str]:
    """Searches a few random two-letter prefixes of `letter` (optionally together with a topic keyword such as
    "Java developer") and returns the usernames found, shuffled."""
    letter = letter.upper()
    keyword = keyword.strip()
    pool = string.ascii_lowercase + string.digits
    prefixes = RANDOM.sample(pool, k=min(rounds * (2 if keyword else 1), len(pool)))
    topic_words = [w for w in re.split(r"\W+", keyword) if len(w) > 1]
    found: Dict[str, str] = {}
    for index, second in enumerate(prefixes):
        prefix = letter.lower() + second
        topic = f"{keyword} " if keyword else ""
        for query in (f'{topic}"Followers" "@{prefix}" site:x.com', f'{topic}"on X" "@{prefix}" site:x.com'):
            for name in extract_usernames(search_urls(query, words=topic_words), letter):
                found.setdefault(name.lower(), name)
        if index < len(prefixes) - 1:
            time.sleep(pause)  # fixed, polite gap between searches
    names = list(found.values())
    RANDOM.shuffle(names)
    return names


def _collection(mongo_uri: str):
    from pymongo import MongoClient
    return MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)


def store_usernames(names: Iterable[str], source: str, mongo_uri: str, keyword: str = "") -> Dict[str, int]:
    """Upserts usernames; returns {'found': n, 'new': n}. Existing entries keep their scrape history and only
    gain the keyword."""
    names = [n for n in dict.fromkeys(names) if USERNAME.fullmatch(n)]
    new = 0
    with _collection(mongo_uri) as client:
        collection = client[DATABASE][COLLECTION]
        for name in names:
            update = {"$addToSet": {"keywords": keyword.lower()}} if keyword else {}
            result = collection.update_one(
                {"_id": name.lower()},
                {**update, "$setOnInsert": {"username": name, "letter": name[0].upper(), "source": source,
                                            "added_at": datetime.now().isoformat(timespec="seconds"),
                                            "last_scraped_at": None, "tweets_scraped": 0}},
                upsert=True)
            new += 1 if result.upserted_id is not None else 0
    return {"found": len(names), "new": new}


def parse_username_list(raw: str) -> List[str]:
    """'@Alice, bob  carol' -> ['Alice', 'bob', 'carol']; raises ValueError on an invalid name."""
    names = [part.lstrip("@") for part in re.split(r"[\s,;]+", raw.strip()) if part]
    bad = [n for n in names if not USERNAME.fullmatch(n)]
    if bad or not names:
        raise ValueError(f"invalid username(s): {', '.join(bad) or 'none given'}")
    return names


def list_profiles(mongo_uri: str, letter: str = "", page: int = 1, page_size: int = 25, keyword: str = "") -> Dict:
    """One alphabetical page of stored profiles, optionally for a single letter and/or discovery keyword."""
    query: Dict = {"letter": letter.upper()} if letter and letter.upper() != "ALL" else {}
    if keyword:
        query["keywords"] = keyword.lower()
    with _collection(mongo_uri) as client:
        collection = client[DATABASE][COLLECTION]
        total = collection.count_documents(query)
        rows = list(collection.find(query).sort("_id", 1).skip((page - 1) * page_size).limit(page_size))
        letters = sorted(collection.distinct("letter"))
        keywords = sorted(collection.distinct("keywords"))
    return {"keywords": keywords, "total": total, "page": page, "page_size": page_size, "letters": letters,
            "profiles": [{k: row.get(k) for k in ("username", "letter", "source", "added_at", "last_scraped_at",
                                                  "tweets_scraped")} | {"keywords": row.get("keywords", [])} for row in
                         rows]}


def mark_scraped(username: str, tweets: int, mongo_uri: str) -> None:
    with _collection(mongo_uri) as client:
        client[DATABASE][COLLECTION].update_one(
            {"_id": username.lower()},
            {"$set": {"last_scraped_at": datetime.now().isoformat(timespec="seconds")},
             "$inc": {"tweets_scraped": tweets}})
