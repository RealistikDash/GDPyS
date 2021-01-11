from web.http import GDPySWeb
from objects.glob import glob
from config import user_config, load_config
import uvloop
import asyncio

# Load config
load_config()

async def main(loop: asyncio.AbstractEventLoop):
    """The main asyncronous function."""

    server = GDPySWeb(loop)

    # Create mysql conn.
    await server.config_sql(
        host= user_config["sql_host"],
        user= user_config["sql_user"],
        password= user_config["sql_password"],
        database= user_config["sql_db"]
    )

    await server.start(user_config["http_port"])

if __name__ == "__main__":
    # Here we are using uvloop rather than the defauly
    # asyncio as its faster. However, it does not support
    # Windows so a simple if statement can be added here.
    loop = uvloop.new_event_loop()
    loop.run_until_complete(main(loop))
