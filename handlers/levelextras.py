# Contains handlers that take care of extras in levels such as rating, liking, comments etc.
from helpers.commenthelper import comment_helper
from helpers.userhelper import user_helper
from helpers.generalhelper import wave_string
from helpers.timehelper import time_ago
from objects.comments import Comment # For pylint to help me work better
import aiohttp
import logging

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
        comment_user = await user_helper.get_object(await user_helper.accid_userid(comment.user_id))
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
            12 : "255,255,255" # TODO: Privileges and colours.
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
