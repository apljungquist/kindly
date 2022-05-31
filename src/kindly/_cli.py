import argparse
import dataclasses
import logging
import os
import pathlib
import subprocess
from textwrap import dedent
from typing import Any, List, Optional

import argcomplete
import pkg_resources

from kindly import api

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class _V1Adapter:
    v1_command: api.V1Command

    @property
    def name(self) -> str:
        return self.v1_command.name

    @property
    def help(self) -> Optional[str]:
        return self.v1_command.help

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("args", nargs="*")

    def __call__(self, args: argparse.Namespace) -> None:
        self.v1_command(args.args)


def _parser(cwd: pathlib.Path) -> argparse.ArgumentParser:
    program_parser = argparse.ArgumentParser(
        description=dedent(
            """\
            Enable tab completion by running
            `eval "$(register-python-argcomplete kindly)"`.
            """
        )
    )
    program_subparsers = program_parser.add_subparsers(required=True)

    # TODO: Define strategy for dealing with conflicts
    # Maybe enable the user to disable (distribution,command) tuples in the tools
    # section of pyproject.toml.
    # One distribution could still provide the same command multiple times (this
    # distribution provides any command that the user specifies in the aliases
    # file); this should probably be an error.

    for entry_point in pkg_resources.iter_entry_points("kindly.provider"):
        cls = entry_point.load()
        provider: api.Provider = cls(cwd)

        # TODO: Better type hints
        commands: dict[str, Any] = {}

        if hasattr(provider, "v1_commands"):
            for command in provider.v1_commands():
                commands[command.name] = _V1Adapter(command)

        if hasattr(provider, "v2_commands"):
            for command in provider.v2_commands():  # type: ignore
                commands[command.name] = command

        for name, command in sorted(commands.items()):
            command_parser = program_subparsers.add_parser(
                name,
                help=name.capitalize().replace("_", " ")
                if command.help is None
                else command.help,
            )
            command.configure_parser(command_parser)  # type: ignore
            command_parser.set_defaults(func=command)

    return program_parser


def cli(cwd: pathlib.Path, args: List[str]) -> None:
    # noinspection PyUnresolvedReferences
    # pylint: disable=protected-access
    logging.basicConfig(level=logging._nameToLevel[os.environ.get("LEVEL", "WARNING")])
    parser = _parser(cwd)
    argcomplete.autocomplete(parser)
    parsed = parser.parse_args(args)
    try:
        parsed.func(parsed)
    except subprocess.SubprocessError:
        parser.exit(1)
