"""A simple example of a pure python provider"""
from __future__ import annotations

import argparse
import dataclasses
import itertools
import pathlib
from typing import Any, Iterable, Optional

from argcomplete import SuppressCompleter


@dataclasses.dataclass(frozen=True)
class GreetingCommand:
    name: str
    help: Optional[str]
    subject: str

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        # TODO: Find better way to play nice with mypy
        action: Any = parser.add_argument(
            "companion", nargs="?", help="Name of your companion"
        )
        action.completer = SuppressCompleter

    def __call__(self, args: argparse.Namespace) -> None:
        print(f"Hello {self.subject.capitalize()}!")
        companion = args.companion
        if companion:
            print(f"I see you brought {companion.capitalize()}.")
        else:
            print("Are you the brain specialist?")


class GreetingProvider:
    # pylint: disable=too-few-public-methods

    def __init__(self, cwd: pathlib.Path) -> None:
        self._cwd = cwd

    def v2_commands(self) -> Iterable[GreetingCommand]:
        for path in itertools.chain([self._cwd], self._cwd.parents):
            if path.parent.name == "home":
                yield GreetingCommand("greet", "Say hello", path.name)
                return
