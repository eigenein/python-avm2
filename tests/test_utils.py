from io import BytesIO

import pytest

from avm2.utils import parse_abc_files
from tests.utils import SWF_1, SWF_2, SWF_3, SWF_4


@pytest.mark.parametrize('io, n_files', [
    (BytesIO(SWF_1), 0),
    (BytesIO(SWF_2), 1),
    (BytesIO(SWF_3), 2),
    (BytesIO(SWF_4), 1),
])
def test_parse_abc_files(io: BytesIO, n_files: int):
    assert len(list(parse_abc_files(io))) == n_files
