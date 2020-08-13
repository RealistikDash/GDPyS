import asyncio
from config import UserConfig

class _Commands:
    def __init__(self, prefix):
        self.commands = {}
        self.prefix = prefix
    
    def command(self, func, *args):
        def wrapper():
            self.commands[func.__name__] = {"func": func, "args": args}
        return wrapper

    def on_upload_comment(self, accountid, comment):
        for name, func in self.commands.items():
            if comment.startswith(self.prefix + name):
                func["func"](*func["args"])
                # add delete comment

commands = _Commands(UserConfig["CommandPrefix"])