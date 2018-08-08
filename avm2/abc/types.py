from __future__ import annotations

from enum import IntFlag
from typing import NamedTuple


class DoABCTagFlags(IntFlag):
    LAZY_INITIALIZE = 1


class DoABCTag(NamedTuple):
    flags: DoABCTagFlags
    name: str
    minor_version: int
    major_version: int
