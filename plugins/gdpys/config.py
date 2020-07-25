import os
import json

class ConfigError(KeyError):
    pass

class Config:
    
    def __init__(self, file: str, default: dict):
        pluginname = file.split("/")[-1].rstrip(".py")
        file2 = __file__.split("/")
        plugins = "/".join(file2[:-2])
        config = plugins + "/config"
        self.pluginconfig = "/".join(file.split("/")[:-1]) + config + "/" + pluginname + ".json"
        
        if not os.path.exists(config):
            os.mkdir(config)

        if not os.path.exists(self.pluginconfig):
            json.dump(default, open(self.pluginconfig, "w"))
    
    def read(self, key):
        try:
            return json.load(open(self.pluginconfig, "r"))[key]
        except KeyError:
            raise ConfigError("Could not find key in config!")
    
    @property
    def config(self):
        return open(self.pluginconfig, "r").read()