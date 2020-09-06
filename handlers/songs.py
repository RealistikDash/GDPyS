from helpers.songhelper import songs
from helpers.generalhelper import create_offsets_from_page, joint_string
from constants import ResponseCodes
import aiohttp
import logging

async def featured_artists_handler(request : aiohttp.web.Request):
    """Handles the featured artists page."""
    post_data = await request.post()

    offset = create_offsets_from_page(int(post_data["page"]), 20) * -1
    artists = songs.top_artists[offset:20]
    response = ""

    for artist in artists:
        response += joint_string({
            4 : artist
        }) + "|"
    
    logging.debug(response[:-1])
    return aiohttp.web.Response(text=response[:-1])
