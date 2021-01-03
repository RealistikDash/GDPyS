from const import HandlerTypes
from aiohttp import web
from dataclasses import dataclass
from typing import Callable
from .sql import MySQLPool
from const import HandlerTypes
from logger import error, info, debug
from helpers.time_helper import Timer
import asyncio
import traceback

class Request:
    """A GDPyS request object. It contains details
    regarding the post request and the user that
    send it."""

    def __init__(self):
        """Fills all defaults for the object. Please
        use classmethods instead of this."""

        self.post_data: dict = {}
        self.get_args: dict = {}
        self.headers: dict = {}
        self.ip: str = "127.0.0.1"
        self.path: str = "/"

    @classmethod
    async def from_aiohttp(cls, aioreq: web.Request):
        """Converts an aiohttp request into a GDPyS
        Web one.
        
        Args:
            aioreq (web.Request): The initial aiohttp
                request object you would like to convert.

        Returns:
            GDPyS web request object.
        """

        # First we set the post_data
        cls.post_data = await aioreq.post()
        # Next we fetch get_args
        cls.get_args = aioreq.rel_url.query
        # Set headers
        cls.headers = aioreq.headers
        # Set path
        cls.path = aioreq.path

        # Now we grab the ip. This requires some logic so we don't
        # get nginx's ip all the time.
        ip = ""
        if ip := aioreq.headers.get("x-real-ip"):
            cls.ip = ip
            return cls
        
        # This one isn't really """safe""" but eh
        if ip := aioreq.headers.get("x-forwarded-for"):
            cls.ip = ip
            return cls
        
        # Ig we have no other choice than to use this.
        cls.ip = aioreq.remote
        return cls

@dataclass
class Handler:
    """A handler object containing all info regarding
    the handlers execution and data."""

    path: str
    handler: Callable[[Request], str]
    status: HandlerTypes = HandlerTypes.PLAIN_TEXT

    def has_status(self, status: HandlerTypes):
        """Checks if the handler has the status `status`"""

        # These are just bitwise operators so we can to this.
        return bool(self.status & status)

class GDPySWeb:
    """A low level aiohttp server specialised for usage
    within GDPyS. Using this implementation allows us to
    reduce overhead from aiohttp's routing system (as we
    do not require something that complex) and allows us
    to add a lot of our own handler-level checks and
    tools."""

    def __init__(self, loop: asyncio.AbstractEventLoop):
        """Prepares the server for configuration and usage."""

        self.handlers: dict = {}
        self.pool: MySQLPool = None
        self.err_handlers: dict = {}
        self.loop = loop

        # Setting the default err_handlers
        self.err_handlers[404] = Handler(
            path= "doesnt natter",
            handler=self._default_not_found_handler,
            status= HandlerTypes.PLAIN_TEXT
        )

        self.err_handlers[500] = Handler(
            path= "doesnt natter",
            handler=self._default_exception_handler,
            status= HandlerTypes.PLAIN_TEXT
        )
    
    # Default misc handlers.
    async def _default_not_found_handler(self, req: Request) -> str:
        """Simplistic 404 error handler.
        
        Args:
            req (Request): The request object containing
                infromation regarding what the server
                was sent.
        """

        # Since this is just the default, we are keeping it
        # simple.
        return "GDPyS 404: path doesn't exist!"
    
    async def _default_exception_handler(self, req: Request, exc: str) -> str:
        """Simple 500 error handler.

        Args:
            req (Request): The request object containing
                infromation regarding what the server
                was sent.
            exc (str): The full traceback for the exception
                in string form.
        """

        # Once again, keeping it simple.
        return f"GDPyS Exception: {exc}"
    
    # MySQL configuration.
    async def config_sql(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        port: int = 3306
    ):
        """Creates the MySQL pool and makes it available to
        use within the handlers.
        
        Args:
            host (str): The hostname of the MySQL server you would like
                to connect. Usually `localhost`.
            user (str): The username of the MySQL user you would like to
                log into.
            password (str): The password of the MySQL user you would like
                to log into.
            database (str): The database you would like to interact with.
            port (int): The port at which the MySQL server is located at.
                Default set to 3306.
        """

        # Create a pool and immidiately set it.
        self.pool = await MySQLPool.connect(
            host,
            user,
            password,
            database,
            port
        )
    
    async def _gd_auth(self, post_data: dict) -> bool:
        """Handles authentication for Geometry Dash handlers."""

        # Not added yet
        raise NotImplementedError("Geometry Dash authentication has not yet been implemented.")
    
    async def _handle_conn(self, req: web.Request) -> web.Response:
        """Handles all requests to the server. Specialised
        for `aiohttp` low level server.
        
        Args:
            req (web.Request): `aiohttp` request object.
        
        Returns:
            aiohttp web.Response object.
        """

        # Create a timer to measure the performance.
        t = Timer()
        t.start()

        # Convert request to GDPyS request.
        request: Request = await Request.from_aiohttp(req)
        resp_str = ""

        # Grab handler from handler list. Check if none, use the 404 one.
        if handler := self.handlers.get(request.path) is None:
            # Use the 404 one.
            handler = self.err_handlers[404]
        
        # Now we calc the args
        try:
            args = [Request]

            # Check if we require the mysql conn.
            if handler.has_status(HandlerTypes.DATABASE):
                args.append(self.pool)
            
            # Check if it is authed.
            if handler.has_status(HandlerTypes.AUTHED)\
            and not await self._gd_auth(request.post_data):
                # Hard code reply for now. TODO
                return web.Response(text="-1")
            
            resp_str = await handler.handler(*args)
        
        except Exception:
            # Get the tb as full string
            tb = traceback.format_exc()

            # Print the traceback so we know something is not right.
            error(f"There was an exception when handling path {request.path} using {handler.handler.__name__}\n{tb}")

            # Call error handler
            # TODO: Maybe allow this to use db and statuses etc.
            handler = self.err_handlers[500]
            resp_str = await handler.handler(request, tb)
        
        # Converting the response we got into aiohttp objects.

        # Plaintext responses are simple.
        if handler.has_status(HandlerTypes.PLAIN_TEXT):
            final_resp = web.Response(text= resp_str)
        
        # JSON responses use aiohttp's cool own function.
        elif handler.has_status(HandlerTypes.JSON):
            final_resp = web.json_response(resp_str)
        
        # End timer.
        t.end()
        
        # Log it.
        info(f"[{request.ip}] {req.method} {request.path} | `{handler.handler.__name__}` {t.time_str()}")

        # Return it
        return final_resp
    
    # Server start
    async def start(self, port: int = 8080):
        """Starts the GDPyS HTTP server on http://127.0.0.1 with port `port`
        and creates a neverending loop to keep it running.
        
        Args:
            port (int): The port at which the HTTP server should listen for
                connections.
        """

        # Start the aiohttp low level server.
        server = web.Server(self._handle_conn)
        runner = web.ServerRunner(server)
        await runner.setup()
        site = web.TCPSite(
            runner,
            "127.0.0.1",
            port
        )

        # Start the server.
        await site.start()

        # Log that its started.
        info(f"GDPyS HTTP: Started listening on http://127.0.0.1:{port}/")

        # Keep alive forever.
        while True:
            await asyncio.sleep(10000)
