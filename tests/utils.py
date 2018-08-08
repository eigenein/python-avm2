from pathlib import Path
from typing import BinaryIO

import tests


def open_test_swf(name: str) -> BinaryIO:
    return (Path(tests.__file__).parent / name).open('rb')
