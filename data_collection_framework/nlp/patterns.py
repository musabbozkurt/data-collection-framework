"""Tweet tokenization patterns, compiled once at import time."""
import re

EMOTICONS = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""

TOKEN_PATTERNS = (
    EMOTICONS,
    r'<[^>]+>',  # HTML tags
    r'(?:@[\w_]+)',  # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # urls
    r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
    r'(?:[\w_]+)',  # other words
    r'(?:\S)',  # anything else
)

TOKENS_RE = re.compile(r'(' + '|'.join(TOKEN_PATTERNS) + ')', re.VERBOSE | re.IGNORECASE)
EMOTICON_RE = re.compile(r'^' + EMOTICONS + '$', re.VERBOSE | re.IGNORECASE)
