"""Helpers for streaming newline-delimited JSON files without loading them fully into memory."""
import json
from pathlib import Path
from typing import Iterator


def iter_text_files(directory: Path) -> Iterator[Path]:
    yield from sorted(Path(directory).glob("*.txt"))


def iter_json_lines(directory: Path) -> Iterator[dict]:
    for path in iter_text_files(directory):
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    yield json.loads(line)


def read_words(directory: Path) -> Iterator[str]:
    """Whitespace separated words (e.g. usernames) of every *.txt file in a directory."""
    for path in iter_text_files(directory):
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                yield from line.split()
