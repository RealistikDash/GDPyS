from conn.mysql import myconn
from objects.comments import Comment, CommandContext
from objects.misc import QueryResponse
from helpers.generalhelper import create_offsets_from_page, dict_keys
from helpers.crypthelper import decode_base64
from constants import Permissions
from exceptions import GDPySCommandError
from config import user_config

"""
COMMANDS = {
    "rate" : {
        "handler" : rate_command,
        "permission" : Permissions.mod_rate
    }
}

async def rate_command(ctx : CommandContext) -> bool:
    # Blah blah code
    return True # True is success
"""

class CommentHelper():
    """Class containing most things regarding level comments."""
    def __init__(self):
        self.comments = {} # Placeholder for maybe cache.

    async def get_comments(self, level_id : int, page : int = 0, amount : int = 10, order : str = "likes") -> QueryResponse:
        """Returns a list of comment objects.
        [WARNING] Order param is not SQLi safe. You have to manually sanetise that."""
        offset = create_offsets_from_page(page, amount)
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(f"SELECT userID, userName, comment, timestamp, likes, percent, isSpam, levelID, commentID FROM comments WHERE levelID = %s ORDER BY {order} DESC LIMIT %s OFFSET %s", (level_id, amount, offset))
            comments_db = await mycursor.fetchall()
            # Count query
            await mycursor.execute("SELECT COUNT(*) FROM comments WHERE levelID = %s", (level_id,))
            count = (await mycursor.fetchone())[0]
        
        comment_list = []

        for comment in comments_db:
            comment_list.append(Comment(
                comment[0],
                comment[7],
                comment[2],
                decode_base64(comment[2]),
                comment[3],
                comment[4],
                comment[5],
                bool(comment[6]),
                comment[1],
                comment[8]
            ))
        
        return QueryResponse(
            count,
            comment_list
        )
    
    async def insert_comment(self, comment : Comment) -> None:
        """Adds comment to database from object."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("INSERT INTO comments (userID, userName, comment, levelID, timestamp, likes, percent, isSpam) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (comment.user_id, comment.username, comment.comment_base64, comment.level_id, comment.timestamp, comment.likes, comment.percent, int(comment.spam)))
            await myconn.conn.commit()
    
    # Command stuff that may be moved to its own class sooner or later.
    async def command_exists(self, command : str) -> bool:
        """Checks if a given comment is a valid command."""
        command = command.split(" ")[0].lower()
        #return command[:-1*len(user_config["command_prefix"])] in dict_keys(COMMANDS)

comment_helper = CommentHelper()
