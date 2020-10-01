Client
======

The client class is the main class for building plugins that interact with GDPyS.

We can use the client class by importing gdpys.client to get a working client object::

    import gdpys
    
    client = gdpys.client # getting the client class

    class Example(gdpys.Plugin):
        def __init__(self):
            self.set_metadata(name="example", author="spook", description="example plugin", version="1.0.0", dependencies=[])
            super().__init__()

        async def loop(self):
            user_id = 1
            comment = "This is an account comment"
            await client.post_account_comment(user_id, comment)
            self.stop()

    def setup():
        return Example
