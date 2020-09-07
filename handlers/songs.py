from helpers.songhelper import songs
from helpers.generalhelper import create_offsets_from_page, joint_string
from constants import ResponseCodes
import aiohttp
import logging

async def featured_artists_handler(request : aiohttp.web.Request):
    """Handles the featured artists page."""
    post_data = await request.post()

    ## Checks yes
    if songs.top_artists == []: # This is a solution to no async inits.
        songs.top_artists = await songs._top_artists()

    offset = create_offsets_from_page(int(post_data["page"]), 20) * -1
    artists = songs.top_artists[offset:20]
    response = ""

    for artist in artists:
        response += joint_string({
            4 : artist
        }) + "|"
    response = response[:-1] + f"#{len(songs.top_artists)}:{offset*-1}:20"
    logging.debug(response)
    return aiohttp.web.Response(text=response[:-1])
