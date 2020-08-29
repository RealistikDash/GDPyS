import asyncio
from aiohttp import web
from handlers.frontend import home_page
from config import user_config
from conn.mysql import create_connection

def config_routes(app: web.Application) -> None:
    """Configures all of the routes and handlers."""
    app.router.add_get("/", home_page)

async def init(loop):
    """Initialises the app and MySQL connection."""
    app = web.Application(loop=loop)
    await create_connection(loop)
    return app

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init(loop))
    config_routes(app)
    web.run_app(app, port=user_config["port"])
