from collections import Counter


def char_ngrams(text: str, n: int) -> Counter:
    """Counts character n-grams inside each word-level n-gram window of a text."""
    words = text.split()
    counts = Counter()
    for i in range(len(words) - n + 1):
        window = " ".join(words[i:i + n])
        counts.update(window[j:j + n] for j in range(len(window) - n + 1))
    return counts
