import json
from itertools import islice
from pathlib import Path
from typing import Iterable

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
        return self.write_files(iter_text_files(directory), database, collection)

    def write_files(self, paths: Iterable[Path], database: str, collection: str) -> int:
        repository = self._repository_factory(database, collection)
        total = 0
        for path in paths:
            documents = self._read_json(path) if path.suffix == ".json" else self._read_lines(path)
            while batch := list(islice(documents, BATCH_SIZE)):
                total += repository.insert_many(batch)
            log.info("Loaded %s into %s.%s", path.name, database, collection)
        return total

    def write_lines(self, lines: Iterable[str], database: str, collection: str) -> int:
        repository = self._repository_factory(database, collection)
        documents = [self._parse(Path("upload"), number, line) for number, line in enumerate(lines, 1) if line.strip()]
        if not all(isinstance(document, dict) for document in documents):
            raise ValueError("Every line must be a JSON object")
        return repository.insert_many(documents) if documents else 0

    def _read_lines(self, path: Path):
        with open(path, encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                if line.strip():
                    yield self._parse(path, number, line)

    @staticmethod
    def _read_json(path: Path):
        try:
            content = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            raise ValueError(f"{path.name} is not valid JSON") from None
        yield from (content if isinstance(content, list) else [content])

    @staticmethod
    def _parse(path: Path, number: int, line: str) -> dict:
        try:
            return json.loads(line)
        except ValueError:
            raise ValueError(f"{path.name}, line {number} is not valid JSON") from None
