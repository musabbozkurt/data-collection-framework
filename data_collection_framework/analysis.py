from collections import Counter
from dataclasses import dataclass
from typing import Callable, Optional

from data_collection_framework.logger import get_logger
from data_collection_framework.storage.files import iter_json_lines

log = get_logger(__name__)


def _user(field: str) -> Callable[[dict], Optional[object]]:
    return lambda tweet: (tweet.get("user") or {}).get(field)


def _place_country(tweet: dict) -> Optional[str]:
    return (tweet.get("place") or {}).get("country")


@dataclass(frozen=True)
class Metric:
    label: str
    extract: Callable[[dict], Optional[object]]
    color: str = "blue"


# Each entry replaces what used to be a copy-pasted analysis method.
METRICS = {
    "language": Metric("languages", _user("lang"), "red"),
    "country": Metric("countries", _place_country),
    "location": Metric("location", _place_country),
    "timezone": Metric("timezone", _user("time_zone")),
    "tweet": Metric("tweet", lambda t: t.get("text")),
    "created_at": Metric("created_at", lambda t: t.get("created_at")),
    "user_id": Metric("user_id", _user("id")),
    "id_str": Metric("id_str", _user("id_str")),
    "username": Metric("username", _user("name")),
    "screen_name": Metric("screen_name", _user("screen_name")),
    "followers_count": Metric("followers_count", _user("followers_count")),
    "friends_count": Metric("friends_count", _user("friends_count")),
    "user_language": Metric("user_lang", _user("lang")),
    "retweet_count": Metric("retweet_count", lambda t: t.get("retweet_count")),
    "favorite_count": Metric("favorite_count", lambda t: t.get("favorite_count")),
}


class Analysis:
    """Counts a tweet attribute over all stored tweets and plots the top values."""

    def __init__(self, directory):
        self._directory = directory

    def count(self, metric: str) -> Counter:
        extract = METRICS[metric].extract
        counter = Counter()
        for tweet in iter_json_lines(self._directory):
            value = extract(tweet)
            if value is not None:
                counter[value] += 1
        return counter

    def plot(self, metric: str, top: int) -> None:
        import matplotlib.pyplot as plt

        spec = METRICS[metric]
        top_items = self.count(metric).most_common(top)
        log.info("Plotting top %s of %s", top, metric)
        fig, ax = plt.subplots()
        ax.bar([str(k) for k, _ in top_items], [v for _, v in top_items], color=spec.color)
        ax.set_xlabel(spec.label.capitalize(), fontsize=10)
        ax.set_ylabel("Number of tweets", fontsize=15)
        ax.set_title(f"Top {top} {spec.label}", fontsize=15, fontweight="bold")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        plt.show()
