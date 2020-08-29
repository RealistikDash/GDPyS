import aiomysql

class Myconn:
    def __init__(self):
        self.conn = None

myconn = Myconn()

async def create_connection(loop, config: dict):
    myconn.conn = await aiomysql.create_pool(
        host=config["sql_server"],
        port=3306,
        user=config["sql_user"],
        password=config["sql_password"],
        db=config["sql_db"],
        loop=loop
    )
