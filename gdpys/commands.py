from listeners import listener
import asyncio

class Commands:
    def __init__(self, prefix):
        self.commands = {}
        self.prefix = prefix
    
    def command(self, coro):
        def wrapper():
            self.commands[coro.__name__] = coro
        return wrapper
  
    @listener.event
    async def on_upload_comment(self, username, comment):
        for name, coro in self.commands.items():
            if comment.startswith(self.prefix + name):
                asyncio.run(coro)
                # add delete comment
                
# fix listeners and add arguments for this to be complete