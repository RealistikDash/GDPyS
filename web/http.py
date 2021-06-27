from const import HandlerTypes
from dataclasses import dataclass
from typing import Callable, Coroutine, Union, Any, Dict
from .sql import MySQLPool
from helpers.auth import Auth
from helpers.common import dict_keys
from const import HandlerTypes, HTTP_CODES, GDPyS
from logger import error, info, debug, warning
from helpers.time import Timer
from exceptions import GDPySAPIBadData, GDPySAPINotFound, GDPySHandlerException
from objects import glob
from urllib.parse import unquote
import asyncio
import select
import signal
import traceback
import os
import socket
import json

WWW_FORM = 'application/x-www-form-urlencoded'
IP_HEADER = "X-Real-IP"
RESP_500 = "GDPyS Exception: {exc}"
RESP_404 = "GDPyS 404: path doesn't exist!"
RESP_400_API = {
	"status": 400,
	"message": "Your request is either missing some data or the "
			   "data sent is plain wrong."
}
RESP_404_API = {
	"status": 404,
	"message": "The object you are looking for has not been found..."
}

class Request:
	"""Request class for storing & parsing all data. Made by lenforiee and
	adapted for use within GDPyS."""
	def __init__(
		self,
		client: socket.socket, 
		loop: asyncio.AbstractEventLoop
	) -> None:
		self.__client: socket.socket = client
		self.__loop: asyncio.AbstractEventLoop = loop

		self.type: str = "GET"
		self.http_ver: str = "1.1"
		self.path: str = "/"
		self.body: bytearray = bytearray()
		self.ip: str = "127.0.0.1"

		self.headers: Dict[str, Any] = {}
		self.get_args: Dict[str, Any] = {}
		self.post: Dict[str, Any] = {}
		self.files: Dict[str, Any] = {}

		self.handle_args: list = [self]
		self.resp_code: int = 200
		self.resp_headers: Dict[str, Any] = {}
	
	def add_header(self, key: str, value: Any) -> None:
		"""Adds header to response back headers."""
		self.resp_headers.update({key: value})

	def _parse_headers(self, data: str) -> None:
		"""Instance funtion to parse headers content
			from client data.
		Params:
			- content: bytes = first chunks splited by \r\n\r\n
				from client response.
		Returns:
			Parsed headers, get_args.
		"""
		self.type, self.path, self.version = data.splitlines()[0].split(" ")
		self.version = self.version.split("/")[1] # Stupid parsing but eh.

		# Parsing get args.
		if "?" in self.path:
			self.path, args = self.path.split("?")

			for arg in args.split("&"):
				key, value = arg.split("=", 1)
				self.get_args[key] = value.strip()

		# Now headers.
		for key, value in [header.split(":", 1) for header in data.splitlines()[1:]]:
			self.headers[key] = value.strip()
		self.ip = self.headers.get(IP_HEADER, "127.0.0.1")

	def _www_form_parser(self) -> None:
		"""Optional parser for parsing form data.
		Returns:
			Updates self.post with form data args.
		"""
		BODY = self.body.decode()

		for args in BODY.split("&"):
			k, v = args.split("=", 1)
			self.post[unquote(k).strip()] = unquote(v).strip()

	def return_json(self, code: int, content: dict) -> bytes:
		"""Returns an response but in json."""
		self.resp_code = code

		resp_back = json.dumps(content)
		self.add_header("Content-Type", "application/json")
		return resp_back.encode()
	
	async def send(self, code: int, data: bytes) -> None:
		"""Sends data back to the client.
		Params:
			- code: int = Status code to send back.
			- data: bytes = Bytes to send back.
		Returns:
			Sends all data to client.
		"""
		resp = bytearray()
		temp = [f"HTTP/1.1 {code} {HTTP_CODES.get(code)}"]

		# Add content len
		if data:
			temp.append(f"Content-Length: {len(data)}")

		# Join headers.
		temp.extend(map(': '.join, self.resp_headers.items()))
		resp += ('\r\n'.join(temp) + '\r\n\r\n').encode()

		# Add body.
		if data:
			resp += data
			
		try: # Send all data to client.
			await self.__loop.sock_sendall(self.__client, resp)
		except Exception as e:
			debug(f"GDPyS Web: Connection ended abruptly with exception: {e}")
	
	def _parse_multipart(self) -> None:
		"""Simplest instance funtion to parse
			multipart I found so far.
		Returns:
			Parsed files & post args from request.
		"""

		# Create an boundary.
		boundary = "--" + self.headers['Content-Type'].split('boundary=', 1)[1]
		parts = self.body.split(boundary.encode())[1:]

		for part in parts[:-1]:

			# We get headers & body.
			headers, body = part.split(b"\r\n\r\n", 1)
			
			temp_headers = {}
			for key, val in [p.split(":", 1) for p in [h for h in headers.decode().split("\r\n")[1:]]]:
				temp_headers[key] = val.strip()

			if not (content := temp_headers.get("Content-Disposition")):
				# Main header don't exist, we can't continue.
				continue

			temp_args = {}
			for key, val in [args.split("=", 1) for args in content.split(";")[1:]]:
				temp_args[key.strip()] = val[1:-1]


			if "filename" in temp_args: self.files[temp_args['filename']] = body[:-2] # It is a file.
			else: self.post[temp_args['name']] = body[:-2].decode() # It's a post arg.

	async def perform_parse(self) -> None:
		"""Performs full parsing on headers and body bytes."""

		buffer = bytearray() # Bytearray is faster than bytes.
		while (offset := buffer.find(b"\r\n\r\n")) == -1:
			buffer += await self.__loop.sock_recv(self.__client, 1024)

		self._parse_headers(buffer[:offset].decode())

		# Headers are parsed so now we put rest to body.
		self.body += buffer[offset + 4:]

		try: content_len = int(self.headers["Content-Length"])
		except KeyError: return # Get args request only.

		if (to_read := ((offset + 4) + content_len) - len(buffer)): # Find how much to read.
			buffer += b"\x00" * to_read # Allocate space.
			with memoryview(buffer)[-to_read:] as view:
				while to_read:
					read_bytes = await self.__loop.sock_recv_into(self.__client, view)
					view = view[read_bytes:]
					to_read -= read_bytes

		# Add to body.
		self.body += memoryview(buffer)[offset + 4 + len(self.body):].tobytes()

		if self.type == "POST":
			if (ctx_type := self.headers.get("Content-Type")):
				if ctx_type.startswith("multipart/form-data") or \
					"form-data" in ctx_type:
					self._parse_multipart()
				elif ctx_type in ("x-www-form", "application/x-www-form-urlencoded"):
					self._www_form_parser()

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
		return self.status & status > 0
	
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
		if all(arg in args for arg in self.req_postargs):
			return True
		
		return False

class GDPySWeb:
	"""A HTTP server based on Python's low level socket package.
	All of the socket and HTTP parsing has been made by Lenforiee.
	This allows us to take full control of the process as well as
	ensure speed due to the removal of unnecessary features."""

	def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
		"""Prepares the server for configuration and usage."""

		self.handlers: dict = {}
		self.pool: MySQLPool = None
		self.loop = loop
		self.auth: Auth = Auth()
		self.alive: bool = True
		self._task_coros: set = set()
		self.tasks: set = set()
		self.main_sock: socket.socket = None

	def add_task(self, task: Coroutine, *args) -> None:
		"""Adds task to server."""
		if args:
			self._task_coros.add((task, args))
		else:
			self._task_coros.add(task)
	
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
	
	async def _gd_auth(self, req: Request) -> bool:
		"""Handles authentication for Geometry Dash handlers."""

		# TODO: Anti-botting checks

		# Verify their GD version is not pre-history.
		if int(req.post["gameVersion"]) < 21\
		or int(req.post["binaryVersion"]) < 34:
			debug(f"GJP failed for user for pre-historic GD version.")
			return False
		
		# Verifying the proper content type
		if req.headers["Content-Type"] != WWW_FORM:
			debug("GJP failed due to unknown Content-Type (likely bot)!")
			return False

		return await self.auth.gjp_check(
			int(req.post["accountID"]),
			req.post["gjp"]
		)
	
	def _rate_limit(self, req: Request) -> bool:
		"""Imposes a rate limit on an endpoint."""

		raise NotImplementedError("Rate limits have not been implemented yet.")
	
	async def _handle_conn(self, request: Request) -> None:
		"""Handles all requests to the server. And routing
		through handlers.
		
		Args:
			req (Request): A current request object.
		
		Returns:
			String of HTTP contents.
		"""

		resp_str = RESP_404.encode()
		request.resp_code = 404

		glob.connections_handled += 1

		if (handler := self.handlers.get(request.path)) is None:
			# Send that 404.
			return await request.send(request.resp_code, resp_str)
		
		try:
			# Check if we require the mysql conn.
			if handler.has_status(HandlerTypes.DATABASE):
				request.handle_args.append(self.pool)
			
			# Check the required args.
			if not handler.verify_postargs(dict_keys(request.post)):
				# Idk just use the error handler.
				raise KeyError

			# Check if it is authed.
			if handler.has_status(HandlerTypes.AUTHED):
				if not (p := await self._gd_auth(request)):
					raise GDPySHandlerException("-1")

				# Add user as arg.
				request.handle_args.append(p)
			
			if handler.has_status(HandlerTypes.RATE_LIMITED)\
				and not self._rate_limit(request):
				# Idk what to do here....
				pass
			
			resp_str = await handler.handler(*request.handle_args)
			request.resp_code = 200
			if isinstance(resp_str, tuple): request.resp_code, resp_str = resp_str

		except GDPySHandlerException as e:
			resp_str = e.encode()
			debug(f"Handler triggered error code {resp_str}") # Temp debug as else it will be triggered a lot.
		
		except GDPySAPINotFound:
			request.resp_code = 404
			resp_str = RESP_404_API

		except GDPySAPIBadData:
			request.resp_code = 400
			resp_str = RESP_400_API

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

			# TODO: Maybe allow this to use db and statuses etc.
			resp_str = RESP_500.format(exc= tb)
			request.resp_code = 500
			return await request.send(request.resp_code, resp_str.encode())
		
		if handler.has_status(HandlerTypes.JSON):
			if "status" not in resp_str: resp_str["status"] = 200
			resp_str = request.return_json(request.resp_code, resp_str)
		elif isinstance(resp_str, str): resp_str = resp_str.encode()

		# Debug log the resp.
		debug(resp_str)

		return await request.send(request.resp_code, resp_str)
	
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
	
	async def _handle_request(self, client: socket.socket):
		"""Handles parsing all headers and all data
		Args:
			client (socket.socket): Currently connected client socket.

		Made by lenforiee
		"""

		# Create a timer to measure the performance.
		t = Timer()
		t.start()

		# Parse request.
		await (request := Request(client, self.loop)).perform_parse()

		# After all the parsing we check the host header, which should
		# be sent all the time.
		if "Host" not in request.headers:
			# This is messed up...
			client.shutdown(socket.SHUT_RDWR)
			client.close()
			return

		# Now we will call our own external handler function
		await self._handle_conn(request)

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
	def start(self, sock_name: str = "/tmp/gdpys.sock", max_conn: int = 5):
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

		async def runner():
			# Check if old socket exists from old instances.
			if os.path.exists(sock_name):
				# Unlink the unix socket
				os.unlink(sock_name)
				debug("Removed old socket file!")
			
			for coroutine in self._task_coros:
				if isinstance(coroutine, tuple):
					coro, args = coroutine
					task = self.loop.create_task(coro(*args))
				else:
					task = self.loop.create_task(coroutine())
				self.tasks.add(task)

			sig_rsock, sig_wsock = os.pipe()
			os.set_blocking(sig_wsock, False)
			signal.set_wakeup_fd(sig_wsock)

			# connection listening sock
			sock = socket.socket(socket.AF_UNIX)
			sock.setblocking(False)

			sock.bind(sock_name)

			# Make the socket fully accessable to avoid future errors.
			os.chmod(sock_name, 0o777)	
			sock.listen(max_conn)

			debug(f"GDPyS HTTP: Started server on socket {sock_name}")
			info(f"{GDPyS.NAME} b{GDPyS.BUILD} has been successfully started!")

			close = False
			while not close:
				await asyncio.sleep(0.001)
				rlist, _, _ = select.select([sock, sig_rsock], [], [], 0)

				for rd in rlist:
					if rd is sock:
						client, _ = await self.loop.sock_accept(sock)
						self.loop.create_task(self._handle_request(client))
					elif rd is sig_rsock:
						print('\x1b[2K', end='\r') # Clears ^C.
						error(f"Received an interuption... ")
						close = True
					else: pass # Just don't read dat.
				
			# server closed, clean things up.
			for sock_fd in (sock.fileno(), sig_rsock, sig_wsock): 
				os.close(sock_fd)
			signal.set_wakeup_fd(-1)

			if self.tasks:
				_plural = lambda a: f"{a}s" if len(self.tasks) > 1 else a
				warning(f"Canceling {len(self.tasks)} active {_plural('task')}..")

				for task in self.tasks:
					task.cancel()

				await asyncio.gather(*self.tasks, return_exceptions=False)

				if still_running := [t for t in asyncio.all_tasks()
								if t is not asyncio.current_task()]:
					try:
						warning("Awaiting all tasks timeout in 5 seconds!")
						await asyncio.wait(still_running, loop=self.loop, timeout=5.0)
					except asyncio.TimeoutError:
						warning("Timeout, force closing all running tasks!")
						to_await = []
						for task in still_running:
							if not task.cancelled():
								task.cancel()
								to_await.append(task)
						await asyncio.gather(*to_await, return_exceptions=False)

			# Lastly kill running pool.
			self.pool.kill()
		
		def _callback(fut) -> None:
			"""Calls after future is finished."""
			self.loop.stop()
		
		def _empty_func(sg, f) -> None:
			"""Function to block other calls."""
			pass

		for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
			signal.signal(sig, _empty_func)

		future = asyncio.ensure_future(runner(), loop=self.loop)
		future.add_done_callback(_callback)
		try:
			self.loop.run_forever()
		finally:
			future.remove_done_callback(_callback)
			info("GDPyS is shutting down...")
			self.loop.close()
