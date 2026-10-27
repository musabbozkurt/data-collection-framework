import operator
import string
from collections import Counter, defaultdict
from itertools import combinations

from data_collection_framework.nlp.patterns import EMOTICON_RE, TOKENS_RE
from data_collection_framework.storage.files import iter_json_lines

_EXTRA_STOPWORDS = {"rt", "via"}


def preprocess(text: str, lowercase: bool = False) -> list:
    tokens = TOKENS_RE.findall(text)
    if lowercase:
        tokens = [t if EMOTICON_RE.search(t) else t.lower() for t in tokens]
    return tokens


def stop_words() -> frozenset:
    from nltk.corpus import stopwords
    return frozenset(stopwords.words("english")) | set(string.punctuation) | _EXTRA_STOPWORDS


def content_terms(tokens: list, stop: frozenset) -> list:
    """Tokens without stop words, hashtags and mentions."""
    return [t for t in tokens if t not in stop and not t.startswith(("#", "@"))]


def term_counter(directory, most_common: int) -> dict:
    """Single pass over all tweets collecting the term statistics."""
    stop = stop_words()
    counts, hashtags, only_terms = Counter(), Counter(), Counter()
    for tweet in iter_json_lines(directory):
        tokens = preprocess(tweet.get("text", ""))
        counts.update(tokens)
        hashtags.update(t for t in tokens if t.startswith("#"))
        only_terms.update(content_terms(tokens, stop))
    return {
        "most_common": counts.most_common(most_common),
        "hashtags": hashtags.most_common(most_common),
        "terms": only_terms.most_common(most_common),
    }


def co_occurrences(directory, search_word: str, most_common: int, max_pairs: int) -> dict:
    """Most frequent term pairs and the terms co-occurring with `search_word`."""
    stop = stop_words()
    pairs = defaultdict(Counter)
    with_word = Counter()
    for tweet in iter_json_lines(directory):
        terms = content_terms(preprocess(tweet.get("text", "")), stop)
        for first, second in combinations(terms, 2):
            if first != second:
                a, b = sorted((first, second))
                pairs[a][b] += 1
        if search_word in terms:
            with_word.update(terms)
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
