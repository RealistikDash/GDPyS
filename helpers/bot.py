import gdpys

client = gdpys.client

class GDPySBot(gdpys.Plugin):
    def __init__(self):
        super().__init__()

    def send_message(self, accountid: int, subject: str, body: str):
        pass # send message

gdpysbot = GDPySBot()

def setup():
    return gdpysbot