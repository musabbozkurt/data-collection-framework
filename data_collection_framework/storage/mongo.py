"""MongoDB access: one shared client and a small repository wrapper."""
from functools import lru_cache
from typing import Iterable, Mapping

from data_collection_framework.config.settings import get_settings


@lru_cache(maxsize=1)
def get_client():
    from pymongo import MongoClient
    return MongoClient(get_settings().mongo_uri)


class MongoRepository:
    """Writes documents into a single collection, batching inserts for speed."""

    def __init__(self, database: str, collection: str, client=None):
        self._collection = (client or get_client())[database][collection]

    def insert_one(self, document: Mapping) -> None:
        self._collection.insert_one(dict(document))

    def insert_many(self, documents: Iterable[Mapping]) -> int:
        batch = [dict(d) for d in documents]
        if batch:
            self._collection.insert_many(batch, ordered=False)
        return len(batch)
