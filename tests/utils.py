from pathlib import Path

import tests.data


def read_test_swf(name: str) -> memoryview:
    return memoryview((Path(tests.data.__file__).parent / name).read_bytes())


SWF_1 = memoryview(bytes.fromhex(
    '465753034F0000007800055F00000FA000000C01004302FFFFFFBF0023000000'
    '010070FB49970D0C7D50000114000000000125C9920D21ED488765303B6DE1D8'
    'B40000860606010001000040000000'
))
SWF_2 = read_test_swf('heroes.swf')
SWF_3 = read_test_swf('Farm_d_13_9_2_2198334.swf')
SWF_4 = read_test_swf('EpicGame.swf')
