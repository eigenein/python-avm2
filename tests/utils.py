from pathlib import Path
from typing import BinaryIO

import tests.data


def open_test_swf(name: str) -> BinaryIO:
    return (Path(tests.data.__file__).parent / name).open('rb')
