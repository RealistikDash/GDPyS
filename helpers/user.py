# Assists with user related functions. Unlike v2, this is for minor things and
# not LITERALLY EVERYTHING USER RELATED lmfao.
from objects.glob import glob
from objects.user import User

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

async def log_login(
    u: User, ip: str, game_ver: int, bin_ver: int
):
    """Logs the user's login alongside some other relevant data for admin
    and security purposes.

    Args:
        u (User): The user object representing the individual logging in.
        ip (str): The IP of the connection that is causing the login attempt.
        game_ver (int): The numeric version of the game the login is being
            prompted by.
        bin_ver (int): The binary version (2nd way of Rob's versioning) of the
            GD client logging in.
    
    Note:
        This automatically inserts a row into the `user_logins` table. 
        Meant only to represent logins on initial cache.**
    """

    await glob.sql.execute(
        "INSERT INTO user_logins (user_id, timestamp, ip, game_ver, bin_ver) "
        "VALUES (%s, UNIX_TIMESTAMP(), %s, %s, %s)",
        (u.id, ip, game_ver, bin_ver)
    )
