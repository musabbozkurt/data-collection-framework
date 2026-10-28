import pytest

from data_collection_framework.x_profile_scraper import (ProfileStore, extract_tweet, merge_tweets, parse_profile,
                                                         parse_proxy, parse_timeline, summarize)


def tweet_result(tweet_id="100", likes=5, tags=("Python",), reply=None):
    return {
        "__typename": "Tweet",
        "rest_id": tweet_id,
        "views": {"count": "1200"},
        "core": {"user_results": {"result": {"is_blue_verified": True, "legacy": {
            "screen_name": "nasa", "name": "NASA", "followers_count": 10}}}},
        "legacy": {
            "full_text": f"hello {tweet_id}", "created_at": "Wed Oct 15 11:16:01 +0000 2025",
            "retweet_count": 2, "favorite_count": likes, "reply_count": 1, "quote_count": 0,
            "in_reply_to_status_id_str": reply,
            "entities": {"hashtags": [{"text": tag} for tag in tags]},
            "extended_entities": {"media": [{"type": "video", "media_url_https": "https://img/1.jpg", "video_info": {
                "variants": [{"content_type": "video/mp4", "bitrate": 100, "url": "low"},
                             {"content_type": "video/mp4", "bitrate": 900, "url": "high"},
                             {"content_type": "application/x-mpegURL", "url": "m3u8"}]}}]},
        },
    }


def timeline(*results):
    entries = [{"entryId": f"tweet-{r['rest_id']}",
                "content": {"itemContent": {"tweet_results": {"result": r}}}} for r in results]
    entries.append({"entryId": "cursor-bottom-1", "content": {}})
    return {"data": {"user": {"result": {"timeline": {"timeline": {"instructions": [
        {"type": "TimelineClearCache"}, {"type": "TimelineAddEntries", "entries": entries}]}}}}}}


def test_extract_tweet_flattens_fields():
    tweet = extract_tweet(tweet_result(likes=7))
    assert tweet["id"] == "100"
    assert tweet["user"]["username"] == "nasa"
    assert tweet["metrics"]["favorite_count"] == 7
    assert tweet["metrics"]["view_count"] == 1200
    assert tweet["hashtags"] == ["Python"]
    assert tweet["media"][0]["video_url"] == "high"
    assert tweet["is_reply"] is False


def test_extract_tweet_unwraps_visibility_results_and_survives_missing_data():
    wrapped = {"__typename": "TweetWithVisibilityResults", "tweet": tweet_result("5")}
    assert extract_tweet(wrapped)["id"] == "5"
    assert extract_tweet({"rest_id": "9"})["text"] == ""
    assert extract_tweet({"legacy": {}}) is None
    assert extract_tweet(None) is None


def test_parse_timeline_skips_cursors_and_reads_pinned_entries():
    data = timeline(tweet_result("1"), tweet_result("2"))
    assert [t["id"] for t in parse_timeline(data)] == ["1", "2"]
    pinned = {"data": {"user": {"result": {"timeline_v2": {"timeline": {"instructions": [
        {"type": "TimelinePinEntry", "entry": {
            "entryId": "tweet-3", "content": {"itemContent": {"tweet_results": {"result": tweet_result("3")}}}}}]}}}}}}
    assert [t["id"] for t in parse_timeline(pinned)] == ["3"]
    assert parse_timeline({}) == []


def test_parse_profile():
    data = {"data": {"user": {"result": {"rest_id": "7", "is_blue_verified": True, "legacy": {
        "screen_name": "nasa", "name": "NASA", "followers_count": 5, "statuses_count": 9}}}}}
    profile = parse_profile(data)
    assert profile["username"] == "nasa"
    assert profile["followers_count"] == 5
    assert parse_profile({}) is None


def test_merge_tweets_dedupes_and_sorts_newest_first():
    old = [extract_tweet(tweet_result("10", likes=1)), extract_tweet(tweet_result("5"))]
    new = [extract_tweet(tweet_result("10", likes=99)), extract_tweet(tweet_result("20"))]
    merged = merge_tweets(old, new)
    assert [t["id"] for t in merged] == ["20", "10", "5"]
    assert merged[1]["metrics"]["favorite_count"] == 99


def test_summarize():
    tweets = [extract_tweet(tweet_result("1", likes=10, tags=("A", "b"))),
              extract_tweet(tweet_result("2", likes=30, tags=("a",), reply="1"))]
    stats = summarize(tweets)
    assert stats["total_likes"] == 40
    assert stats["average_likes"] == 20.0
    assert stats["replies"] == 1
    assert stats["top_hashtags"][0] == ("a", 2)
    assert stats["most_liked"]["id"] == "2"
    assert summarize([]) == {"tweets": 0}


def test_parse_proxy():
    assert parse_proxy("host:8080") == {"server": "http://host:8080"}
    assert parse_proxy("host:8080:me:secret") == {"server": "http://host:8080", "username": "me", "password": "secret"}
    assert parse_proxy("") is None
    assert parse_proxy("a:b:c") is None


def test_store_saves_checkpoint_and_csv(tmp_path):
    store = ProfileStore("NASA", tmp_path)
    tweets = merge_tweets([], [extract_tweet(tweet_result("1")), extract_tweet(tweet_result("2"))])
    first = store.save(tweets, {"name": "NASA"}, 2)
    second = store.save(tweets, None, 0)
    assert first["session_count"] == 1
    assert second["session_count"] == 2
    assert second["profile"] == {"name": "NASA"}
    assert second["newest_tweet_id"] == "2"
    assert second["oldest_tweet_id"] == "1"
    assert [t["id"] for t in store.load_tweets()] == ["2", "1"]
    assert store.csv_file.read_text(encoding="utf-8").splitlines()[0].startswith("id,created_at")


def test_store_rejects_bad_usernames(tmp_path):
    with pytest.raises(ValueError):
        ProfileStore("../etc", tmp_path)


READER_SAMPLE = (
    "Title: NASA (@NASA) on X\n\n[115 Following](https://x.com/NASA/following)[92.3M Followers](https://x.com/NASA/verified_followers)\n"
    "*   [](https://x.com/NASA/status/20)[![Image 1: @NASA](https://pbs.twimg.com/a_normal.jpg)](https://x.com/NASA)  "
    "[NASA](https://x.com/NASA) [@NASA](https://x.com/NASA) [14h](https://x.com/NASA/status/20)   Launch [#Artemis](https://x.com/hashtag/Artemis) "
    "is go ![Image 2](https://pbs.twimg.com/media/abc?format=webp)   [142](https://x.com/compose/post?in_reply_to=20) 271 2.1K 1.3M\n"
)


def test_parse_reader_markdown_without_login():
    from data_collection_framework.x_profile_scraper import parse_reader_markdown, parse_reader_profile
    [tweet] = parse_reader_markdown(READER_SAMPLE, "NASA")
    assert tweet["id"] == "20" and tweet["text"] == "Launch #Artemis is go"
    assert tweet["metrics"]["favorite_count"] == 2100 and tweet["metrics"]["view_count"] == 1300000
    assert tweet["hashtags"] == ["Artemis"] and len(tweet["media"]) == 1
    assert parse_reader_profile(READER_SAMPLE)["followers_count"] == 92300000
