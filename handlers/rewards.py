from helpers.rewardshelper import rewards_helper
from helpers.userhelper import user_helper
from helpers.crypthelper import decode_chk, cipher_xor, encode_base64, solo_gen3
from helpers.timehelper import tomorrow,get_timestamp
from objects.quests import Quest
from constants import XorKeys
import aiohttp
import random
import logging

async def quests_handler(request : aiohttp.web.Request):
    """Returns quests to game client."""
    post_data = await request.post()
    
    # Creating variables GD for some reason needs...
    chk_decoded = decode_chk(post_data["chk"])
    user = await user_helper.get_object(int(post_data["accountID"])) # We are assuming it is a cached object so we reduce DB calls.
    device_id = post_data["udid"]
    base_id = rewards_helper.gen_id()
    quests = await rewards_helper.get_quests() # This is so we can pop quests we already used without messing up the global quests.
    quest_str = []

    for i in range(3): # Get  3 raandom quests. This is a basic form of quest differentiation and is prob due for a redo
        curr_quest : Quest = random.choice(quests)
        quests.remove(curr_quest)
        quest_str.append(
            f"{base_id + i},{curr_quest.sort},{curr_quest.amount},{curr_quest.reward},{curr_quest.text}"
        )
    
    resp1 = encode_base64(cipher_xor(f"bruhh:{user.user_id}:{chk_decoded}:{device_id}:{user.account_id}:{tomorrow()-get_timestamp()}:{quest_str[0]}:{quest_str[1]}:{quest_str[2]}", XorKeys.quests))
    hashed = solo_gen3(resp1)
    response = f"bruhh{resp1}|{hashed}"
    logging.debug(response)
    return aiohttp.web.Response(text=response)
