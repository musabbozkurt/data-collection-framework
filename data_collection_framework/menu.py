#!/usr/bin/env python3
"""Interactive console menu built from the same command registry as the Server."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)))

from data_collection_framework.commands.base import CommandError  # noqa: E402
from data_collection_framework.commands.definitions import build_registry  # noqa: E402
from data_collection_framework.logger import get_logger  # noqa: E402

log = get_logger("menu")


def main() -> None:
    commands = build_registry().all()
    while True:
        print("-" * 30, "WELCOME TO DATA COLLECTION FRAMEWORK", "-" * 30)
        for number, command in enumerate(commands, 1):
            print(f"{number}. {command.title}")
        print(f"{len(commands) + 1}. Exit")
        choice = input(f"Enter your choice [1-{len(commands) + 1}]: ").strip()
        if not choice.isdigit() or not 1 <= int(choice) <= len(commands) + 1:
            print("Invalid choice")
            continue
        if int(choice) == len(commands) + 1:
            return
        command = commands[int(choice) - 1]
        try:
            args = {param.name: input(f"{param.label}: ") for param in command.params}
            print(command.run(args))
        except CommandError as error:
            print(f"Error: {error}")
        except Exception:
            log.exception("Command failed")
            print("Command failed; see pypro.log")


if __name__ == "__main__":
    main()
