import gdpys

client = gdpys.client

class GDPySBot(gdpys.Plugin):
    def __init__(self):
        super().__init__()

    #@client.command()
    #async def command(): # wtf do I do here
    #    pass

def setup():
    return GDPySBot