# Architecture and configuration

## Project layout

- `src/` PHP front end (PDO + prepared statements, `password_hash`, CSRF tokens, escaped output)
    - `lib/` small classes: `Database`, `UserRepository`, `Auth`, `Csrf`, `PythonServerClient`, `CommandCatalog`
    - `index.php` renders every command form from `CommandCatalog` (no per-command code)
- `data_collection_framework/` Python back end
    - `commands/` Command pattern: `base.py` (Command, Param validators, registry) and `definitions.py`
    - `api/app.py` REST + GraphQL (served by `api_server.py`), `server.py` legacy TCP loop, all through
      `commands/dispatch.py`; `menu.py` console UI; both only call the registry
    - `config/settings.py` lazy, immutable settings (env vars override the config file)
    - `storage/` shared MongoDB client/repository (batched inserts) and streaming file readers
    - collectors (`TweetCollector`, `FollowerCollector`, `StreamCollector`, `MongoWriter`) receive their dependencies
      by injection
    - `Analysis` is table-driven (one `Metric` per plot), `nlp/` holds n-grams, tokenization and term statistics

## Adding a command

1. Python: register a `Command(name, title, params, handler)` in `commands/definitions.py`.
2. PHP: add the same name and fields to `src/lib/CommandCatalog.php`.

The Python side is authoritative for validation; the PHP side only checks required/numeric values.

## Settings in [config.ini](../data_collection_framework/config/config.ini)

- `word_list_for_streaming` comma separated keywords for `streamfromlist`
- `file_path_for_*` / `streaming_txt_file` data folders (relative to `data_collection_framework/`, created on start):
    - `file_path_for_list_of_username`: `*.txt` files with the usernames for the "from the user list" commands: one or
      more per line, optional `@`, `#` comments.
      [usernames.template.txt](../data_collection_framework/config/usernames.template.txt) is copied there as
      `usernames.txt` the first time the list is needed
    - `file_path_for_mongo`: `*.txt` files with one tweet JSON per line (used by store data and the plots)
    - `streaming_txt_file`: where streamed tweets are written (used by term frequency)
    - `file_path_for_cross_val`: at least 2 sub folders (one per class) with text files
- `mongo_uri` (or `MONGO_URI`), `PY_SERVER_HOST`, `PY_SERVER_PORT`, `PY_SERVER_TOKEN`

## Networking

- The PHP container reaches the server through `host.docker.internal`.
- Docker Desktop (macOS/Windows) works with the default `127.0.0.1` bind. On Linux set `PY_SERVER_HOST=0.0.0.0` for
  the server and **always set `PY_SERVER_TOKEN`**, because the server executes commands.

## Testing and CI

GitHub Actions (`.github/workflows/ci.yml`) runs on every push and pull request: pytest on Python 3.15, a `php -l`
syntax check of `src/`, and a smoke test (`scripts/smoke_test.sh`) that starts the whole compose stack, signs up and in,
loads the pages and checks that PHP reaches the Python server. Run the smoke test locally against a running stack with
`bash scripts/smoke_test.sh`.

## Notes

- Old MD5 password hashes are not migrated; the schema (`db_scripts/`) only runs on a fresh DB volume
  (`docker-compose down -v` to reset).
