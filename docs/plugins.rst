.. currentmodule:: gdpys

Plugins
=======

GDPyS plugins are extensions to the main server and they are kinda like if discord.py cogs and spigot plugins had a baby.
This guide will show you how to make and use plugins correctly.

First thing we want to create a python file in the plugins directory, lets call our plugin anticheat.

Lets put some starter code in there::

    import gdpys # importing the main module

    class AntiCheat(gdpys.Plugin): # create our plugin
        def __init__(self): # init
            print("Plugin started") # if your plugin needs to initalize, you may do that here. (make sure to call super()__init__() last)
            super().__init__()

        async def loop(self): # create a loop that will run every second
            pass # in our case, in this loop we can try to see if someone is cheating.

    def setup():
        return AntiCheat # tell the plugin manager what class to find

This is not even the slightest bit of what plugins are capable of.

Metadata and dependencies
-------------------------

Next, we can set the metadata of our plugin, and even add dependencies (the metadata of a plugin is almost required but it might still work without it)::

    import gdpys # importing the main module

    class AntiCheat(gdpys.Plugin): # create our plugin
        def __init__(self): # init
            self.set_metadata(name="anticheat", author="spook", description="anticheat for GDPyS", version="1.0.0", dependencies=[])
            print("Plugin started") # if your plugin needs to initalize, you may do that here. (make sure to call super()__init__() last)
            super().__init__()

        async def loop(self): # create a loop that will run every second
            pass # in our case, in this loop we can try to see if someone is cheating.

    def setup():
        return AntiCheat # tell the plugin manager what class to find

Config
------

If we want our plugin to be configurable we can use the built in config method::

    import gdpys # importing the main module

    class AntiCheat(gdpys.Plugin): # create our plugin
        def __init__(self): # init
            # set the metadata of the plugin so other plugins and the server admin can see it.
            self.set_metadata(name="anticheat", author="spook", description="anticheat for GDPyS", version="1.0.0", dependencies=[])
            self.create_config({
                "ban_people": True, # set the default values
                "other_config_option": "1"
            })
            print("Plugin started") # if your plugin needs to initalize, you may do that here. (make sure to call super()__init__() last)
            super().__init__()

        async def loop(self): # create a loop that will run every second
            if self.config["ban_people"]: # in our case, in this loop we can try to see if someone is cheating.
                pass # now we can ban people

    def setup():
        return AntiCheat # tell the plugin manager what class to find