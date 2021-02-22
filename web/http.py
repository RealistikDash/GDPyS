from const import HandlerTypes
from dataclasses import dataclass
from typing import Callable, Union
from .sql import MySQLPool
from helpers.auth import Auth
from helpers.common import dict_keys
from const import HandlerTypes, HTTP_CODES
from logger import error, info, debug
from helpers.time_helper import Timer
from exceptions import GDException
from objects.glob import glob
import asyncio
import traceback
import os
import socket

class Request:
    """Request class for storing & parsing all data.
    Made by Lenforiee and adapted for use within GDPyS."""

    def __init__(self, client: socket.socket, loop: asyncio.AbstractEventLoop):
        """Init placeholders."""

        self._client: socket.socket = client
        self._loop: asyncio.AbstractEventLoop = loop

        self.type: str = "GET"
        self.http_ver: str = "HTTP/1.1"
        self.path: str = "/"
        self.body: Union[bytearray, bytes] = b''
        self.headers: dict = {}
        self.get_args: dict = {}
        self.post: dict = {}
        self.files: dict = {}
        self.ip: str = "0.0.0.0"

        # send back data
        self._send_headers: list = []
        self._send_code: int = 200

    async def _parse_headers(self, content: str) -> None:
        """Parses all headers from single client"""

        # Best instance to parse headers so far I made.

        # We will split first line of headers
        lines = content.splitlines()[0].split(" ")

        # Unpack all data
        self.type, self.path, self.http_ver = lines

        if "?" in self.path:
            # We have to parse query args
            args = self.path.split("?", 1)
            # Update path
            self.path = args[0]

            # Now we will loop all args
            for arg in args[1].split("&"):
                # now split arg
                arg = arg.split("=", 1)

                if len(arg) != 2:
                    debug("GDPyS Web: Invalid GET argument size!")
                    #return
                    continue
                
                self.get_args.update({arg[0]: arg[1]})
        
        for header in content.splitlines()[1:]:
            # Now we will parse headers in request
            header = header.split(':', 1)

            if len(header) != 2:
                debug("GDPyS Web: Invalid header size!")
                #return
                continue
            
            self.headers.update({header[0]: header[1].lstrip()})
        
        # This is the reason we need nginx.
        self.ip = self.headers.get("X-Real-IP")

    async def _parse_multipart(self):
        """Parses multipart from post request"""
        # Honestly I have no idea how to parse multipart
        # if this code will ever work it's only by my luck.

        # Ok so after long deep searching I think, I'm kinda able
        # to know how to parse them

        # Lets build boundary, it's gonna be useful for parsing multipart
        # What is boundary? its like key to parse multiple data from multipart
        # boundary have 26 of '-' however we need 28 of them.
        boundary = "--" + self.headers['Content-Type'].split('boundary=')[1]

        # We will get all multiparts from there.
        for parts in self.body[:-4].split(boundary.encode()):
            if not parts:
                # Sometimes it can be empty and fuck
                # our instance
                continue

            # we need to separate headers from body in parts.
            headers, body = parts.split(b'\r\n\r\n')

            # Parse exisng headers.
            temp_headers = {}
            for header in headers.decode().split("\r\n")[1:]:
                header = header.split(":", 1)

                # Header didn't send data??
                if len(header) != 2:
                    debug("GDPyS Web: Invalid multipart header!")
                    continue

                # Update our temp headers dict.
                temp_headers.update({header[0]: header[1].lstrip()})

            if not temp_headers.get("Content-Disposition"):
                # Main header somehow don't exist???
                return
            
            temp_args = {}
            for args in temp_headers["Content-Disposition"].split(";")[1:]:
                # basically now its like args in path query
                args = args.split("=", 1)

                if len(args) != 2:
                    debug("GDPyS Web: Invalid multipart arguments!")
                    continue

                temp_args.update({args[0].lstrip(): args[1][1:-1]})

            # Get our type, if it has filename its file if not its post arg
            if 'filename' in temp_args:
                self.files.update({temp_args['name']: body[:-2]})
            else:
                self.post.update({temp_args['name']: body[:-2].decode()})

    async def _parse_www_form(self):
        """Parses form data from request"""

        # this is simple to parse
        for parts in self.body.split(b"&"):
            parts = parts.decode().split("=", 1)

            if len(parts) != 2:
                debug("GDPyS Web: Malformed www-form data, ignoring.")
                continue
            
            self.post.update({parts[0]: parts[1]})

    async def _parse(self) -> None:
        """Parses all data from single client"""

        # I'm sure if we read 1024 bytes we will get everything.
        buf = await self._loop.sock_recv(self._client, 1024)

        # Now we will split headers & parse them.
        buf_list = buf.split(b'\r\n\r\n')
        await self._parse_headers(buf_list[0].decode())

        # work out already read and remaining
        read_already = buf[len(buf_list[0]) + 4:]
        content_length = self.headers.get('Content-Length')

        if not content_length:
            # well its only headers
            self.body = read_already
        else:
            if len(read_already) != int(content_length):
                # Still data remaining, well here
                # ill just use recv_into to recive 
                # remaining chunks to bytearray, this
                # is the fastest and best I could find.

                to_read = int(content_length) - len(read_already)
                temp_buf = bytearray(to_read)

                while to_read:
                    read_bytes = await self._loop.sock_recv_into(self._client, temp_buf)
                    to_read -= read_bytes

                self.body = read_already + bytes(temp_buf)
            else:
                # We have already read all data.
                self.body = read_already

            if (content := self.headers.get('Content-Type')):
                # Eh multipart, I spend literally most of my time
                # to make this parser so its better should work.
                if 'multipart/form-data' in content:
                    await self._parse_multipart()
                elif 'x-www-form' in content:
                    await self._parse_www_form()

    def add_header(self, header: str, index: int = -1) -> None:
        """Adds response header into list"""

        if index > -1:
            self._send_headers.insert(index, header)
        else:
            self._send_headers.append(header)

    async def send(self, code: int, body: bytes):
        """Sends data to a client"""

        # we will query all headers
        self.add_header(f"HTTP/1.1 {code} {HTTP_CODES.get(code)}", 0)

        if body:
            self.add_header(f'Content-Length: {len(body)}', 1)

        # join & encode headers
        joined_headers = '\r\n'.join(self._send_headers)
        response = f'{joined_headers}\r\n\r\n'.encode()

        # add body if exists
        if body:
            response += body

        try: # Send all data to the client.
            await self._loop.sock_sendall(self._client, response)
        except Exception as e:
            debug(f"GDPyS Web: Connection ended abruptly with exception: {e}")


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
    """A HTTP server based on Python's low level socket package.
    All of the socket and HTTP parsing has been made by Lenforiee.
    This allows us to take full control of the process as well as
    ensure speed due to the removal of unnecessary features."""

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
    
    async def _gd_auth(self, post: dict) -> bool:
        """Handles authentication for Geometry Dash handlers."""

        # TODO: Anti-botting checks

        # Verify their GD version is not pre-history.
        if int(post["gameVersion"]) < 21\
        or int(post["binaryVersion"]) < 34:
            debug(f"GJP failed for user for pre-historic GD version.")
            return False

        return await self.auth.gjp_check(
            int(post["accountID"]),
            post["gjp"]
        )
    
    def _rate_limit(self, req: Request) -> bool:
        """Imposes a rate limit on an endpoint."""

        raise NotImplementedError("Rate limits have not been implemented yet.")
    
    async def _handle_conn(self, request: Request) -> str:
        """Handles all requests to the server. And routing
        through handlers.
        
        Args:
            req (Request): A current request object.
        
        Returns:
            String of HTTP contents.
        """

        resp_str = ""

        # Grab handler from handler list. Check if none, use the 404 one.
        if (handler := self.handlers.get(request.path)) is None:
            # Use the 404 one.
            handler = self.err_handlers[404]
        
        # Now we calc the args
        try:
            args = [request]

            # Check if we require the mysql conn.
            if handler.has_status(HandlerTypes.DATABASE):
                args.append(self.pool)
            
            # Check if they have the required args.
            if not handler.verify_postargs(dict_keys(request.post)):
                # Idk just use the error handler.
                raise KeyError
            
            # Check if it is authed.
            if handler.has_status(HandlerTypes.AUTHED):
                if not (p := await self._gd_auth(request.post)):
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
        except KeyError as e:
            resp_str = "Incorrect post data." # Just assume it tbh
            debug(f"Request sent incorrect post data. {e}")
        
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
        
        # Just ensure it is str.
        resp_str = str(resp_str) if not handler.has_status(HandlerTypes.JSON) else resp_str

        # Debug log the resp.
        debug(resp_str)

        # Return it
        return resp_str
    
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
    
    async def _handle_sock(self, client: socket.socket):
        """Handles parsing all headers and all data
        Args:
            client (socket.socket): Currently connected client socket.

        Made by Lenforiee
        """

        # Create a timer to measure the performance.
        t = Timer()
        t.start()

        # Make request object & parse headers.
        request = Request(client, self.loop)
        await request._parse()

        # After all the parsing we check the host header, which should
        # be sent all the time.
        if not request.headers.get("Host"):
            # This is messed up...
            client.shutdown(socket.SHUT_RDWR)
            client.close()
            return

        # Now we will call our own external handler function
        response = await self._handle_conn(request)

        # We send the response to the client. Just return a 200 as GD doesnt 
        # need anything else.
        await request.send(200, response.encode())

        # End timer.
        t.end()
        
        # Log it.
        info(f"[{request.ip}] {request.type} {request.path} | {t.time_str()}")

        # Lastly try to close connection
        try:
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        except socket.error:
            pass
    
    # Server start
    async def start(self, sock_name: str = "/tmp/gdpys.sock", max_conn: int = 5):
        """Starts the GDPyS HTTP server on socket `sock`, looping forever
        to receive connections.

        Note:
            This server is based on pure Python sockets for S P E E D and
                customisation purposes.
            This HTTP server currently only supports UNIX systems (Linux
                and MacOS) due to UNIX sockets (which are faster) but port
                support (and thus Windows support) will be added if there
                is demand.
        
        Args:
            sock_name (int): The UNIX socket file on which the GDPyS HTTP 
                server shall be ran.
            max_conn (int): The max concurrent connections to be allowed by
                the server.
        """

        # Log that its started.
        debug(f"GDPyS HTTP is starting with {len(self.handlers)} registered handlers.")

        # Check if old socket exists from old instances.
        if os.path.exists(sock_name):
            # Unlink the unix socket
            os.unlink(sock_name)
            debug("Removed old socket file!")

        # Create socket
        with socket.socket(socket.AF_UNIX) as sock:
            # Bind the socket.
            sock.bind(sock_name)
            # Make is non-blocking for async.
            sock.setblocking(False)
            sock.listen(max_conn)

            # Make the socket fully accessable to avoid future errors.
            os.chmod(sock_name, 0o777)

            info(f"GDPyS HTTP: Started server on socket {sock_name}")

            # Run server forever.
            while True:
                client, _ = await self.loop.sock_accept(sock)
                self.loop.create_task(self._handle_sock(client))
