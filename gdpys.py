import asyncio
from aiohttp import web
import logging
import random
from handlers.frontend import home_page
from handlers.login import login_handler
from handlers.register import register_handler
from handlers.profiles import profile_comment_handler, profile_handler, user_search_handler
from handlers.songs import featured_artists_handler, get_songinfo_handler
from helpers.userhelper import user_helper
from helpers.songhelper import songs
from config import user_config, load_config
from constants import ASCII_ART, Colours
from conn.mysql import create_connection

def config_routes(app: web.Application) -> None:
    """Configures all of the routes and handlers."""
    app.router.add_get("/", home_page)
    app.router.add_post("/database/accounts/loginGJAccount.php", login_handler)
    app.router.add_post("/database/accounts/registerGJAccount.php", register_handler)
    app.router.add_post("/database/getGJAccountComments20.php", profile_comment_handler)
    app.router.add_post("/database/getGJUserInfo20.php", profile_handler)
    app.router.add_post("/database/getGJTopArtists.php", featured_artists_handler)
    app.router.add_post("/database/getGJSongInfo.php", get_songinfo_handler)
    app.router.add_post("/database/getGJUsers20.php", user_search_handler)

def welcome_sequence():
    """Startup welcome print art things."""
    print(ASCII_ART.format(reset = Colours.reset, col1 = random.choice(Colours.all_col), col2 = random.choice(Colours.all_col), col3 = random.choice(Colours.all_col), col4 = random.choice(Colours.all_col), col5 = random.choice(Colours.all_col)))

async def init(loop):
    """Initialises the app and MySQL connection and all the other systems."""
    app = web.Application(loop=loop)
    await create_connection(loop, user_config)
    await user_helper.cron_calc_ranks()
    songs.top_artists = await songs._top_artists()
    return app

if __name__ == "__main__":
    load_config()
    # Configures the logger.
    logging_level = logging.DEBUG if user_config["debug"] else logging.INFO
    logging.basicConfig(level = logging_level)
    welcome_sequence()
    # Inits the app.
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init(loop))
    config_routes(app)
    try:
        web.run_app(app, port=user_config["port"])
    except KeyboardInterrupt:
        print("Shutting down! Bye!")
