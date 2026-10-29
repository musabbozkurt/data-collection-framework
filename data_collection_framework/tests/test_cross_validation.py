import pytest

from data_collection_framework.cross_validation import evaluate

TEXTS = [f"space rocket moon launch {i}" for i in range(8)] + [f"python code bug test {i}" for i in range(8)]
LABELS = ["nasa"] * 8 + ["dev"] * 8


def test_evaluate_separates_two_profiles():
    result = evaluate(TEXTS, LABELS, 4, 3, 0.25, 1, 0.25, 1)
    assert result["classes"] == ["dev", "nasa"]
    assert len(result["accuracy_scores"]) == 4
    assert result["mean_accuracy"] > 0.9
    assert sum(map(sum, result["confusion_matrix"])) == 16


def test_evaluate_needs_two_profiles_with_enough_tweets():
    with pytest.raises(ValueError, match="at least 2 profiles"):
        evaluate(TEXTS[:8], LABELS[:8], 4, 3, 0.25, 1, 0.25, 1)
