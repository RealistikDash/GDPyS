from conn.mysql import myconn
from objects.comments import Comment
from helpers.searchhelper import QueryResponse # Expected never to use it outside... Guess I was wrong.
from helpers.generalhelper import create_offsets_from_page
from helpers.crypthelper import decode_base64

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

comment_helper = CommentHelper()
