from __future__ import annotations

from io import BytesIO

import pytest

from avm2.swf.parser import parse
from tests.utils import SWF_1, SWF_2, SWF_3, SWF_4


@pytest.mark.parametrize('io, n_tags', [
    (BytesIO(SWF_1), 5),
    (BytesIO(SWF_2), 10),
    (BytesIO(SWF_3), 1995),
    (BytesIO(SWF_4), 9),
])
def test_parse(io: BytesIO, n_tags: int):
    assert len(list(parse(io))) == n_tags
