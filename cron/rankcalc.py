from conn.mysql import myconn
from constants import Permissions

ranks = {}  # For now I will store it here.


async def cron_calc_ranks() -> None:
    """Calculates all ranks for users and stores them in cache."""  # I may move this to a cron category however that does not currently exist.
    async with myconn.conn.cursor() as mycursor:
        await mycursor.execute("SELECT extID FROM users WHERE extID IN (SELECT accountID FROM accounts WHERE privileges & %s AND isBot = 0) ORDER BY stars DESC", (Permissions.authenticate,))
        users = await mycursor.fetchall()

    curr_rank = 0  # There is most likely a better way to do this but I don't know it yet
    for user in users:
        curr_rank += 1
        ranks[int(user[0])] = curr_rank
