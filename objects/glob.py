# The global object shared between most major GDPyS systems.
from __future__ import annotations

import asyncio
from typing import Callable
from typing import Coroutine
from typing import TYPE_CHECKING

from helpers.cache import LRUCache
from helpers.time import get_timestamp
from web.sql import MySQLPool

if TYPE_CHECKING:
    from objects.user import User
    from objects.song import Song
    from objects.level import Level


user_cache: LRUCache[User] = LRUCache(
    capacity=200,
)  # Should be a dict or a weakref dict.
song_cache: LRUCache[Song] = LRUCache(capacity=200)
level_cache: LRUCache[Level] = LRUCache(capacity=200)

privileges: dict = {}

# Global MySQL connection.
sql: MySQLPool
routes: dict = {}

# TODO: Move.
star_lb = None
cp_lb = None

# Statistics
connections_handled: int = 0
startup_time: int = get_timestamp()
registered_users: int = 0  # Cached in cron
feature_id: int = 0  # Latest feature id (to be incremented).


def add_route(path: str, status: int, args: tuple = ()) -> Callable:
    global routes
    """Adds a route to global route lists."""

    def wrapper(handler: Coroutine) -> Coroutine:
        variables = {"path": path, "status": status, "args": args, "handler": handler}
        routes[path] = variables
        return handler

    return wrapper
