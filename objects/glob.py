# Shared global class. https://cdn.discordapp.com/attachments/768893339683913728/798677938932547624/1200px-Flag_of_Poland.png
from __future__ import annotations

import asyncio
from typing import Callable
from typing import Coroutine

from helpers.cache import Cache
from helpers.time import get_timestamp
from web.sql import MySQLPool

# The global object shared between most major GDPyS systems.

# User cache.
user_cache: Cache = Cache(cache_length=20, cache_limit=200)
# Song Cache
song_cache: Cache = Cache(cache_length=20, cache_limit=200)

level_cache: Cache = Cache(cache_length=200, cache_limit=20)

# All of the privileges. Using a dict as we want
# them to never expire.
privileges: dict = {}

# Global MySQL connection.
sql: MySQLPool
routes: dict = {}

# I am SO SORRY for placing this here but circular imports suck.
star_lb = None
cp_lb = None

# Some statistics
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
