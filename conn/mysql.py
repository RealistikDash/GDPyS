import aiomysql


class Myconn:
    def __init__(self):
        self.conn = None
        self.pool = None


myconn = Myconn()


async def create_connection(loop, config: dict):
    # Create the pool.
    myconn.pool = await aiomysql.create_pool(
        host=config["sql_server"],
        port=3306,
        user=config["sql_user"],
        password=config["sql_password"],
        db=config["sql_db"],
        loop=loop,
    )

    # Create the main connection based on the pool (for compatibility reasons)
    myconn.conn = await myconn.pool.acquire()

def conn_cleanup(conn: aiomysql.Connection) -> None:
    """Closes the connection and cleans up after it."""
    conn.close()
    myconn.pool.release(conn)
