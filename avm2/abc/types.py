from __future__ import annotations

from enum import IntFlag
from typing import NamedTuple


class ABCFileFlags(IntFlag):
    LAZY_INITIALIZE = 1


class ABCFile(NamedTuple):
    flags: ABCFileFlags
    name: str
    minor_version: int
    major_version: int
