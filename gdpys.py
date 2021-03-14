from web.http import GDPySWeb
from objects.glob import glob
from config import conf
from const import HandlerTypes
from cron.cron import cron_runner
import uvloop
import asyncio

# Handler imports.
from handlers.login import register_account, login_account
from handlers.profiles import (
    user_info,
    update_stats,
    account_comments,
    upload_acc_comment,
    delete_acc_comment,
    update_social,
    profile_search,
    req_mod
)
from handlers.misc import get_song
from handlers.leaderboards import get_leaderboard

# Load config

# Local Consts
DB_PREFIX = "/database"
# path, handler coro, handlertype, required_postargs
HANDLERS = (
    ("/accounts/registerGJAccount.php", register_account, HandlerTypes.PLAIN_TEXT, ("userName", "password", "email", "secret")),
    ("/accounts/loginGJAccount.php", login_account, HandlerTypes.PLAIN_TEXT, ("udid", "userName", "password", "secret", "sID")),
    ("/getGJUserInfo20.php", user_info, HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED, ("gameVersion", "binaryVersion", "gdw", "accountID", "gjp", "targetAccountID", "secret")),
    ("/updateGJUserScore22.php", update_stats, HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED, ("secret", "accGlow", "iconType", "accountID", "gjp", "userCoins", "seed2", "seed")),
    ("/getGJAccountComments20.php", account_comments, HandlerTypes.PLAIN_TEXT, ("accountID", "total", "page", "secret", "gdw")),
    ("/uploadGJAccComment20.php", upload_acc_comment, HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED, ("accountID", "gjp", "comment", "secret", "chk", "cType")),
    ("/deleteGJAccComment20.php", delete_acc_comment, HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED, ("accountID", "gjp", "secret", "commentID")),
    ("/updateGJAccSettings20.php", update_social, HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED, ("accountID", "gjp", "secret")),
    ("/getGJSongInfo.php", get_song, HandlerTypes.PLAIN_TEXT, ("secret", "songID")),
    ("/getGJUsers20.php", profile_search, HandlerTypes.PLAIN_TEXT, ("str", "page", "total")),
    ("/requestUserAccess.php", req_mod, HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED, ("accountID", "gjp", "secret", "gameVersion", "binaryVersion", "gdw")),
    ("/getGJScores20.php", get_leaderboard, HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED, ("accountID", "secret", "gdw", "type"))
)

async def main(loop: asyncio.AbstractEventLoop):
    """The main asyncronous function."""

    server = GDPySWeb(loop)

    # Create mysql conn.
    await server.config_sql(
        host= conf.sql_host,
        user= conf.sql_user,
        password= conf.sql_password,
        database= conf.sql_db
    )

    # SET ALL THE HANDLERS
    for handler in HANDLERS:
        server.add_handler(
            path= DB_PREFIX + handler[0],
            status= handler[2],
            handler= handler[1],
            req_postargs= handler[3]
        )
    
    # Schedule cron running thing.
    loop.create_task(cron_runner())

    await server.start(conf.http_sock, conf.http_max_conn)

if __name__ == "__main__":
    # Here we are using uvloop rather than the defauly
    # asyncio as its faster. However, it does not support
    # Windows so a simple if statement can be added here.
    loop = uvloop.new_event_loop()
    loop.run_until_complete(main(loop))
