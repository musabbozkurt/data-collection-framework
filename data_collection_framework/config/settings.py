"""Application settings, loaded lazily once. Environment variables override the config file."""
import configparser
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

PACKAGE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = Path(__file__).resolve().parent / "config.ini"
SECTION = "your-config"

_PATH_KEYS = (
    "file_path_for_timeline_outputs",
    "file_path_for_followers_outputs",
    "file_path_for_list_of_username",
    "file_path_for_mongo",
    "file_path_for_tokenization",
    "file_path_for_cross_val",
    "streaming_txt_file",
    "streaming_db",
)


@dataclass(frozen=True)
class Settings:
    file_path_for_timeline_outputs: Path
    file_path_for_followers_outputs: Path
    file_path_for_list_of_username: Path
    file_path_for_mongo: Path
    file_path_for_tokenization: Path
    file_path_for_cross_val: Path
    streaming_txt_file: Path
    streaming_db: Path
    consumer_key: str
    consumer_secret: str
    access_key: str
    access_secret: str
    bearer_token: str
    word_list_for_streaming: tuple
    mongo_uri: str
    server_host: str
    server_port: int
    server_token: str

    def ensure_directories(self) -> None:
        for key in _PATH_KEYS:
            getattr(self, key).mkdir(parents=True, exist_ok=True)


def _default_mongo_uri() -> str:
    """Matches the MongoDB container of docker-compose.yml, which requires the root credentials."""
    password = quote_plus(os.environ.get("MONGO_ROOT_PASSWORD", "password"))
    return f"mongodb://root:{password}@localhost:27017/?authSource=admin"


def _load(config_file: Path = CONFIG_FILE) -> Settings:
    parser = configparser.RawConfigParser()
    parser.read(config_file)
    section = parser[SECTION] if parser.has_section(SECTION) else {}

    def get(key: str, default: str = "") -> str:
        return section.get(key, default).strip()

    def secret(key: str) -> str:
        return os.environ.get(f"TWITTER_{key.upper()}") or get(key)

    paths = {key: PACKAGE_DIR / get(key, f"data_folders/{key}/") for key in _PATH_KEYS}
    keywords = tuple(w.strip() for w in get("word_list_for_streaming").split(",") if w.strip())

    return Settings(
        **paths,
        consumer_key=secret("consumer_key"),
        consumer_secret=secret("consumer_secret"),
        access_key=secret("access_key"),
        access_secret=secret("access_secret"),
        bearer_token=secret("bearer_token"),
        word_list_for_streaming=keywords,
        mongo_uri=os.environ.get("MONGO_URI") or get("mongo_uri", _default_mongo_uri()),
        server_host=os.environ.get("PY_SERVER_HOST", "127.0.0.1"),
        server_port=int(os.environ.get("PY_SERVER_PORT", "5555")),
        server_token=os.environ.get("PY_SERVER_TOKEN", ""),
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = _load()
    settings.ensure_directories()
    return settings
