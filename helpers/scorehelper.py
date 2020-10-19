from conn.mysql import myconn
from helpers.generalhelper import safe_id_list
from helpers.lang import lang
from objects.levels import Score
import logging


class ScoreHelper:
    """Helps with the level scores."""

    def __init__(self):
        pass  # No caching here.

    def _score_obj_from_tuple(self, db_result: tuple) -> Score:
        """Returns a score object from database tuple."""
        return Score(
            ID=db_result[0],
            account_id=db_result[1],
            level_id=db_result[2],
            percentage=db_result[3],
            timestamp=int(db_result[4]),
            attempts=db_result[5],
            coins=db_result[6],
        )

    async def get_from_db(self, level_id: int) -> list:
        """Gets a list of user scores from database for level."""
        logging.debug(lang.debug("level_scores_gotten", level_id))
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "SELECT scoreID, accountID, levelID, percent, uploadDate, attempts, coins FROM levelscores WHERE levelID = %s ORDER BY percent DESC LIMIT 100",
                (level_id,),
            )
            return [self._score_obj_from_tuple(i) for i in await mycursor.fetchall()]

    async def get_from_db_filtered(self, level_id: int, filters: list):
        """Gets a list of user scores from database for level set by account ids in filters list."""
        logging.debug(lang.debug("level_scores_gotten", level_id))
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                f"SELECT scoreID, accountID, levelID, percent, uploadDate, attempts, coins FROM levelscores WHERE levelID = %s AND accountID IN ({safe_id_list(filters)})",
                (level_id,),
            )
            return [self._score_obj_from_tuple(i) for i in await mycursor.fetchall()]

    async def save_score_to_db(self, score: Score) -> None:
        """Adds a score to db (NO CHECKS)."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "INSERT INTO levelscores (accountID, levelID, percent, uploadDate, attempts, coins) VALUES (%s,%s,%s,%s,%s,%s)",
                (
                    score.account_id,
                    score.level_id,
                    score.percentage,
                    score.timestamp,
                    score.attempts,
                    score.coins,
                ),
            )
            await myconn.conn.commit()

    async def delete_score(self, score_id: int):
        """Deletes a score with the given ID."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "DELETE FROM levelscores WHERE scoreID = %s LIMIT 1", (score_id,)
            )
            await myconn.conn.commit()

    async def get_score_for_user(self, account_id: int, level_id: int) -> Score:
        """Returns the top score for user on a certain level (can return None)."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "SELECT scoreID, accountID, levelID, percent, uploadDate, attempts, coins FROM levelscores WHERE levelID = %s AND accountID = %s ORDER BY percent DESC LIMIT 1",
                (level_id, account_id),
            )
            score_db = await mycursor.fetchone()

        if score_db is None:  # No score set by user on that level.
            logging.debug(lang.debug("no_score"))
            return None

        return self._score_obj_from_tuple(score_db)

    async def overwrite_score(self, score: Score) -> bool:
        """Checks if the current score should be overwritten."""
        curr_score = await self.get_score_for_user(score.account_id, score.level_id)

        if curr_score is None:
            return True  # It is a new score.

        return score.percentage > curr_score.percentage  # Replace based on percentage


score_helper = ScoreHelper()  # Global score helper.
