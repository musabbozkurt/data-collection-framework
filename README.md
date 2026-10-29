# Data Collection Framework

Collects tweets, followers and streams, stores them in MongoDB and analyses them.
A PHP web UI (login + command forms) talks to a Python command server.

```
Browser ──► PHP (Apache, :3000) ──JSON over TCP──► Python server.py (:5555) ──► MongoDB / Twitter API
                │
              MariaDB (users)
```

## Quick start

Requires `Python 3.8+` and `Docker`. Optional: copy [.env.example](.env.example) to `.env` and change the
passwords/token (defaults work for local dev).

1. `docker-compose up -d --build` (MariaDB, phpMyAdmin, PHP app, MongoDB, mongo-express)
2. Start the Python server: `make server` (the first run creates `.venv` and installs the packages; it reads
   `PY_SERVER_TOKEN` and `TWITTER_*` from the environment or `.env`). Stop it with `kill $(lsof -t -i:5555)`
   (macOS/Linux).
    - Without `make`:
      `python3 -m venv .venv && .venv/bin/python -m pip install -r data_collection_framework/requirements.txt`,
      then `.venv/bin/python data_collection_framework/server.py`.
3. Open http://localhost:3000/, sign up, sign in and run commands.

No X login or API credentials are needed for the scraper, profile and MongoDB pages. Credentials for the older API
collectors: see [docs/twitter-api-credentials.md](docs/twitter-api-credentials.md).

Prefer a console? Run `make menu` (same commands).

## Documentation

- [Web UI pages](docs/pages.md): what each page does (scrapers, discovery, store, analytics, cross validation)
- [Twitter / X API credentials](docs/twitter-api-credentials.md): how to get keys and API tier notes
- [Architecture and configuration](docs/architecture.md): project layout, adding a command, `config.ini`, networking, CI

## Services in [docker-compose.yml](docker-compose.yml)

| Service           | URL                       | Credentials                                                |
|-------------------|---------------------------|------------------------------------------------------------|
| PHP app           | http://localhost:3000     | sign up in the UI                                          |
| phpMyAdmin        | http://localhost:8080     | MariaDB user/password from `.env` (default `user`)         |
| mongo-express     | http://localhost:8081     | `mexpress` / `MONGO_EXPRESS_PASSWORD` (default `mexpress`) |
| MariaDB / MongoDB | bound to `127.0.0.1` only | see `.env.example`                                         |

## Tests

```
make test
```

Manual check: http://localhost:3000/ → Sign up → Sign in.
