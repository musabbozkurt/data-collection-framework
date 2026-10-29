"""X profile scraper: opens a profile in a Playwright browser and captures the GraphQL JSON that the X web app
itself loads (instead of parsing HTML). Supports a reusable login session, checkpoints/resume, JSON/CSV export,
an optional proxy and a quick engagement summary.

Use only with your own account and in line with X's terms; scrolling is deliberately slow and no
bot-detection evasion is attempted.

    python x_profile_scraper.py login                 # sign in once in a visible browser, session is saved
    python x_profile_scraper.py user NASA --max 100   # scrape; add --resume to continue a previous run
"""
import argparse
import asyncio
import csv
import html as htmllib
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from data_collection_framework.storage.mongo import AUTHOR_PATH

DATA_DIR = Path(os.environ.get("X_PROFILE_DATA_DIR") or Path(__file__).resolve().parent / "x_profile_data")
SESSION_FILE = Path(os.environ.get("X_SESSION_FILE") or DATA_DIR / "x_session.json")
MONGO_DATABASE, MONGO_COLLECTION = "x_profile_db", "profile_tweets"
PROXY_SCHEME = "http"  # proxies given as host:port are plain forward proxies
USERNAME_PATTERN = re.compile(r"(?a)\w{1,15}")
GRAPHQL_MARKERS = ("UserTweets", "UserByScreenName", "TweetDetail", "TweetResultByRestId")
CSV_FIELDS = ("id", "created_at", "username", "text", "retweet_count", "favorite_count", "reply_count",
              "quote_count", "view_count", "hashtags", "is_reply", "media_urls")


def dig(data: Any, *path: str) -> Any:
    """Safe nested lookup: returns None as soon as a key is missing or a value is not a dict."""
    for key in path:
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    return data


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _media(legacy: Dict) -> List[Dict]:
    items = []
    for item in dig(legacy, "extended_entities", "media") or []:
        entry = {"type": item.get("type", ""), "url": item.get("media_url_https", "")}
        variants = [v for v in dig(item, "video_info", "variants") or [] if v.get("content_type") == "video/mp4"]
        if variants:
            entry["video_url"] = max(variants, key=lambda v: v.get("bitrate", 0))["url"]
        items.append(entry)
    return items


def extract_tweet(result: Dict) -> Optional[Dict]:
    """Turns one GraphQL tweet result into a flat, defensive dict; returns None when it has no usable id."""
    if not isinstance(result, dict):
        return None
    if result.get("__typename") == "TweetWithVisibilityResults":
        result = result.get("tweet") or {}
    legacy = result.get("legacy") or {}
    tweet_id = result.get("rest_id")
    if not tweet_id:
        return None
    user = dig(result, "core", "user_results", "result") or {}
    user_legacy = user.get("legacy") or {}
    user_core = user.get("core") or {}
    return {
        "id": str(tweet_id),
        "text": legacy.get("full_text", ""),
        "created_at": legacy.get("created_at", ""),
        "user": {
            "username": user_legacy.get("screen_name") or user_core.get("screen_name", ""),
            "display_name": user_legacy.get("name") or user_core.get("name", ""),
            "followers_count": user_legacy.get("followers_count", 0),
            "verified": bool(user.get("is_blue_verified", False)),
        },
        "metrics": {
            "retweet_count": legacy.get("retweet_count", 0),
            "favorite_count": legacy.get("favorite_count", 0),
            "reply_count": legacy.get("reply_count", 0),
            "quote_count": legacy.get("quote_count", 0),
            "view_count": _to_int(dig(result, "views", "count")),
        },
        "hashtags": [tag.get("text", "") for tag in dig(legacy, "entities", "hashtags") or []],
        "media": _media(legacy),
        "is_reply": legacy.get("in_reply_to_status_id_str") is not None,
        "scraped_at": time.time(),
    }


def _timeline_instructions(data: Dict) -> List[Dict]:
    result = dig(data, "data", "user", "result") or {}
    for key in ("timeline", "timeline_v2"):
        instructions = dig(result, key, "timeline", "instructions")
        if instructions:
            return instructions
    return []


def parse_timeline(data: Dict) -> List[Dict]:
    """Extracts the tweets (pinned and regular) from a UserTweets response."""
    entries = []
    for instruction in _timeline_instructions(data):
        if instruction.get("type") == "TimelineAddEntries":
            entries.extend(instruction.get("entries") or [])
        elif instruction.get("type") == "TimelinePinEntry" and instruction.get("entry"):
            entries.append(instruction["entry"])
    tweets = []
    for entry in entries:
        if str(entry.get("entryId", "")).startswith("tweet-"):
            tweet = extract_tweet(dig(entry, "content", "itemContent", "tweet_results", "result"))
            if tweet:
                tweets.append(tweet)
    return tweets


def parse_profile(data: Dict) -> Optional[Dict]:
    """Extracts the account details from a UserByScreenName response."""
    user = dig(data, "data", "user", "result")
    if not user:
        return None
    legacy = user.get("legacy") or {}
    return {
        "id": user.get("rest_id", ""),
        "username": legacy.get("screen_name", ""),
        "name": legacy.get("name", ""),
        "followers_count": legacy.get("followers_count", 0),
        "friends_count": legacy.get("friends_count", 0),
        "statuses_count": legacy.get("statuses_count", 0),
        "description": legacy.get("description", ""),
        "location": legacy.get("location", ""),
        "created_at": legacy.get("created_at", ""),
        "verified": bool(user.get("is_blue_verified", False)),
    }


def merge_tweets(existing: Iterable[Dict], new: Iterable[Dict]) -> List[Dict]:
    """Merges by id (newer data wins) and sorts newest first; X ids grow with time."""
    merged = {tweet["id"]: tweet for tweet in existing}
    merged.update({tweet["id"]: tweet for tweet in new})
    return sorted(merged.values(), key=lambda tweet: int(tweet["id"]), reverse=True)


def summarize(tweets: List[Dict], top_hashtags: int = 5) -> Dict:
    """Quick engagement statistics over a list of tweets."""
    if not tweets:
        return {"tweets": 0}
    likes = [_to_int(t["metrics"]["favorite_count"]) for t in tweets]
    best = max(tweets, key=lambda t: _to_int(t["metrics"]["favorite_count"]))
    tags = Counter(tag.lower() for t in tweets for tag in t["hashtags"])
    return {
        "tweets": len(tweets),
        "total_likes": sum(likes),
        "average_likes": round(sum(likes) / len(likes), 1),
        "total_retweets": sum(_to_int(t["metrics"]["retweet_count"]) for t in tweets),
        "total_views": sum(_to_int(t["metrics"]["view_count"]) for t in tweets),
        "replies": sum(1 for t in tweets if t["is_reply"]),
        "with_media": sum(1 for t in tweets if t["media"]),
        "top_hashtags": tags.most_common(top_hashtags),
        "most_liked": {"id": best["id"], "likes": _to_int(best["metrics"]["favorite_count"]),
                       "text": best["text"][:140]},
    }


def parse_proxy(value: str) -> Optional[Dict]:
    """'host:port' or 'host:port:user:password' -> Playwright proxy settings."""
    parts = value.strip().split(":") if value else []
    if len(parts) not in (2, 4):
        return None
    proxy = {"server": f"{PROXY_SCHEME}://{parts[0]}:{parts[1]}"}
    if len(parts) == 4:
        proxy.update(username=parts[2], password=parts[3])
    return proxy


READER_URL = "https://r.jina.ai/https://x.com/"
TWEET_LINE = re.compile(r"^\*\s+\[\]\(https://x\.com/(\w+)/status/(\d+)\)(.*)$")
COUNTS = re.compile(r"\[([\d.,]{1,12}[KMB]?)\]\(https://x\.com/compose/post\?in_reply_to=\d{1,25}\)\s{1,5}"
                    r"([\d.,]{1,12}[KMB]?)\s{1,5}([\d.,]{1,12}[KMB]?)\s{1,5}([\d.,]{1,12}[KMB]?)")
UNITS = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}


def parse_count(text: str) -> int:
    """'1.3M' -> 1300000, '7,8K' -> 7800, '12' -> 12."""
    text = text.strip().upper().replace(",", ".")
    try:
        return int(float(text[:-1]) * UNITS[text[-1]]) if text[-1:] in UNITS else int(float(text))
    except ValueError:
        return 0


def _clean_text(body: str) -> str:
    cut = [i for i in (body.find("![Image"), body.find("[Video"), body.find("[](https://x.com/"),
                       body.find("[](https://pbs.twimg"), body.find("Show more")) if i >= 0]
    counts = COUNTS.search(body)
    if counts:
        cut.append(counts.start())
    body = body[:min(cut)] if cut else body
    body = re.sub(r"\[([^\]]{0,500})\]\([^)]{0,500}\)", r"\1", body)
    return re.sub(r"\s+", " ", body).strip()


def parse_reader_markdown(markdown: str, username: str) -> List[Dict]:
    """Extracts tweets from the logged-out page text produced by the Jina Reader (no login needed)."""
    tweets = []
    for line in markdown.splitlines():
        match = TWEET_LINE.match(line)
        if not match:
            continue
        author, tweet_id, body = match.groups()
        # drop the avatar, author name, handle and the dated link, keep what follows
        dated = re.search(rf"\[@{re.escape(author)}\]\(https://x\.com/{re.escape(author)}\)\s{{1,5}}"
                          rf"\[([^\]]{{1,100}})\]\(https://x\.com/{re.escape(author)}/status/{tweet_id}\)", body, re.I)
        created = dated.group(1) if dated else ""
        content = body[dated.end():] if dated else body
        counts = COUNTS.search(content)
        replies, reposts, likes, views = (parse_count(g) for g in counts.groups()) if counts else (0, 0, 0, 0)
        text = _clean_text(content)
        tweets.append({
            "id": tweet_id, "text": text, "created_at": created,
            "user": {"username": author, "display_name": "", "followers_count": 0, "verified": False},
            "metrics": {"retweet_count": reposts, "favorite_count": likes, "reply_count": replies,
                        "quote_count": 0, "view_count": views},
            "hashtags": re.findall(r"\[#(\w+)\]", content),
            "media": [{"type": "photo", "url": u} for u in
                      re.findall(r"\((https://pbs\.twimg\.com/media/[^)\s]+)\)", content)],
            "is_reply": False, "scraped_at": time.time(),
        })
    return tweets


ARTICLE = re.compile(r"<article.*?</article>", re.S)
AUTO_DIV = re.compile(r'<div class="([^"]*)" dir="auto">(.*?)</div>', re.S)
ENGAGEMENT_TOKEN = re.compile(r'data-engagement-action="(reply|retweet|like|generic)"|<span ([^>]*)>([^<]+)</span>')


def _engagement(article: str) -> Dict[str, int]:
    """Counts shown next to the reply/retweet/like icons: the first left-to-right span after each icon."""
    counts: Dict[str, int] = {}
    kind = None
    for action, attributes, value in ENGAGEMENT_TOKEN.findall(article):
        if action:
            kind = action
        elif kind and 'dir="ltr"' in attributes:
            counts[kind] = parse_count(value)
            kind = None
    return counts


def _post_html(article: str) -> str:
    """Inner HTML of the first div that holds the post text."""
    for classes, inner in AUTO_DIV.findall(article):
        if "whitespace-pre-wrap" in classes:
            return inner
    return ""


def parse_reader_html(markup: str) -> List[Dict]:
    """Extracts tweets from the logged-out page HTML (more complete than the text version: every post has an id)."""
    tweets = []
    for article in ARTICLE.findall(markup):
        stamp = re.search(r'"timestamp":(\d+)', article)
        article = re.sub(r"<svg.*?</svg>|<script.*?</script>", "", article, flags=re.S)
        link = re.search(r'href="/(\w+)/status/(\d+)"', article)
        if not link:
            continue
        author, tweet_id = link.groups()
        text = htmllib.unescape(re.sub(r"<[^>]+>", "", _post_html(article)))
        counts = _engagement(article)
        tweets.append({
            "id": tweet_id, "text": re.sub(r"\s+", " ", text).strip(),
            "created_at": datetime.fromtimestamp(int(stamp.group(1)) / 1000).isoformat(
                timespec="seconds") if stamp else "",
            "user": {"username": author, "display_name": "", "followers_count": 0, "verified": False},
            "metrics": {"retweet_count": counts.get("retweet", 0), "favorite_count": counts.get("like", 0),
                        "reply_count": counts.get("reply", 0), "quote_count": 0,
                        "view_count": counts.get("generic", 0)},
            "hashtags": re.findall(r'href="/hashtag/[^"]*"[^>]*>#?([^<]+)<', article),
            "media": [{"type": "photo", "url": u} for u in dict.fromkeys(
                htmllib.unescape(u) for u in
                re.findall(r'src="(https://pbs\.twimg\.com/(?:media|card_img)/[^"]+)"', article))],
            "is_reply": False, "scraped_at": time.time(),
        })
    return tweets


def parse_reader_profile(markdown: str) -> Optional[Dict]:
    """Name, bio counts from the profile header of the Reader output."""
    title = re.search(r"^Title:[ \t]*([^\n]{1,200})\(@(\w{1,15})\)", markdown, re.M)
    if not title:
        return None
    followers = re.search(r"\[([\d.,]{1,12}[KMB]?) Followers\]", markdown)
    following = re.search(r"\[([\d.,]{1,12}[KMB]?) Following\]", markdown)
    posts = re.search(r"^([\d.,]{1,12}[KMB]?) posts", markdown, re.M)
    return {"name": title.group(1).strip(), "username": title.group(2),
            "followers_count": parse_count(followers.group(1)) if followers else None,
            "friends_count": parse_count(following.group(1)) if following else None,
            "statuses_count": parse_count(posts.group(1)) if posts else None}


def fetch_reader(username: str, timeout: int = 60, html: bool = True) -> str:
    """Public page without any X login (a third-party reader renders it); HTML by default, text if html=False."""
    import requests
    headers = {"User-Agent": "Mozilla/5.0"}
    if html:
        headers["X-Return-Format"] = "html"
    response = requests.get(READER_URL + username, timeout=timeout, headers=headers)
    response.raise_for_status()
    return response.text


class ProfileStore:
    """Keeps one directory per profile with tweets.json, checkpoint.json and a CSV export."""

    def __init__(self, username: str, base: Path = DATA_DIR):
        if not USERNAME_PATTERN.fullmatch(username):
            raise ValueError("invalid username")
        self.directory = base / username.lower()
        self.tweets_file = self.directory / "tweets.json"
        self.checkpoint_file = self.directory / "checkpoint.json"
        self.csv_file = self.directory / "tweets.csv"

    def load_tweets(self) -> List[Dict]:
        if not self.tweets_file.exists():
            return []
        return json.loads(self.tweets_file.read_text(encoding="utf-8"))

    def load_checkpoint(self) -> Dict:
        if not self.checkpoint_file.exists():
            return {}
        return json.loads(self.checkpoint_file.read_text(encoding="utf-8"))

    def save(self, tweets: List[Dict], profile: Optional[Dict], new_count: int) -> Dict:
        """Writes the tweets, CSV and checkpoint (oldest/newest ids, session count)."""
        self.directory.mkdir(parents=True, exist_ok=True)
        previous = self.load_checkpoint()
        checkpoint = {
            "username": self.directory.name,
            "total_tweets": len(tweets),
            "newest_tweet_id": tweets[0]["id"] if tweets else None,
            "oldest_tweet_id": tweets[-1]["id"] if tweets else None,
            "oldest_tweet_date": tweets[-1]["created_at"] if tweets else None,
            "session_count": previous.get("session_count", 0) + 1,
            "last_session_tweets": new_count,
            "profile": profile or previous.get("profile"),
            "last_updated": datetime.now().isoformat(timespec="seconds"),
        }
        self.tweets_file.write_text(json.dumps(tweets, indent=2, ensure_ascii=False), encoding="utf-8")
        self.checkpoint_file.write_text(json.dumps(checkpoint, indent=2, ensure_ascii=False), encoding="utf-8")
        self._write_csv(tweets)
        return checkpoint

    def _write_csv(self, tweets: List[Dict]) -> None:
        with self.csv_file.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
            writer.writeheader()
            for tweet in tweets:
                writer.writerow({
                    "id": tweet["id"], "created_at": tweet["created_at"], "username": tweet["user"]["username"],
                    "text": tweet["text"], **{k: tweet["metrics"][k] for k in (
                        "retweet_count", "favorite_count", "reply_count", "quote_count", "view_count")},
                    "hashtags": " ".join(tweet["hashtags"]), "is_reply": tweet["is_reply"],
                    "media_urls": " ".join(m["url"] for m in tweet["media"]),
                })


class ProfileScraper:
    """Drives the browser: loads the profile, listens to GraphQL responses and scrolls the timeline."""

    def __init__(self, username: str, max_tweets: int = 50, headless: bool = True, scroll_delay: float = 3.0,
                 patience: int = 8, proxy: Optional[Dict] = None, session_file: Path = SESSION_FILE,
                 base_url: str = "https://x.com"):
        self.username = username
        self.max_tweets = max_tweets
        self.headless = headless
        self.scroll_delay = scroll_delay
        self.patience = patience
        self.proxy = proxy
        self.session_file = session_file
        self.base_url = base_url
        self.seen: Dict[str, Dict] = {}
        self.profile: Optional[Dict] = None

    async def _on_response(self, response) -> None:
        url = response.url
        if response.request.resource_type not in ("xhr", "fetch") or not any(m in url for m in GRAPHQL_MARKERS):
            return
        try:
            data = await response.json()
        except Exception:  # not JSON or the page navigated away; skip this response
            return
        if "UserTweets" in url:
            for tweet in parse_timeline(data):
                self.seen.setdefault(tweet["id"], tweet)
        elif "UserByScreenName" in url:
            self.profile = parse_profile(data) or self.profile

    async def run(self, known_ids: Iterable[str] = ()) -> Dict:
        """Scrolls until max_tweets new tweets were captured or nothing was seen for `patience` scrolls."""
        from playwright.async_api import async_playwright
        known = set(known_ids)
        async with async_playwright() as playwright:
            options: Dict[str, Any] = {"headless": self.headless}
            if os.environ.get("IN_DOCKER"):
                options["args"] = ["--no-sandbox"]  # the container user cannot create Chromium's own sandbox
            if self.proxy:
                options["proxy"] = self.proxy
            browser = await playwright.chromium.launch(**options)
            try:
                state = str(self.session_file) if self.session_file.exists() else None
                context = await browser.new_context(storage_state=state, viewport={"width": 1280, "height": 900})
                page = await context.new_page()
                page.on("response", self._on_response)
                await page.goto(f"{self.base_url}/{self.username}", wait_until="domcontentloaded")
                await self._scroll(page, known)
            finally:
                await browser.close()
        return {"tweets": list(self.seen.values()), "profile": self.profile,
                "new": [t for t in self.seen.values() if t["id"] not in known]}

    async def _scroll(self, page, known: set) -> None:
        idle = 0
        await asyncio.sleep(self.scroll_delay)
        while idle < self.patience:
            before = len(self.seen)
            if sum(1 for i in self.seen if i not in known) >= self.max_tweets:
                break
            await page.evaluate("window.scrollBy(0, window.innerHeight * 0.8)")
            await asyncio.sleep(self.scroll_delay)
            idle = 0 if len(self.seen) > before else idle + 1


def scrape(username: str, max_tweets: int = 50, resume: bool = False, headless: bool = True,
           scroll_delay: float = 3.0, patience: int = 8, store: Optional[ProfileStore] = None,
           mongo_uri: Optional[str] = None) -> str:
    """Scrapes one profile, merges with earlier sessions, saves files (and MongoDB) and returns a text report."""
    store = store or ProfileStore(username)
    existing = store.load_tweets() if resume else []
    known = {t["id"] for t in existing}
    if SESSION_FILE.exists():
        scraper = ProfileScraper(username, max_tweets, headless, scroll_delay, patience,
                                 proxy=parse_proxy(os.environ.get("X_PROXY", "")))
        try:
            result = asyncio.run(scraper.run(known_ids=known))
        except ImportError as error:
            raise RuntimeError("Playwright is not installed. Run 'make setup' and 'make browsers'.") from error
        except Exception as error:
            if "Executable doesn't exist" in str(error):
                raise RuntimeError("The Playwright browser is missing. Run 'make browsers'.") from error
            raise
    else:
        markdown = fetch_reader(username, html=False)
        found = parse_reader_html(fetch_reader(username)) or parse_reader_markdown(markdown, username)
        result = {"tweets": found, "profile": parse_reader_profile(markdown),
                  "new": [t for t in found if t["id"] not in known],
                  "note": f"Requested {max_tweets}, but X only shows the newest {len(found)} posts to visitors who are "
                          "not signed in. Fetching more needs a saved X login session (make x-login)."}

    if not result["tweets"]:
        raise RuntimeError(f"No posts found for @{username}. Check that the username exists and is spelled correctly "
                           "(private or empty accounts show no posts without a login).")
    tweets = merge_tweets(existing, result["tweets"])
    checkpoint = store.save(tweets, result["profile"], len(result["new"]))
    stored = _save_to_mongo(result["new"], mongo_uri) if mongo_uri else None
    return _report(username, result, tweets, checkpoint, store, stored, max_tweets)


def _save_to_mongo(tweets: List[Dict], mongo_uri: str) -> Optional[int]:
    from pymongo import MongoClient
    try:
        with MongoClient(mongo_uri, serverSelectionTimeoutMS=5000) as client:
            collection = client[MONGO_DATABASE][MONGO_COLLECTION]
            collection.create_index(AUTHOR_PATH)
            for tweet in tweets:
                collection.update_one({"_id": tweet["id"]}, {"$set": tweet}, upsert=True)
        return len(tweets)
    except Exception as error:  # the files are already saved, so MongoDB trouble is only reported
        print(f"⚠️ Could not save to MongoDB: {error}")
        return None


def _report(username: str, result: Dict, tweets: List[Dict], checkpoint: Dict, store: ProfileStore,
            stored: Optional[int], max_tweets: int = 0) -> str:
    stats = summarize(tweets)
    profile = result["profile"] or checkpoint.get("profile") or {}
    lines = [
        f"@{username}: {len(result['new'])} new tweets, {len(tweets)} in total (session {checkpoint['session_count']})"]
    if profile:
        details = [f"{profile[key]} {label}" for key, label in (("followers_count", "followers"),
                                                                ("statuses_count", "posts")) if
                   profile.get(key) is not None]
        lines.append(f"Profile: {profile.get('name')}" + (" - " + ", ".join(details) if details else ""))
    lines.append(f"Likes: {stats['total_likes']} (avg {stats['average_likes']}), retweets: {stats['total_retweets']}, "
                 f"views: {stats['total_views']}, replies: {stats['replies']}, with media: {stats['with_media']}")
    if stats["top_hashtags"]:
        lines.append("Top hashtags: " + ", ".join(f"#{tag} ({count})" for tag, count in stats["top_hashtags"]))
    lines.append(f"Most liked ({stats['most_liked']['likes']}): {stats['most_liked']['text']}")
    if result.get("note") and len(result["tweets"]) < max_tweets:
        lines.append(f"Note: {result['note']}")
    lines.append(f"Saved to {store.directory}")
    if stored is not None:
        lines.append(f"MongoDB: {stored} tweets upserted into {MONGO_DATABASE}.{MONGO_COLLECTION}")
    return "\n".join(lines)


YANDEX_PATHS = (
    "/Applications/Yandex.app/Contents/MacOS/Yandex",
    "/usr/bin/yandex-browser",
    os.path.expandvars(r"%LOCALAPPDATA%\Yandex\YandexBrowser\Application\browser.exe"),
)


def browser_options(browser: str) -> Dict[str, Any]:
    """Launch options for the visitor's own browser (edge, chrome or yandex); anything else uses bundled Chromium."""
    if browser == "edge":
        return {"channel": "msedge"}
    if browser == "chrome":
        return {"channel": "chrome"}
    if browser == "yandex":
        path = next((p for p in YANDEX_PATHS if Path(p).exists()), None)
        if path:
            return {"executable_path": path}
    return {}


def has_session(session_file: Path = SESSION_FILE) -> bool:
    return session_file.exists()


def login(session_file: Path = SESSION_FILE, timeout: int = 300, browser: str = "") -> str:
    """Opens a visible browser window on this machine (the visitor's own browser when installed); once you finish
    signing in to X (any method) the session is saved."""
    from playwright.sync_api import sync_playwright
    session_file.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        options = browser_options(browser)
        try:
            window = playwright.chromium.launch(headless=False, **options)
        except Exception:  # that browser is not installed or not drivable: fall back to bundled Chromium
            window = playwright.chromium.launch(headless=False)
        try:
            context = window.new_context(viewport={"width": 1280, "height": 900})
            page = context.new_page()
            page.goto("https://x.com/login")
            deadline = time.time() + timeout
            while time.time() < deadline:
                if any(c["name"] == "auth_token" for c in context.cookies("https://x.com")):
                    page.wait_for_timeout(2000)  # let X finish setting its cookies
                    context.storage_state(path=str(session_file))
                    session_file.chmod(0o600)  # the file holds your login cookies
                    return f"X account connected. Session saved to {session_file}"
                if page.is_closed():
                    break
                page.wait_for_timeout(1000)
        except Exception as error:  # the window was closed while waiting
            if "closed" not in str(error).lower():
                raise
        finally:
            window.close()
    raise RuntimeError("X sign-in was not completed (window closed or 5 minutes passed). Try again.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape an X profile's tweets with Playwright.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("login", help="sign in once and save the session")
    user = commands.add_parser("user", help="scrape a profile")
    user.add_argument("username")
    user.add_argument("--max", type=int, default=50, help="new tweets to collect (default 50)")
    user.add_argument("--resume", action="store_true", help="keep earlier results and add new tweets")
    user.add_argument("--headed", action="store_true", help="show the browser window")
    user.add_argument("--delay", type=float, default=3.0, help="seconds between scrolls (default 3)")
    args = parser.parse_args()

    if args.command == "login":
        print(login())
        return
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from data_collection_framework.config.settings import get_settings
    print(scrape(args.username.lstrip("@"), args.max, args.resume, not args.headed, args.delay,
                 mongo_uri=get_settings().mongo_uri))


if __name__ == "__main__":
    main()
