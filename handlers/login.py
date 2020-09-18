import aiohttp
from helpers.auth import auth
from helpers.userhelper import user_helper
from helpers.ratelimit import rate_limiter
from helpers.generalhelper import get_ip
from constants import Permissions, ResponseCodes
import logging

async def login_handler(request: aiohttp.web.Request):
    """Handles the login request sent by the Geometry Dash client. Takes an aiohttp request arg."""
    post_data = await request.post()
    if not rate_limiter.bump_and_check(get_ip(request), "login"):
        return aiohttp.web.Response(text=ResponseCodes.generic_fail)
    try:
        account_id = await user_helper.get_accountid_from_username(post_data["userName"])
    except AssertionError:
        logging.debug("Assert error, couldnt get obj from username")
        return aiohttp.web.Response(text=ResponseCodes.generic_fail)
    user_obj = await user_helper.get_object(account_id)
    logging.debug(user_obj)
    # Here, we are doing some checks such as whether the user has the correct privilegesm
    if not await auth.check_password(post_data["userName"], post_data["password"]):
        logging.debug("Failed at password check.")
        return aiohttp.web.Response(text=ResponseCodes.generic_fail)
    if not await user_helper.has_privilege(user_obj, Permissions.authenticate):
        logging.debug("No auth perms")
        return aiohttp.web.Response(text=ResponseCodes.login_contact_rob)
    return aiohttp.web.Response(text=f"{user_obj.account_id},{user_obj.user_id}")
