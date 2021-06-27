from exceptions import GDPySHandlerException
from objects.song import Song
from objects.user import User
from web.http import Request
from objects.level import Level
from objects import glob
from helpers.crypt import base64_decode, base64_encode, sha1_hash
from logger import info, debug
from utils.gdform import gd_dict_str
from const import LevelStatus, DB_PREFIX, HandlerTypes

@glob.add_route(
    path= DB_PREFIX + "/uploadGJLevel21.php",
    status= HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED,
    args= ("gameVersion", "auto", "seed2", "secret", "wt2", "gdw", "levelInfo", "levelID")
)
async def upload_level(req: Request, user: User) -> str:
    """Handles the endpoint `uploadGJLevel21.php`."""

    # TODO: Perm checks
    # Check whether we are updating the level.
    if l_id := int(req.post["levelID"]):
        # Ok so if we do not have the level on the server, we get them to 
        # upload again. If it exists, we update.
        if level := await Level.from_id(l_id):
            debug(f"{user} is updating the level {level}!")
            # Some stuff we have to decode and ensure correct types.
            desc = base64_decode(req.post["levelDesc"])
            level.update(
                description= desc,
                unlisted= req.post["unlisted"] == "1",
                ldm= req.post["ldm"] == 1,
                # TODO: More.
            )
            await level.write(req.post["levelString"])
            return level.id
        
    else:
        # We are uploading new level.
        debug(f"{user} is uploading a new level!")
        l: Level = await Level.from_submit(user, req)
        await l.insert()
        await l.write(req.post["levelString"])
        info(f"Uploaded new level {l}.")
        return l.id

# Pure SQL level search. 0 caching. This is kinda bad but i couldnt think of
# an efficient way that works with our current level object way without
# employing like elastic search, which is REALLY overkill for our scope.
# TODO: Investigate caching frequently used search filters, such as:
# - Featured/Epic Levels
# - Gauntlets
# - Mappacks
# - Recent levels
# - Most liked levels
# - Most downloaded levels

BASE_QUERY = (
    "SELECT l.id, name, description, version, user_id, difficulty, downloads, "
    "track_id, game_version, likes, length, l.stars, featured_id, "
    "original, two_player, song_id, extra_str, l.coins, "
    "coins_verified, requested_stars, rate_status, demon_diff, objects, working_time, "
    "u.username FROM levels l INNER JOIN users u ON l.user_id = u.id "
)

BASE_COUNT = "SELECT COUNT(*) FROM levels "
PAGE_SIZE = 20
SECURITY_APPEND = "xI25fpAapCQg"

@glob.add_route(
    path= DB_PREFIX + "/getGJLevels21.php",
    status= HandlerTypes.PLAIN_TEXT,
    args= ("type", "gdw", "gameVersion", "str", "len", "page")
)
async def level_search(req: Request) -> str:
    """Handles level search (`getGJLevels21.php`)."""

    query_where = []
    query_where_fmt = []

    # Setting and confirming values.
    search_type = int(req.post["type"])
    search_query = req.post["str"]
    offset = int(req.post["page"]) * PAGE_SIZE

    info(f"Level search for '{search_query}' ({search_type}, {offset})")

    #### IGNORE FOR TESTING.
    levels_db = await glob.sql.fetchall(BASE_QUERY + f"LIMIT {PAGE_SIZE} OFFSET {offset}")
    count_db = (await glob.sql.fetchone(BASE_COUNT))[0]

    level_strs = []
    user_strs = []
    song_strs = []
    security_strs = []
    for level in levels_db:
        level_strs.append(gd_dict_str({
            1: level[0],
            2: level[1],
            3: base64_encode(level[2]),
            5: level[3],
            6: level[4],
            8: 10 if level[11] else 0,
            9: level[5],
            10: level[6],
            12: level[7],
            13: level[8],
            14: level[9],
            15: level[10],
            # 16: dislikes
            17: 1 if level[11] == 10 else 0,
            18: level[11] == 10,
            19: level[12],
            25: 1 if level[11] == 1 else 0,
            30: level[13],
            31: level[14],
            35: level[15],
            36: level[16],
            37: level[17],
            38: level[18],
            39: level[19],
            # Level Status check for epic.
            42: 1 if level[20] & LevelStatus.EPIC else 0,
            43: level[21],
            # 44: is in gauntlet
            45: level[22],
            46: level[23],
            47: level[23]
        }))

        # Grab song
        if level[15]:
            song_strs.append(
                (await Song.from_id(level[15])).resp()
            )
        
        # User string weirdness...
        user_strs.append(f"{level[4]}:{level[24]}:{level[4]}")

        # THIS SECURTIY AIDS.
        level_id = str(level[0])
        security_strs.append(
            f"{level_id[0]}{level_id[-1]}{level[11]}{level[17]}"
        )
    
    # Build final resp.
    level_str = "|".join(level_strs)
    user_str = "|".join(user_strs)
    song_str = "~:~".join(song_strs)
    page_info = f"{count_db}:{offset}:{PAGE_SIZE}"
    security_str = sha1_hash("".join(security_strs) + SECURITY_APPEND)

    return "#".join((level_str, user_str, song_str, page_info, security_str))

@glob.add_route(
    path= DB_PREFIX + "/downloadGJLevel22.php",
    status= HandlerTypes.PLAIN_TEXT,
    args= ("levelID", "secret", "gdw", "extras", "rs", "udid")
)
async def download_level(req: Request) -> str:
    """Handles `downloadGJLevel22.php`"""

    level_id = int(req.post["levelID"])

    # Daily and weekly levels.
    if level_id in (-1, -2):
        ...
    else:
        level: Level = await Level.from_id(level_id)
        if not level: raise GDPySHandlerException("-1")
    
    info(f"Serving level {level}")

    level_str = await level.load()
    # TODO: Download increment.
    main_resp =  gd_dict_str({
        1: level.id,
        2: level.name,
        3: base64_encode(level.description),
        4: level_str,
        5: level.version,
        6: level.creator.id,
        8: 10 if level.difficulty else 0,
        9: level.difficulty,
        10: level.downloads,
        12: level.track_id,
        13: level.game_version,
        14: level.likes,
        15: level.length,
        17: 1 if level.stars == 10 else 0,
        18: level.stars,
        19: level.feature_id,
        25: 1 if level.stars == 1 else 0,
        26: level.replay,
        27: level.password,
        28: level.timestamp,
        29: level.update_ts,
        30: level.original,
        31: 1 if level.original else 0,
        35: level.song.id if level.song else 0,
        36: level.extra_str,
        37: level.coins,
        38: 1 if level.coins_verified else 0,
        39: level.requested_stars,
        40: 1 if level.ldm else 0,
        41: 0, # TODO: DAILY NUMBER.
        42: 1 if level.epic else 0,
        43: level.demon_diff,
        45: level.objects,
        46: level.working_time,
        47: level.working_time
    })

    # This is taken from Cvolton's GMDPrivateServer.
    # https://github.com/Cvolton/GMDprivateServer/blob/master/incl/lib/generateHash.php#L16-L26
    security_str = ""
    s_len = len(level_str) // 40
    for i in range(40):
        security_str += level_str[i * s_len]
    security_str = sha1_hash(security_str + SECURITY_APPEND)

    security_str2 = ",".join(
        (str(level.creator.id), str(level.stars), "1" if level.demon else "0", str(level.id),
        "1" if level.coins_verified else "0", str(level.feature_id), level.password, "0")
    )
    security_str2_h = sha1_hash(security_str2 + SECURITY_APPEND)

    return "#".join(
        (main_resp, security_str, security_str2_h, security_str2)
    )
