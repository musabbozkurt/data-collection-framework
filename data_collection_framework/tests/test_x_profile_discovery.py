import pytest

from data_collection_framework.commands.base import CommandError
from data_collection_framework.x_profile_discovery import (extract_usernames, parse_username_list, username_from_url)


@pytest.mark.parametrize("url,expected", [
    ("https://x.com/Alice", "Alice"),
    ("https://twitter.com/bob/status/123", "bob"),
    ("https://x.com/i/trending/1", None),
    ("https://help.x.com/en", None),
    ("https://x.com/", None),
    ("https://example.com/alice", None),
    ("https://x.com/this_name_is_too_long", None),
])
def test_username_from_url(url, expected):
    assert username_from_url(url) == expected


def test_extract_usernames_filters_letter_and_duplicates():
    urls = ["https://x.com/Alice", "https://x.com/alice/status/1", "https://x.com/bob", "https://x.com/home"]
    assert extract_usernames(urls) == ["Alice", "bob"]
    assert extract_usernames(urls, "a") == ["Alice"]


def test_parse_username_list():
    assert parse_username_list("@Alice, bob  carol;dave") == ["Alice", "bob", "carol", "dave"]
    with pytest.raises(ValueError):
        parse_username_list("ok, not valid!")
    with pytest.raises(ValueError):
        parse_username_list("  ")


def test_scrapeselected_limits_and_validates():
    from data_collection_framework.commands.definitions import build_registry
    from data_collection_framework.config.settings import get_settings
    registry = build_registry(get_settings())
    with pytest.raises(CommandError, match="at most"):
        registry.execute("scrapeselected", {"usernames": "a,b,c,d,e,f", "max_tweets": "3"})
    with pytest.raises(CommandError, match="(?i)invalid"):
        registry.execute("addprofiles", {"usernames": "bad name!"})


def test_mentions_filters_by_topic_words():
    from data_collection_framework.x_profile_discovery import mentions
    result = {"title": "Ann (@ann_dev) on X", "body": "Senior Java engineer"}
    assert mentions(result, ["java"])
    assert mentions(result, [])
    assert not mentions(result, ["rust", "golang"])
