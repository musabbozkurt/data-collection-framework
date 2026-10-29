from data_collection_framework.nlp.char_ngrams import char_ngrams
from data_collection_framework.nlp.ngrams import ngrams
from data_collection_framework.nlp.term_frequency import content_terms, count_pairs, count_terms, preprocess
from data_collection_framework.nlp.tokenization import stem


def test_ngrams_counts_word_windows():
    assert ngrams("a b a b", 2) == {"a b": 2, "b a": 1}


def test_ngrams_shorter_than_n_is_empty():
    assert not ngrams("a b", 3)


def test_char_ngrams_returns_counts():
    assert char_ngrams("ab ab", 2)["ab"] == 2


def test_stem_keeps_six_characters():
    assert stem("kitaplarimiz") == "kitapl"


def test_preprocess_keeps_hashtags_mentions_and_lowercases_words():
    tokens = preprocess("Hello @bob #Python :)", lowercase=True)
    assert tokens == ["hello", "@bob", "#python", ":)"]


def test_content_terms_drops_stopwords_hashtags_and_mentions():
    assert content_terms(["the", "#tag", "@bob", "cat"], frozenset({"the"})) == ["cat"]


def test_term_statistics_work_on_texts():
    texts = ["Python rocks #python", "python code rocks"]
    stats = count_terms(texts, 3)
    assert stats["terms"][0][0] in {"python", "rocks"}
    assert stats["hashtags"] == [("#python", 1)]
    pairs = count_pairs(texts, "code", 3, 3)
    assert (("python", "rocks"), 2) in pairs["pairs"]
    assert ("python", 1) in pairs["search"]
