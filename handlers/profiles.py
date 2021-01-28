from objects.user import User
from web.http import Request # Pylint appeasement.
from web.builders import gd_dict_str, gd_builder
from helpers.common import paginate_list
from helpers.crypt import base64_encode, base64_decode
from helpers.time_helper import time_ago
from const import ReqStats
from exceptions import GDException
from typing import List
from objects.comments import AccountComment

async def user_info(req: Request, user: User):
    """Handles the `getGJUserInfo20.php` endpoint."""

    # Check if we are fetching ourselves.
    checking_self = req.post_args["accountID"] == req.post_args["targetAccountID"]

    # If we are checking ourselves, we can just set the target user to that.
    if checking_self:
        target: User = user
    # We have to fetch the user directly.
    else:
        target: User = await User.from_id(req.post_args["targetAccountID"])

        # TODO: Blocked check

    resp_dict = {
        1: target.name,
        2: target.id,
        3: target.stats.stars,
        4: target.stats.demons,
        6: target.stats.rank,
        7: target.id,
        8: target.stats.cp,
        9: target.stats.display_icon,
        10: target.stats.colour1,
        11: target.stats.colour2,
        13: target.stats.coins,
        14: target.stats.icon,
        15: 0, # "Special" value. Not sure what it does.
        16: target.id,
        17: target.stats.u_coins,
        # States.
        18: 0 if target.req_states & ReqStats.MESSAGES else 1,
        19: 0 if target.req_states & ReqStats.REQUESTS else 1,
        20: target.youtube_url,
        21: target.stats.icon,
        22: target.stats.ship,
        23: target.stats.ball,
        24: target.stats.ufo,
        25: target.stats.wave,
        26: target.stats.robot,
        28: int(target.stats.glow),
        29: 1,
        30: target.stats.rank,
        31: 0, # TODO: Friend state.,
        43: target.stats.spider,
        44: target.twitter_url,
        45: target.twitch_url,
        46: target.stats.diamonds,
        48: target.stats.explosion,
        49: 0, # TODO: Mod levels (when privileges are done.)
        50: 0 if target.req_states & ReqStats.COMMENTS else 1
    }

    return gd_dict_str(resp_dict)

async def update_stats(req: Request, user: User):
    """Handles the `updateGJUserScore22.php` endpoint."""

    # TODO: Analyse the data coming in for Cheatless AC.
    # TODO: Investigate the use of seed and seed2 for anticheat.

    # Converting these to int also ensures proper input is passed.
    stars        = int(req.post_args.get("stars", 0))
    demons       = int(req.post_args.get("demons", 0))
    display_icon = int(req.post_args.get("icon", 0))
    diamonds     = int(req.post_args.get("diamonds", 0))
    colour1      = int(req.post_args.get("color1", 0))
    colour2      = int(req.post_args.get("color2", 1))
    icon         = int(req.post_args.get("accIcon", 0))
    ship         = int(req.post_args.get("accShip", 0))
    ball         = int(req.post_args.get("accBall", 0))
    ufo          = int(req.post_args.get("accBird", 0))
    wave         = int(req.post_args.get("accDart", 0))
    robot        = int(req.post_args.get("accRobot", 0))
    glow         = int(req.post_args.get("accGlow", 0))
    spider       = int(req.post_args.get("accSpider", 0))
    explosion    = int(req.post_args.get("accExplosion", 0))
    coins        = int(req.post_args.get("coins", 0))
    u_coins      = int(req.post_args.get("userCoints", 0))

    # Now we set them for the user.
    await user.stats.set_stats(
        stars= stars,
        diamonds= diamonds,
        coins= coins,
        u_coins = u_coins,
        demons= demons,
        colour1= colour1,
        colour2= colour2,
        icon= icon,
        ship= ship,
        ufo= ufo,
        wave= wave,
        robot= robot,
        ball= ball,
        spider= spider,
        explosion= explosion,
        display_icon= display_icon,
        glow= glow
    )

    # We have to return the users account ID.
    return user.id

async def account_comments(req: Request):
    """Handles the `getGJAccountComments20.php` endpoint."""

    # We fetch data from post data.
    page = int(req.post_args["page"])
    target_id = int(req.post_args["accountID"])

    target_user = await User.from_id(target_id)
    
    # Check if user found.
    if not target_user:
        raise GDException("-1")

    # Ok so first we have to only grab the specific section
    # the gd client wants as its only asking for like 10
    # at a time.
    a_com = paginate_list(
        target_user.account_comments,
        page,
        10
    )


    f_comments = "|".join([
        gd_dict_str({
            2: base64_encode(i.content),
            4: i.likes,
            6: i.id,
            9: time_ago(i.timestamp),
            12: "255,255,255" # TODO: When privilege groups are added.
        }, "~") for i in a_com
    ])

    # We append pagination details.
    f_comments += f"#{len(target_user.account_comments)}:{page}:10"
    return f_comments

async def upload_acc_comment(req: Request, user: User) -> str:
    """Handles the `uploadGJAccComment20.php` endpoint."""

    # We grab the content from post args and immidiately decode b64
    content = base64_decode(req.post_args["comment"])

    # Now we create the account comment object from scratch.
    com = AccountComment.from_text(
        account_id= user.id,
        content= content
    )

    # And lastly we insert it into the db.
    await com.insert()

    # Idk just give them a success.
    return 1

async def delete_acc_comment(req: Request, user: User) -> str:
    """Handles the `deleteGJAccComment20.php` endpoint."""

    # Get the comment object from the id provided.
    com = await AccountComment.from_db(
        req.post_args["commentID"]
    )

    # Check if the user is the same as the poser.
    if com.account_id != user.id:
        # They are sending the reqs not through the client.
        raise GDException("-1")

    # Delete the comment.
    await com.delete()
    
    # Send a success message.
    return 1
