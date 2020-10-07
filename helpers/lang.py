import json
import os
from config import user_config

class Lang:
    def __init__(self):
        for f in os.listdir("lang"):
            if f == user_config["lang"] + ".json":
                lang = json.load(open("lang/" + f, "r"))
                for key, value in lang.items():
                    setattr(self, key, value)
lang = Lang()