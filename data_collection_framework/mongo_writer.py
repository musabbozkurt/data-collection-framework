import json
from itertools import islice
from pathlib import Path

from data_collection_framework.logger import get_logger
from data_collection_framework.storage.files import iter_text_files
from data_collection_framework.storage.mongo import MongoRepository

log = get_logger(__name__)
BATCH_SIZE = 1000


class MongoWriter:
    """Loads every *.txt file (one JSON document per line) of a directory into a MongoDB collection."""

    def __init__(self, repository_factory=MongoRepository):
        self._repository_factory = repository_factory

    def write_to_mongo(self, directory: Path, database: str, collection: str) -> int:
        repository = self._repository_factory(database, collection)
        total = 0
        for path in iter_text_files(directory):
            with open(path, encoding="utf-8") as handle:
                documents = (json.loads(line) for line in handle if line.strip())
                while batch := list(islice(documents, BATCH_SIZE)):
                    total += repository.insert_many(batch)
            log.info("Loaded %s into %s.%s", path.name, database, collection)
        return total
