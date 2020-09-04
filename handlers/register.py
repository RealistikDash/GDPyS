import aiohttp
from helpers.filterhelper import check_username
from helpers.userhelper import user_helper
from helpers.generalhelper import get_ip
from constants import ResponseCodes

async def register_handler(request: aiohttp.web.Request):
    """Handles the Geometry Dash register event."""
    post_data = await request.post()

    # This is giving me bad vibes.
    username = post_data["userName"]
    password = post_data["password"]
    email = post_data["email"]
    ip = get_ip(request)
    if not check_username(username):
        return aiohttp.web.Response(text=ResponseCodes.generic_fail)
    if user_helper.get_accountid_from_username(username):
        return aiohttp.web.Response(text=ResponseCodes.generic_fail2)
    await user_helper.create_user(
        username,
        password, email,
        ip
    )
    return aiohttp.web.Response(text=ResponseCodes.generic_success)
