from conn.mysql import myconn
from helpers.userhelper import user_helper

# Lists of user objects in order of stars
top_stars = []
top_cp = []


async def get_list(order: str = "stars") -> list:
    """Gets list of users ordered desc by arg."""
    async with myconn.conn.cursor() as mycursor:
        # TODO: isBanned alternative
        await mycursor.execute(f"SELECT extID FROM users WHERE isBanned = 0 ORDER BY {order} DESC LIMIT 100")
        list_id = await mycursor.fetchall()
    return [i[0] for i in list_id]


async def cron_top_stars():
    """Caches top 100 leaderboards."""
    top_stars.clear()
    # We have to cache all the user objects.
    for account_id in await get_list("stars"):
        # Honestly I have no clue how to not store the objects separately twice plus this helps when adding features like lb freezing.
        top_stars.append(await user_helper.get_object(account_id))


async def cron_top_cp():
    """Caches top cp leaderboards."""
    top_cp.clear()
    # We have to cache all the user objects.
    for account_id in await get_list("creatorPoints"):
        # Honestly I have no clue how to not store the objects separately twice plus this helps when adding features like lb freezing.
        top_cp.append(await user_helper.get_object(account_id))
