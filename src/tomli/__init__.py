"""Compatibility shim for :mod:`tomli` using Python's :mod:`tomllib`."""

from __future__ import annotations

from typing import Any, BinaryIO

import tomllib


def load(fp: BinaryIO) -> Any:
    return tomllib.load(fp)


def loads(data: bytes | str) -> Any:
    if isinstance(data, bytes):
        return tomllib.loads(data.decode("utf-8"))
    return tomllib.loads(data)


__all__ = ["load", "loads"]
