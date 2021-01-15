# This contains the majority of the constants used within GDPyS.
from enum import IntEnum, IntFlag

class HandlerTypes(IntFlag):
    """This `IntFlag` class contains enumeration for GDPyS
    handler types."""

    # Args passed.
    DATABASE     = 1 << 0
    AUTHED       = 1 << 1
    RATE_LIMITED = 1 << 2

    # Response Types
    PLAIN_TEXT   = 1 << 5
    JSON         = 1 << 6

class XorKeys:
    """XOR cipher keys frequently used within Geometry Dash."""

    LEVEL_PASSWORD = 26364
    MESSAGE = 14251
    GJP = 37526
    QUESTS = 19847
    CHESTS = 59182

class ReqStats(IntFlag):
    """Profile statuses on whether eg friend reqs are enabled."""

    MESSAGES = 1 << 0
    REQUESTS = 1 << 1
    COMMENTS = 1 << 2

class Privileges(IntFlag):
    """The GDPyS privileges."""

    LOGIN   = 1 << 0
    COMMENT = 1 << 1

class GenericResponse:
    """Common Geometry Dash response codes."""

    COMMON_SUCCESS = "1"
    COMMON_FAIL = "-1"
    NOT_FOUND = "-2"
