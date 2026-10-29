"""Registers every command. Heavy libraries (tweepy, matplotlib, sklearn, nltk) are imported lazily."""
import base64
import json
import logging
from functools import partial

from data_collection_framework.analytics import (CHOICES, FIELD_PATTERN, analyze, available_metrics, collection_fields,
                                                 collection_texts, labelled_texts, tweet_authors)
from data_collection_framework.commands.base import (Command, CommandError, CommandRegistry, Param, decimal,
                                                     future_timestamp,
                                                     integer, text)
from data_collection_framework.config import editor
from data_collection_framework.config.settings import Settings, get_settings
from data_collection_framework.nlp.term_frequency import co_occurrences, plot_pairs, term_counter
from data_collection_framework.storage.files import (USERNAMES_TEMPLATE, read_usernames,
                                                     save_usernames)
from data_collection_framework.storage.mongo import MongoRepository, documents_page, overview, profile_groups

log = logging.getLogger(__name__)
SELECTED_LIMIT = 5
MAX_KEYWORDS = 5
BASE64_PATTERN = r"[A-Za-z0-9+/=]{4,60000}"
WORD_PATTERN = r"\S{1,100}"
NAME_PATTERN = r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}"
USERNAME = Param("username", "Twitter username", text(r"(?a)\w{1,15}"))
TWEET_COUNT = Param("tweet_count", "How many tweets do you want to collect?", integer(1, 3200))
DATABASE = Param("database", "Database name", text(NAME_PATTERN))
COLLECTION = Param("collection", "Collection name", text(NAME_PATTERN))
FILENAME = Param("filename", "File name", text(NAME_PATTERN))
END_TIME = Param("end_time", "Finishing date (YYYY-MM-DD HH:MM:SS)", future_timestamp)
KEYWORD = Param("keyword", "Word or hashtag to track", text(WORD_PATTERN))
SCRAPE_KEYWORDS = Param("keywords", "Comma separated keywords", text(r".{1,300}"))
SCRAPE_LIMIT = Param("limit", "Pages per keyword", integer(1, 5))
PROFILE_MAX = Param("max_tweets", "New tweets to collect", integer(1, 500))
LETTER = Param("letter", "Letter A-Z or ALL", text(r"(?i)[a-z]|all"))
LETTER_FILTER = Param("letter", "Letter filter",
                      lambda value: "" if value.strip() == "-" else text(r"(?i)[a-z]|all")(value))
KEYWORD_OPTIONAL = Param("keyword", "Topic keyword or '-' for none",
                         lambda value: "" if value.strip() == "-" else text(r"[\w .+#&-]{1,40}")(value).strip())
USERNAMES = Param("usernames", "Usernames (comma separated)", text(r"[@A-Za-z0-9_, ]{1,800}"))
BROWSER = Param("browser", "Browser to sign in with", text(r"edge|chrome|yandex|other"))
RESUME = Param("resume", "Keep earlier results (yes/no)", lambda value: text(r"(?i)yes|no")(value).lower() == "yes")
PAGE_SIZE = Param("page_size", "Documents per page", integer(1, 50))
PAGE = Param("page", "Page number", integer(1, 1_000_000))
METRIC = Param("metric", "What to analyse", text("|".join(CHOICES) + "|" + FIELD_PATTERN))
TEXT_FIELD = Param("text_field", "Field that holds the text", text(r"[A-Za-z0-9_.\-]{1,100}"))
LABEL_FIELD = Param("label_field", "Field that labels the documents, or '-' for the profile",
                    lambda value: "" if value.strip() == "-" else text(r"[A-Za-z0-9_.\-]{1,100}")(value))
TOP = Param("top", "How many entries", integer(1, 100))
NGRAM = Param("n", "n-gram size", integer(1, 5))
USER_OPTIONAL = Param("username", "Profile or '-' for all",
                      lambda value: "" if value.strip() == "-" else text(r"(?a)\w{1,15}")(value))
FILES = Param("files", "Files (relative paths, comma separated)",
              text(r"[\w.\-/, ]{3,30000}"))
UPLOAD_DATA = Param("data", "Documents (base64, one JSON document per line)", text(BASE64_PATTERN))
DATA_SUFFIXES = (".txt", ".json")
SKIPPED_FILES = ("checkpoint.json",)
BARS = Param("bars", "How many bars do you want to see in your plot?", integer(1, 100))

CROSS_VALIDATION_PARAMS = (
    Param("folds", "Number of folds for cross validation", integer(2, 100)),
    Param("splits", "Number of shuffle splits", integer(1, 100)),
    Param("test_size", "Test size between 0 and 1", decimal(0, 1)),
    Param("random_state", "Random state", integer(0, 2 ** 31 - 1)),
    Param("train_test_size", "Train/test split test size between 0 and 1", decimal(0, 1)),
    Param("svm_c", "C value of the SVC kernel", integer(1, 10_000)),
)

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


def listed_usernames(settings):
    try:
        names = read_usernames(settings.file_path_for_list_of_username)
    except ValueError as error:
        raise CommandError(str(error)) from None
    if not names:
        raise CommandError("No usernames found. Add them to the .txt file in "
                           f"{settings.file_path_for_list_of_username}")
    return names


def save_username_file(settings, data):
    try:
        text = base64.b64decode(data, validate=True).decode("utf-8")
        return f"Saved {save_usernames(settings.file_path_for_list_of_username, text)} usernames"
    except ValueError as error:
        raise CommandError(str(error) or "Invalid file") from None


def save_settings_file(data):
    try:
        payload = json.loads(base64.b64decode(data, validate=True).decode("utf-8"))
        files = editor.save_settings(payload["values"], payload.get("clear", []))
    except (ValueError, KeyError, TypeError) as error:
        raise CommandError(str(error) if isinstance(error, editor.SettingsError) else "Invalid settings data") from None
    return json.dumps(files)


def twitter_client(settings):
    from data_collection_framework.twitter.client import build_client
    try:
        return build_client(settings)
    except RuntimeError as error:
        raise CommandError(str(error)) from None


def collect_tweets(settings, usernames, tweet_count, database=None):
    from data_collection_framework.tweet_collector import TweetCollector
    collector = TweetCollector(twitter_client(settings), settings.file_path_for_timeline_outputs)
    total = sum(collector.get_all_tweets(name, tweet_count, database) for name in usernames)
    return f"Collected {total} tweets"


def collect_followers(settings, usernames):
    from data_collection_framework.follower_collector import FollowerCollector
    collector = FollowerCollector(twitter_client(settings), settings.file_path_for_followers_outputs)
    total = sum(collector.write_on_file(name) for name in usernames)
    return f"Collected {total} followers"


def stream(settings, database, collection, filename, end_time, keywords):
    from data_collection_framework.stream_collector import StreamCollector
    if not settings.bearer_token:
        raise RuntimeError(
            "Twitter bearer token is missing. Set TWITTER_BEARER_TOKEN or bearer_token in config.ini.")
    streamer = StreamCollector(settings.bearer_token, MongoRepository(database, collection),
                               settings.streaming_txt_file / filename, end_time)
    streamer.stream(keywords)
    return "Streaming finished"


def scrape_x(settings, keywords, limit):
    from data_collection_framework.x_batch_scraper import scrape
    words = [word.strip() for word in keywords.split(",") if word.strip()]
    if not words or len(words) > MAX_KEYWORDS or any(len(word) > 50 for word in words):
        raise CommandError(f"Give 1-{MAX_KEYWORDS} comma separated keywords of at most 50 characters each.")
    saved = scrape(words, limit, settings.mongo_uri)
    lines = [f"{keyword}: {len(urls)} saved" + "".join(f"\n  {url}" for url in urls)
             for keyword, urls in saved.items()]
    return "\n".join(lines)


def scrape_profile(settings, username, max_tweets, resume):
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


def discover_profiles(settings, letter, keyword):
    from data_collection_framework import x_profile_discovery as discovery
    letters = list(discovery.LETTERS) if letter.upper() == "ALL" else [letter.upper()]
    found = []
    for one in letters:
        found.extend(discovery.discover_letter(one, keyword=keyword))
    stored = discovery.store_usernames(found, "search", settings.mongo_uri, keyword)
    if not stored["found"]:
        raise CommandError("The search engines returned no profiles this time"
                           + (f" for '{keyword}'" if keyword else "")
                           + ". Try again, pick another letter or keyword, or add usernames by hand.")
    return f"Found {stored['found']} profiles ({stored['new']} new): " + ", ".join(f"@{n}" for n in found[:30])


def add_profiles(settings, usernames):
    from data_collection_framework import x_profile_discovery as discovery
    try:
        names = discovery.parse_username_list(usernames)
    except ValueError as error:
        raise CommandError(str(error)) from None
    stored = discovery.store_usernames(names, "manual", settings.mongo_uri)
    return f"Added {stored['new']} new profiles ({stored['found']} given)"


def list_profiles(settings, letter, keyword, page, page_size):
    from data_collection_framework import x_profile_discovery as discovery
    return json.dumps(discovery.list_profiles(settings.mongo_uri, letter, page, page_size, keyword))


def scrape_selected(settings, usernames, max_tweets):
    import re
    import time
    from data_collection_framework import x_profile_discovery as discovery
    from data_collection_framework.x_profile_scraper import scrape
    try:
        names = list(dict.fromkeys(discovery.parse_username_list(usernames)))
    except ValueError as error:
        raise CommandError(str(error)) from None
    if len(names) > SELECTED_LIMIT:
        raise CommandError(f"Select at most {SELECTED_LIMIT} profiles per run.")
    lines = []
    for index, name in enumerate(names):
        if index:
            time.sleep(3)  # fixed pause between profiles
        try:
            report = scrape(name, max_tweets, True, mongo_uri=settings.mongo_uri)
            count = int(re.search(r"(\d{1,9}) new tweets", report).group(1))
            discovery.mark_scraped(name, count, settings.mongo_uri)
            lines.append(f"✔ @{name}: {count} new posts")
        except Exception as error:  # one bad profile must not stop the others
            log.exception("Scraping @%s failed", name)
            lines.append(f"✘ @{name}: {error}")
    return "\n".join(lines)


def connect_x(browser):
    from data_collection_framework.x_profile_scraper import login
    try:
        return login(browser=browser)
    except RuntimeError as error:
        log.exception("X sign-in failed")
        raise CommandError(str(error)) from None
    except Exception as error:
        log.exception("X sign-in failed")
        raise CommandError("Could not open the sign-in browser. Run 'make browsers' once on the machine "
                           f"that runs the Python server ({type(error).__name__}).") from None


def x_session():
    from data_collection_framework.x_profile_scraper import has_session
    return "connected" if has_session() else "not connected"


def mongo_databases():
    return json.dumps(overview())


def mongo_documents(database, collection, page, page_size):
    return json.dumps(documents_page(database, collection, page, page_size))


def mongo_groups(database, collection, page, page_size):
    return json.dumps(profile_groups(database, collection, page, page_size))


def mongo_profile_documents(database, collection, username, page, page_size):
    return json.dumps(documents_page(database, collection, page, page_size, username=username))


def mongo_analytics(database, collection, metric, top, username, n):
    return json.dumps(analyze(metric, top, username, n, database, collection))


def mongo_terms(database, collection, text_field, most_common, max_pairs, search_word):
    from data_collection_framework.nlp.term_frequency import count_pairs, count_terms
    texts = collection_texts(database, collection, text_field)
    pairs = count_pairs(texts, search_word.lower(), most_common, max_pairs)
    return json.dumps({"documents": len(texts), "terms": count_terms(texts, most_common),
                       "pairs": [[list(pair), count] for pair, count in pairs["pairs"]],
                       "search": pairs["search"], "search_word": search_word})


def mongo_cross_validation(database, collection, text_field, label_field, folds, splits, test_size, random_state,
                           train_test_size, svm_c):
    from data_collection_framework.cross_validation import evaluate
    texts, labels = labelled_texts(database, collection, None, text_field, label_field)
    try:
        return json.dumps(evaluate(texts, labels, folds, splits, test_size, random_state, train_test_size, svm_c))
    except ValueError as error:
        raise CommandError(str(error)) from None


def cross_validation(settings, folds, splits, test_size, random_state, train_test_size, svm_c):
    from data_collection_framework.cross_validation import TermFrequency
    TermFrequency.termfreq(settings.file_path_for_cross_val, folds, splits, test_size, random_state,
                           train_test_size, svm_c)
    return "Cross validation finished; see the server console for the report"


def term_frequency(settings, most_common, max_pairs, search_word):
    stats = term_counter(settings.streaming_txt_file, most_common)
    pairs = co_occurrences(settings.streaming_txt_file, search_word, most_common, max_pairs)
    print(stats, pairs, sep="\n")
    plot_pairs(pairs["pairs"])
    return f"Most common terms: {stats['most_common']}"


def plot(settings, metric):
    def run(bars):
        from data_collection_framework.analysis import Analysis
        Analysis(settings.file_path_for_mongo).plot(metric, bars)
        return "Plot displayed on the server"

    return run


def data_roots(settings):
    from data_collection_framework.x_profile_scraper import DATA_DIR
    roots = (settings.file_path_for_mongo.resolve().parent, DATA_DIR.resolve())
    return {root.name: root for root in roots}


def list_data_files(settings):
    files = []
    for name, root in data_roots(settings).items():
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix in DATA_SUFFIXES and path.name not in SKIPPED_FILES:
                relative = path.relative_to(root)
                files.append({"id": f"{name}/{relative.as_posix()}",
                              "folder": f"{name}/{relative.parent.as_posix()}".rstrip("/."),
                              "name": path.name, "size": path.stat().st_size})
    return json.dumps(files)


def store_files(settings, database, collection, files):
    from data_collection_framework.mongo_writer import MongoWriter
    roots = data_roots(settings)
    paths = []
    for item in files.split(","):
        key, _, relative = item.strip().partition("/")
        root = roots.get(key)
        path = (root / relative).resolve() if root else None
        if (path is None or ".." in relative.split("/") or not path.is_file() or root not in path.parents
                or path.suffix not in DATA_SUFFIXES or path.name in SKIPPED_FILES):
            raise CommandError(f"Unknown file: {item.strip()}")
        paths.append(path)
    try:
        total = MongoWriter().write_files(paths, database, collection)
    except ValueError as error:
        raise CommandError(str(error)) from None
    return f"Stored {total} documents from {len(paths)} file(s) into {database}.{collection}"


def store_upload(database, collection, data):
    from data_collection_framework.mongo_writer import MongoWriter
    try:
        lines = base64.b64decode(data, validate=True).decode("utf-8").splitlines()
        return f"Stored {MongoWriter().write_lines(lines, database, collection)}"
    except ValueError as error:
        raise CommandError(str(error) or "Invalid upload") from None


def store_data(settings, database, collection):
    from data_collection_framework.mongo_writer import MongoWriter
    return f"Stored {MongoWriter().write_to_mongo(settings.file_path_for_mongo, database, collection)} documents"


def build_registry(settings: Settings = None) -> CommandRegistry:
    settings = settings or get_settings()
    registry = CommandRegistry()

    def bind(handler):
        return partial(handler, settings)

    registry.register(Command("collecttweetfromuserlist", "Collect tweets of the listed usernames", (TWEET_COUNT,),
                              lambda tweet_count: collect_tweets(settings, listed_usernames(settings), tweet_count,
                                                                 "CollectTweetFromUserList")))
    registry.register(Command("collecttweetfromusername", "Collect tweets from a username", (USERNAME, TWEET_COUNT),
                              lambda username, tweet_count: collect_tweets(settings, [username], tweet_count,
                                                                           "CollectTweetFromUsername")))
    registry.register(Command("collectfollowerfromuserlist", "Collect followers of the listed usernames", (),
                              lambda: collect_followers(settings, listed_usernames(settings))))
    registry.register(Command("collectfollowerfromusername", "Collect followers from a username", (USERNAME,),
                              lambda username: collect_followers(settings, [username])))
    registry.register(Command("scrapexbatch", "Scrape X pages for keywords (no API credits needed)",
                              (SCRAPE_KEYWORDS, SCRAPE_LIMIT), bind(scrape_x)))
    registry.register(Command("scrapexprofile", "Scrape an X profile's tweets with a browser session",
                              (USERNAME, PROFILE_MAX, RESUME), bind(scrape_profile)))
    registry.register(Command("discoverprofiles", "Find X profiles for a letter (web search) and store them",
                              (LETTER, KEYWORD_OPTIONAL), bind(discover_profiles)))
    registry.register(Command("addprofiles", "Add X usernames by hand", (USERNAMES,), bind(add_profiles)))
    registry.register(Command("listprofiles", "List stored X profiles alphabetically (JSON)",
                              (LETTER_FILTER, KEYWORD_OPTIONAL, PAGE, PAGE_SIZE), bind(list_profiles)))
    registry.register(Command("scrapeselected", "Scrape the newest posts of several stored profiles",
                              (USERNAMES, PROFILE_MAX), bind(scrape_selected)))
    registry.register(Command("connectx", "Sign in to X in a browser window and save the session", (BROWSER,),
                              connect_x))
    registry.register(Command("xsession", "Report whether an X session is saved", (), x_session))
    registry.register(Command("mongodatabases", "List MongoDB databases and collections (JSON)", (),
                              mongo_databases))
    registry.register(Command("mongodocuments", "Show one page of a collection's documents, newest first (JSON)",
                              (DATABASE, COLLECTION, PAGE, PAGE_SIZE), mongo_documents))
    registry.register(Command("mongogroups", "List the usernames of a collection with their document counts (JSON)",
                              (DATABASE, COLLECTION, PAGE, PAGE_SIZE), mongo_groups))
    registry.register(Command("mongoprofiledocuments", "Show one page of a profile's documents (JSON)",
                              (DATABASE, COLLECTION, USERNAME, PAGE, PAGE_SIZE), mongo_profile_documents))
    registry.register(Command("storedata", "Store collected text files in MongoDB", (DATABASE, COLLECTION),
                              bind(store_data)))
    for name, (metric, title) in PLOTS.items():
        registry.register(Command(name, title, (BARS,), plot(settings, metric)))
    registry.register(Command("streamfromlist", "Stream the configured keyword list",
                              (DATABASE, COLLECTION, FILENAME, END_TIME),
                              lambda database, collection, filename, end_time: stream(
                                  settings, database, collection, filename, end_time,
                                  settings.word_list_for_streaming)))
    registry.register(Command("streamfrominput", "Stream a given keyword",
                              (DATABASE, COLLECTION, FILENAME, END_TIME, KEYWORD),
                              lambda database, collection, filename, end_time, keyword: stream(
                                  settings, database, collection, filename, end_time, [keyword])))
    registry.register(Command("crossvalidation", "Cross validation and F1 macro scoring", CROSS_VALIDATION_PARAMS,
                              bind(cross_validation)))
    registry.register(Command("termfrequency", "Term frequency and co-occurrence", (
        Param("most_common", "How many most common terms?", integer(1, 1000)),
        Param("max_pairs", "How many top co-occurrences?", integer(1, 1000)),
        Param("search_word", "Word to find co-occurrences for", text(WORD_PATTERN)),
    ), bind(term_frequency)))
    registry.register(Command("mongoanalytics", "Chart data computed from the stored tweets (JSON)",
                              (DATABASE, COLLECTION, METRIC, TOP, USER_OPTIONAL, NGRAM), mongo_analytics))
    registry.register(Command("listdatafiles", "List the collected data files that can be stored (JSON)", (),
                              bind(list_data_files)))
    registry.register(Command("storefiles", "Store the selected data files in MongoDB", (DATABASE, COLLECTION, FILES),
                              bind(store_files)))
    registry.register(Command("storeupload", "Store uploaded JSON documents in MongoDB",
                              (DATABASE, COLLECTION, UPLOAD_DATA), store_upload))
    registry.register(Command("getsettings", "Show the editable settings; secrets are never returned (JSON)", (),
                              lambda: json.dumps(editor.read_settings())))
    registry.register(Command("savesettings", "Write settings to config.ini and .env (JSON list of changed files)",
                              (Param("data", "Settings (base64 JSON)", text(BASE64_PATTERN)),),
                              save_settings_file))
    registry.register(Command("listusernames", "List the usernames of the list file (JSON)", (),
                              lambda: json.dumps(listed_usernames(settings))))
    registry.register(Command("saveusernames", "Replace the username list with an uploaded file",
                              (Param("data", "File content (base64)", text(BASE64_PATTERN)),),
                              bind(save_username_file)))
    registry.register(Command("usernamestemplate", "Template of the username list file", (),
                              lambda: USERNAMES_TEMPLATE.read_text(encoding="utf-8")))
    registry.register(
        Command("analysismetrics", "List the analyses that fit a collection (JSON)", (DATABASE, COLLECTION),
                lambda database, collection: json.dumps(available_metrics(database, collection))))
    registry.register(Command("collectionfields", "List the text and label fields of a collection (JSON)",
                              (DATABASE, COLLECTION),
                              lambda database, collection: json.dumps(collection_fields(database, collection))))
    registry.register(Command("mongoterms", "Term frequency and co-occurrence of a collection's texts (JSON)", (
        DATABASE, COLLECTION, TEXT_FIELD,
        Param("most_common", "How many most common terms?", integer(1, 1000)),
        Param("max_pairs", "How many top co-occurrences?", integer(1, 1000)),
        Param("search_word", "Word to find co-occurrences for, or '-'",
              lambda value: "" if value.strip() == "-" else text(WORD_PATTERN)(value)),
    ), mongo_terms))
    registry.register(Command("tweetauthors", "List the profiles that have stored tweets (JSON)",
                              (DATABASE, COLLECTION),
                              lambda database, collection: json.dumps(tweet_authors(database, collection))))
    registry.register(Command("mongocrossvalidation", "Cross validate a classifier on the stored tweets (JSON)",
                              (DATABASE, COLLECTION, TEXT_FIELD, LABEL_FIELD) + CROSS_VALIDATION_PARAMS,
                              mongo_cross_validation))
    return registry
