from enum import IntEnum, IntFlag


class Signature(IntEnum):
    UNCOMPRESSED = ord('F')
    ZLIB = ord('C')
    LZMA = ord('Z')


class TagType(IntEnum):
    PLACE_OBJECT = 4
    PLACE_OBJECT_2 = 26
    PLACE_OBJECT_3 = 70
    REMOVE_OBJECT = 5
    REMOVE_OBJECT_2 = 28
    SHOW_FRAME = 1
    SET_BACKGROUND_COLOR = 9
    FRAME_LABEL = 43
    PROTECT = 24
    END = 0
    EXPORT_ASSETS = 56
    IMPORT_ASSETS = 57
    ENABLE_DEBUGGER = 58
    ENABLE_DEBUGGER_2 = 64
    SCRIPT_LIMITS = 65
    SET_TAB_INDEX = 66
    FILE_ATTRIBUTES = 69
    IMPORT_ASSETS_2 = 71
    SYMBOL_CLASS = 76
    METADATA = 77
    DEFINE_SCALING_GRID = 78
    DEFINE_SCENE_AND_FRAME_LABEL_DATA = 86
    DO_ACTION = 12
    DO_INIT_ACTION = 59
    DO_ABC = 82
    DEFINE_SHAPE = 2
    DEFINE_SHAPE_2 = 22
    DEFINE_SHAPE_3 = 32
    DEFINE_SHAPE_4 = 83
    DEFINE_BITS = 6
    JPEG_TABLES = 8
    DEFINE_BITS_JPEG_2 = 21
    DEFINE_BITS_JPEG_3 = 35
    DEFINE_BITS_LOSSLESS = 20
    DEFINE_BITS_LOSSLESS_2 = 36
    DEFINE_BITS_JPEG_4 = 90
    DEFINE_MORPH_SHAPE = 46
    DEFINE_MORPH_SHAPE_2 = 84
    DEFINE_FONT = 10
    DEFINE_FONT_INFO = 13
    DEFINE_FONT_INFO_2 = 62
    DEFINE_FONT_2 = 48
    DEFINE_FONT_3 = 75
    DEFINE_FONT_ALIGN_ZONES = 73
    DEFINE_FONT_NAME = 73
    DEFINE_TEXT = 11
    DEFINE_TEXT_2 = 33
    DEFINE_EDIT_TEXT = 37
    CSM_TEXT_SETTINGS = 74
    DEFINE_FONT_4 = 91
    DEFINE_SOUND = 14
    START_SOUND = 15
    START_SOUND_2 = 89
    SOUND_STREAM_HEAD = 18
    SOUND_STREAM_HEAD_2 = 45
    SOUND_STREAM_BLOCK = 19
    DEFINE_BUTTON = 7
    DEFINE_BUTTON_2 = 34
    DEFINE_BUTTON_CXFORM = 23
    DEFINE_BUTTON_SOUND = 17
    DEFINE_SPRITE = 39
    DEFINE_VIDEO_STREAM = 60
    VIDEO_FRAME = 61
    ENABLE_TELEMETRY = 93
    DEFINE_BINARY_DATA = 87
    PRODUCT_INFO = 41


class DoABCTagFlags(IntFlag):
    LAZY_INITIALIZE = 1
