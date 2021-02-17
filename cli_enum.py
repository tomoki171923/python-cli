from enum import IntEnum, auto

class CliEnum(IntEnum):
    SEVERIY_INFO = auto()
    SEVERIY_WARN = auto()
    SEVERIY_ERROR = auto()

    CMD_OPTION_STOP = auto()
    CMD_OPTION_CONTINUE = auto()
    
    RETURN_TYPE_DICT = auto()
    RETURN_TYPE_STRING = auto()
