import asyncio
import gdpys
import re

client = gdpys.client

class GDPySBot(gdpys.Plugin):
    def __init__(self, loop):
        self.isgdpysbot = True
        self.user = loop.create_task(client.get_user_object(0))
        super().__init__()

    async def loop(self):
        pass

    @client.on_comment
    async def mention(self, ctx):
        comment = ctx.comment
        account = ctx.account
        level = ctx.level
        mentions = re.findall("@([0-9a-zA-Z]+)", comment.comment)
        m = mentions[0] # grab the first mention (stop those spam mentioners)
        m.replace("@", "")
        await client.send_message("Mentioned",
        f"You have been mentioned by {account.username}, on {level.name} with id {level.ID}",
        self.user.account_id,
        client.username_to_id(m))

def setup():
    return GDPySBot