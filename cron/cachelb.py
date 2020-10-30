from helpers.userhelper import user_helper

# Lists of user objects in order of stars
top_stars = []
top_cp = []


async def get_list(conn, order: str = "stars") -> list:
    """Gets list of users ordered desc by arg."""
    async with conn.cursor() as mycursor:
        await mycursor.execute(
            f"SELECT extID FROM users WHERE isBanned = 0 ORDER BY {order} DESC LIMIT 100"
        )  # TODO: isBanned alternative
        list_id = await mycursor.fetchall()
    return [i[0] for i in list_id]


async def cron_top_stars(conn):
    """Caches top 100 leaderboards."""
    top_stars.clear()
    # We have to cache all the user objects.
    for account_id in await get_list(conn, "stars"):
        top_stars.append(
            await user_helper.get_object(account_id)
        )  # Honestly I have no clue how to not store the objects separately twice plus this helps when adding features like lb freezing.


async def cron_top_cp(conn):
    """Caches top cp leaderboards."""
    top_cp.clear()
    # We have to cache all the user objects.
    for account_id in await get_list(conn, "creatorPoints"):
        top_cp.append(
            await user_helper.get_object(account_id)
        )  # Honestly I have no clue how to not store the objects separately twice plus this helps when adding features like lb freezing.
