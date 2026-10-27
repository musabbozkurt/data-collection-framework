from collections import Counter


def ngrams(text: str, n: int) -> Counter:
    """Counts word n-grams of a text."""
    words = text.split()
    return Counter(" ".join(words[i:i + n]) for i in range(len(words) - n + 1))
