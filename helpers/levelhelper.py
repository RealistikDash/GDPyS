from helpers.generalhelper import dict_keys
from helpers.crypthelper import hash_sha1
from conn.mysql import myconn
from objects.levels import Level

class LevelHelper():
    """Helps with anything regarding levels. This includes level object creation and caching, comments etc."""
    def __init__(self):
        """Inits the level helper."""
        self.level_cache = {}
    
    async def _create_level_obj(self, level_id : int) -> Level:
        """Private function that creates a level object from db."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT gameVersion,binaryVersion,userName,levelID,levelName,levelDesc,levelVersion,levelLength,audioTrack,password,original,twoPlayer,songID,objects,coins,requestedStars,levelInfo,extraString,starStars,uploadDate,updateDate,starCoins,starFeatured,starEpic,starDemonDiff,userID,extID,isLDM,downloads,likes FROM levels WHERE levelID = %s LIMIT 1", (level_id,))
            level = await mycursor.fetchone()
        if level is None:
            return None
        return Level(
            game_version=level[0],
            binary_version=level[1],
            username=level[2],
            ID=level[3],
            name=level[4],
            description=level[5],
            version=level[6],
            length=level[7],
            track=level[8],
            password=level[9],
            original=bool(level[10]),
            two_player=bool(level[11]),
            song_id=level[12],
            objects=level[13],
            coins=level[14],
            requested_stars=level[15],
            info=level[16],
            extra=level[17],
            stars=level[18],
            upload_timestamp=level[19],
            update_timestamp=level[20],
            verified_coins=bool(level[21]),
            featured=bool(level[22]),
            epic=bool(level[23]),
            demon_diff=level[24],
            user_id=level[25],
            account_id=level[26],
            ldm=bool(level[27]),
            downloads=level[28],
            likes=level[29],
            string=None
        )
    
    async def _cache_level_obj(self, level_id : int) -> None:
        """Caches a level ID."""
        level_obj = await self._create_level_obj(level_id)
        if level_obj is None:
            return
        self.level_cache[level_id] = level_obj

    async def get_level_obj(self, level_id : int):
        """Returns a level object."""
        level_id = int(level_id)
        if level_id not in dict_keys(self.level_cache):
            await self._cache_level_obj(level_id)
        return self.level_cache[level_id]
    
    def star_to_difficulty(self, star_count : int) -> int:
        """Converts star count to in-game difficultry values."""
        return {
            1 : 0,
            2 : 10,
            3 : 20,
            4 : 30,
            5 : 30,
            6 : 40,
            7 : 40,
            8 : 50,
            9 : 50
        }.get(star_count, 0)
    
    async def multi_gen(self, levels : list) -> str:
        """
        Ported from GMDPrivateServer by Cvolton
        /incl/lib/generateHash.php
        Let me sleep
        """
        Hash = ""
        for level in levels:
            #async with myconn.conn.cursor() as mycursor:
            #    await mycursor.execute("SELECT levelID, starStars, starCoins FROM levels WHERE levelID = %s", (level,))
            #    data = await mycursor.fetchone()
            level = await self.get_level_obj(level) # Use this as we are expecting them to be already cached.

            Hash += f"{str(level.level_id)[0]}{(level.level_id)[len(str(level.level_id))-1]}{level.stars}{int(level.verified_coins)}"
        
        return hash_sha1(Hash + "xI25fpAapCQg")

level_helper = LevelHelper() # Shared object between all imports for caching to work correctly etc.
