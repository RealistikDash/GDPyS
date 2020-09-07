from helpers.songhelper import songs
from helpers.generalhelper import create_offsets_from_page, joint_string, pipe_string
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

async def get_songinfo_handler(request : aiohttp.web.Request):
    """Gets song info for GD songs."""
    post_data = await request.post()

    song = await songs.get_song_obj(post_data["songID"])

    # Checks
    if song is None:
        return aiohttp.web.Response(text=ResponseCodes.generic_fail)
    
    response = pipe_string({
        1 : song.ID,
        2 : song.name,
        3 : song.author_id,
        4 : song.author_name,
        5 : song.file_size,
        6 : "",
        10 : song.url,
        7 : ""
    })
    logging.debug(response)

    return aiohttp.web.Response(text=response)
