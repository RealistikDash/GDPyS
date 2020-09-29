# Contains handlers that take care of extras in levels such as rating, liking, comments etc.
from helpers.commenthelper import comment_helper
from helpers.userhelper import user_helper
from helpers.generalhelper import wave_string
from helpers.timehelper import time_ago, get_timestamp
from helpers.auth import auth
from helpers.crypthelper import decode_base64
from helpers.filterhelper import check_comment
from helpers.priveliegehelper import priv_helper
from helpers.crypthelper import decode_base64
from objects.comments import Comment, CommentBan
from gdpys import client
from constants import ResponseCodes, Permissions
import aiohttp
import logging

commands = client.client

async def level_comments_handler(request : aiohttp.web.Request):
    """Responsible for sending the game level comments."""
    post_data = await request.post()
    
    # Used variables
    level_id = int(post_data.get("levelID", 0))
    page = int(post_data["page"])
    mode = int(post_data.get("mode", 0))
    amount = int(post_data.get("count", 10))

    comments = await comment_helper.get_comments(level_id, page, amount, "likes" if mode else "timestamp")
    count = comments.total_results
    response = ""

    for comment in comments.results:
        comment : Comment
        try:
            comment_user = await user_helper.get_object(await user_helper.accid_userid(comment.user_id))
        except AssertionError: # The user does not exist
            logging.debug(f"Failed searching for user {comment.user_id}. Should be skipped.")
        else:
            privilege = await priv_helper.get_privilege_from_privs(comment_user.privileges)
            logging.debug(comment.user_id)
            response += wave_string({
                #1 : comment.level_id,
                2 : comment.comment_base64,
                3 : comment.user_id,
                4 : comment.likes,
                5 : 0,
                7 : int(comment.spam),
                9 : time_ago(comment.timestamp),
                6 : comment.comment_id,
                10 : comment.percent,
                11 : user_helper.mod_badge_level(comment_user.privileges),
                12 : str(privilege.colour)
            }) + ":" + wave_string({
                1: comment_user.username,
                7 : 1,
                9 : comment_user.icon,
                10 : comment_user.colour1,
                11 : comment_user.colour2,
                14 : comment_user.icon_type,
                15 : 0,
                16 : comment_user.account_id
            }) + "|"
    
    response = response[:-1]
    final_resp = f"{response}#{comments.total_results}:{page}:10"
    logging.debug(final_resp)
    return aiohttp.web.Response(text=final_resp)

async def post_comment_handler(request : aiohttp.web.Request) -> aiohttp.web.Response:
    """Handles posting level comments."""
    post_data = await request.post()

    account_id = int(post_data["accountID"])
    percent = int(post_data.get("percent", 0))
    game_version = int(post_data.get("gameVersion", 0)) # Why?
    content = post_data["comment"]
    level_id = int(post_data["levelID"])
    user = await user_helper.get_object(account_id)

    # Couple of checks to ensure security
    if not await auth.check_gjp(account_id, post_data["gjp"]):
        return aiohttp.web.Response(text=ResponseCodes.generic_fail)
    
    if not user_helper.has_privilege(user, Permissions.post_comment):
        return aiohttp.web.Response(text=ResponseCodes.generic_fail)

    if not check_comment(decode_base64(content)):
        return aiohttp.web.Response(text=ResponseCodes.generic_fail)

    # Creating the object.
    comment_obj = Comment(
        user.user_id,
        level_id,
        content,
        decode_base64(content),
        get_timestamp(),
        0,
        percent,
        False,
        user.username,
        None # No comment ID yet.
    )
    # TODO : Command stuff
    if commands.command_exists(comment_obj.comment):
        result = await commands.execute_command(comment_obj)
        logging.debug(result)
        if type(result) == bool:
            result = ResponseCodes.generic_success if result else ResponseCodes.generic_fail
            logging.debug(result)
            return aiohttp.web.Response(text=result)
        # It is a comment ban.
        result = result.rob_response()
        logging.debug(result)
        return aiohttp.web.Response(text=result)
    # Now we add it to the database.
    await comment_helper.insert_comment(comment_obj)
    return aiohttp.web.Response(text=ResponseCodes.generic_success)
