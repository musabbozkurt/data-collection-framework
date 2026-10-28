import operator
import string
from collections import Counter, defaultdict
from itertools import combinations
from typing import Iterable, Iterator

from data_collection_framework.nlp.patterns import EMOTICON_RE, TOKENS_RE
from data_collection_framework.storage.files import iter_json_lines

_EXTRA_STOPWORDS = {"rt", "via", "amp"}
_FALLBACK_STOPWORDS = frozenset(
    "a an and are as at be but by for from has have he her his i if in into is it its just me my no not of on "
    "or our she so that the their them then there they this to was we were what when which who will with you "
    "your".split())


def preprocess(text: str, lowercase: bool = False) -> list:
    tokens = TOKENS_RE.findall(text)
    if lowercase:
        tokens = [t if EMOTICON_RE.search(t) else t.lower() for t in tokens]
    return tokens


def stop_words() -> frozenset:
    """English stop words from NLTK when its corpus is installed, otherwise a small built-in list."""
    try:
        from nltk.corpus import stopwords
        words = frozenset(stopwords.words("english"))
    except (ImportError, LookupError):
        words = _FALLBACK_STOPWORDS
    return words | set(string.punctuation) | _EXTRA_STOPWORDS


def content_terms(tokens: list, stop: frozenset) -> list:
    """Tokens without stop words, hashtags, mentions, links and bare numbers."""
    return [t for t in tokens if t not in stop and not t.startswith(("#", "@", "http")) and len(t) > 2
            and not t.replace(",", "").replace(".", "").isdigit()]


def _file_texts(directory) -> Iterator[str]:
    return (tweet.get("text", "") for tweet in iter_json_lines(directory))


def term_counter(directory, most_common: int) -> dict:
    """Term statistics of the tweets stored as files."""
    return count_terms(_file_texts(directory), most_common)


def co_occurrences(directory, search_word: str, most_common: int, max_pairs: int) -> dict:
    """Co-occurrences of the tweets stored as files."""
    return count_pairs(_file_texts(directory), search_word, most_common, max_pairs)


def count_terms(texts: Iterable[str], most_common: int) -> dict:
    """Single pass over tweet texts collecting the term statistics."""
    stop = stop_words()
    counts, hashtags, only_terms = Counter(), Counter(), Counter()
    for text in texts:
        tokens = preprocess(text, lowercase=True)
        counts.update(tokens)
        hashtags.update(t for t in tokens if t.startswith("#"))
        only_terms.update(content_terms(tokens, stop))
    return {
        "most_common": counts.most_common(most_common),
        "hashtags": hashtags.most_common(most_common),
        "terms": only_terms.most_common(most_common),
    }


def count_pairs(texts: Iterable[str], search_word: str, most_common: int, max_pairs: int) -> dict:
    """Most frequent term pairs and the terms co-occurring with `search_word`."""
    stop = stop_words()
    pairs = defaultdict(Counter)
    with_word = Counter()
    for text in texts:
        terms = sorted(set(content_terms(preprocess(text, lowercase=True), stop)))
        for first, second in combinations(terms, 2):
            pairs[first][second] += 1
        if search_word and search_word in terms:
            with_word.update(t for t in terms if t != search_word)
    top_pairs = [((a, b), n) for a, counter in pairs.items() for b, n in counter.most_common(5)]
    top_pairs.sort(key=operator.itemgetter(1), reverse=True)
    return {"pairs": top_pairs[:max_pairs], "search": with_word.most_common(most_common)}


def plot_pairs(pairs: list) -> None:
    import matplotlib.pyplot as plt
    if not pairs:
        return
    labels = [" + ".join(p) for p, _ in pairs]
    fig, ax = plt.subplots()
    bars = ax.bar(range(len(pairs)), [n for _, n in pairs], 0.7, color="r")
    ax.set_ylabel("Count")
    ax.set_xticks(range(len(pairs)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.bar_label(bars)
    fig.tight_layout()
    plt.show()
