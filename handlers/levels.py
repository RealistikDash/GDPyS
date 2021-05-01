from objects.user import User
from web.http import Request
from objects.level import Level
from helpers.crypt import base64_decode

async def upload_level(req: Request, user: User) -> str:
    """Handles the endpoint `uploadGJLevel21.php`."""

    # Check whether we are updating the level.
    if l_id := int(req.post["levelID"]):
        level: Level = await Level.from_id(l_id)
        # Ok so if we do not have the level on the server, we get them to 
        # upload again. If it exists, we update.
        if level:
            # Some stuff we have to decode and ensure correct types.
            desc = base64_decode(req.post["levelDesc"])
            level.update(
                description= desc,
                unlisted= req.post["unlisted"] == "1",
                ldm= req.post["ldm"] == 1
            )
