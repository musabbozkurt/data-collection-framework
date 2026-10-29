import json
import socket
import threading
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from data_collection_framework import server
from data_collection_framework.api.app import create_app
from data_collection_framework.commands.base import Command, CommandRegistry, Param, integer
from data_collection_framework.config.settings import get_settings

TOKEN = "secret-token"


@pytest.fixture
def parts():
    registry = CommandRegistry()
    registry.register(Command("double", "Double a number", (Param("n", "Number", integer(1, 100)),),
                              lambda n: str(n * 2)))
    registry.register(Command("boom", "Always fails", (), lambda: 1 / 0))
    settings = replace(get_settings(), server_token=TOKEN)
    return registry, settings


@pytest.fixture
def client(parts):
    registry, settings = parts
    return TestClient(create_app(settings, registry))


AUTH = {"Authorization": f"Bearer {TOKEN}"}


def test_health_needs_no_token(client):
    assert client.get("/health").json() == {"status": "ok", "commands": 2}


def test_rest_runs_a_command(client):
    reply = client.post("/api/commands/double", json={"args": {"n": 21}}, headers=AUTH)
    assert reply.json() == {"ok": True, "message": "42"}


def test_rest_reports_validation_errors_as_ok_false(client):
    reply = client.post("/api/commands/double", json={"args": {"n": 0}}, headers=AUTH)
    assert reply.json()["ok"] is False


def test_rest_unknown_command_and_server_error_are_replies(client):
    assert client.post("/api/commands/nope", json={}, headers=AUTH).json()["ok"] is False
    assert client.post("/api/commands/boom", json={}, headers=AUTH).json()["message"].startswith("Command failed")


def test_rest_requires_the_token(client):
    assert client.post("/api/commands/double", json={"args": {"n": 1}}).status_code == 401
    assert client.get("/api/commands").status_code == 401


def test_rest_rejects_bad_bodies(client):
    assert client.post("/api/commands/double", content="not json", headers=AUTH).status_code == 400
    assert client.post("/api/commands/double", json=[1], headers=AUTH).status_code == 400
    assert client.post("/api/commands/double", content="x" * 70000, headers=AUTH).status_code == 413


def test_rest_lists_commands(client):
    names = [item["name"] for item in client.get("/api/commands", headers=AUTH).json()]
    assert names == ["double", "boom"]


def graphql(client, query, headers=AUTH):
    return client.post("/graphql", json={"query": query}, headers=headers).json()


def test_graphql_runs_a_command(client):
    data = graphql(client, 'mutation { run(name: "double", args: {n: 4}) { ok message } }')
    assert data["data"]["run"] == {"ok": True, "message": "8"}


def test_graphql_lists_commands(client):
    data = graphql(client, "{ commands { name params { name } } }")
    assert data["data"]["commands"][0] == {"name": "double", "params": [{"name": "n"}]}


def test_graphql_requires_the_token(client):
    data = graphql(client, 'mutation { run(name: "double", args: {n: 4}) { ok message } }', headers={})
    assert data["data"]["run"] == {"ok": False, "message": "Unauthorized"}
    assert graphql(client, "{ commands { name } }", headers={})["errors"]


def test_all_transports_give_the_same_reply(parts, client):
    registry, settings = parts
    settings = replace(settings, server_host="127.0.0.1", server_port=0)
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)

    def serve_once():
        conn, _ = listener.accept()
        with conn:
            conn.sendall(json.dumps(server.handle(conn, registry, settings)).encode() + b"\n")

    thread = threading.Thread(target=serve_once)
    thread.start()
    with socket.create_connection(listener.getsockname()) as conn:
        conn.sendall(json.dumps({"command": "double", "args": {"n": 5}, "token": TOKEN}).encode() + b"\n")
        tcp = json.loads(conn.makefile().readline())
    thread.join()
    listener.close()
    rest = client.post("/api/commands/double", json={"args": {"n": 5}}, headers=AUTH).json()
    gql = graphql(client, 'mutation { run(name: "double", args: {n: 5}) { ok message } }')["data"]["run"]
    assert tcp == rest == gql == {"ok": True, "message": "10"}


def test_kebab_case_and_legacy_names_both_work():
    client = TestClient(create_app(replace(get_settings(), server_token="")))
    paths = client.get("/openapi.json").json()["paths"]
    assert "/api/commands/analysis-metrics" in paths
    assert "example" in paths["/api/commands/analysis-metrics"]["post"]["requestBody"]["content"]["application/json"]
    for name in ("mongo-databases", "mongodatabases"):
        assert client.post(f"/api/commands/{name}", json={}).status_code == 200
