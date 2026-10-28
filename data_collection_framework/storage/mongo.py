"""MongoDB access: one shared client and a small repository wrapper."""
import json
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


SYSTEM_DATABASES = {"admin", "config", "local"}
MAX_TEXT = 300  # longer strings are shortened so a page of documents stays readable


def _shorten(value):
    if isinstance(value, str):
        return value if len(value) <= MAX_TEXT else value[:MAX_TEXT] + "…"
    if isinstance(value, dict):
        return {key: _shorten(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_shorten(item) for item in value[:20]]
    return value


def overview(client=None) -> dict:
    """Returns {database: {collection: document count}} without the MongoDB system databases."""
    client = client or get_client()
    return {name: {collection: client[name][collection].estimated_document_count()
                   for collection in sorted(client[name].list_collection_names())}
            for name in sorted(client.list_database_names()) if name not in SYSTEM_DATABASES}


def documents_page(database: str, collection: str, page: int, page_size: int, client=None) -> dict:
    """Returns one page of documents, newest first, as JSON-safe dicts (ObjectIds and dates become strings)."""
    target = (client or get_client())[database][collection]
    total = target.estimated_document_count()
    pages = max(1, -(-total // page_size))
    page = min(page, pages)
    cursor = target.find().sort("_id", -1).skip((page - 1) * page_size).limit(page_size)
    return {"page": page, "pages": pages, "total": total,
            "documents": [_shorten(json.loads(json.dumps(document, default=str))) for document in cursor]}
