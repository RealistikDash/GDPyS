# This is like the 50th time i re-use this
from helpers.common import JsonFile
from logger import info
import os
import json

__name__ = "ConfigModule"
__author__ = "RealistikDash"

default_config = {
    "http_port": 8080,
    "sql_host": "localhost",
    "sql_user": "root",
    "sql_db": "GDPyS",
    "sql_password": ""
}

user_config = {}

config_options = list(default_config.keys())


def load_config(location: str = "config.json"):
    """Loads a JSON configuration file located at `location`,
    manages the updating of it to contain all keys located within
    the `default_config` dict and sets `user_config` to it.
    
    Args:
        location (str): The location of the configuration file.
    """
    config = JsonFile(location)
    user_config_temp = config.get_file()

    if user_config_temp is None:
        info("Creating the new configuration file...")
        config.write_file(default_config)
        info("Generated new config! Please modify it and start GDPyS again.")
        raise SystemExit

    # Checks for default configuration updates.
    config_keys = list(user_config_temp.keys())
    updated_conf = False

    for def_conf_option in config_options:
        if def_conf_option not in config_keys:
            updated_conf = True
            user_config_temp[def_conf_option] = default_config[def_conf_option]

    if updated_conf:
        config.write_file(user_config_temp)
        info(
            "Your config has been updated! Please change the new values to your liking."
        )
        raise SystemExit

    #global user_config
    #user_config = user_config_temp

    # I wish i could simply use the solution above
    for key, val in user_config_temp.items():
        user_config[key] = val
