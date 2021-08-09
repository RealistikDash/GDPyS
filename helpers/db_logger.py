from typing import Union
from const import LogTypes
from objects.glob import sql
from .time import get_timestamp
import asyncio

INSERT_PREFIX = "INSERT INTO logs (type, message, extra, timestamp) VALUES "

# Logs actions to the database.
class DBLogger:
    """Manages logging server events to the database. Manages a log queue,
    to which new logs are added internally to lower the speed cost of logging
    on actions that use it. All logs are then commited (inserted) into the
    database on cron or server shutdown."""

    def __init__(self) -> None:
        self.log_queue: list[list] = []
        self.log_lock = asyncio.Lock() # So we dont log while committing
    
    async def log(self, l_type: LogTypes, message: str, extra: Union[str, dict, int, None]):
        """Queues a message to me logged into the database.
        
        Args:
            l_type (LogTypes): The type of the message logged.
            message (str): A simple textual summary of the log.
            extra (str | dict | int | None): Extra data provided for the log,
                specifically formated in the format taken by the specified
                `l_type`.

        Note:
            This function acquires the `log_lock` async lock.
        """

        extra_type = type(extra)
        if extra is None: extra = ""
        elif extra_type is dict: extra = repr(extra)
        elif extra_type is int: extra = str(extra)

        async with self.log_lock.acquire():
            self.log_queue.append(
                [l_type, message, extra, get_timestamp()]
            )
    
    async def commit(self) -> None:
        """Commits all queued log messages to the database, inserting rows.
        
        Note:
            This function acquires the `log_lock` async lock.
        """

        # If nothing is queued, dont even acquire lock.
        if not self.log_queue: return

        async with self.log_lock.acquire():
            # Start building our massive (potentially) query
            log_args = []
            log_str = "(%s, %s, %s, %s) " * len(self.log_queue)
            for args in self.log_queue: log_args += args

            # Run database query that inserts everything.
            await sql.execute(INSERT_PREFIX + log_str, log_args)

            # Clean up queue so we dont keep on adding the same old logs.
            self.log_queue.clear()
