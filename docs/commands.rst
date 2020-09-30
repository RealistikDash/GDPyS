.. currentmodule:: gdpys

Commands
========

Commands are built into the Client class of GDPyS plugins and can be used like this::

    import gdpys
    
    permissions = gdpys.permissions # getting permissions object
    client = gdpys.client # getting the client class

    class CommandExample(gdpys.Plugin):
        def __init__(self):
            self.set_metadata(name="commandexample", author="spook", description="command example plugin", version="1.0.0", dependencies=[])
            super().__init__()

        @client.command(name="rate", permission=permissions.mod_rate)
        async def rate(self): # arguments are not yet implemented
            pass # do stuff on [prefix]rate

    def setup():
        return CommandExample