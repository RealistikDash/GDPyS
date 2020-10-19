from conn.mysql import myconn
from helpers.generalhelper import dict_keys
from helpers.lang import lang
from objects.misc import RGB, Privilege
from config import user_config
import logging


class PrivilegeHelper:
    """Handles all of the stuff regarding privileges. I am a god at masterful descriptions."""

    def __init__(self):
        """Begins the caches etc."""
        self.privilege_cache = {}  # Caches privileges, in dict for easy lookup
        self.DEFAULT = Privilege(0, "Default", 30, RGB(255, 255, 255))

    async def cache_privs(self) -> None:
        """Caches all server privileges."""
        self.privilege_cache.clear()  # So we don't have overlap
        # Prevent config not loading in time
        self.DEFAULT = Privilege(
            0, "Default", user_config["default_priv"], RGB(255, 255, 255)
        )
        # Fetching all of the db privs.
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "SELECT id, name, privileges, colour FROM privilegegroups"
            )  # A server shouldn't have any more than like 10 groups
            privs_db = await mycursor.fetchall()

        for priv in privs_db:
            colour_list = priv[3].split(",")
            try:
                colour = RGB(colour_list[0], colour_list[1], colour_list[2])
            except IndexError:
                logging.warn(lang.warn("privilege_invalid_colour", priv[1]))
                colour = RGB(255, 255, 255)
            self.privilege_cache[priv[2]] = Privilege(priv[0], priv[1], priv[2], colour)
            logging.debug(lang.debug("privelege_cached", priv[1], priv[0]))

    async def get_privilege_from_privs(self, privilege_num: int) -> Privilege:
        """Returns privilege from priv num."""
        if privilege_num in dict_keys(self.privilege_cache):
            return self.privilege_cache[privilege_num]
        return self.DEFAULT


priv_helper = PrivilegeHelper()
