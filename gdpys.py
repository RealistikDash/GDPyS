import asyncio
from aiohttp import web
import logging
import random
from handlers.frontend import home_page
from handlers.login import login_handler
from handlers.register import register_handler
from config import user_config
from constants import ASCII_ART, Colours
from conn.mysql import create_connection

def config_routes(app: web.Application) -> None:
    """Configures all of the routes and handlers."""
    app.router.add_get("/", home_page)
    app.router.add_post("/database/accounts/loginGJAccount.php", login_handler)
    app.router.add_post("/database/accounts/registerGJAccount.php", register_handler)

def welcome_sequence():
    """Startup welcome print art things."""
    print(ASCII_ART.format(reset = Colours.reset, col1 = random.choice(Colours.all_col), col2 = random.choice(Colours.all_col), col3 = random.choice(Colours.all_col), col4 = random.choice(Colours.all_col), col5 = random.choice(Colours.all_col)))

async def init(loop):
    """Initialises the app and MySQL connection."""
    app = web.Application(loop=loop)
    await create_connection(loop, user_config)
    return app

if __name__ == "__main__":
    # Configures the logger.
    logging_level = logging.DEBUG if user_config["debug"] else logging.INFO
    logging.basicConfig(level = logging_level)
    welcome_sequence()
    # Inits the app.
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init(loop))
    config_routes(app)
    web.run_app(app, port=user_config["port"])
