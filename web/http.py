from const import HandlerTypes
from aiohttp import web
from dataclasses import dataclass
from typing import Callable, Union
from .sql import MySQLPool
from helpers.auth import Auth
from helpers.common import dict_keys
from const import HandlerTypes
from logger import error, info, debug
from helpers.time_helper import Timer
from exceptions import GDException
from objects.glob import glob
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
    req_postargs: Union[list, tuple] = ()

    def has_status(self, status: HandlerTypes):
        """Checks if the handler has the status `status`.
        
        Args:
            status (HandlerTypes): The status we are checking
                for within the handler.
        """

        # These are just bitwise operators so we can to this.
        return bool(self.status & status)
    
    def verify_postargs(self, args: Union[list, tuple]) -> bool:
        """Check if the provided post `args` contain the
        required information for the handler.
        
        Args:
            args (list, tuple): A list or tuple of the
                post args provided.
        
        Returns:
            A bool of whether all required post args are
                included.
        """

        # Iterate through all required post args and see if
        # they are in the args list.
        for arg in self.req_postargs:
            if arg not in args: return False
        
        return True

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
        self.auth: Auth = Auth()

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

        # Set it globally.
        glob.sql = self.pool
    
    async def _gd_auth(self, post_data: dict) -> bool:
        """Handles authentication for Geometry Dash handlers."""

        # TODO: Anti-botting checks for vers and binaryver and secrets
        return await self.auth.gjp_check(
            int(post_data["accountID"]),
            post_data["gjp"]
        )
    
    def _rate_limit(self, req: Request) -> bool:
        """Imposes a rate limit on an endpoint."""

        raise NotImplementedError("Rate limits have not been implemented yet.")
    
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
        if (handler := self.handlers.get(request.path)) is None:
            # Use the 404 one.
            handler = self.err_handlers[404]
        
        # Now we calc the args
        try:
            args = [Request]

            # Check if we require the mysql conn.
            if handler.has_status(HandlerTypes.DATABASE):
                args.append(self.pool)
            
            # Check if they have the required args.
            if not handler.verify_postargs(dict_keys(request.post_data)):
                # Idk just use the error handler.
                raise KeyError
            
            # Check if it is authed.
            if handler.has_status(HandlerTypes.AUTHED):
                if not (p := await self._gd_auth(request.post_data)):
                    raise GDException("-1")

                # Add user as arg.
                args.append(p)
            
            if handler.has_status(HandlerTypes.RATE_LIMITED)\
            and not self._rate_limit(request):
                # Idk what to do here....
                pass
            
            resp_str = await handler.handler(*args)
        
        except GDException as e:
            # GDExceptions are different, with them being called when the
            # handler is executed correctly BUT it is sending an error 
            # code to the client.
            resp_str = str(e)
            debug(f"Handler triggered error code {resp_str}") # Temp debug as else it will be triggered a lot.
        
        # This is so we don't reveal post request required fields to people scouting.
        except KeyError:
            resp_str = "Incorrect post data." # Just assume it tbh
            debug("Request sent incorrect post data.")
        
        # There has been an actual exception within the handler.
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
    
    def add_handler(
        self,
        path: str,
        status: Union[HandlerTypes, int],
        handler: Callable[[Request], str],
        req_postargs: tuple = ()
    ) -> None:
        """Creates a handler object and adds it to handle any request coming
        to `path`.
        
        Note:
            All `handler` args should be coroutine functions. REGULAR FUNCTIONS
                WILL NOT WORK AND WILL BREAK THINGS!

        Args:
            path (str): The URL patch at which the handler should be employed.
            status (HandlerStatus, int): The core status of the handler, it
                contains information such as response type (eg JSON or simple
                plain text, GD authed and DB).
            handler (Callable): The coroutine function for the handler. Must
                return str for plaintext handlers and dict/list for JSON
                ones.
            req_postargs (tuple, list): A list of all of the post arguments
                required for the request.
        """

        # Creating the handler object and setting.
        self.handlers[path] = Handler(
            path= path,
            handler= handler,
            status= status,
            req_postargs= req_postargs
        )
    
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
        debug(f"Server starting with {len(self.handlers)} handlers.")
        info(f"GDPyS HTTP: Started listening on http://127.0.0.1:{port}/")

        # Keep alive forever.
        while True:
            await asyncio.sleep(10000)
