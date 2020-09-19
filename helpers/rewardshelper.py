# Helper class for those small rewards stuff that are too small for their own functions.
from helpers.timehelper import get_timestamp
from objects.quests import Quest
from conn.mysql import myconn

class RewardsHelper():
    """Helps with the rewards aspects of the game."""
    def __init__(self):
        self.cached_quests = []
    
    def gen_id(self):
        """Generates a unique id (primarily used for quests) that should never repeat for user."""
        return get_timestamp()//20
    
    async def cache_quests(self):
        """Caches quests from db to Python object list."""
        quests = []
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT type,amount,reward,name FROM quests")
            db_quests = await mycursor.fetchall()
        
        for quest in db_quests:
            quests.append(Quest(
                quest[0],
                quest[3],
                quest[1],
                quest[2]
            ))
        
        self.cached_quests = quests
    
    async def get_quests(self):
        """Returns a list of quests (and ensures they are cached)."""
        if len(self.cached_quests) == 0:
            await self.cache_quests()
        return self.cached_quests

rewards_helper = RewardsHelper() # We share this class.
