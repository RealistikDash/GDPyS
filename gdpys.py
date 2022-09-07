from __future__ import annotations

import asyncio

import uvloop

from config import conf
from cron.cron import cron_runner
from handlers import api
from handlers import leaderboards
from handlers import levels
from handlers import login
from handlers import misc
from handlers import profiles
from objects import glob
from web.http import GDPySWeb

# This is only to initialise this files.
# Init cron


async def main():
    """The main asyncronous function."""

    # Create mysql conn.
    await server.config_sql(
        host=conf.sql_host,
        user=conf.sql_user,
        password=conf.sql_password,
        database=conf.sql_db,
    )

    # Add all global routes.
    for route in glob.routes.values():
        server.add_handler(
            path=route["path"],
            status=route["status"],
            handler=route["handler"],
            req_postargs=route["args"],
        )

    # Schedule cron running thing.
    server.add_task(cron_runner)


if __name__ == "__main__":
    # Here we are using uvloop rather than the defauly
    # asyncio as its faster. However, it does not support
    # Windows so a simple if statement can be added here.
    loop = uvloop.new_event_loop()
    server = GDPySWeb(loop)
    loop.run_until_complete(main())
    server.start(conf.http_sock, conf.http_max_conn)
