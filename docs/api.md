# API

`docker-compose up -d --build` starts the Python API (`python-api`, http://127.0.0.1:8000). Every transport runs the
same command registry and answers `{"ok": bool, "message": str}`.

If `PY_SERVER_TOKEN` is set, send `Authorization: Bearer <token>` (REST/GraphQL) or `"token"` (TCP).

## REST

```
curl http://127.0.0.1:8000/health
curl -H "Authorization: Bearer $PY_SERVER_TOKEN" http://127.0.0.1:8000/api/commands
curl -X POST -H "Authorization: Bearer $PY_SERVER_TOKEN" -H "Content-Type: application/json" \
  -d '{"args": {}}' http://127.0.0.1:8000/api/commands/mongo-databases
```

Endpoints use kebab-case (`analysis-metrics`); the old names (`analysismetrics`) still work. `/docs` lists every
command with parameters and an example body.

Errors: 401 bad token, 400 invalid JSON, 413 body over 64 KB. Command failures are `ok: false` with HTTP 200.
Interactive docs: http://127.0.0.1:8000/docs

## GraphQL

`POST /graphql`:

```
{ commands }
mutation { run(name: "mongodatabases", args: {}) { ok message } }
```

## Choosing the transport used by PHP

Set `API_TRANSPORT` in `.env`: `rest` (default), `graphql`, or `tcp` (legacy; run `make server` on the host and
set `PY_SERVER_HOST`/`PY_SERVER_PORT`). Then `docker-compose up -d`.

## Notes

- The container is headless. Save an X session on your machine with `make x-login`; it is shared by a volume.
- Keep `PY_SERVER_TOKEN` set if the port is exposed beyond localhost.
