from __future__ import annotations

import os
import sys

import aiofiles

from . import glob
from .comment import Comment
from .song import Song
from .user import User
from config import conf
from const import Difficulty
from const import LevelLengths
from const import LevelStatus
from const import Privileges
from const import Security
from helpers.crypt import base64_decode
from helpers.time import get_timestamp
from web.http import Request

# Local Consts.
MAX_CACHE_SIZE = 5000


class Level:
    """An object representing the values and qualities of a Geometry Dash
    level in code. It contains all of the functions and properties to work
    with levels."""

    __slots__ = (
        "id",
        "name",
        "creator",
        "comments",
        "description",
        "song",
        "track_id",
        "version",
        "length",
        "two_player",
        "unlisted",
        "extra_str",
        "replay",
        "game_version",
        "binary_version",
        "timestamp",
        "update_ts",
        "original",
        "likes",
        "downloads",
        "stars",
        "difficulty",
        "demon_diff",
        "coins",
        "coins_verified",
        "requested_stars",
        "feature_id",
        "rate_status",
        "ldm",
        "objects",
        "password",
        "working_time",
        "update_locked",
        "_cache",
    )

    def __init__(self) -> None:
        """Sets all the placeholder attributes. Use classmethods instead
        please."""

        self.id: int = 0
        self.name: str = ""
        self.creator: User = User()
        self.comments: list[Comment] = []  # Ordered by newest first.
        self.description: str = ""
        self.song: Song = Song()
        self.track_id: int = 0  # The in-game song IDs. Don't like how its done.
        self.version: int = 1
        self.length: LevelLengths = 0
        self.two_player: bool = False
        self.unlisted: bool = False
        # Contains batch nodes to help with rendering
        self.extra_str: str = "0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0"
        self.replay: str = ""
        self.game_version: int = 22
        self.binary_version: int = 35
        self.timestamp: int = 0
        self.update_ts: int = 0
        self.original: int = 0  # The ID of the original level.

        # Some general statistics.
        self.likes: int = 0
        self.downloads: int = 0
        self.stars: int = 0
        self.difficulty: Difficulty = Difficulty.NA
        self.demon_diff: int = 0  # TODO: Demon diff enums.
        self.coins: int = 0
        self.coins_verified: bool = False
        self.requested_stars: int = 0
        self.feature_id: int = (
            0  # Funnily enough features are NOT bools, but rather ordered by feaid
        )
        self.rate_status: LevelStatus = 0
        self.ldm: bool = False
        self.objects: int = 0
        self.password: int = 0
        self.working_time: int = 0  # Time spent building the level.
        self.update_locked: bool = (
            False  # If true, the level wont be able to be updated
        )

        # Special cache for small levels.
        self._cache: str = ""

    @property
    def path(self) -> str:
        """Returns the path to the level's local location in storage."""

        path = f"{conf.dir_levels}/{self.id}"

        # Check if the level exists locally.
        # if not os.path.exists(path): return

        return path

    @property
    def demon(self) -> bool:
        """Returns a bool of whether the level has a demon rating."""

        # We can just use the star rating as
        # unrated levels cant be demons.
        return self.stars == 10

    @property
    def auto(self) -> bool:
        """Returns a bool of whether the level has the auto rating."""

        # We can just use the star rating as
        # unrated levels cant be auto.
        return self.stars == 1

    @property
    def rated(self) -> bool:
        """Bool corresponding to whether the level has been rated."""

        return self.stars > 0

    @property
    def featured(self) -> bool:
        """Returns a bool of whether the level is featured."""

        return self.feature_id > 0

    # Rating status attributes prior to refactor.
    @property
    def epic(self) -> bool:
        """Checks if the level is rated epic."""

        return self.has_status(LevelStatus.EPIC)

    # Operator overloads, etc
    def __eq__(self, o: User) -> bool:
        return self.id == o.id

    def __ne__(self, o: User) -> bool:
        return self.id != o.id

    async def load(self) -> str:
        """Loads the level data directly from storage and returns it.

        Note:
            If the level is really small, it can be cached for s p e e d.
        """

        # Check cache first in case its a really small level.
        if self._cache:
            return self._cache

        # Nope, we have to load it from storage.
        p = self.path

        # Check if it even is locally available
        if not p:
            return

        # Loading directly from storage.
        async with aiofiles.open(p, "r") as f:
            contents = await f.read()

        # Check if the contents are below 5kb to see
        # if we can cache.
        if sys.getsizeof(contents) <= MAX_CACHE_SIZE:
            self._cache = contents

        # Return it
        return contents

    async def write(self, contents: str) -> None:
        """Writes the level string to local storage.

        Args:
            contents (str): The level string to be saved.
        """

        # If the level is small enough, cache it for
        # faster access later.
        # TODO: Determine max level size
        if sys.getsizeof(contents) <= MAX_CACHE_SIZE:
            self._cache = contents

        # Write the level to storage.
        async with aiofiles.open(f"{conf.dir_levels}/{self.id}", "w+") as f:
            await f.write(contents)

    def cache(self) -> None:
        """Adds the current level into the global level cache."""

        glob.level_cache.cache(self.id, self)

    @classmethod
    async def from_sql(cls, level_id: int, full: bool = True):
        """Fetches the level data from the MySQL database and creates an
        instance of `Level`.

        Args:
            level_id (int): The ID of the level in the database.
            full (bool): Whether non-crucial data will be also fetched (such
                as comments).
        """

        # Create the instance of Level.
        self = cls()

        # Fetch data from MySQL
        level_db = await glob.sql.fetchone(
            "SELECT id, name, user_id, description,"
            "song_id, extra_str, replay, game_version,"
            "binary_version, timestamp, downloads, likes,"
            "stars, difficulty, demon_diff, coins, coins_verified,"
            "requested_stars, featured_id, rate_status, ldm,"
            "objects, password, working_time, level_ver, "
            "track_id, length, two_player, unlisted, update_locked FROM levels "
            "WHERE id = %s LIMIT 1",
            (level_id,),
        )

        # Stop an exception if level is not found.
        if level_db is None:
            return

        # Set simple data and store.
        (
            self.id,
            self.name,
            user_id,
            self.description,
            song_id,
            self.extra_str,
            self.replay,
            self.game_version,
            self.binary_version,
            self.timestamp,
            self.downloads,
            self.likes,
            self.stars,
            self.difficulty,
            self.demon_diff,
            self.coins,
            self.coins_verified,
            self.requested_stars,
            self.feature_id,
            self.rate_status,
            self.ldm,
            self.objects,
            self.password,
            self.working_time,
            self.version,
            self.track_id,
            self.length,
            self.two_player,
            self.unlisted,
            self.update_locked,
        ) = level_db

        # GDPyS custom objects.
        self.creator = await User.from_id(user_id)
        self.song = await Song.from_id(song_id)

        if full:
            await self._fetch_comments()

        return self

    @classmethod
    async def from_id(cls, level_id: int):
        """Creates an instance of `Level` from data in MySQL database.

        Args:
            level_id (int): The ID of the level in the database.

        Returns:
            `None` if not found, else instance of `Level`.
        """

        # Cache can save us A LOT of time. Check it in case we already have it
        if cache_l := glob.level_cache.get(level_id):
            return cache_l

        # We are required to utilise the sql (slow).
        return await Level.from_sql(level_id, True)

    @classmethod
    async def from_submit(cls, u: User, req: Request):
        """Creates a level object using data from level submit.

        Args:
            u (User): The user uploading the level.
            req (Request): The HTTP request object representing the request
                made by the user uploading the level.

        Note:
            This has no error handling, meaning it wont attempt to handle
                weird values and just raise an error.
            This DOES do value checks.
        """

        # Create object instance.
        self = cls()

        # Set object
        self.creator = u
        self.game_version = int(req.post["gameVersion"])
        self.binary_version = int(req.post["binaryVersion"])
        # Enforce max lvl len
        self.name = req.post["levelName"][: Security.MAX_LEVEL_NAME_LEN]
        self.description = base64_decode(req.post["levelDesc"])[
            : Security.MAX_LEVEL_DESC_LEN
        ]

        # Song weirdness.
        if (song_id := int(req.post["songID"])) not in (-1, 0):
            self.song = await Song.from_id(song_id)
        else:
            self.track_id = int(req.post["audioTrack"])

        if len(passwd := req.post["password"]) > 8:
            raise ValueError("Level password exceeds max char limit.")
        self.password = passwd
        self.two_player = req.post["twoPlayer"] == "1"
        self.objects = int(req.post["objects"])
        if (coin_c := int(req.post["coins"])) > 3:
            raise ValueError("Coin count exceeds limit.")
        self.coins = coin_c
        self.unlisted = req.post["unlisted"] == "1"
        self.replay = req.post["levelInfo"]
        self.extra_str = req.post["extraString"]
        self.requested_stars = int(req.post["requestedStars"])
        self.working_time = int(req.post["wt2"])
        self.original = int(req.post["original"])

        return self

    def __repr__(self) -> str:
        """Debug representation of the object."""
        return f"<Level {self.name} ({self.id})>"

    async def insert(self) -> None:
        """Inserts the level data directly into the MySQL table.

        Note:
            This also sets the level ID locally based on `cur.lastrowid`.
        """

        if self.id:
            raise FileExistsError("Level is already uploaded (has ID assigned).")

        song_id = self.song.id if self.song else 0
        self.timestamp = self.update_ts = get_timestamp()

        # We are inserting into the database, and using the cur.lastrowid for
        # setting the id locally.
        self.id = await glob.sql.execute(
            "INSERT INTO levels (name, user_id, description, song_id, replay,"
            "game_version, binary_version, timestamp, update_ts, coins, requested_stars,"
            "ldm, objects, password, working_time, level_ver, track_id, length,"
            "two_player, unlisted, extra_str, original) VALUES (%s,%s,%s,%s,%s,%s,%s,"
            "UNIX_TIMESTAMP(),UNIX_TIMESTAMP(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                self.name,
                self.creator.id,
                self.description,
                song_id,
                self.replay,
                self.game_version,
                self.binary_version,
                self.coins,
                self.requested_stars,
                1 if self.ldm else 0,
                self.objects,
                self.password,
                self.working_time,
                self.version,
                self.track_id,
                self.length,
                1 if self.two_player else 0,
                1 if self.unlisted else 0,
                self.extra_str,
                self.original,
            ),
        )

    async def update(self, **kwargs) -> None:
        """Updates the level's data set within the kwargs locally and in
        MySQL.

        Note:
            The input here has to be generally trusted as no checks are
                performed on the data passed here. You may get DB errors or
                someone exploiting you if you don't verify this.
            This also ensures the state of the level in memory and database
                are exactly the same, as this sets ALL of the modifiable
                attributes of the objects to the database, regardless of
                whether they were modified.

        Kwargs:
            name (str): The name of the level.
            desc (str): The plain-text description for the level.
            version (int): The in-game version of the level.
            length (LevelLength): An int enum corresponding to the length of
                the level.
            ldm (bool): Bool corresponding to the availability of low detail
                mode for the level.
            coins (int): The quantity of u_coins present within the level.
            coins_verified (bool): Whether the u_coins are verified (reward
                the user).
            verified_coins (bool): Whether
            two_player (bool): Corresponding to whether the level allows input
                from two individual players.
            password (str): The 6 digit password of the level (str due to 0s).
            objects (str): The total object count of the level.
            song_id (int): The ID of the song to set.
            work_time (int): Time spent working on the level (wt2).
            unlisted (bool): Whether the level should appear in pulic search.
            game_version (int): The version of the game the level has been
                uploaded with.
            binary_version (int): Similar to Game Version but is incremented
                fully each update.
            track_id (int): The ID of the in-game song for this map.
            replay (str): The replay string for the verification of the level.
            feature_id (int): The ID of the feature (by which level on the
                featured page are ordered).
            downloads (int): The amount of times the level has been
                downloaded.
            likes (int): The amount of people that liked the level (can be
                negative).
            rate_status (LevelStatus): Int flag of the level representing the
                special ratings of the level.
            original (int): The level ID of the original level (0 if unique).
            update_locked (bool): Whether the level should be stopped from
                being updated in the future.
        """

        # Check if we are not setting an unuploaded level. We need the level
        # id to set the mysql query.
        if not self.id:
            raise FileNotFoundError("Level has not been uploaded yet.")

        # Custom object setting is a bit special.
        if song_id := int(kwargs.get("song_id")):
            self.song = await Song.from_id(song_id)
            song_id = self.song.id
            # Ensure that only one of them exists at once, with custom songs
            # taking priority.
            self.track_id = 0
        else:
            song_id = 0
            self.track_id = kwargs.get("track_id", 0)

        # TODO: Cleanup. Possibly loop through all of the args and just
        # `setattr` them. That might not be too secure tho. /shrug
        self.name = kwargs.get("name", self.name)
        self.description = kwargs.get("desc", self.description)
        self.version = kwargs.get("version", self.version)
        self.length = kwargs.get("length", self.length)
        self.ldm = kwargs.get("ldm", self.ldm)
        self.coins = kwargs.get("coins", self.coins)
        self.coins_verified = kwargs.get("verified_coins", self.coins_verified)
        self.two_player = kwargs.get("two_player", self.two_player)
        self.password = kwargs.get("password", self.password)
        self.objects = kwargs.get("objects", self.objects)
        self.working_time = kwargs.get("work_time", self.working_time)
        self.unlisted = kwargs.get("unlisted", self.unlisted)
        self.game_version = kwargs.get("game_version", self.game_version)
        self.binary_version = kwargs.get("binary_version", self.binary_version)
        self.rate_status = kwargs.get("rate_status", self.rate_status)
        self.replay = kwargs.get("replay", self.replay)
        self.feature_id = kwargs.get("feature_id", self.feature_id)
        self.downloads = kwargs.get("downloads", self.downloads)
        self.likes = kwargs.get("likes", self.likes)
        self.update_ts = get_timestamp()
        self.update_locked = kwargs.get("update_locked", self.update_locked)

        # Update time. I hate myself.
        await glob.sql.execute(
            """
            UPDATE levels SET
                name = %s,
                description = %s,
                version=%s,
                length=%s,
                ldm=%s,
                coins=%s,
                coins_verified=%s,
                two_player=%s,
                password=%s,
                working_time=%s,
                unlisted=%s,
                game_version=%s,
                binary_version=%s,
                track_id=%s,
                song_id=%s,
                rate_status=%s,
                replay=%s,
                feature_id=%s,
                downloads=%s,
                likes=%s,
                update_ts = UNIX_TIMESTAMP(),
                original=%s,
                update_locked=%s
            WHERE
                id = %s
                LIMIT 1
            """,
            (
                self.name,
                self.description,
                self.version,
                self.length,
                1 if self.ldm else 0,
                self.coins,
                1 if self.coins_verified else 0,
                1 if self.two_player else 0,
                self.password,
                self.working_time,
                1 if self.unlisted else 0,
                self.game_version,
                self.binary_version,
                self.track_id,
                song_id,
                self.rate_status,
                self.replay,
                self.feature_id,
                self.downloads,
                self.likes,
                self.original,
                1 if self.update_locked else 0,
                self.id,
            ),
        )

    async def _fetch_comments(self):
        """Fetches level comments from the MySQL database and sets them in the
        object."""

        comments_db = await glob.sql.fetchall(
            "SELECT id, user_id, level_id, content, timestamp, progress, likes "
            "FROM comments WHERE level_id = %s",
            (self.id,),
        )

        for comment_tuple in comments_db:
            self.comments.append(await Comment.from_tuple(comment_tuple))

    def has_status(self, status: LevelStatus) -> bool:
        """Checks if the level has the `status` rating status.

        Args:
            status (LevelStauts): The level status to check for in the level's
                rating.

        Example: # Since this might be a bad desc.
        ```py
        # The level object we are working with.
        l = Level()

        # We are checking if the level is epic.
        epic = l.has_stauts(LevelStatus.EPIC)
        ...
        ```

        Returns:
            `bool` corresponding to whether the level has the status.
        """

        return self.rate_status & status > 0
