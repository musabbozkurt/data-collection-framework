# Data Collection Framework

Collects tweets, followers and streams, stores them in MongoDB and analyses them.
A PHP web UI (login + command forms) talks to a Python command server.

```
Browser ──► PHP (Apache, :3000) ──REST (or GraphQL / TCP)──► Python API (:8000) ──► MongoDB / Twitter API
                │
              MariaDB (users)
```

## Quick start

Requires `Docker`. Optional: copy [.env.example](.env.example) to `.env` and change the passwords/token (defaults work
for local dev).

1. `docker-compose up -d --build` starts everything: PHP app, Python API, MariaDB, phpMyAdmin, MongoDB, mongo-express.
2. Open http://localhost:3000/, sign up, sign in and run commands.

Optional: `make x-login` opens a browser on your machine to save an X session for deeper profile scrapes (the container
shares it through a volume). Use `make server` only for the legacy TCP mode (`API_TRANSPORT=tcp`).
See [docs/api.md](docs/api.md).

No X login or API credentials are needed for the scraper, profile and MongoDB pages. Credentials for the older API
collectors: see [docs/twitter-api-credentials.md](docs/twitter-api-credentials.md).

Prefer a console? Run `make menu` (same commands).

## Documentation

- [Web UI pages](docs/pages.md): what each page does (scrapers, discovery, store, analytics, cross validation)
- [Twitter / X API credentials](docs/twitter-api-credentials.md): how to get keys and API tier notes
- [REST / GraphQL API](docs/api.md): endpoints, token, switching transport
- [Architecture and configuration](docs/architecture.md): project layout, adding a command, `config.ini`, networking, CI

## Services in [docker-compose.yml](docker-compose.yml)

| Service           | URL                       | Credentials                                                |
|-------------------|---------------------------|------------------------------------------------------------|
| PHP app           | http://localhost:3000     | sign up in the UI                                          |
| Python API        | http://127.0.0.1:8000     | `Authorization: Bearer <PY_SERVER_TOKEN>`                  |
| phpMyAdmin        | http://localhost:8080     | MariaDB user/password from `.env` (default `user`)         |
| mongo-express     | http://localhost:8081     | `mexpress` / `MONGO_EXPRESS_PASSWORD` (default `mexpress`) |
| MariaDB / MongoDB | bound to `127.0.0.1` only | see `.env.example`                                         |

## Tests

```
make test
```

Manual check: http://localhost:3000/ → Sign up → Sign in.
