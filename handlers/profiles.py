from helpers.userhelper import user_helper
from objects.comments import AccountComment
from objects.accounts import Account # Makes it WAY easier to work with the objects inside VSCode
from helpers.generalhelper import create_offsets_from_page, joint_string, pipe_string
from helpers.timehelper import time_ago
from helpers.auth import auth
from helpers.searchhelper import search_helper
from constants import ResponseCodes
import aiohttp
import logging

async def profile_comment_handler(request : aiohttp.web.Request):
    """Handles fetching profile comments."""
    post_data = await request.post()

    offset = create_offsets_from_page(post_data["page"]) * -1
    user = await user_helper.get_object(int(post_data["accountID"]))

    comment_count = len(user.acc_comments)

    #CHECKS
    if comment_count == 0:
        return aiohttp.web.Response(text=ResponseCodes.empty_list)
    
    # I might make this a separate helper function however since account comments aare only ever used in one place I'll make the struct here.
    response = ""
    for comment in user.acc_comments[offset:10]:
        comment : AccountComment
        response += f"2~{comment.comment_base64}~3~{comment.user_id}~4~{comment.likes}~5~0~6~{comment.comment_id}~7~{int(comment.spam)}~9~{time_ago(comment.timestamp)}|"
    response = response[:-1] + f"#{comment_count}:{offset*1}:10"
    logging.debug(response)
    return aiohttp.web.Response(text=response)

async def profile_handler(request : aiohttp.web.Request):
    """Handles user profiles."""
    post_data = await request.post()

    if not await auth.check_gjp(post_data["accountID"], post_data["gjp"]):
        return aiohttp.web.Response(text=ResponseCodes.generic_fail)
    
    # Define variables that will be used in the handler
    account_id = int(post_data["accountID"])
    target_id = int(post_data["targetAccountID"])
    checking_self = account_id == target_id
    user = await user_helper.get_object(target_id)
    response = ""
    friend_state = 0
    
    logging.debug(friend_state)
    logging.debug(response)

    response += joint_string({
        1 : user.username,
        2 : user.user_id,
        13 : user.coins,
        17 : user.user_coins,
        10 : user.colour1,
        11 : user.colour2,
        3 : user.stars,
        46 : user.diamonds,
        4 : user.demons,
        8 : user.cp,
        18: int(user.state_msg),
        19 : int(user.state_req),
        50 : int(user.state_comment),
        20 : user.youtube,
        21 : user.icon,
        22 : user.ship,
        23: user.ball,
        24: user.ufo,
        25 : user.wave,
        26 : user.robot,
        28 : int(user.glow),
        43 : user.spider,
        47 : user.explosion,
        30 : user_helper.get_rank(user.account_id),
        16: user.account_id,
        31 : friend_state,
        44 : user.twitter,
        45: user.twitch,
        29 : 1,
        49 : user_helper.mod_badge_level(user.privileges)
    })
    if checking_self:
        extra_acc = await user_helper.get_account_extra(account_id)
        response += joint_string({
            "38" : extra_acc.count_messages,
            "39" : extra_acc.count_reqs,
            "40" : extra_acc.count_new_friends
        })
    logging.debug(response)
    return aiohttp.web.Response(text=response)

async def user_search_handler(request : aiohttp.web.Request):
    """Handles user account searching."""
    post_data = await request.post()

    response = ""
    offset = create_offsets_from_page(post_data.get("page", 0))
    users = await search_helper.get_users(post_data["str"], offset)

    for user in users.results:
        user: Account
        response += joint_string({
            1 : user.username,
            2: user.user_id,
            13 : user.coins,
            17 : user.user_coins,
            9 : user.icon,
            10 : user.colour1,
            11 : user.colour2,
            14 : user.icon_type,
            15 : 0,
            16 : user.account_id,
            3 : user.stars,
            8 : user.cp,
            4 : user.demons
        }) + "|"

    response = response[:-1] + f"#{users.total_results}:{offset}:10"
    logging.debug(response)
    return aiohttp.web.Response(text=response)

async def post_account_comment_handler(request : aiohttp.web.Request):
    """Handles account comment posting."""
    post_data = await request.post()

    if not await auth.check_gjp(post_data["accountID"], post_data["gjp"]):
        return aiohttp.web.Response(text=ResponseCodes.generic_fail)
    
    response = await user_helper.post_account_comment(int(post_data["accountID"]), post_data["comment"])
    logging.debug(response)
    return aiohttp.web.Response(text=ResponseCodes.generic_success if response else ResponseCodes.generic_fail)

async def update_profile_stats_handler(request : aiohttp.web.Request):
    """Updates stored statistics regarding the player and responds with appropeate response."""
    post_data = await request.post()
    account_id = int(post_data["accountID"])

    if not await auth.check_gjp(account_id, post_data["gjp"]):
        return aiohttp.web.Response(text=ResponseCodes.generic_fail)

    user = await user_helper.get_object(account_id)

    # Updating stats based on data sent by game. TODO: Some form of anticheat

    logging.debug(post_data)
    user.stars = int(post_data.get("stars", 0))
    user.demons = int(post_data.get("demons", 0))
    user.icon = int(post_data.get("icon", 0))
    user.diamonds = int(post_data.get("diamonds", 0))
    user.colour1 = int(post_data.get("color1", 0))
    user.colour2 = int(post_data.get("colour2", 0))
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

async def save_user_data_handler(request : aiohttp.web.Request):
    """Handles saving user data."""
    post_data = await request.post()

    if not await auth.check_password(post_data["userName"], post_data["password"]):
        return aiohttp.web.Response(text=ResponseCodes.generic_fail)
    
    return user_helper.load_user_data(await user_helper.get_accountid_from_username(post_data["userName"]))

async def get_account_url_handler(request : aiohttp.web.Request):
    """Returns URL to database folder."""
    url = str(request.url)[:-27] # Weird but it works so can't complain. -18
    logging.debug(url)
    return aiohttp.web.Response(text=url)
