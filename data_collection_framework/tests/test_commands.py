from datetime import datetime, timedelta

import pytest

from data_collection_framework.commands.base import (Command, CommandError, CommandRegistry, Param, future_timestamp,
                                                     integer, text)


def make_registry(calls):
    registry = CommandRegistry()
    registry.register(Command("echo", "Echo", (Param("name", "Name", text(r"[a-z]{1,5}")),
                                               Param("count", "Count", integer(1, 3))),
                              lambda name, count: calls.append((name, count)) or "done"))
    return registry


def test_execute_parses_and_dispatches():
    calls = []
    assert make_registry(calls).execute("echo", {"name": "bob", "count": "2"}) == "done"
    assert calls == [("bob", 2)]


@pytest.mark.parametrize("args", [{"name": "bob"}, {"name": "BOB", "count": 1}, {"name": "bob", "count": 9},
                                  {"name": "bob", "count": "x"}, {"name": "../etc", "count": 1}])
def test_invalid_arguments_are_rejected(args):
    registry = make_registry([])
    with pytest.raises(CommandError):
        registry.execute("echo", args)


def test_unknown_command():
    registry = make_registry([])
    with pytest.raises(CommandError):
        registry.execute("nope", {})


def test_future_timestamp():
    future = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    assert future_timestamp(future) > datetime.now()


def test_past_timestamp_is_rejected():
    with pytest.raises(ValueError):
        future_timestamp("2000-01-01 00:00:00")


def test_real_registry_exposes_all_commands():
    from data_collection_framework.commands.definitions import build_registry
    names = {c.name for c in build_registry().all()}
    assert {"plotlanguage", "storedata", "streamfrominput", "termfrequency", "crossvalidation", "mongoanalytics",
            "mongocrossvalidation"} <= names
    assert len(names) == 50


class FakeCollection:
    def __init__(self, documents):
        self.documents = documents

    def estimated_document_count(self):
        return len(self.documents)

    def find(self, *_):
        return self

    def sort(self, *_):
        return self

    def skip(self, count):
        self.documents = self.documents[count:]
        return self

    def limit(self, count):
        return self.documents[:count]


class FakeDatabase:
    def __init__(self, collections):
        self.collections = collections

    def list_collection_names(self):
        return list(self.collections)

    def __getitem__(self, name):
        return self.collections[name]


class FakeClient:
    def __init__(self, databases):
        self.databases = databases

    def list_database_names(self):
        return list(self.databases)

    def __getitem__(self, name):
        return self.databases[name]


def test_mongo_overview_and_documents_page():
    from data_collection_framework.storage.mongo import documents_page, overview
    client = FakeClient({"admin": FakeDatabase({}),
                         "demo": FakeDatabase({"tweets": FakeCollection(
                             [{"n": i, "text": "x" * 1000} for i in range(5)])})})
    assert overview(client) == {"demo": {"tweets": 5}}
    first = documents_page("demo", "tweets", 1, 2, client)
    assert (first["page"], first["pages"], first["total"]) == (1, 3, 5)
    assert first["documents"][0]["text"].endswith("…")
    client["demo"]["tweets"].documents = [{"n": i} for i in range(5)]
    last = documents_page("demo", "tweets", 99, 2, client)  # out-of-range pages fall back to the last one
    assert last["page"] == 3
    assert [d["n"] for d in last["documents"]] == [4]


def test_storefiles_rejects_unknown_files():
    from data_collection_framework.commands.base import CommandError
    from data_collection_framework.commands.definitions import build_registry
    registry = build_registry()
    with pytest.raises(CommandError, match="Unknown file"):
        registry.execute("storefiles", {"database": "d", "collection": "c", "files": "data_folders/nope.txt"})
    with pytest.raises(CommandError, match="Unknown file"):
        registry.execute("storefiles",
                         {"database": "d", "collection": "c", "files": "data_folders/../config/config.ini"})
