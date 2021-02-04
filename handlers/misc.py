from objects.song import Song
from exceptions import GDException
from const import Secrets
from logger import debug

async def get_song(req) -> str:
    """Handles `getGJSongInfo.php` endpoint."""

    # Mini check for stupid bots.
    if req.post["secret"] not in Secrets.ALL:
        raise GDException("-1")

    # Grab Song object and return its repr.
    if s := await Song.from_id(
        int(req.post["songID"])
    ):
        return repr(s)
    
    debug(f"Requested song {req.post['songID']} could not be found...")
    raise GDException("-1")
