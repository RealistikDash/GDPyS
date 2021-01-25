from web.http import GDPySWeb
from objects.glob import glob
from config import user_config, load_config
from const import HandlerTypes
import uvloop
import asyncio

# Handler imports.
from handlers.login import register_account, login_account
from handlers.profiles import (
    user_info,
    update_stats,
    account_comments,
    upload_acc_comment
)

# Load config
load_config()

# Local Consts
DB_PREFIX = "/database"
# path, handler coro, handlertype, required_postargs
HANDLERS = (
    ("/accounts/registerGJAccount.php", register_account, HandlerTypes.PLAIN_TEXT, ("userName", "password", "email", "secret")),
    ("/accounts/loginGJAccount.php", login_account, HandlerTypes.PLAIN_TEXT, ("udid", "userName", "password", "secret", "sID")),
    ("/getGJUserInfo20.php", user_info, HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED, ("gameVersion", "binaryVersion", "gdw", "accountID", "gjp", "targetAccountID", "secret")),
    ("/updateGJUserScore22.php", update_stats, HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED, ("secret", "accGlow", "iconType", "accountID", "gjp", "userCoins", "seed2", "seed")),
    ("/getGJAccountComments20.php", account_comments, HandlerTypes.PLAIN_TEXT, ("accountID", "total", "page", "secret", "gdw")),
    ("/uploadGJAccComment20.php", upload_acc_comment, HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED, ("accountID", "gjp", "comment", "secret", "chk", "cType"))
)

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

    # SET ALL THE HANDLERS
    for handler in HANDLERS:
        server.add_handler(
            path= DB_PREFIX + handler[0],
            status= handler[2],
            handler= handler[1],
            req_postargs= handler[3]
        )

    await server.start(user_config["http_port"])

if __name__ == "__main__":
    # Here we are using uvloop rather than the defauly
    # asyncio as its faster. However, it does not support
    # Windows so a simple if statement can be added here.
    loop = uvloop.new_event_loop()
    loop.run_until_complete(main(loop))
