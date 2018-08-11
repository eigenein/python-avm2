from __future__ import annotations

from typing import NamedTuple

from avm2.swf.enums import DoABCTagFlags, TagType


class Tag(NamedTuple):
    type_: TagType
    raw: memoryview


class DoABCTag(NamedTuple):
    flags: DoABCTagFlags
    name: str
    abc_file: memoryview
