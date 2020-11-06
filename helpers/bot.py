import gdpys

client = gdpys.client

class GDPySBot(gdpys.Plugin):
    def __init__(self):
        self.isgdpysbot = True
        super().__init__()

    def send_message(self, accountid: int, subject: str, body: str):
        pass # send message

    async def loop(self):
        pass

gdpysbot = GDPySBot()

def setup():
    return gdpysbot