STEM_LENGTH = 6


def stem(term: str) -> str:
    """Crude prefix stemmer (first 6 characters), suitable for agglutinative languages such as Turkish."""
    return term[:STEM_LENGTH]


def tokenize(text: str) -> list:
    import nltk
    return [stem(token) for token in nltk.word_tokenize(text)]
