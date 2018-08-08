from __future__ import annotations

from io import BytesIO
from typing import BinaryIO

import pytest

from avm2.swf.parser import parse
from tests.utils import open_test_swf

SWF_1: BinaryIO = BytesIO(bytes.fromhex(
    '465753034F0000007800055F00000FA000000C01004302FFFFFFBF0023000000'
    '010070FB49970D0C7D50000114000000000125C9920D21ED488765303B6DE1D8'
    'B40000860606010001000040000000'
))
SWF_2 = open_test_swf('heroes.swf')
SWF_3 = open_test_swf('Farm_d_13_9_2_2198334.swf')
SWF_4 = open_test_swf('EpicGame.swf')


@pytest.mark.parametrize('io, n_tags', [
    (SWF_1, 5),
    (SWF_2, 10),
    (SWF_3, 1995),
    (SWF_4, 9),
])
def test_parse(io: BinaryIO, n_tags: int):
    assert len(list(parse(io))) == n_tags
