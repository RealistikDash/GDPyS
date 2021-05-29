# This contains the majority of the constants used within GDPyS.
from enum import IntEnum, IntFlag

class GDPyS:
    """Metadata on GDPyS."""

    NAME: str = "GDPyS v3"
    BUILD: int = 20210529 # Not really build as its Python but it sounds cool.

class HandlerTypes(IntFlag):
    """This `IntFlag` class contains enumeration for GDPyS handler types."""

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
    MESSAGE        = 14251
    GJP            = 37526
    QUESTS         = 19847
    CHESTS         = 59182

class ReqStats(IntFlag):
    """Profile statuses on whether eg friend reqs are enabled."""

    MESSAGES              = 1 << 0
    REQUESTS              = 1 << 1
    COMMENTS              = 1 << 2
    MESSAGES_FRIENDS_ONLY = 1 << 3
    COMMENTS_FRIENDS_ONLY = 1 << 4

class Privileges(IntFlag):
    """The GDPyS privileges."""

    LOGIN       = 1 << 0
    PUBLIC      = 1 << 1
    COMMENT     = 1 << 2
    RATE        = 1 << 3
    MOD_BADGE   = 1 << 4
    ELDER_BADGE = 1 << 5
    SUPPORTER   = 1 << 6

class GenericResponse:
    """Common Geometry Dash response codes."""

    COMMON_SUCCESS = "1"
    COMMON_FAIL    = "-1"
    NOT_FOUND      = "-2"

class Regexes:
    """Commonly used regexes."""

    EMAIL = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"

class Secrets:
    """All of the Geometry Dash secret values."""

    DEFAULT = "Wmfd2893gb7"

    # List of all.
    ALL = (DEFAULT,)

class Difficulty:
    """All of the difficulty face enums for levels."""

    NA     = 0
    EASY   = 10
    NORMAL = 20
    HARD   = 30
    HARDER = 40
    INSANE = 50

class GDCol:
    """Geometry Dash letters corresponding to `FLAlertLayer` colours."""

    BLURPLE = "b"
    GREEN   = "g"
    LBLUE   = "l",
    ORANGE  = "o"
    PINK    = "p"
    LRED    = "r"
    YELLOW  = "y"
    RED     = ""

    ALL = (
        BLURPLE, GREEN, LBLUE, ORANGE, PINK, LRED, YELLOW, RED
    )

class LeaderboardTypes:
    """In-game leaderboard type enums."""

    TOP      = 0
    RELATIVE = 1
    CP       = 2
    FRIENDS  = 3

class LevelLengths:
    """Enums for all of the possible level lengths."""
    TINY   = 0
    SHORT  = 1
    MEDIUM = 2
    LONG   = 3
    XL     = 4

class LevelStatus:
    """Int flags for level statuses (such as epic, magic, awarded)."""

    EPIC    = 2 << 0
    MAGIC   = 2 << 1
    AWARDED = 2 << 2

# Source of these can be found on https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
HTTP_CODES = {
    100: 'Continue',
    101: 'Switching Protocols',
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    306: '(Unused)', # ehhh
    307: 'Temporary Redirect',
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required', # soon?
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request-URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported'
}
