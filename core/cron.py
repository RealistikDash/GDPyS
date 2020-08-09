import time as pytime
#gdpys things
from console import logger, Log, Success, Fail
from functions import UserIDCache, Ranks
from core.mysqlconn import mydb
from config import UserConfig
from helpers.timer import Timer

def cron_thread():
    Log("Cron thread started!")
    while True:
        Log("Running cron!")
        time = Timer()
        time.start()
        cron_cursor = mydb.cursor() #create cursor specifically for cron jobs
        cache_user_ids(cron_cursor)
        cache_ranks(cron_cursor)
        calculate_cp(cron_cursor)
        max_star_count_ban(cron_cursor)
        cron_cursor.close() #close it after all is done
        time.end()
        Log(f"Cron done! Took {time.ms_return()}s")
        pytime.sleep(UserConfig["CronThreadDelay"])

def cache_user_ids(cron_cursor):
    """Caches all UserIDs from table. Used to remove the query from AIDToUID."""
    Log("Caching UserIDs.")
    cron_cursor.execute("SELECT extID, userID FROM users")
    UserIDs = cron_cursor.fetchall()
    for a in UserIDs:
        UserIDCache[int(a[0])] = a[1]

def cache_ranks(cron_cursor):
    time = Timer()
    time.start()
    logger.info("Caching ranks... ")
    cron_cursor.execute("SELECT extID FROM users WHERE isBanned = 0 ORDER BY stars")
    Leaderboards = cron_cursor.fetchall()
    Leaderboards.reverse()
    Ranks.clear()

    UserRank = 0

    for User in Leaderboards:
        UserRank += 1
        Ranks[str(User[0])] = UserRank
    time.end()
    logger.info(f"Done! {time.ms_return()}ms")

def calculate_cp(cron_cursor):
    """Cron job that calculates CP for the whole server."""
    time = Timer()
    time.start()
    logger.info("Beginning to calculate CP... ")
    #first we get all user ids
    cron_cursor.execute("SELECT userID FROM users")
    UserIDs = cron_cursor.fetchall()

    #fetching the counts and calculation total pp
    for UserID in UserIDs:
        calc_user_cp(cron_cursor, UserID[0])
    mydb.commit()
    time.end()
    logger.info(f"Done! {time.ms_return()}ms")

def calc_user_cp(cron_cursor, UserID : int):
    """Calculates CP for specified user id."""
    UserCP = 0
    #count rated levels
    cron_cursor.execute("SELECT COUNT(*) FROM levels WHERE starStars > 0 AND userID = %s", (UserID,))
    UserCP += cron_cursor.fetchone()[0]
    #count featured levels
    cron_cursor.execute("SELECT COUNT(*) FROM levels WHERE starFeatured > 0 AND userID = %s", (UserID,))
    UserCP += cron_cursor.fetchone()[0]
    #count epic levels
    cron_cursor.execute("SELECT COUNT(*) FROM levels WHERE starEpic > 0 AND userID = %s", (UserID,))
    UserCP += cron_cursor.fetchone()[0]
    #count magic levels
    if UserConfig["MagicGivesCP"]:
        cron_cursor.execute("SELECT COUNT(*) FROM levels WHERE magic > 0 AND userID = %s", (UserID,))
        UserCP += cron_cursor.fetchone()[0]
    #count awarded levels
    if UserConfig["AwardGivesCP"]:
        cron_cursor.execute("SELECT COUNT(*) FROM levels WHERE awarded > 0 AND userID = %s", (UserID,))
        UserCP += cron_cursor.fetchone()[0]
    
    #lastly we give the cp to them
    cron_cursor.execute("UPDATE users SET creatorPoints = %s WHERE userID = %s LIMIT 1", (UserCP, UserID))
    mydb.commit()

def max_star_count_ban(cron_cursor) -> None:
    """[CheatlessAC Cron] Bans people who have a star count higher than the total starcount of the server."""
    # TODO : Make the same thing for usercoins and regular coins
    if UserConfig["CheatlessCronChecks"] and UserConfig["CheatlessAC"]:
        time = Timer()
        time.start()
        logger.info("Running CheatlessAC Cron Starcount Check... ")
        TotalStars = 187 #from RobTop levels
        #get all star rated levels
        cron_cursor.execute("SELECT starStars FROM levels WHERE starStars > 0")
        StarredLevels = cron_cursor.fetchall()

        #add em all up
        for Level in StarredLevels:
            TotalStars += Level[0]
        
        #count query
        cron_cursor.execute("SELECT COUNT(*) FROM users WHERE stars > %s", (TotalStars,))
        BannedCount = cron_cursor.fetchone()[0]
        #ban em
        cron_cursor.execute("UPDATE users SET isBanned = 1 WHERE stars > %s", (TotalStars,))
        mydb.commit()
        time.end()
        logger.info(f"Done with {BannedCount} users banned! {time.ms_return()}ms")
