"""Runs one command and builds the {"ok", "message"} reply shared by the TCP, REST and GraphQL front ends."""
import hmac
from typing import Any, Dict

from data_collection_framework.commands.base import CommandError, CommandRegistry
from data_collection_framework.config.settings import Settings
from data_collection_framework.logger import get_logger

log = get_logger("dispatch")


def authorized(settings: Settings, token: Any) -> bool:
    return not settings.server_token or hmac.compare_digest(str(token or ""), settings.server_token)


def run_command(registry: CommandRegistry, settings: Settings, command: str, args: Any, token: Any) -> Dict[str, Any]:
    if not authorized(settings, token):
        return _reply(False, "Unauthorized")
    try:
        args = args or {}
        if not isinstance(args, dict):
            raise CommandError("'args' must be an object")
        log.info("Request: command=%s args=%s", command, args)
        return _reply(True, registry.execute(str(command), args))
    except CommandError as error:
        return _reply(False, str(error))
    except Exception as error:  # keep the server alive whatever a command does
        return _reply(False, _failure_message(error))


def _reply(ok: bool, message: Any) -> Dict[str, Any]:
    return {"ok": ok, "message": message}


def _failure_message(error: Exception) -> str:
    response = getattr(error, "response", None)
    if response is not None and getattr(response, "status_code", None):
        log.error("Twitter API error: %s", error)
        return f"Twitter API error: {str(error).strip()}"
    log.exception("Command failed")
    return "Command failed; see the server log"
