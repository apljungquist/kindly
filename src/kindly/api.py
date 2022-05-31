"""Specification of public interface for plugins"""
from __future__ import annotations

import pathlib
import sys
from typing import Iterable, List, Optional

if sys.version_info[1] < 8:
    from typing_extensions import Protocol
else:
    from typing import Protocol


class V1Command(Protocol):
    @property
    def name(self) -> str:
        """Return name of command"""

    @property
    def help(self) -> Optional[str]:
        """Return help message, if any

        If None is returned the help message will be chosen by kindly.
        """

    def __call__(self, args: List[str]) -> None:
        """Implementation of the command

        Receives any arguments that were not consumed by parsing.
        """


class V1Command(Protocol):
    @property
    def name(self) -> str:
        """Return name of command"""

    @property
    def help(self) -> Optional[str]:
        """Return help message, if any

        If None is returned the help message will be chosen by kindly.
        """

    def __call__(self, args: List[str]) -> None:
        """Implementation of the command

        Receives any arguments that were not consumed by parsing.
        """


class Provider(Protocol):
    # pylint: disable=too-few-public-methods
    def __init__(self, cwd: pathlib.Path) -> None:
        ...

    def v1_commands(self) -> Iterable[V1Command]:
        ...

    # It would be nice with a bit more interactivity.
    # v2 will probably delegate parsing to providers.
    # v3 will probably delegate parsing and tab completion to providers.
    # Some notes on autocompletion:
    # * shtab seems to generate completions ahead of time making it unsuitable for context aware parsers
    # * argcomplete targets primarily bash, but it sounds like bash-level completions is available in zsh
    #   Getting this working in bash was actually quite easy though I admittedly have not tried any non-trivial parsers.
    #   It is not self contained but it may be possible to bootstrap the autocompletion in init_enb.sh.
    #   Or at least make it easy by providing an rc/fragment that can be sourced.
    # * pyzshcomplete does not support subparsers
    # * click?
