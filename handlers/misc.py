from objects.song import Song
from objects.glob import glob
from exceptions import GDPySHandlerException
from const import Secrets, GDPyS
from helpers.time import time_ago, get_timestamp
from logger import debug

async def get_song(req) -> str:
    """Handles `getGJSongInfo.php` endpoint."""

    # Mini check for stupid bots.
    if req.post["secret"] not in Secrets.ALL:
        raise GDPySHandlerException("-1")

    # Grab Song object and return its gd style resp.
    if s := await Song.from_id(
        int(req.post["songID"])
    ):
        return s.resp()
    
    debug(f"Requested song {req.post['songID']} could not be found...")
    raise GDPySHandlerException("-1")

async def index(req) -> str:
    """The GDPyS index page `/`."""

    return (
        f"Running {GDPyS.NAME} Build {GDPyS.BUILD}\n"
        f"Connections handled: {glob.connections_handled}\n"
        f"Users registered: {glob.registered_users}\n"
        f"Cached users: {glob.user_cache.cached_items}\n"
        f"Server started {time_ago(get_timestamp() - glob.startup_time, False)} ago"
    )
