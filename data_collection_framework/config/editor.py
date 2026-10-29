"""Reads and writes the two settings files from the web UI: config.ini and the project's .env.

Files are edited line by line, so comments and the order of the keys stay as they are. Secret values are
never returned; leaving one empty on save keeps the stored value.
"""
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from data_collection_framework.config.settings import CONFIG_FILE, PACKAGE_DIR, SECTION

ENV_FILE = PACKAGE_DIR.parent / ".env"
CONFIG, ENV = "config", "env"

FOLDER = r"[\w][\w.\-/]{0,150}"
NAME = r"[\w.\-]{1,64}"
SECRET = r"[^\s'\"$`\\#]{1,300}"
PORT = r"\d{2,5}"
URI = r"mongodb(\+srv)?://[^\s'\"$`\\#]{1,500}"
KEYWORDS = r"[^\n\r'\"$`\\]{1,500}"
TOKEN_NOTE = "Letters, digits and symbols except spaces, quotes, $, `, \\ and #."


@dataclass(frozen=True)
class Field:
    file: str
    key: str
    label: str
    help: str
    pattern: str
    secret: bool = False


FIELDS = (
    Field(CONFIG, "mongo_uri", "MongoDB connection URI",
          "Used by the Python server. The MONGO_URI environment variable overrides it.", URI, True),
    Field(CONFIG, "word_list_for_streaming", "Streaming keywords",
          "Comma separated keywords used by \"Stream the configured keyword list\".", KEYWORDS),
    Field(CONFIG, "consumer_key", "Twitter API key", "Only needed for the API based collectors.", SECRET, True),
    Field(CONFIG, "consumer_secret", "Twitter API secret", "Pairs with the API key.", SECRET, True),
    Field(CONFIG, "access_key", "Twitter access token", "Generate it after enabling Read permission.", SECRET, True),
    Field(CONFIG, "access_secret", "Twitter access token secret", "Pairs with the access token.", SECRET, True),
    Field(CONFIG, "bearer_token", "Twitter bearer token", "Only needed for streaming.", SECRET, True),
    Field(CONFIG, "file_path_for_timeline_outputs", "Timeline outputs folder",
          "Collected timelines are written here.", FOLDER),
    Field(CONFIG, "file_path_for_followers_outputs", "Followers outputs folder",
          "Collected followers are written here.", FOLDER),
    Field(CONFIG, "file_path_for_list_of_username", "Username list folder",
          "Holds the .txt file with the usernames for the \"from the user list\" commands.", FOLDER),
    Field(CONFIG, "file_path_for_mongo", "Files for MongoDB folder",
          "Folder with .txt files (one JSON document per line) that Store Data can load.", FOLDER),
    Field(CONFIG, "file_path_for_tokenization", "Tokenization folder", "Input of the tokenization tools.", FOLDER),
    Field(CONFIG, "file_path_for_cross_val", "Cross validation folder",
          "At least 2 sub folders (one per class) with text files.", FOLDER),
    Field(CONFIG, "streaming_txt_file", "Streaming files folder", "Streamed tweets are written here.", FOLDER),
    Field(CONFIG, "streaming_db", "Streaming database folder", "Working folder of the streaming collector.", FOLDER),
    Field(ENV, "PY_SERVER_PORT", "Python server port", "Port of the command server.", PORT),
    Field(ENV, "PY_SERVER_TOKEN", "Python server token",
          "Shared secret between PHP and the Python server. Set it whenever the server is not on 127.0.0.1.",
          SECRET, True),
    Field(ENV, "DB_NAME", "MariaDB database", "Database that holds the web users.", NAME),
    Field(ENV, "DB_USER", "MariaDB user", "", NAME),
    Field(ENV, "DB_PASSWORD", "MariaDB user password", "", SECRET, True),
    Field(ENV, "MARIADB_ROOT_PASSWORD", "MariaDB root password", "", SECRET, True),
    Field(ENV, "MONGO_ROOT_PASSWORD", "MongoDB root password", "", SECRET, True),
    Field(ENV, "MONGO_EXPRESS_PASSWORD", "mongo-express password", "", SECRET, True),
)
# Inside Docker the .env file belongs to the host (Docker Compose reads it), so only config.ini is editable.
if os.environ.get("SETTINGS_CONFIG_ONLY"):
    FIELDS = tuple(field for field in FIELDS if field.file == CONFIG)
BY_KEY = {field.key: field for field in FIELDS}
_LINE = re.compile(r"^\s*(\w+)\s*[=:](.*)$")


class SettingsError(ValueError):
    """The submitted settings are invalid; the message is safe to show to the user."""


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def _parse(path: Path) -> Dict[str, str]:
    if not path.is_file():
        return {}
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _LINE.match(line)
        if match and not line.lstrip().startswith(("#", ";")):
            values[match.group(1)] = _unquote(match.group(2).strip())
    return values


def _files(config_file: Path, env_file: Path) -> Dict[str, Path]:
    return {CONFIG: config_file, ENV: env_file}


def read_settings(config_file: Path = CONFIG_FILE, env_file: Path = ENV_FILE) -> List[Dict]:
    """The fields with their current values; secrets only report whether a value is set."""
    stored = {file: _parse(path) for file, path in _files(config_file, env_file).items()}
    rows = []
    for field in FIELDS:
        value = stored[field.file].get(field.key, "")
        rows.append({"file": field.file, "key": field.key, "label": field.label, "help": field.help,
                     "secret": field.secret, "is_set": value != "", "value": "" if field.secret else value})
    return rows


def _render(field: Field, value: str) -> str:
    if field.file == CONFIG:
        return f"{field.key} = {value}"
    return f"{field.key}={value}" if re.fullmatch(r"[\w.\-/:@,]*", value) else f"{field.key}='{value}'"


def _checked(field: Field, value) -> Optional[str]:
    """The cleaned value, or None when a secret was left empty (keep the stored one)."""
    if not isinstance(value, str):
        raise SettingsError(f"{field.label}: invalid value.")
    value = value.strip()
    if value == "":
        if field.secret:
            return None
        raise SettingsError(f"{field.label} cannot be empty.")
    parent_folder = field.key.startswith("file_path") and ".." in value.split("/")
    if not re.fullmatch(field.pattern, value) or parent_folder:
        hint = f" {TOKEN_NOTE}" if field.pattern == SECRET else ""
        raise SettingsError(f"{field.label}: invalid value.{hint}")
    return value


def _field(key: str) -> Field:
    field = BY_KEY.get(key)
    if field is None:
        raise SettingsError(f"Unknown setting: {key}")
    return field


def _validated(updates: Dict[str, str], clear: List[str]) -> Dict[str, Optional[str]]:
    changes: Dict[str, Optional[str]] = {}
    for key, value in updates.items():
        checked = _checked(_field(key), value)
        if checked is not None:
            changes[key] = checked
    for key in clear:
        if not _field(key).secret:
            raise SettingsError(f"Unknown setting: {key}")
        changes[key] = ""
    return changes


def _apply(lines: List[str], fields: List[Field], changes: Dict[str, Optional[str]], section: bool) -> List[str]:
    pending = {field.key: field for field in fields}
    result = []
    in_section = not section
    for line in lines:
        header = line.strip()
        if header.startswith("[") and header.endswith("]"):
            in_section = header == f"[{SECTION}]" or not section
        match = _LINE.match(line) if in_section and not header.startswith(("#", ";")) else None
        if match and match.group(1) in pending:
            field = pending.pop(match.group(1))
            result.append(_render(field, changes[field.key] or ""))
        else:
            result.append(line)
    for field in pending.values():
        result.append(_render(field, changes[field.key] or ""))
    return result


def save_settings(updates: Dict[str, str], clear: Optional[List[str]] = None,
                  config_file: Path = CONFIG_FILE, env_file: Path = ENV_FILE) -> List[str]:
    """Writes the changed values and returns the files that were updated ("config", "env")."""
    changes = _validated(updates, clear or [])
    if not changes:
        raise SettingsError("Nothing to save: enter a new value first.")
    written = []
    for file, path in _files(config_file, env_file).items():
        fields = [BY_KEY[key] for key in changes if BY_KEY[key].file == file]
        if not fields:
            continue
        lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
        if file == CONFIG and not any(line.strip() == f"[{SECTION}]" for line in lines):
            lines.insert(0, f"[{SECTION}]")
        path.write_text("\n".join(_apply(lines, fields, changes, file == CONFIG)) + "\n", encoding="utf-8")
        if file == ENV:
            path.chmod(0o600)
        written.append(file)
    return written
