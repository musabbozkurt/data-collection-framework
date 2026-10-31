# AGENTS.md (project guide for AI agents and contributors)

Guide for people and AI agents changing this project. Keep it short and current; details live in this `docs/` folder.

## What it is

A PHP web UI (login + command forms) that calls a Python back end through one command registry. Data goes to
MongoDB (collected tweets/profiles) and MariaDB (users only). Everything starts with `docker-compose up -d --build`.

```
Browser -> PHP (src/, :3000) --REST (default) / GraphQL / TCP--> Python API (:8000) -> MongoDB / X
                |
            MariaDB (users)
```

## Layout

| Path                                                    | Purpose                                                                               |
|---------------------------------------------------------|---------------------------------------------------------------------------------------|
| `src/*.php`                                             | One page per file (`mongo.php`, `store.php`, `analytics.php`, `settings.php`, …)      |
| `src/lib/`                                              | PHP classes: `Auth`, `Csrf`, `Database`, `CommandCatalog`, `*Client` (transports)     |
| `src/templates/`, `src/css/`, `src/js/`                 | Shared layout/menu, styles, scripts (CSP: external files only, no inline)             |
| `data_collection_framework/commands/`                   | `base.py` (Command, Param validators), `definitions.py` (the registry), `dispatch.py` |
| `data_collection_framework/api/app.py`                  | REST + GraphQL over the registry; `api_server.py` starts it                           |
| `data_collection_framework/server.py`, `menu.py`        | Legacy TCP server and console menu (same registry)                                    |
| `data_collection_framework/config/`                     | `settings.py` (immutable, env overrides `config.ini`), `editor.py` (Settings page)    |
| `data_collection_framework/storage/`, `nlp/`            | MongoDB access, file readers, tokenization / n-grams                                  |
| `data_collection_framework/tests/`                      | pytest                                                                                |
| `docs/`, `README.md`                                    | `pages.md`, `architecture.md`, `api.md`, `twitter-api-credentials.md`                 |
| `Dockerfile`, `Dockerfile.python`, `docker-compose.yml` | PHP image, Python API image, the whole stack                                          |

## Adding or changing a command

1. Python: register `Command(name, title, params, handler)` in `commands/definitions.py`. Use the validators in
   `base.py`; raise `CommandError` for user-facing problems (the message is shown on the page).
2. REST name: add `name -> kebab-case` to `SLUGS` in `api/app.py` and, for new parameter names, a value in `EXAMPLES`.
   Old names keep working; PHP still sends the plain name.
3. PHP: add the command to `src/lib/CommandCatalog.php` and/or call it from a page via `PythonServerClient::fromEnv()`.
4. Update the command-count assertion in `tests/test_commands.py`, add tests, update `pages.md` / `api.md`.

Handlers return a string; all transports reply `{"ok": bool, "message": str}`. Optional params use the `-` sentinel.

## Standards

- **Python:** type hints, small functions, constructor injection, no global state; module-level constants instead of
  repeated literals; dedicated exceptions instead of bare `Exception`. Bound/simplify regexes (no super-linear
  backtracking; prefer `\w`). Never log secrets.
- **PHP 8.5:** `declare(strict_types=1)`, PDO prepared statements, `htmlspecialchars` on all output, CSRF token on every
  POST, `password_hash`. Throw `AppException` for user-facing errors.
- **Sonar-friendly (the project is scanned):** max 3 returns per function, cognitive complexity <= 15, no nested
  ternaries (use `if`), labels tied to inputs (`for`/`id`), no duplicated string literals (use constants), one
  assertion per test and one raising call per `pytest.raises`, FastAPI params use `Annotated`.
- **JS/CSS:** `.dataset` over `getAttribute`, optional chaining, `!==`; no inline scripts or styles (CSP).
- **UI text:** every page and setting has a short, clear description; keep menu names and page titles consistent.
- **Security:** token auth via `PY_SERVER_TOKEN`; keep ports bound to `127.0.0.1`; the Settings page is admin-only
  (lowest user id) and never returns secrets.

## Run, test, verify

```
docker-compose up -d --build        # whole stack: http://localhost:3000 (UI), http://127.0.0.1:8000/docs (API)
make test                           # pytest (creates .venv)
bash scripts/smoke_test.sh          # signs up a throw-away user and checks pages + PHP -> Python
make x-login                        # one-time X sign-in on the host (container is headless)
make server                         # legacy TCP mode (API_TRANSPORT=tcp)
```

PHP is not installed on the host: lint inside the container, e.g.
`docker compose exec -T php-app php -l /var/www/html/<file>`. `src/` is mounted read-only, so PHP edits show up
without a rebuild; Python changes need `docker compose up -d --build python-api`.

## Gotchas

- Settings changes need a Python restart (`docker compose restart python-api`). In Docker, `MONGO_URI` comes from
  Compose and only `config.ini` is editable on the Settings page.
- On Linux set `APP_UID`/`APP_GID` in `.env` if the project folders are not owned by uid 1000.
- The X scraper works without login (latest posts only); deeper scrolling needs `make x-login`.
- Generated or local files stay out of git: `.env`, `.venv`, `pypro.log`, collected data.
- Docker tags are pinned (`php:8.5.12-apache`, `python:3.15.2-slim`, DB images); bump them deliberately and rerun the
  smoke test. `.dockerignore` and `Dockerfile.python.dockerignore` are separate per image.
- The user commits changes themselves; do not commit unless asked.
