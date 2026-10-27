from pathlib import Path

from data_collection_framework.logger import get_logger
from data_collection_framework.storage.mongo import MongoRepository

log = get_logger(__name__)
PAGE_SIZE = 1000  # maximum page size of the v2 followers endpoint


class FollowerCollector:
    """Collects the followers of a user (Twitter API v2) into a text file and MongoDB."""

    def __init__(self, client, output_dir: Path, repository_factory=MongoRepository):
        self._client = client
        self._output_dir = Path(output_dir)
        self._repository_factory = repository_factory

    def write_on_file(self, screen_name: str, database: str = "Followers") -> int:
        user_id = self._client.get_user(username=screen_name).data.id
        names = []
        token = None
        while True:
            response = self._client.get_users_followers(user_id, max_results=PAGE_SIZE, pagination_token=token)
            names.extend(user.username for user in response.data or [])
            token = (response.meta or {}).get("next_token")
            if not token:
                break

        with open(self._output_dir / f"{screen_name}.txt", "a", encoding="utf-8") as handle:
            handle.writelines(name + "\n" for name in names)
        self._repository_factory(database, screen_name).insert_many(
            {f"Follower of {screen_name}": name} for name in names)
        log.info("Collected %s followers of %s", len(names), screen_name)
        return len(names)
