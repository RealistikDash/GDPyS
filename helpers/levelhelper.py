from helpers.generalhelper import dict_keys
from helpers.timehelper import get_timestamp
from helpers.crypthelper import hash_sha1
from conn.mysql import myconn
from objects.levels import Level, Rating, DailyLevel
from config import user_config
from aiofile import AIOFile
import logging

class LevelHelper():
    """Helps with anything regarding levels. This includes level object creation and caching, comments etc."""
    def __init__(self):
        """Inits the level helper."""
        self.level_cache = {}
        self.daily = None # is DailyLevel object if cached.
    
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

            Hash += f"{str(level.ID)[0]}{str(level.ID)[len(str(level.ID))-1]}{level.stars}{int(level.verified_coins)}"
        
        return hash_sha1(Hash + "xI25fpAapCQg")
    
    
    def solo_gen(self, level_str: str):
        """Port of genSolo from Cvolton's GMDPrivateServer."""
        return_str = ""
        str_len = len(level_str) // 40
        for i in range(40):
            return_str += level_str[i * str_len]
        return hash_sha1(return_str + "xI25fpAapCQg")
    
    def solo_gen2(self, level_string : str) -> str:
        return hash_sha1(level_string + "xI25fpAapCQg")
    
    async def bump_download(self, level_id : int):
        """Bumps a level's download count by one."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("UPDATE levels SET downloads = downloads + 1 WHERE levelID = %s", (level_id,))
            await myconn.conn.commit()
        
        # Bump cached downloads if exists
        if level_id in dict_keys(self.level_cache):
            self.level_cache[level_id].downloads += 1
    
    async def bump_likes(self, level_id : int):
        """Bumps a level's like count by one."""
        if level_id in dict_keys(self.level_cache):
            # Only run this check if already cached so we dont cache only for this tiny action.
            if self.level_cache[level_id].downloads < self.level_cache[level_id].likes: # More likes than downloads is impossible. Check for it.
                return
            self.level_cache[level_id].likes += 1
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("UPDATE levels SET likes = likes + 1 WHERE levelID = %s", (level_id,))
            await myconn.conn.commit()
        
        if level_id in dict_keys(self.level_cache):
            self.level_cache[level_id].likes += 1
    
    async def upload_level(self, level : Level) -> int:
        """Uploads a level from level object, returns levelID."""
        # First we check if a level like this already exists from the same user
        # I want to think of a better way to use cursors etc
        level_id = 0
        timestamp = get_timestamp()
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT levelID FROM levels WHERE extID = %s AND levelName = %s", (level.account_id, level.name))
            level_count = await mycursor.fetchone()
            if level_count is None:
                # We are currently updating an existing level.
                await mycursor.execute("""UPDATE levels SET
                                gameVersion = %s,
                                binaryVersion = %s,
                                levelDesc = %s,
                                levelVersion = %s,
                                levelLength = %s,
                                audioTrack = %s,
                                password = %s,
                                original = %s,
                                twoPlayer = %s,
                                objects = %s,
                                coins = %s,
                                requestedStars = %s,
                                extraString = %s,
                                levelInfo = %s,
                                songID = %s,
                                updateDate = %s
                            WHERE
                                levelID = %s""",(
                                    level.game_version,
                                    level.binary_version,
                                    level.description,
                                    level.version,
                                    level.length,
                                    level.track,
                                    level.password,
                                    level.original,
                                    level.two_player,
                                    level.objects,
                                    level.coins,
                                    level.requested_stars,
                                    level.extra,
                                    level.info,
                                    level.song_id,
                                    timestamp,
                                    level_count[0]
                                ))
                level_id = mycursor.lastrowid
                await myconn.conn.commit()
            
            else:
                # It is a new level, insert it instead.
                await mycursor.execute("""INSERT INTO levels 
                                            (
                                                levelName, 
                                                gameVersion, 
                                                binaryVersion, 
                                                userName, 
                                                levelDesc, 
                                                levelVersion, 
                                                levelLength, 
                                                audioTrack, 
                                                password, 
                                                original, 
                                                twoPlayer, 
                                                songID, 
                                                objects, 
                                                coins, 
                                                requestedStars, 
                                                extraString, 
                                                levelInfo,  
                                                uploadDate, 
                                                userID, 
                                                extID, 
                                                updateDate, 
                                                unlisted, 
                                                isLDM,
                                                secret
                                            )
                                        VALUES 
                                            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '')""", (
                                                level.name,
                                                level.game_version,
                                                level.binary_version,
                                                level.username,
                                                level.description,
                                                level.version,
                                                level.length,
                                                level.track,
                                                level.password,
                                                level.original,
                                                level.two_player,
                                                level.song_id,
                                                level.objects,
                                                level.coins,
                                                level.requested_stars,
                                                level.extra,
                                                level.info,
                                                timestamp,
                                                level.user_id,
                                                level.account_id,
                                                timestamp,
                                                0, # TODO: unlisted
                                                level.ldm
                                            ))
                level_id = mycursor.lastrowid
                await myconn.conn.commit()
            logging.debug(level_id)
            #After all the database work, we finally save the level to files.
            async with AIOFile(user_config["level_path"] + str(level_id), "w+") as file: #tbh this should be a function
                await file.write(level.string)
                await file.fsync()
        
        return level_id

    async def rate_level(self, rating : Rating) -> None:
        """Rates a level."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("UPDATE levels SET starStars = %s, starFeatured=%s,starEpic = %s, starCoins=%s,starDemonDiff=%s WHERE levelID = %s LIMIT 1", (
                rating.stars, int(rating.featured), int(rating.epic), int(rating.verified_coins), rating.demon_diff, rating.level_id
            ))
            await myconn.conn.commit()

    async def _daily_level_from_db(self) -> DailyLevel:
        """Gets daily level from database."""
        timestamp = get_timestamp()
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT feaID, levelID, timestamp, type FROM dailyfeatures WHERE timestamp < %s AND type = 0 ORDER BY timestamp DESC LIMIT 1", (timestamp,))
            daily = await mycursor.fetchone()
        if daily is None:
            logging.warning("No daily level set! Please set one or else there won't be a daily level.")
            return None
        logging.debug("Cached new daily level.")
        return DailyLevel(
            daily[0],
            daily[1],
            int(daily[2]),
            bool(daily[3])
        )
    
    async def get_daily_level(self) -> DailyLevel:
        """Gets the current daily level."""
        if self.daily is None:
            self.daily = await self._daily_level_from_db()
        if self.daily.timestamp < get_timestamp():
            self.daily = await self._daily_level_from_db()
        return self.daily

level_helper = LevelHelper() # Shared object between all imports for caching to work correctly etc.
