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
    assert {"plotlanguage", "storedata", "streamfrominput", "termfrequency", "crossvalidation"} <= names
    assert len(names) == 24
