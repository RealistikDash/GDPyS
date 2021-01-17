from objects.user import User
from web.http import Request # Pylint appeasement.
from web.builders import gd_dict_str
from const import ReqStats

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
        18: 1 if target.req_states & ReqStats.MESSAGES else 0,
        19: 1 if target.req_states & ReqStats.REQUESTS else 0,
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
        50: 1 if target.req_states & ReqStats.COMMENTS else 0
    }

    return gd_dict_str(resp_dict)
