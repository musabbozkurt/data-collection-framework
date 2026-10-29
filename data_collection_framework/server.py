#!/usr/bin/env python3
"""Line-delimited JSON command server used by the PHP front end.

Request : {"command": "plotlanguage", "args": {"bars": 5}, "token": "..."}\n
Response: {"ok": true, "message": "..."}\n
"""
import json
import os
import socket
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)))

from data_collection_framework.commands.base import CommandError, CommandRegistry  # noqa: E402
from data_collection_framework.commands.definitions import build_registry  # noqa: E402
from data_collection_framework.commands.dispatch import run_command  # noqa: E402
from data_collection_framework.config.settings import Settings, get_settings  # noqa: E402
from data_collection_framework.logger import get_logger  # noqa: E402

log = get_logger("server")
MAX_REQUEST_BYTES = 64 * 1024


def read_request(conn: socket.socket) -> dict:
    buffer = b""
    while b"\n" not in buffer and len(buffer) < MAX_REQUEST_BYTES:
        chunk = conn.recv(4096)
        if not chunk:
            break
        buffer += chunk
    try:
        request = json.loads(buffer.split(b"\n", 1)[0].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CommandError("Request is not valid JSON") from error
    if not isinstance(request, dict):
        raise CommandError("Request must be a JSON object")
    return request


def handle(conn: socket.socket, registry: CommandRegistry, settings: Settings) -> dict:
    try:
        request = read_request(conn)
    except CommandError as error:
        return {"ok": False, "message": str(error)}
    return run_command(registry, settings, request.get("command", ""), request.get("args"), request.get("token"))


def serve(settings: Settings = None) -> None:
    settings = settings or get_settings()
    registry = build_registry(settings)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((settings.server_host, settings.server_port))
        server.listen(5)
        log.info("Listening on %s:%s", settings.server_host, settings.server_port)
        while True:
            conn, addr = server.accept()
            with conn:
                log.info("Connection from %s:%s", *addr)
                response = handle(conn, registry, settings)
                try:
                    conn.sendall(json.dumps(response).encode("utf-8") + b"\n")
                except OSError:
                    log.warning("Client went away before the response was sent")


if __name__ == "__main__":
    try:
        serve()
    except KeyboardInterrupt:
        log.info("Server stopped")
