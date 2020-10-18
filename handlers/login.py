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
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_FAIL)
    try:
        account_id = await user_helper.get_accountid_from_username(
            post_data["userName"]
        )
    except AssertionError:
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_FAIL)
    user_obj = await user_helper.get_object(account_id)
    logging.debug(user_obj)
    # Here, we are doing some checks such as whether the user has the correct privileges
    if not await auth.check_password(post_data["userName"], post_data["password"]):
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_FAIL)
    if not user_helper.has_privilege(user_obj, Permissions.AUTH):
        return aiohttp.web.Response(text=ResponseCodes.LOGIN_CONTACT_ROB)
    return aiohttp.web.Response(text=f"{user_obj.account_id},{user_obj.user_id}")
