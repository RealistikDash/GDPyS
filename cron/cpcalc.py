from conn.mysql import myconn
from helpers.generalhelper import create_offsets_from_page, dict_keys
from helpers.userhelper import user_helper
import logging
import math

PAGE_SIZE = 100 # You may make it larger to speed things up if you have a lot of free memory. Default should be fine.

async def cron_calc_cp():
    """Server CP calculation."""
    # So I may make this more GDPyS style (using all of the level objects etc) but in this case, speed matters
    # a LOT more than usual. I have found this way to be MUCH faster and therefore decided to implement it as such here.
    cp_users = {} # Dict (with keys being account IDs) that store user's final CP count.
    async with myconn.conn.cursor() as mycursor:
        # We wipe the whole server's CP values in case a person lost all their levels ratings (as he won't be recalculated for efficiency reasons).
        await mycursor.execute("UPDATE users SET creatorPoints = 0")
        # Now we get all the levels that would give cp.
        # To avoid having large memory usage, the whole system will work in pages, doing each page at a time
        await mycursor.execute("SELECT COUNT(*) FROM levels WHERE starStars > 0 OR starFeatured > 0 OR starEpic > 0 OR awarded > 0 OR magic>0")
        count = (await mycursor.fetchone())[0]
        pages = math.ceil(count/PAGE_SIZE)
        logging.debug(f"CP cron has {pages} pages.")
        for i in range(pages):
            logging.debug(f"Running page {i+1}/{pages}")
            offset = create_offsets_from_page(i, PAGE_SIZE)
            await mycursor.execute("SELECT extID, starStars,starFeatured,starEpic,awarded,magic FROM levels WHERE starStars > 0 OR starFeatured > 0 OR starEpic > 0 OR awarded > 0 OR magic>0 LIMIT %s OFFSET %s", (PAGE_SIZE, offset))
            levels_db = await mycursor.fetchall()
            for level in levels_db:
                if level[0] not in dict_keys(cp_users):
                    cp_users[level[0]] = 0
                
                # Checks for each CP condition.
                for i in range(1,6): # The SQL condition columns are 1-5. Just did this so I don't have to write 5 if statements separately
                    if level[i]:
                        cp_users[level[0]] += 1
            del levels_db # Not sure how much this helps
        
        # Now we set the new values to the users
        for user in dict_keys(cp_users):
            await mycursor.execute("UPDATE users SET creatorPoints = %s WHERE userID = %s LIMIT 1", (cp_users[user], user))
            # If user is cached, update their CP values.
            if user in dict_keys(user_helper.object_cache):
                user_helper.object_cache[user].cp = cp_users[user]
