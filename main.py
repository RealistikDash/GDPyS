import asyncio
from aiohttp import web
import logging
import random
from config import user_config, load_config

# Handler Imports
from handlers.frontend import home_page
from handlers.login import login_handler
from handlers.register import register_handler
from handlers.profiles import (
    profile_comment_handler,
    profile_handler,
    user_search_handler,
    post_account_comment_handler,
    update_profile_stats_handler,
    get_account_url_handler,
    save_user_data_handler,
    load_save_data_handler,
    update_acc_settings_handler,
    leaderboards_handler,
    mod_check_handler,
    friends_list_handler,
)
from handlers.songs import featured_artists_handler, get_songinfo_handler
from handlers.levels import (
    level_search_modular_hanlder,
    download_level,
    upload_level_handler,
    get_daily_handler,
    get_map_packs_handler,
    get_gauntlets_handler,
)
from handlers.rewards import quests_handler
from handlers.levelextras import (
    level_comments_handler,
    post_comment_handler,
    rate_level_handler,
    level_scores_handler,
)

# Helper Imports
from helpers.userhelper import user_helper
from helpers.songhelper import songs
from helpers.ratelimit import rate_limiter
from helpers.priveliegehelper import priv_helper
from helpers.lang import lang
from helpers.generalhelper import time_coro
from cron.cron import run_cron
from constants import ASCII_ART, Colours
from conn.mysql import create_connection
from os import path
from tools.main import tools
import os
import importlib
from threading import Thread


def config_routes(app: web.Application) -> None:
    """Configures all of the routes and handlers."""
    app.router.add_get("/", home_page)

    routes = [
        ("/database/getGJLevelScores211.php", level_scores_handler),
        ("/database/getGJGauntlets21.php", get_gauntlets_handler),
        ("/database/getGJMapPacks21.php", get_map_packs_handler),
        ("/database/getGJDailyLevel.php", get_daily_handler),
        ("/database/requestUserAccess.php", mod_check_handler),
        ("/database/suggestGJStars20.php", rate_level_handler),
        ("/database/getGJScores20.php", leaderboards_handler),
        ("/database/updateGJAccSettings20.php", update_acc_settings_handler),
        ("/database/uploadGJComment21.php", post_comment_handler),
        ("/database/getGJComments21.php", level_comments_handler),
        ("/database/getGJChallenges.php", quests_handler),
        ("/database/getGJUserList20.php", friends_list_handler),
        ("/database/accounts/syncGJAccountNew.php", load_save_data_handler),
        ("/database/uploadGJLevel21.php", upload_level_handler),
        ("/database/accounts/backupGJAccountNew.php", save_user_data_handler),
        ("/database/getAccountURL.php", get_account_url_handler),
        ("/database/updateGJUserScore22.php", update_profile_stats_handler),
        ("/database/uploadGJAccComment20.php", post_account_comment_handler),
        ("/database/downloadGJLevel22.php", download_level),
        ("/database/getGJLevels21.php", level_search_modular_hanlder),
        ("/database/getGJUsers20.php", user_search_handler),
        ("/database/getGJSongInfo.php", get_songinfo_handler),
        ("/database/getGJTopArtists.php", featured_artists_handler),
        ("/database/getGJUserInfo20.php", profile_handler),
        ("/database/getGJAccountComments20.php", profile_comment_handler),
        ("/database/accounts/registerGJAccount.php", register_handler),
        ("/database/accounts/loginGJAccount.php", login_handler),
    ]

    for r, h in routes:
        logging.debug(lang.debug("adding_handler", r, h.__name__))
        app.router.add_post(r, time_coro(h))

    # app.add_subapp("/api/", api)
    app.add_subapp("/tools/", tools)


def welcome_sequence(no_ascii: bool = False):
    """Startup welcome print art things."""
    if not no_ascii:
        print(
            ASCII_ART.format(
                reset=Colours.RESET,
                col1=random.choice(Colours.all_col),
                col2=random.choice(Colours.all_col),
                col3=random.choice(Colours.all_col),
                col4=random.choice(Colours.all_col),
                col5=random.choice(Colours.all_col),
            )
        )
    # No cache warning
    # if user_config["no_cache"]:
    #    logging.warning("CACHING DISABLED (through user config)! This will lead to a MASSIVE performance hit. Keep it on unless under MASSIVE memory limitations.")


def pre_run_checks():
    """Runs checks before startup to make sure all runs smoothly."""
    if not path.exists(user_config["level_path"]) or not path.exists(
        user_config["save_path"]
    ):
        logging.error(lang.error("START_LVLPATH"))
        logging.info(
            lang.info(
                "SET_LVLPATH", user_config["level_path"], user_config["save_path"]
            )
        )
        raise SystemExit


def start_plugins():
    """Start plugins"""
    plugins = []
    homepath = path.dirname(path.realpath(__file__))
    for plugin in os.listdir(homepath + "/plugins/"):
        if (
            not path.isdir(homepath + "/plugins/" + plugin)
            and plugin.endswith(".py")
            and plugin != "__init__.py"
        ):
            plugin = plugin.strip(".py")
            print(f'Loading plugin "{plugin}".')
            plugins.append(plugin)
            Thread(
                target=lambda: importlib.import_module(
                    "." + plugin, "plugins"
                ).setup()()
            ).start()


async def init(loop):
    """Initialises the app and MySQL connection and all the other systems."""
    app = web.Application(loop=loop)
    await create_connection(loop, user_config)
    await priv_helper.cache_privs()
    await run_cron()
    # await cron_gather()
    songs.top_artists = await songs._top_artists()
    # Setting up rate limiter
    rate_limiter.add_to_struct(
        "register", limit=2
    )  # One IP may only register twice a day.
    rate_limiter.add_to_struct(
        "login", limit=10
    )  # One IP may only try to login ten times a day.
    return app


if __name__ == "__main__":
    load_config()
    # Configures the logger.
    logging_level = logging.DEBUG if user_config["debug"] else logging.INFO
    logging.basicConfig(level=logging_level)
    lang.load_langs(user_config["lang"])
    start_plugins()
    welcome_sequence()
    pre_run_checks()
    # Inits the app.
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init(loop))
    config_routes(app)
    try:
        web.run_app(app, port=user_config["port"])
    except RuntimeError:
        print("Shutting down! Bye!")
