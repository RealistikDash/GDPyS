from helpers.rewardshelper import rewards_helper
from helpers.userhelper import user_helper
from helpers.crypthelper import decode_chk
import aiohttp

async def quests_handler(request : aiohttp.web.Request):
    """Returns quests to game client."""
    post_data = await request.post()
    
