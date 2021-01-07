# This contains the majority of the constants used within GDPyS.
from enum import IntEnum, IntFlag

class HandlerTypes(IntFlag):
    """This `IntFlag` class contains enumeration for GDPyS
    handler types."""

    # Args passed.
    DATABASE   = 1 << 0
    AUTHED     = 1 << 1

    # Response Types
    PLAIN_TEXT = 1 << 5
    JSON       = 1 << 6

class XorKeys:
    """XOR cipher keys frequently used within Geometry Dash."""

    LEVEL_PASSWORD = 26364
    MESSAGE = 14251
    GJP = 37526
    QUESTS = 19847
    CHESTS = 59182
