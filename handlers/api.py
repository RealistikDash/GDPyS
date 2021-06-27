# All of the GDPyS API handlers.
from exceptions import GDPySAPIBadData, GDPySAPINotFound
from web.http import Request
from objects.user import User
from const import HandlerTypes
from objects import glob

@glob.add_route("/api/user", HandlerTypes.JSON)
async def get_user_api(req: Request) -> dict:
    """Handles `/api/user`."""

    # Grab account ID.
    acc_id = req.get_args.get("id")

    if acc_id is None or not acc_id.isnumeric():
        raise GDPySAPIBadData()

    u = await User.from_id(int(acc_id))

    if u is None: raise GDPySAPINotFound

    return u.api()
