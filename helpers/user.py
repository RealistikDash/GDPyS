# Assists with user related functions. Unlike v2, this is for minor things and
# not LITERALLY EVERYTHING USER RELATED lmfao.
from objects.glob import glob

async def get_user_count() -> int:
    """Gets the total number of users in the database.
    
    Note:
        This value is already cached in `glob.registered_users`. Use that
            rather than running this SQL query and appending unnecessary
            stress onto your database.
    """

    return (await glob.sql.fetchone(
        "SELECT COUNT(*) FROM users"
    ))[0]
