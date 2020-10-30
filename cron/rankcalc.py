from constants import Permissions

ranks = {}  # For now I will store it here.


async def cron_calc_ranks(conn) -> None:
    """Calculates all ranks for users and stores them in cache."""  # I may move this to a cron category however that does not currently exist.
    async with conn.cursor() as mycursor:
        await mycursor.execute(
            "SELECT extID FROM users WHERE extID IN (SELECT accountID FROM accounts WHERE privileges & %s AND isBot = 0) ORDER BY stars DESC",
            (Permissions.AUTH,),
        )
        users = await mycursor.fetchall()

    for rank, user in enumerate(users):
        # Add 1 to rank as lists are 0 indexed.
        ranks[int(user[0])] = rank + 1
