import os
import json
from helpers.generalhelper import dict_keys, JsonFile

__name__ = "ConfigModule"
__author__ = "RealistikDash"

default_config = {
    "port": 80,
    "sql_server": "localhost",
    "sql_user": "root",
    "sql_db": "gdpys",
    "sql_password": "",
    "debug": False,
    "level_path": "data/levels/",
    "save_path": "data/saves/",
    "command_prefix": "!",
    "default_priv": 30,
    "cache_level_strs": True,
    "lang": "en",
    "gdpysbot_enabled": "true"
}

user_config = {}

config_options = list(default_config.keys())


def load_config(location: str = "config.json"):
    config = JsonFile(location)
    user_config_temp = config.get_file()

    if user_config_temp is None:
        print("Generating new config")
        config.write_file(default_config)
        print("Generated new config! Please edit it and restart GDPyS.")
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
        print("Your config has been updated! Please change the new vaulues to your liking.")
        raise SystemExit

    for key in dict_keys(user_config_temp):
        user_config[key] = user_config_temp[key]
