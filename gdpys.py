from __future__ import annotations

import asyncio

import handlers
import logger
from config import conf
from cron.cron import cron_runner
from objects import glob
from web.http import GDPySWeb

try:
    import uvloop

    uvloop.install()
except ImportError:
    logger.warning(
        "The uvloop module is not installed. Falling back to asyncio. This will cause performance issues.",
    )


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
    loop = asyncio.get_event_loop()
    server = GDPySWeb(loop)
    loop.run_until_complete(main())
    server.start(conf.http_sock, conf.http_max_conn)
