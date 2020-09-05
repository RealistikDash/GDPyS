from helpers.userhelper import user_helper
from objects.comments import AccountComment
from helpers.generalhelper import create_offsets_from_page
from helpers.timehelper import time_ago
from constants import ResponseCodes
import aiohttp

async def profile_comment_handler(request : aiohttp.web.Request):
    """Handles fetching profile comments."""
    post_data = await request.post()

    offset = create_offsets_from_page(post_data["page"]) * -1
    user = await user_helper.get_object(int(post_data["accountID"]))

    comment_count = len(user.acc_comments)

    #CHECKS
    if len(comment_count) == 0:
        return aiohttp.web.Response(text=ResponseCodes.empty_list)
    
    # I might make this a separate helper function however since account comments aare only ever used in one place I'll make the struct here.
    response = ""
    for comment in user.acc_comments[offset:10]:
        response += f"2~{comment.comment_base64}~3~{comment.user_id}~4~{comment.likes}~5~0~~6~{comment.comment_id}~7~{int(comment.spam)}~9~{time_ago(comment.timestamp)}|" # I should make a builder for this.....

    return aiohttp.web.Response(text=response[:-1])
