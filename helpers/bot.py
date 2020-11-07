import gdpys
import re

client = gdpys.client

class GDPySBot(gdpys.Plugin):
    def __init__(self):
        self.isgdpysbot = True
        self.user = client.get_user_object(0)
        super().__init__()

    def send_message(self, accountid: int, subject: str, body: str):
        pass # send message

    async def loop(self):
        pass

    @client.on_comment()
    async def mention(self, ctx):
        comment = ctx.comment
        account = ctx.account
        level = ctx.level
        mentions = re.findall("@[a-zA-Z]+", comment.comment)
        for m in mentions:
            m.replace("@", "")
            user = client.send_message("Mentioned",
            f"You have been mentioned by {account.username}, on {level.name} with id {level.ID}",
            self.user.user_id,
            client.username_to_id(m))

gdpysbot = GDPySBot()

def setup():
    return gdpysbot