import json
import os

class Lang:
    def __init__(self):
        for f in os.listdir("lang"):
            if f.endswith(".json"):
                lang = json.load(open("lang/" + f, "r"))
                for key, value in lang.items():
                    setattr(self, key, value)


lang = Lang()