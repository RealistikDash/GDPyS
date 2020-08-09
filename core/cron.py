import time as pytime
#gdpys things
from console import logger, Log, Success, Fail
from functions import UserIDCache, Ranks
from core.mysqlconn import mydb
from config import UserConfig
from helpers.timer import Timer

def cron_thread():
    Log("Cron thread started!")
    time = Timer()
    while True:
        Log("Running cron!")
        time.start()
        cron_cursor = mydb.cursor() #create cursor specifically for cron jobs
        cache_user_ids(cron_cursor)
        cache_ranks(cron_cursor)
        calculate_cp(cron_cursor)
        max_star_count_ban(cron_cursor)
        cron_cursor.close() #close it after all is done
        Log(f"Cron done! Took {time.end()}s")
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
    
    #Cronjob code
    cp_values = {}
    cron_cursor.execute("UPDATE users SET creatorPoints = 0") #set everyones cp to 0 as we wont be calculating everyone
    #now we get specific levels that match our criteria
    cron_cursor.execute("SELECT userID, starStars, starFeatured, starEpic, awarded, magic FROM levels WHERE starStars > 0 OR starFeatured > 0 OR starEpic > 0 OR awarded > 0 OR magic > 0")
    rated_levels = cron_cursor.fetchall()
    for level in rated_levels:
        if level[0] not in list(cp_values.keys()):
            cp_values[level[0]] = 0
        cp_values[level[0]] += calc_cp_for_level(level)
    
    #finally apply calcs
    for cp in list(cp_values.keys()):
        cron_cursor.execute("UPDATE users SET creatorPoints = %s WHERE userID = %s LIMIT 1", (cp_values[cp], cp))
    mydb.commit()

    time.end()
    logger.info(f"Done! {time.ms_return()}ms")

def calc_cp_for_level(level_response: tuple) -> int:
    """Calculates cp given for level."""
    cp_given = 0
    if level_response[1]:
        cp_given += 1
    if level_response[2]:
        cp_given += 1
    if level_response[3]:
        cp_given += 1
    if level_response[4] and UserConfig["AwardGivesCP"]:
        cp_given += 1
    if level_response[5] and UserConfig["MagicGivesCP"]:
        cp_given += 1
    return cp_given

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

if __name__ == "__main__":
    Log("Would you like to start the cron job? (y/N)")
    a = input("")
    if a.lower() == "y":
        cron_thread()
