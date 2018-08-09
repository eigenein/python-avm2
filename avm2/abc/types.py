from __future__ import annotations

from typing import NamedTuple


class ABCFile(NamedTuple):
    minor_version: int
    major_version: int
