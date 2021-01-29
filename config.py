from helpers.common import JsonFile, dict_keys
from logger import info, debug
import os
import json

__name__ = "ConfigModule"
__author__ = "RealistikDash"
__version__ = "v2.0.0"

class ConfigReader:
    """A parent class meant for the easy management, updating
    and the creation of a configuration `JSON` file."""

    def __init__(self):
        """Sets placeholder variables."""

        # Set to true if a new value was added to the config.
        self.updated: bool = False
        self.updated_keys: list = []

        # An object around the configuration file.
        self.json: JsonFile = JsonFile("config.json")
    
    def __init_subclass__(cls, stop_on_update: bool = False):
        """Sets and reads the config child class."""

        cls.__init__(cls)

        # Now we read all of the annotated valiables.
        for var_name, key_type in cls.__annotations__.items():

            # We are checking for a possible default value (in case its a new field)
            default = getattr(cls, var_name, None)

            # Read the key.
            key_val = cls.read_json(cls, var_name, default)

            # Force it to be the sepcified type.
            key_val = key_type(key_val)

            # Set the attribute.
            setattr(cls, var_name, key_val)

        if cls.updated:
            info("The config has just been updated! Please edit according to your preferences!")
            debug("Keys added: " + ", ".join(cls.updated_keys))
            raise SystemExit
    
    def read_json(self, key: str, default = None):
        """Reads a value directly from the json file and returns
        if. If the value is not already in the JSON file, it adds
        it and sets it as `default`.
        
        Args:
            key (str): The JSON key to fetch the value of.
            default (any): The value for the key to be set to if the
                value is not set.
                
        Returns:
            Value of the key.
        """

        # Handle a case where the file is empty/not found.
        if self.json.file is None:
            # Set it to an empty dict so it can be handled with the thing below.
            self.json.file = {}

        # Check if the key is present. If not, set it.
        if key not in dict_keys(self.json.file):
            # Set it so we can check if the key was modified.
            self.updated = True
            self.updated_keys.append(key)
            # Set the value in dict.
            self.json.file[key] = default

            # Write it to the file.
            self.json.write_file(self.json.file)

            # Return default
            return default
        
        # It exists, just return it.
        return self.json.file[key]

# TODO: Notifications for config updates.
class Config(ConfigReader):
    """The main GDPyS class for the storage of config values.
    These values are read directly from the `config.json` file."""

    http_port: int = 8080
    sql_host: str = "localhost"
    sql_user: str = "root"
    sql_db: str = "GDPyS"
    sql_password: str = ""

conf = Config()

