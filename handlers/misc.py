from objects.song import Song
from exceptions import GDPySHandlerException
from const import Secrets
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
