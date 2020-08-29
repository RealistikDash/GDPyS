class Myconn:
    def __init__(self):
        self.conn = None

myconn = Myconn()

async def create_connection(loop):
    myconn.conn = await aiomysql.create_pool(
        host=user_config["sql_server"],
        port=3306,
        user=user_config["sql_user"],
        password=user_config["sql_password"],
        db=user_config["sql_db"],
        loop=loop
    )
