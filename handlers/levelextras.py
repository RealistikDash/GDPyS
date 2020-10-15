# Contains handlers that take care of extras in levels such as rating, liking, comments etc.
from helpers.commenthelper import comment_helper
from helpers.userhelper import user_helper
from helpers.levelhelper import level_helper
from helpers.generalhelper import wave_string, joint_string
from helpers.timehelper import time_ago, get_timestamp
from helpers.auth import auth
from helpers.crypthelper import decode_base64
from helpers.filterhelper import check_comment
from helpers.priveliegehelper import priv_helper
from helpers.crypthelper import decode_base64
from helpers.lang import lang
from helpers.scorehelper import score_helper
from objects.comments import Comment, CommentBan
from gdpys.client import client
from objects.levels import Rating, Score
from constants import ResponseCodes, Permissions
from config import user_config
import aiohttp
import logging

commands = client

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
            comment_user = await user_helper.get_object(await user_helper.userid_accid(comment.user_id))
        except AssertionError: # The user does not exist
            logging.debug(lang.debug("comment_user_search_fail", comment.user_id))
        else:
            privilege = await priv_helper.get_privilege_from_privs(comment_user.privileges)
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
        return aiohttp.web.Response(text=ResponseCodes.comment_ban)

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
    if comment_obj.comment.startswith(user_config["command_prefix"]) and client._command_exists(comment_obj.comment):
        result = await client._execute_command(comment_obj)
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

async def rate_level_handler(request : aiohttp.web.Request):
    """Handles GD level rating."""
    post_data = await request.post()

    account_id = int(post_data["accountID"])
    level_id = int(post_data["levelID"])
    stars = int(post_data["stars"])
    featured = post_data.get("feature", "0") == "1"
    user = await user_helper.get_object(account_id)
    # Permission checks
    if not await auth.check_gjp(account_id, post_data["gjp"]):
        return aiohttp.web.Response(text=ResponseCodes.generic_fail)
    if not user_helper.has_privilege(user, Permissions.mod_rate):
        return aiohttp.web.Response(text=ResponseCodes.generic_fail2)
    
    rating = Rating(
        level_id,
        stars,
        featured,
        0,
        1,
        0
    )
    await level_helper.rate_level(rating)
    return aiohttp.web.Response(text=ResponseCodes.generic_success)

async def level_scores_handler(request : aiohttp.web.Request) -> aiohttp.web.Response:
    """Handles score submission and score leaderboards."""
    post_data = await request.post()

    # Authentication
    account_id = int(post_data["accountID"]) # Lets declare this as we will re-use it later
    if not auth.check_gjp(account_id, post_data["gjp"]):
        return aiohttp.web.Response(text=ResponseCodes.generic_fail)

    # Creating the current score object.
    level_id = int(post_data["levelID"])
    percent = int(post_data.get("percent", 0))
    attempts = int(post_data.get("s1", 8354)) - 8354 # Rob tried to pull a sneaky on us
    coins = int(post_data.get("s9", 5819)) - 5819
    score = Score(
        ID = None, # It is a new score
        account_id=account_id,
        level_id=level_id,
        percentage=percent,
        timestamp=get_timestamp(),
        attempts=attempts,
        coins=coins
    )

    logging.debug(score)
    # Checking and overwriting the score.
    if await score_helper.overwrite_score(score=score) and score.percentage > 0:
        logging.debug(lang.debug("overwrite_score"))
        old_score = await score_helper.get_score_for_user(score.account_id, score.level_id)
        if old_score is not None:
            await score_helper.delete_score(old_score.ID)
        # TODO: Implement anticheat (Cheatless V2)
        await score_helper.save_score_to_db(score)
    
    # Scores leaderboard.
    lb_type = int(post_data["type"])
    lbs_get = { # Budget switch statement.
        1 : score_helper.get_from_db
    }.get(lb_type, score_helper.get_from_db)
    leaderboards = await lbs_get(level_id)

    # Creating the server response.
    response = ""
    for i in range(len(leaderboards)):
        lb_score : Score = leaderboards[i]
        user = await user_helper.get_object(lb_score.account_id)
        response += joint_string({
            1 : user.username,
            2 : user.user_id,
            3 : lb_score.percentage,
            6 : i+1, # +1 since it starts from 0
            9 : user.icon,
            10 : user.colour1,
            11 : user.colour2,
            13 : lb_score.coins,
            14 : user.icon_type,
            15 : 0,
            16 : user.account_id,
            42 : time_ago(lb_score.timestamp)
        }) + "|"
    response = response[:-1]
    logging.debug(response)
    return aiohttp.web.Response(text=response)
