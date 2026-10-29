"""Helpers for streaming newline-delimited JSON files without loading them fully into memory."""
import json
import re
import shutil
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


USERNAME = re.compile(r"(?a)\w{1,15}")
USERNAMES_FILE = "usernames.txt"
USERNAMES_TEMPLATE = Path(__file__).resolve().parent.parent / "config" / "usernames.template.txt"


def parse_usernames(text: str, label: str = "file") -> list:
    """Usernames in a text: one or more per line, an optional leading @, '#' starts a comment.
    Duplicates are dropped; an invalid name raises ValueError."""
    names = {}
    for number, line in enumerate(text.splitlines(), 1):
        for word in line.split("#", 1)[0].split():
            name = word.lstrip("@")
            if not USERNAME.fullmatch(name):
                raise ValueError(f"{label}, line {number}: '{word}' is not a valid username")
            names.setdefault(name.lower(), name)
    return list(names.values())


def read_usernames(directory: Path) -> list:
    """Usernames of every *.txt file in a directory. Copies the template there when the folder has no file yet."""
    directory = Path(directory)
    if not any(directory.glob("*.txt")):
        directory.mkdir(parents=True, exist_ok=True)
        shutil.copy(USERNAMES_TEMPLATE, directory / USERNAMES_FILE)
    names = {}
    for path in iter_text_files(directory):
        for name in parse_usernames(path.read_text(encoding="utf-8"), path.name):
            names.setdefault(name.lower(), name)
    return list(names.values())


def save_usernames(directory: Path, text: str) -> int:
    """Validates the text and makes it the username list (usernames.txt); returns how many usernames it holds."""
    names = parse_usernames(text, "Uploaded file")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for path in iter_text_files(directory):
        if path.name != USERNAMES_FILE:
            path.rename(path.with_suffix(".txt.bak"))
    (directory / USERNAMES_FILE).write_text(text, encoding="utf-8")
    return len(names)
