"""Registers every command. Heavy libraries (tweepy, matplotlib, sklearn, nltk) are imported lazily."""
import json
import logging

from data_collection_framework.commands.base import (Command, CommandError, CommandRegistry, Param, decimal,
                                                     future_timestamp,
                                                     integer, text)
from data_collection_framework.config.settings import Settings, get_settings
from data_collection_framework.nlp.term_frequency import co_occurrences, plot_pairs, term_counter
from data_collection_framework.storage.files import read_words
from data_collection_framework.storage.mongo import MongoRepository, documents_page, overview

log = logging.getLogger(__name__)
NAME_PATTERN = r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}"
USERNAME = Param("username", "Twitter username", text(r"[A-Za-z0-9_]{1,15}"))
TWEET_COUNT = Param("tweet_count", "How many tweets do you want to collect?", integer(1, 3200))
DATABASE = Param("database", "Database name", text(NAME_PATTERN))
COLLECTION = Param("collection", "Collection name", text(NAME_PATTERN))
FILENAME = Param("filename", "File name", text(NAME_PATTERN))
END_TIME = Param("end_time", "Finishing date (YYYY-MM-DD HH:MM:SS)", future_timestamp)
KEYWORD = Param("keyword", "Word or hashtag to track", text(r"[^\s]{1,100}"))
SCRAPE_KEYWORDS = Param("keywords", "Comma separated keywords", text(r"[^,\s][^,]{0,49}(,\s*[^,\s][^,]{0,49}){0,4}"))
SCRAPE_LIMIT = Param("limit", "Pages per keyword", integer(1, 5))
PROFILE_MAX = Param("max_tweets", "New tweets to collect", integer(1, 500))
RESUME = Param("resume", "Keep earlier results (yes/no)", lambda value: text(r"(?i)yes|no")(value).lower() == "yes")
PAGE_SIZE = Param("page_size", "Documents per page", integer(1, 50))
PAGE = Param("page", "Page number", integer(1, 1_000_000))
BARS = Param("bars", "How many bars do you want to see in your plot?", integer(1, 100))

PLOTS = {
    "plotlanguage": ("language", "Plot Language Analysis"),
    "plotcountry": ("country", "Plot Country Analysis"),
    "plotlocation": ("location", "Plot Location Analysis"),
    "plottimezone": ("timezone", "Plot Timezone Analysis"),
    "plottweet": ("tweet", "Plot Tweet Analysis"),
    "plottweetcreatedat": ("created_at", "Plot Tweet Created At Analysis"),
    "plotuserid": ("user_id", "Plot User ID Analysis"),
    "plotstringofid": ("id_str", "Plot String of ID Analysis"),
    "plotusername": ("username", "Plot Username Analysis"),
    "plotscreenname": ("screen_name", "Plot ScreenName Analysis"),
    "plotfollowerscount": ("followers_count", "Plot Followers Count Analysis"),
    "plotfriendscount": ("friends_count", "Plot Friends Count Analysis"),
    "plotuserlanguage": ("user_language", "Plot User Language Analysis"),
    "plotretweet": ("retweet_count", "Plot Retweet Count Analysis"),
    "plotfavourite": ("favorite_count", "Plot Favorite Count Analysis"),
}


def build_registry(settings: Settings = None) -> CommandRegistry:
    settings = settings or get_settings()
    registry = CommandRegistry()

    def collect_tweets(usernames, tweet_count, database=None):
        from data_collection_framework.tweet_collector import TweetCollector
        from data_collection_framework.twitter.client import build_client
        collector = TweetCollector(build_client(settings), settings.file_path_for_timeline_outputs)
        total = sum(collector.get_all_tweets(name, tweet_count, database) for name in usernames)
        return f"Collected {total} tweets"

    def collect_followers(usernames):
        from data_collection_framework.follower_collector import FollowerCollector
        from data_collection_framework.twitter.client import build_client
        collector = FollowerCollector(build_client(settings), settings.file_path_for_followers_outputs)
        total = sum(collector.write_on_file(name) for name in usernames)
        return f"Collected {total} followers"

    def stream(database, collection, filename, end_time, keywords):
        from data_collection_framework.stream_collector import StreamCollector
        if not settings.bearer_token:
            raise RuntimeError(
                "Twitter bearer token is missing. Set TWITTER_BEARER_TOKEN or bearer_token in config.ini.")
        streamer = StreamCollector(settings.bearer_token, MongoRepository(database, collection),
                                   settings.streaming_txt_file / filename, end_time)
        streamer.stream(keywords)
        return "Streaming finished"

    def scrape_x(keywords, limit):
        from data_collection_framework.x_batch_scraper import scrape
        saved = scrape([word.strip() for word in keywords.split(",")], limit, settings.mongo_uri)
        lines = [f"{keyword}: {len(urls)} saved" + "".join(f"\n  {url}" for url in urls)
                 for keyword, urls in saved.items()]
        return "\n".join(lines)

    def scrape_profile(username, max_tweets, resume):
        import requests
        from data_collection_framework.x_profile_scraper import scrape
        try:
            return scrape(username, max_tweets, resume, mongo_uri=settings.mongo_uri)
        except RuntimeError as error:
            log.exception("Profile scrape failed")
            raise CommandError(str(error)) from None
        except requests.RequestException as error:
            log.exception("Profile scrape failed")
            raise CommandError("Could not reach the page reader. Check your internet connection and try again "
                               f"({type(error).__name__}).") from None

    def mongo_databases():
        return json.dumps(overview())

    def mongo_documents(database, collection, page, page_size):
        return json.dumps(documents_page(database, collection, page, page_size))

    def cross_validation(folds, splits, test_size, random_state, train_test_size, svm_c):
        from data_collection_framework.cross_validation import TermFrequency
        TermFrequency.termfreq(settings.file_path_for_cross_val, folds, splits, test_size, random_state,
                               train_test_size, svm_c)
        return "Cross validation finished; see the server console for the report"

    def term_frequency(most_common, max_pairs, search_word):
        stats = term_counter(settings.streaming_txt_file, most_common)
        pairs = co_occurrences(settings.streaming_txt_file, search_word, most_common, max_pairs)
        print(stats, pairs, sep="\n")
        plot_pairs(pairs["pairs"])
        return f"Most common terms: {stats['most_common']}"

    def plot(metric):
        def run(bars):
            from data_collection_framework.analysis import Analysis
            Analysis(settings.file_path_for_mongo).plot(metric, bars)
            return "Plot displayed on the server"

        return run

    def store_data(database, collection):
        from data_collection_framework.mongo_writer import MongoWriter
        return f"Stored {MongoWriter().write_to_mongo(settings.file_path_for_mongo, database, collection)} documents"

    registry.register(Command("collecttweetfromuserlist", "Collect tweets from the username list", (TWEET_COUNT,),
                              lambda tweet_count: collect_tweets(read_words(settings.file_path_for_list_of_username),
                                                                 tweet_count, "CollectTweetFromUserList")))
    registry.register(Command("collecttweetfromusername", "Collect tweets from a username", (USERNAME, TWEET_COUNT),
                              lambda username, tweet_count: collect_tweets([username], tweet_count,
                                                                           "CollectTweetFromUsername")))
    registry.register(Command("collectfollowerfromuserlist", "Collect followers from the username list", (),
                              lambda: collect_followers(read_words(settings.file_path_for_list_of_username))))
    registry.register(Command("collectfollowerfromusername", "Collect followers from a username", (USERNAME,),
                              lambda username: collect_followers([username])))
    registry.register(Command("scrapexbatch", "Scrape X pages for keywords (no API credits needed)",
                              (SCRAPE_KEYWORDS, SCRAPE_LIMIT), scrape_x))
    registry.register(Command("scrapexprofile", "Scrape an X profile's tweets with a browser session",
                              (USERNAME, PROFILE_MAX, RESUME), scrape_profile))
    registry.register(Command("mongodatabases", "List MongoDB databases and collections (JSON)", (),
                              mongo_databases))
    registry.register(Command("mongodocuments", "Show one page of a collection's documents, newest first (JSON)",
                              (DATABASE, COLLECTION, PAGE, PAGE_SIZE), mongo_documents))
    registry.register(Command("storedata", "Store collected text files in MongoDB", (DATABASE, COLLECTION),
                              store_data))
    for name, (metric, title) in PLOTS.items():
        registry.register(Command(name, title, (BARS,), plot(metric)))
    registry.register(Command("streamfromlist", "Stream the configured keyword list",
                              (DATABASE, COLLECTION, FILENAME, END_TIME),
                              lambda database, collection, filename, end_time: stream(
                                  database, collection, filename, end_time, settings.word_list_for_streaming)))
    registry.register(Command("streamfrominput", "Stream a given keyword",
                              (DATABASE, COLLECTION, FILENAME, END_TIME, KEYWORD),
                              lambda database, collection, filename, end_time, keyword: stream(
                                  database, collection, filename, end_time, [keyword])))
    registry.register(Command("crossvalidation", "Cross validation and F1 macro scoring", (
        Param("folds", "Number of folds for cross validation", integer(2, 100)),
        Param("splits", "Number of shuffle splits", integer(1, 100)),
        Param("test_size", "Test size between 0 and 1", decimal(0, 1)),
        Param("random_state", "Random state", integer(0, 2 ** 31 - 1)),
        Param("train_test_size", "Train/test split test size between 0 and 1", decimal(0, 1)),
        Param("svm_c", "C value of the SVC kernel", integer(1, 10_000)),
    ), cross_validation))
    registry.register(Command("termfrequency", "Term frequency and co-occurrence", (
        Param("most_common", "How many most common terms?", integer(1, 1000)),
        Param("max_pairs", "How many top co-occurrences?", integer(1, 1000)),
        Param("search_word", "Word to find co-occurrences for", text(r"[^\s]{1,100}")),
    ), term_frequency))
    return registry
