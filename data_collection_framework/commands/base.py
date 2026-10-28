"""Command pattern: every operation the Server/Menu can run is a declarative Command in a registry."""
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


class CommandError(Exception):
    """Raised for unknown commands or invalid arguments; the message is safe to show to the user."""


@dataclass(frozen=True)
class Param:
    name: str
    label: str
    parser: Callable[[str], Any]

    def parse(self, raw: Any) -> Any:
        if raw is None or str(raw).strip() == "":
            raise CommandError(f"'{self.name}' is required")
        try:
            return self.parser(str(raw).strip())
        except ValueError as error:
            raise CommandError(f"Invalid '{self.name}': {error}") from error


def text(pattern: str) -> Callable[[str], str]:
    compiled = re.compile(pattern)

    def parse(value: str) -> str:
        if not compiled.fullmatch(value):
            raise ValueError("unexpected characters or length")
        return value

    return parse


def integer(minimum: int, maximum: int) -> Callable[[str], int]:
    def parse(value: str) -> int:
        number = int(value)
        if not minimum <= number <= maximum:
            raise ValueError(f"must be between {minimum} and {maximum}")
        return number

    return parse


def decimal(minimum: float, maximum: float) -> Callable[[str], float]:
    def parse(value: str) -> float:
        number = float(value)
        if not minimum < number < maximum:
            raise ValueError(f"must be between {minimum} and {maximum}")
        return number

    return parse


def future_timestamp(value: str) -> datetime:
    moment = datetime.strptime(value, TIMESTAMP_FORMAT)
    if moment <= datetime.now():
        raise ValueError("must be in the future")
    return moment


@dataclass(frozen=True)
class Command:
    name: str
    title: str
    params: Tuple[Param, ...]
    handler: Callable[..., str]

    def run(self, raw_args: Dict[str, Any]) -> str:
        args = {p.name: p.parse(raw_args.get(p.name)) for p in self.params}
        return self.handler(**args)


class CommandRegistry:
    def __init__(self):
        self._commands: Dict[str, Command] = {}

    def register(self, command: Command) -> None:
        self._commands[command.name] = command

    def get(self, name: str) -> Optional[Command]:
        return self._commands.get(name)

    def all(self):
        return list(self._commands.values())

    def execute(self, name: str, args: Dict[str, Any]) -> str:
        command = self.get(name)
        if command is None:
            raise CommandError(f"Unknown command '{name}'")
        return command.run(args)
