# All of the GDPyS API handlers.
from __future__ import annotations

from const import HandlerTypes
from exceptions import GDPySAPIBadData
from exceptions import GDPySAPINotFound
from objects import glob
from objects.user import User
from web.http import Request


@glob.add_route("/api/user", HandlerTypes.JSON)
async def get_user_api(req: Request) -> dict:
    """Handles `/api/user`."""

    # Grab account ID.
    acc_id = req.get_args.get("id")

    if acc_id is None or not acc_id.isnumeric():
        raise GDPySAPIBadData()

    u = await User.from_id(int(acc_id))

    if u is None:
        raise GDPySAPINotFound

    return u.api()
