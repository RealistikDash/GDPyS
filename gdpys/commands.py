from listeners import listener
import asyncio

class Commands:
    def __init__(self, prefix):
        self.commands = {}
        self.prefix = prefix
    
    def command(self, func):
        def wrapper():
            self.commands[func.__name__] = func
        return wrapper
  
    @listener.event
    async def on_upload_comment(self, username, comment):
        for name, func in self.commands.items():
            if comment.startswith(self.prefix + name):
                func()
                # add delete comment
                
# fix listeners and add arguments for this to be complete