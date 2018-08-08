from io import BytesIO

from avm2.abc.types import ABCFile, ABCFileFlags
from avm2.utils import parse_abc_files
from tests.utils import SWF_2


def test_parse_abc_file_2():
    abc_file, = parse_abc_files(BytesIO(SWF_2))  # type: ABCFile
    assert abc_file.major_version == 46
    assert abc_file.minor_version == 16
    assert abc_file.name == 'merged'
    assert abc_file.flags == ABCFileFlags.LAZY_INITIALIZE
