# Couldn't think of a good name for the file but this just caches the gauntlets and map-packs. Bunched them up as they are REALLY similar.
from objects.levels import Gauntlet, MapPack
from objects.misc import RGB
from helpers.lang import lang
import logging

map_packs = []
gauntlets = []


async def cron_cache_mappacks(conn):
    """Cron job that caches the map packs."""
    map_packs.clear()
    # We get all of the map packs from the database.
    async with conn.cursor() as mycursor:
        await mycursor.execute(
            "SELECT ID, name, levels, stars, coins, difficulty, rgbcolors FROM mappacks"
        )  # Shouldnt be too much I think.
        packs_db = await mycursor.fetchall()

    for pack in packs_db:
        # Create the necessary variables and maybe error handle.
        level_list = pack[2].split(",")
        colour_list = pack[6].split(",")
        try:
            colour = RGB(colour_list[0], colour_list[1], colour_list[2])
        except IndexError:
            logging.warn(lang.warn("pack_invalid_colour", pack[1]))
            colour = RGB(255, 255, 255)
        map_packs.append(
            MapPack(pack[0], pack[1], level_list, pack[3], pack[4], pack[5], colour)
        )


async def cron_cache_gauntlets(conn):
    """Caches the in-game gauntlets."""
    gauntlets.clear()
    # Getting all of the gauntlets from the database.
    async with conn.cursor() as mycursor:
        await mycursor.execute(
            "SELECT ID, level1,level2,level3,level4,level5 FROM gauntlets"
        )
        gauntlets_db = await mycursor.fetchall()

    for gauntlet in gauntlets_db:
        gauntlets.append(
            Gauntlet(
                gauntlet[0],
                gauntlet[1],
                gauntlet[2],
                gauntlet[3],
                gauntlet[4],
                gauntlet[5],
            )
        )
