"""Various utils related to handling file system paths"""
import itertools
import pathlib


def find_upwards(start: pathlib.Path, name: str) -> pathlib.Path:
    for parent in itertools.chain([start], start.parents):
        path = parent / name
        if path.exists():
            return path
    raise FileNotFoundError
