from helpers.userhelper import user_helper
from objects.comments import AccountComment
from objects.accounts import (
    Account,
)  # Makes it WAY easier to work with the objects inside VSCode
from helpers.generalhelper import (
    create_offsets_from_page,
    joint_string,
    pipe_string,
    string_bool,
    paginate_list,
    create_offsets_from_page
)
from helpers.timehelper import time_ago
from helpers.auth import auth
from helpers.searchhelper import search_helper
from helpers.lang import lang
from constants import ResponseCodes, Permissions
from cron.cachelb import top_stars, top_cp
from objects.accounts import FriendRequest, Message # To be nicer to PyLint
import aiohttp
import logging


async def profile_comment_handler(request: aiohttp.web.Request):
    """Handles fetching profile comments."""
    post_data = await request.post()

    offset = create_offsets_from_page(post_data["page"]) * -1
    user = await user_helper.get_object(int(post_data["accountID"]))

    comment_count = len(user.acc_comments)

    # CHECKS
    if comment_count == 0:
        return aiohttp.web.Response(text=ResponseCodes.EMPTY_LIST)

    # I might make this a separate helper function however since account comments aare only ever used in one place I'll make the struct here.
    response = ""
    for comment in user.acc_comments[offset:10]:
        comment: AccountComment
        response += f"2~{comment.comment_base64}~3~{comment.user_id}~4~{comment.likes}~5~0~6~{comment.comment_id}~7~{int(comment.spam)}~9~{time_ago(comment.timestamp)}|"
    response = response[:-1] + f"#{comment_count}:{offset*1}:10"
    logging.debug(response)
    return aiohttp.web.Response(text=response)


async def profile_handler(request: aiohttp.web.Request):
    """Handles user profiles."""
    post_data = await request.post()

    if not await auth.check_gjp(post_data["accountID"], post_data["gjp"]):
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_FAIL)

    # Define variables that will be used in the handler
    account_id = int(post_data["accountID"])
    target_id = int(post_data["targetAccountID"])
    checking_self = account_id == target_id
    user = await user_helper.get_object(target_id)
    response = ""
    friend_state = await user_helper.get_relationship(account_id, target_id)

    logging.debug(friend_state)

    response += joint_string(
        {
            1: user.username,
            2: user.user_id,
            13: user.coins,
            17: user.user_coins,
            10: user.colour1,
            11: user.colour2,
            3: user.stars,
            46: user.diamonds,
            4: user.demons,
            8: user.cp,
            18: int(user.state_msg),
            19: int(user.state_req),
            50: int(user.state_comment),
            20: user.youtube,
            21: user.icon,
            22: user.ship,
            23: user.ball,
            24: user.ufo,
            25: user.wave,
            26: user.robot,
            28: int(user.glow),
            43: user.spider,
            47: user.explosion,
            30: user_helper.get_rank(user.account_id),
            16: user.account_id,
            31: friend_state,
            44: user.twitter,
            45: user.twitch,
            29: 1,
            49: user_helper.mod_badge_level(user.privileges),
        }
    )
    if checking_self:
        extra_acc = await user_helper.get_account_extra(account_id)
        response += joint_string(
            {
                "38": extra_acc.count_messages,
                "39": extra_acc.count_reqs,
                "40": extra_acc.count_new_friends,
            }
        )
    logging.debug(response)
    return aiohttp.web.Response(text=response)


async def user_search_handler(request: aiohttp.web.Request):
    """Handles user account searching."""
    post_data = await request.post()

    response = ""
    offset = create_offsets_from_page(post_data.get("page", 0))
    users = await search_helper.get_users(post_data["str"], offset)

    for user in users.results:
        user: Account
        response += (
            joint_string(
                {
                    1: user.username,
                    2: user.user_id,
                    13: user.coins,
                    17: user.user_coins,
                    9: user.icon,
                    10: user.colour1,
                    11: user.colour2,
                    14: user.icon_type,
                    15: 0,
                    16: user.account_id,
                    3: user.stars,
                    8: user.cp,
                    4: user.demons,
                }
            )
            + "|"
        )

    response = response[:-1] + f"#{users.total_results}:{offset}:10"
    logging.debug(response)
    return aiohttp.web.Response(text=response)


async def post_account_comment_handler(request: aiohttp.web.Request):
    """Handles account comment posting."""
    post_data = await request.post()

    if not await auth.check_gjp(post_data["accountID"], post_data["gjp"]):
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_FAIL)

    response = await user_helper.post_account_comment(
        int(post_data["accountID"]), post_data["comment"]
    )
    logging.debug(response)
    return aiohttp.web.Response(
        text=ResponseCodes.GENERIC_SUCCESS if response else ResponseCodes.GENERIC_FAIL
    )


async def update_profile_stats_handler(request: aiohttp.web.Request):
    """Updates stored statistics regarding the player and responds with appropeate response."""
    post_data = await request.post()
    account_id = int(post_data["accountID"])

    if not await auth.check_gjp(account_id, post_data["gjp"]):
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_FAIL)

    user = await user_helper.get_object(account_id)

    # Updating stats based on data sent by game. TODO: Some form of anticheat

    user.stars = int(post_data.get("stars", 0))
    user.demons = int(post_data.get("demons", 0))
    user.icon = int(post_data.get("icon", 0))
    user.diamonds = int(post_data.get("diamonds", 0))
    user.colour1 = int(post_data.get("color1", 0))
    user.colour2 = int(post_data.get("color2", 0))
    user.ship = int(post_data.get("accShip", 0))
    user.ball = int(post_data.get("accBall", 0))
    user.ufo = int(post_data.get("accBird", 0))
    user.wave = int(post_data.get("accDart", 0))
    user.robot = int(post_data.get("accRobot", 0))
    user.glow = int(post_data.get("accGlow", 0))
    user.spider = int(post_data.get("accSpider", 0))
    user.explosion = int(post_data.get("accExplosion", 0))
    user.coins = int(post_data.get("coins", 0))
    user.user_coins = int(post_data.get("userCoints", 0))

    # Set new user obj to db.
    await user_helper.update_user_stats(user)

    # For some reason we need to return userid
    return aiohttp.web.Response(text=str(user.user_id))


async def save_user_data_handler(request: aiohttp.web.Request):
    """Handles saving user data."""
    post_data = await request.post()

    if not await auth.check_password(post_data["userName"], post_data["password"]):
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_FAIL)
    await user_helper.save_user_data(
        await user_helper.get_accountid_from_username(post_data["userName"]),
        post_data["saveData"],
    )
    return aiohttp.web.Response(text=ResponseCodes.GENERIC_SUCCESS)


async def get_account_url_handler(request: aiohttp.web.Request):
    """Returns URL to database folder."""
    url = str(request.url)[:-27]  # Weird but it works so can't complain. -18
    logging.debug(url)
    return aiohttp.web.Response(text=url)


async def load_save_data_handler(request: aiohttp.web.Response):
    """Handles loading save data."""
    post_data = await request.post()

    if not await auth.check_password(post_data["userName"], post_data["password"]):
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_FAIL)

    save_data = (
        await user_helper.load_user_data(
            await user_helper.get_accountid_from_username(post_data["userName"])
        )
    ) + ";21;30;a;a"
    logging.debug(save_data)
    return aiohttp.web.Response(text=save_data)


async def update_acc_settings_handler(request: aiohttp.web.Response):
    """Handles updateaccsetings."""
    post_data = await request.post()

    account_id = int(post_data["accountID"])
    if not await auth.check_gjp(account_id, post_data["gjp"]):
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_FAIL)

    # TODO: Some filters of these.
    await user_helper.update_profile_settings(
        account_id,
        post_data["yt"],
        post_data["twitter"],
        post_data["twitch"],
        int(post_data["mS"]),
        int(post_data["frS"]),
        int(post_data.get("cs", 0)),
    )
    return aiohttp.web.Response(text=ResponseCodes.GENERIC_SUCCESS)


async def leaderboards_handler(request: aiohttp.web.Response):
    """Handles top leaderboards in-game."""
    post_data = await request.post()
    obj_list = []
    lb_type = post_data["type"]

    if lb_type == "top":
        obj_list = top_stars
    elif lb_type == "creators":
        obj_list = top_cp

    return_str = ""
    rank = 0  # Weird solution but it works :tm:
    for account in obj_list:
        account: Account
        rank += 1
        return_str += (
            joint_string(
                {
                    1: account.username,
                    2: account.user_id,
                    3: account.stars,
                    4: account.stars,
                    6: rank,
                    7: account.account_id,
                    8: account.cp,
                    9: account.icon,
                    10: account.colour1,
                    11: account.colour2,
                    13: account.coins,
                    14: account.icon_type,
                    15: 0,
                    16: account.account_id,
                    17: account.user_coins,
                    46: account.diamonds,
                }
            )
            + "|"
        )
    return_str = return_str[:-1]
    logging.debug(return_str)
    return aiohttp.web.Response(text=return_str)


async def mod_check_handler(request: aiohttp.web.Response):
    """Handles the mod check."""
    post_data = await request.post()

    account_id = int(post_data["accountID"])
    if not await auth.check_gjp(account_id, post_data["gjp"]):
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_FAIL)

    user = await user_helper.get_object(account_id)

    if user_helper.has_privilege(user, Permissions.MOD_ELDER):
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_SUCCESS2)
    elif user_helper.has_privilege(user, Permissions.MOD_REGULAR):
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_SUCCESS2)
    return aiohttp.web.Response(text=ResponseCodes.GENERIC_FAIL)


async def friends_list_handler(request: aiohttp.web.Response):
    """Returns the friends list."""
    post_data = await request.post()

    account_id = int(post_data["accountID"])
    friends_type = int(post_data["type"])

    if not await auth.check_gjp(account_id, post_data["gjp"]):
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_FAIL)

    id_function = {  # Coro to get a list of friends ids.
        0: user_helper.get_friends,  # Regular friends.
        1: user_helper.get_blocked   # Blocked
    }.get(friends_type, user_helper.get_friends)

    friend_ids = await id_function(account_id)

    response = ""
    # Create server response.
    for friend_id in friend_ids:
        user = await user_helper.get_object(friend_id)
        if user is not None:
            response += (
                joint_string(
                    {
                        1: user.username,
                        2: user.user_id,
                        9: user.icon,
                        10: user.colour1,
                        11: user.colour2,
                        14: user.icon_type,
                        15: 0,
                        16: user.account_id,
                        18: 0,
                        41: 0,  # IS NEW # TODO : New friends.
                    }
                )
                + "|"
            )
    response = response[:-1]
    logging.debug(response)
    return aiohttp.web.Response(text=response)

async def friend_req_handler(request: aiohttp.web.Response):
    """Handles friend requests."""

    post_data = await request.post()
    account_id = int(post_data["accountID"])

    if not await auth.check_gjp(account_id, post_data["gjp"]):
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_FAIL)
    
    sent = string_bool(post_data.get("getSent", "0"))
    page = int(post_data["page"])
    offset = create_offsets_from_page(page, 10)
    requests = []
    response = ""

    if sent:
        requests = await user_helper.get_friend_requests_from(account_id)
    else:
        requests = await user_helper.get_friend_requests_to(account_id)
    
    for req in paginate_list(requests, page, 10):
        req : FriendRequest
        user = await user_helper.get_object(req.target_id if sent else req.account_id)
        response += joint_string({
            1: user.username,
            2: user.user_id,
            9: user.icon,
            10: user.colour1,
            11: user.colour2,
            14: user.icon_type,
            15: 0,
            16: user.account_id,
            32: req.id,
            35: req.content_base64,
            37: req.timestamp,
            41: req.new
        }) + "|"
    
    response = f"{response[:-1]}#{len(requests)}:{offset}:10"
    logging.debug(response)
    return aiohttp.web.Response(text=response)

async def message_list_handler(request: aiohttp.web.Response):
    """Handles message list."""

    # Looks familiar huh??
    post_data = await request.post()
    account_id = int(post_data["accountID"])

    if not await auth.check_gjp(account_id, post_data["gjp"]):
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_FAIL)

    sent = string_bool(post_data.get("getSent", "0"))
    page = int(post_data["page"])
    offset = create_offsets_from_page(page, 10)
    messages = await user_helper.get_messages(account_id, sent, page)
    message_count = await user_helper.get_message_count(account_id, sent)
    response = ""

    for msg in messages:
        msg: Message
        user = await user_helper.get_object(msg.target_id if not sent else msg.account_id)
        response += joint_string({
            1: msg.id,
            2: user.account_id,
            3: user.user_id,
            4: msg.subject_base64,
            6: user.username,
            7: time_ago(msg.timestamp),
            8: msg.read,
            9: int(sent)
        }) + "|"
    
    response = f"{response[:-1]}#{message_count}:{offset}:10"
    logging.debug(response)
    return aiohttp.web.Response(text=response)

async def download_message_handler(request: aiohttp.web.Response):
    """Handles fetching a message for the client."""

    post_data = await request.post()
    account_id = int(post_data["accountID"])

    if not await auth.check_gjp(account_id, post_data["gjp"]):
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_FAIL)

    message_id = int(post_data["messageID"])
    sender = int(post_data.get("isSender", 0))

    message = await user_helper.get_message(message_id, account_id)

    if message is None:
        logging.debug(lang.debug("message_not_found", message_id))
        return aiohttp.web.Response(text=ResponseCodes.GENERIC_FAIL)
    
    # Get the user object.
    user = await user_helper.get_object(account_id if sender else message.target_id)

    response = joint_string({
        2: user.account_id,
        5: message.content_base64,
        6: user.username,
        1: message.id,
        3: user.user_id,
        4: message.subject_base64,
        8: message.read,
        9: sender,
        7: time_ago(message.timestamp)
    })

    await user_helper.mark_message_as_read(message_id)
    logging.debug(response)

    return aiohttp.web.Response(text=response)
