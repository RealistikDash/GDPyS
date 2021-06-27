from objects.user import User
from web.http import Request # Pylint appeasement.
from utils.gdform import gd_dict_str
from helpers.common import paginate_list
from helpers.crypt import base64_encode, base64_decode
from helpers.time import time_ago
from objects import glob
from utils.security import verify_stats_seed, verify_textbox
from exceptions import GDPySHandlerException
from objects.comments import AccountComment
from const import ReqStats, HandlerTypes, DB_PREFIX
from logger import debug

# LOCAL CONSTS
REQ_STATES = {
    "0": ReqStats.MESSAGES,
    "1": ReqStats.MESSAGES_FRIENDS_ONLY
}

COMMENT_STATES = {
    "0": ReqStats.COMMENTS,
    "1": ReqStats.COMMENTS_FRIENDS_ONLY
}

@glob.add_route(
    path= DB_PREFIX + "/getGJUserInfo20.php",
    status= HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED,
    args= ("gameVersion", "binaryVersion", "gdw", "accountID", "gjp", "targetAccountID", "secret")
)
async def user_info(req: Request, user: User):
    """Handles the `getGJUserInfo20.php` endpoint."""

    # Check if we are fetching ourselves.
    checking_self = req.post["accountID"] == req.post["targetAccountID"]

    # If we are checking ourselves, we can just set the target user to that.
    if checking_self:
        target: User = user
    # We have to fetch the user directly.
    else:
        target: User = await User.from_id(req.post["targetAccountID"])

        # TODO: Blocked check

    # Here we build it ourselves as it has extra data
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
        18: 0 if target.messages_enabled else 2 if target.messages_fo else 1,
        19: 0 if target.friend_requests_enabled else 1,
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
        49: target.badge_level,
        50: 0 if target.comment_history_enabled else 2 if target.comment_history_fo else 1
    }

    return gd_dict_str(resp_dict)

@glob.add_route(
    path= DB_PREFIX + "/updateGJUserScore22.php",
    status= HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED,
    args= ("secret", "accGlow", "iconType", "accountID", "gjp", "userCoins", "seed2", "seed")
)
async def update_stats(req: Request, user: User):
    """Handles the `updateGJUserScore22.php` endpoint."""

    # TODO: Analyse the data coming in for Cheatless AC.
    # TODO: Investigate the use of seed and seed2 for anticheat.

    # Verifiying some neiche post args.
    if not verify_stats_seed(req.post["seed"]):
        raise GDPySHandlerException("-1")

    # Converting these to int also ensures proper input is passed.
    stars        = int(req.post.get("stars", 0))
    demons       = int(req.post.get("demons", 0))
    display_icon = int(req.post.get("icon", 0))
    diamonds     = int(req.post.get("diamonds", 0))
    colour1      = int(req.post.get("color1", 0))
    colour2      = int(req.post.get("color2", 1))
    icon         = int(req.post.get("accIcon", 0))
    ship         = int(req.post.get("accShip", 0))
    ball         = int(req.post.get("accBall", 0))
    ufo          = int(req.post.get("accBird", 0))
    wave         = int(req.post.get("accDart", 0))
    robot        = int(req.post.get("accRobot", 0))
    glow         = int(req.post.get("accGlow", 0))
    spider       = int(req.post.get("accSpider", 0))
    explosion    = int(req.post.get("accExplosion", 0))
    coins        = int(req.post.get("coins", 0))
    u_coins      = int(req.post.get("userCoints", 0))

    # Now we set them for the user.
    await user.stats.set_stats(
        stars=        stars,
        diamonds=     diamonds,
        coins=        coins,
        u_coins=      u_coins,
        demons=       demons,
        colour1=      colour1,
        colour2=      colour2,
        icon=         icon,
        ship=         ship,
        ufo=          ufo,
        wave=         wave,
        robot=        robot,
        ball=         ball,
        spider=       spider,
        explosion=    explosion,
        display_icon= display_icon,
        glow=         glow
    )

    # We have to return the users account ID.
    return user.id

@glob.add_route(
    path= DB_PREFIX + "/getGJAccountComments20.php",
    status= HandlerTypes.PLAIN_TEXT,
    args= ("accountID", "total", "page", "secret", "gdw")
)
async def account_comments(req: Request):
    """Handles the `getGJAccountComments20.php` endpoint."""

    # We fetch data from post data.
    page = int(req.post["page"])
    target_id = int(req.post["accountID"])

    target_user = await User.from_id(target_id)
    
    # Check if user found.
    if not target_user:
        raise GDPySHandlerException("-1")

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
            12: str(target_user.privilege.colour)
        }, "~") for i in a_com
    ])

    # We append pagination details.
    f_comments += f"#{len(target_user.account_comments)}:{page}:10"
    return f_comments

@glob.add_route(
    path= DB_PREFIX + "/uploadGJAccComment20.php",
    status= HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED,
    args= ("accountID", "gjp", "comment", "secret", "chk", "cType")
)
async def upload_acc_comment(req: Request, user: User) -> str:
    """Handles the `uploadGJAccComment20.php` endpoint."""

    # We grab the content from post args and immidiately decode b64
    content = base64_decode(req.post["comment"])

    # Now we create the account comment object from scratch.
    com = AccountComment.from_text(
        account_id= user.id,
        content= content
    )

    # And lastly we insert it into the db.
    await com.insert()

    # Idk just give them a success.
    return 1

@glob.add_route(
    path= DB_PREFIX + "/deleteGJAccComment20.php",
    status= HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED,
    args= ("accountID", "gjp", "secret", "commentID")
)
async def delete_acc_comment(req: Request, user: User) -> str:
    """Handles the `deleteGJAccComment20.php` endpoint."""

    # Get the comment object from the id provided.
    com = await AccountComment.from_db(
        req.post["commentID"]
    )

    # Check if the user is the same as the poser.
    if com.account_id != user.id:
        # They are sending the reqs not through the client.
        raise GDPySHandlerException("-1")

    # Delete the comment.
    await com.delete()
    
    # Send a success message.
    return 1

@glob.add_route(
    path= DB_PREFIX + "/updateGJAccSettings20.php",
    status= HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED,
    args= ("accountID", "gjp", "secret")
)
async def update_social(req: Request, user: User) -> str:
    """Handles the `updateGJAccSettings20.php` endpoint."""

    # Set post data to vars.
    youtube = req.post.get("yt")
    twitter = req.post.get("twitter")
    twitch  = req.post.get("twitch")

    # Verify values
    for social in (youtube, twitch, twitter):
        if not verify_textbox(social, ["."]):
            debug("User failed value verification check.")
            raise GDPySHandlerException("-1")
    
    new_req_state = 0

    new_req_state += REQ_STATES.get(req.post["mS"], 0)

    new_req_state += ReqStats.REQUESTS if req.post["frS"] == "0" else 0

    new_req_state += COMMENT_STATES.get(req.post.get("cS"), 0)

    new_req_state = ReqStats(new_req_state)

    # Lastly we update them.
    await user.update_socials(
        youtube= youtube,
        twitter= twitter,
        twitch= twitch,
        req_state= new_req_state
    )

    # Return a success!
    return 1

@glob.add_route(
    path= DB_PREFIX + "/getGJUsers20.php",
    status= HandlerTypes.PLAIN_TEXT,
    args= ("str", "page", "total")
)
async def profile_search(req: Request) -> str:
    """Handles `getGJUsers20.php`."""

    # NOTE: For speed reasons, we are only getting exact results.

    # UserID search.
    search = req.post["str"]
    if search.isnumeric():
        u = await User.from_id(int(search))
    else:
        u = await User.from_name(search)
    
    # If not found.
    if u is None:
        return "#0:0:10"
    
    return u.resp() + "#1:0:10"

@glob.add_route(
    path= DB_PREFIX + "/requestUserAccess.php",
    status= HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED,
    args= ("accountID", "gjp", "secret", "gameVersion", "binaryVersion", "gdw")
)
async def req_mod(req: Request, user: User) -> str:
    """Handles `requestUserAccess.php` (mod check.)"""

    # Here we simply utilise their mod badge level as it would be a bit
    # useless to create a new permission for this.

    lvl = user.badge_level

    return lvl if lvl != 0 else -1 # Weird request requirement but ok.
