# This contains the majority of the constants used within GDPyS.
from __future__ import annotations

import http
import re
from enum import IntFlag

# {404: 'Not Found', ...}
HTTP_CODES = {c.value: c.phrase for c in http.HTTPStatus}
DB_PREFIX = "/database"


class GDPyS:
    """Metadata on GDPyS."""

    NAME: str = "GDPyS v3"
    BUILD: int = 2022_09_07  # Not really build as its Python but it sounds cool.


class HandlerTypes(IntFlag):
    """This `IntFlag` class contains enumeration for GDPyS handler types."""

    # Args passed.
    DATABASE = 1 << 0
    AUTHED = 1 << 1
    RATE_LIMITED = 1 << 2

    # Response Types
    PLAIN_TEXT = 1 << 5
    JSON = 1 << 6


class XorKeys:
    """XOR cipher keys frequently used within Geometry Dash."""

    LEVEL_PASSWORD = "26364"
    MESSAGE = "14251"
    GJP = "37526"
    QUESTS = "19847"
    CHESTS = "59182"


class ReqStats(IntFlag):
    """Profile statuses on whether eg friend reqs are enabled."""

    MESSAGES = 1 << 0
    REQUESTS = 1 << 1
    COMMENTS = 1 << 2
    MESSAGES_FRIENDS_ONLY = 1 << 3
    COMMENTS_FRIENDS_ONLY = 1 << 4


class Privileges(IntFlag):
    """The GDPyS privileges."""

    LOGIN = 1 << 0
    PUBLIC = 1 << 1
    COMMENT = 1 << 2
    LEVEL_UPL = 1 << 3
    RATE = 1 << 4
    MOD_BADGE = 1 << 5
    ELDER_BADGE = 1 << 6
    SUPPORTER = 1 << 7
    DEV_DEBUG = 1 << 8


class GenericResponse:
    """Common Geometry Dash response codes."""

    COMMON_SUCCESS = "1"
    COMMON_FAIL = "-1"
    NOT_FOUND = "-2"


class Regexes:
    """Commonly used regexes."""

    EMAIL = re.compile(r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$")

    # These regexes are taken from gd.py and are used for getting song data from
    # the NG songs page.
    # https://github.com/nekitdev/gd.py/blob/b9d5e29c09f953f54b9b648fb677e987d9a8e103/gd/newgrounds_parser.py#L48-L51
    NG_SONG_LINK = re.compile(r"(https:\\\/\\\/audio\.ngfiles\.com\\\/[^\"']+)")
    NG_SONG_SIZE = re.compile(r"[\"']filesize[\"'][ ]*:[ ]*(\d+)")
    NG_SONG_NAME = re.compile(r"<title>([^<>]+)</title>")
    NG_SONG_AUTH = re.compile(r"[\"']artist[\"'][ ]*:[ ]*[\"']([^\"']+)[\"']")


class Secrets:
    """All of the Geometry Dash secret values."""

    DEFAULT = "Wmfd2893gb7"

    # List of all.
    ALL = (DEFAULT,)


class Difficulty:
    """All of the difficulty face enums for levels."""

    NA = 0
    EASY = 10
    NORMAL = 20
    HARD = 30
    HARDER = 40
    INSANE = 50


class GDCol:
    """Geometry Dash letters corresponding to `FLAlertLayer` colours."""

    BLURPLE = "b"
    GREEN = "g"
    LBLUE = ("l",)
    ORANGE = "o"
    PINK = "p"
    LRED = "r"
    YELLOW = "y"
    RED = ""

    ALL = (BLURPLE, GREEN, LBLUE, ORANGE, PINK, LRED, YELLOW, RED)


class LeaderboardTypes:
    """In-game leaderboard type enums."""

    TOP = 0
    RELATIVE = 1
    CP = 2
    FRIENDS = 3


class LevelLengths:
    """Enums for all of the possible level lengths."""

    TINY = 0
    SHORT = 1
    MEDIUM = 2
    LONG = 3
    XL = 4


class LevelStatus:
    """Int flags for level statuses (such as epic, magic, awarded)."""

    EPIC = 2 << 0
    MAGIC = 2 << 1
    AWARDED = 2 << 2


class Security:
    """Security related constants."""

    # Mainly to stop impersonation.
    BANNED_USERNAMES = ("robtop", "viprin", "michigun")  # All lower case
    # Stop poor security practises
    BANNED_PASSWORDS = (  # All lower case
        "123456",
        "12345678",
        "abc123",
        "password",
        "111111",
        "picture1",
        "123456789",
        "qwerty",
        "password1",
        "iloveyou",
        "qwertyuiop",
        "abcdef",
        "unknown",
        "asdfgh",
        "zxcvbn",
        "112233",
    )
    MAX_LEVEL_NAME_LEN = 20
    MAX_LEVEL_DESC_LEN = 255


class LogTypes:
    """Integer enumerations for the types of logs available."""

    SRV_STARTUP = 0
    USR_PRIV_CHANGE = 1
    USR_DELETE = 2
    LVL_RATE = 3
    LVL_DELETE = 4
