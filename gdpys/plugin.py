from time import sleep
import os, asyncio, time

class Plugin:
    def __init__(self):
        """Start main loop"""
        time.sleep(6) # wait for functions to finish
        self.stopped = False
        loop = asyncio.new_event_loop()
        if self.metadata == False:
            print(f"Warning: Plugin {self.__class__} has invalid metadata!")
        while True:
            if self.stopped: break
            loop.run_until_complete(self.loop())
            sleep(1)

    def create_config(self, template):
        """Create config for plugins"""
        configpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/plugins/config"
        if os.path.exists(configpath + "/" + self.name + "/config.json"):
            return
        if self.metadata == False:
            print("Warning: Config could not be created due to insufficent metadata.")
        if not os.path.exists(configpath):
            os.mkdir(configpath)
        if not os.path.exists(configpath + "/" + self.name):
            os.mkdir(configpath + "/" + self.name)
        config = open(configpath + "/" + self.name + "/config.json", "w")
        config.write(str(template).replace("'", '"'))
        config.close()

    @property
    def config(self):
        configpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/plugins/config"
        config = open(configpath + "/" + self.name + "/config.json", "r")
        return config.read()

    def set_metadata(self, name="", author="", description="", version="", dependencies={}):
        """Set metadata, will be given a warning if this is not done at startup."""
        self.name = name
        self.author = author
        self.description = description
        self.version = version
        self.dependencies = dependencies
    
    def stop(self):
        """Stop the plugin"""
        self.stopped = True

    @property
    def metadata(self):
        """Returns plugin metadata"""
        try:
            return {"name": self.name, "author": self.author, "description": self.description, "version": self.version, "dependencies": self.dependencies}
        except AttributeError:
            return False