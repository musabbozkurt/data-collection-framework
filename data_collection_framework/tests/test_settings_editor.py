import pytest

from data_collection_framework.config import editor

CONFIG = "[your-config]\n# comment\nmongo_uri = mongodb://old\nstreaming_db = data/db/\n"
ENV = "# env\nPY_SERVER_PORT=5555\nPY_SERVER_TOKEN=old-token\n"


@pytest.fixture
def files(tmp_path):
    config, env = tmp_path / "config.ini", tmp_path / ".env"
    config.write_text(CONFIG, encoding="utf-8")
    env.write_text(ENV, encoding="utf-8")
    return config, env


def row(rows, key):
    return next(item for item in rows if item["key"] == key)


def test_read_hides_secrets(files):
    rows = editor.read_settings(*files)
    token = row(rows, "PY_SERVER_TOKEN")
    assert token["is_set"] is True
    assert token["value"] == ""
    assert row(rows, "PY_SERVER_PORT")["value"] == "5555"


def test_save_updates_values_and_keeps_comments(files):
    written = editor.save_settings({"PY_SERVER_PORT": "6000", "streaming_db": "other/"}, [], *files)
    assert sorted(written) == ["config", "env"]
    assert "PY_SERVER_PORT=6000" in files[1].read_text(encoding="utf-8")
    assert "# comment" in files[0].read_text(encoding="utf-8")
    assert "streaming_db = other/" in files[0].read_text(encoding="utf-8")


def test_empty_secret_keeps_stored_value(files):
    editor.save_settings({"PY_SERVER_TOKEN": "", "PY_SERVER_PORT": "6001"}, [], *files)
    assert "PY_SERVER_TOKEN=old-token" in files[1].read_text(encoding="utf-8")


def test_secret_can_be_cleared(files):
    editor.save_settings({}, ["PY_SERVER_TOKEN"], *files)
    assert "PY_SERVER_TOKEN=\n" in files[1].read_text(encoding="utf-8")


def test_missing_key_is_appended(files):
    editor.save_settings({"bearer_token": "abc123"}, [], *files)
    assert "bearer_token = abc123" in files[0].read_text(encoding="utf-8")


def test_special_characters_are_quoted_in_env(files):
    editor.save_settings({"DB_PASSWORD": "p@ss!w*rd"}, [], *files)
    assert "DB_PASSWORD='p@ss!w*rd'" in files[1].read_text(encoding="utf-8")


@pytest.mark.parametrize("key,value", [
    ("PY_SERVER_PORT", "abc"),
    ("file_path_for_mongo", "../outside"),
    ("file_path_for_mongo", "/etc"),
    ("DB_PASSWORD", "bad'quote"),
    ("DB_PASSWORD", "line\nbreak"),
    ("mongo_uri", "http://not-mongo"),
    ("unknown_key", "x"),
])
def test_invalid_values_are_rejected(files, key, value):
    with pytest.raises(editor.SettingsError):
        editor.save_settings({key: value}, [], *files)


def test_nothing_to_save_is_an_error(files):
    with pytest.raises(editor.SettingsError):
        editor.save_settings({"PY_SERVER_TOKEN": ""}, [], *files)


def test_env_file_is_created_with_only_the_changed_keys(tmp_path):
    config, env = tmp_path / "config.ini", tmp_path / ".env"
    config.write_text(CONFIG, encoding="utf-8")
    editor.save_settings({"PY_SERVER_PORT": "6000"}, [], config, env)
    assert env.read_text(encoding="utf-8") == "PY_SERVER_PORT=6000\n"
