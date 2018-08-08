from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import pytest

import tests
from avm2.swf.parser import parse

SWF_1: BinaryIO = BytesIO(bytes.fromhex(
    '465753034F0000007800055F00000FA000000C01004302FFFFFFBF0023000000'
    '010070FB49970D0C7D50000114000000000125C9920D21ED488765303B6DE1D8'
    'B40000860606010001000040000000'
))
SWF_2: BinaryIO = (Path(tests.__file__).parent / 'heroes.swf').open('rb')


@pytest.mark.parametrize('io, n_tags', [
    (SWF_1, 5),
    (SWF_2, 10),
])
def test_parse(io: BinaryIO, n_tags: int):
    assert len(list(parse(io))) == n_tags
