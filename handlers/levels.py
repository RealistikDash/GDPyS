import logging
import aiohttp
from helpers.levelhelper import level_helper
from helpers.searchhelper import search_helper
from helpers.generalhelper import create_offsets_from_page, string_bool, joint_string
from helpers.songhelper import songs
from helpers.userhelper import user_helper
from objects.levels import SearchQuery, Level

async def level_search_modular_hanlder(request : aiohttp.web.Request) -> aiohttp.web.Response:
    """Handles the get levels endpoint."""
    post_data = await  request.post()

    offset = create_offsets_from_page(int(post_data["page"]))
    # Okay so here we have to create the search query object. May have to redo it but this should be sufficient for the time being.
    query = SearchQuery(
        int(post_data["type"]),
        offset,
        None, # Uncertain if order is used.
        int(post_data.get("gauntlet", 0)),
        string_bool(post_data["featured"]),
        string_bool(post_data["original"]),
        string_bool(post_data["epic"]),
        string_bool(post_data["twoPlayer"]),
        string_bool(post_data["star"]),
        string_bool(post_data.get("noStar", "0")),
        post_data.get("len", ""),
        int(post_data.get("song", 0)),
        int(post_data.get("customSong", 0)),
        post_data.get("diff", ""),
        post_data.get("str", "")
    )
    logging.debug(query)

    levels = await search_helper.get_levels(query)

    # Getting final reponse
    response = ""
    lvls_list = []
    song_str = ""
    user_str = ""
    gauntlet_append = "" if not query.gauntlet else f"44:{query.gauntlet}:"
    for level in levels.results:
        level : Level
        response += gauntlet_append
        lvls_list.append(level.ID)
        user_str += user_helper.get_user_string(level.user_id) + "|"
        if level.song_id:
            song_str += songs.song_string(songs.get_song_obj(level.song_id)) + "~:~"
        #THIS IS WHERE THE **FUN** BEGINS
        response += joint_string(
            {
                1 : level.ID,
                2 : level.name,
                5 : level.version,
                6 : level.user_id,
                8: 10,
                9 : level_helper.star_to_difficulty(level.stars),
                10 : level.downloads,
                12 : level.track,
                13 : level.game_version,
                14 : level.likes,
                17 : True if level.stars == 10 else False,
                25 : True if level.stars == 1 else False,
                18 : level.stars,
                19 : int(level.featured),
                42 : int(level.epic),
                45 : level.objects,
                3 : level.description,
                15 : level.length,
                30 : int(level.original),
                31 : 0,
                37 : level.coins,
                38 : int(level.verified_coins),
                39 : level.requested_stars,
                41 : 1,
                47 : 2,
                40 : int(level.ldm),
                35 : level.song_id
            }
        )
    
    response = response[:-1] + "#" + user_str[:-1] + "#" + song_str[:-3] + f"#{levels.total_results}:{offset}:10#" + await level_helper.multi_gen(lvls_list)
    logging.debug(response)
    return aiohttp.web.Response(text=response)
