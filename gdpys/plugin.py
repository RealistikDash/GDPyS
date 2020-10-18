from time import sleep
import os
import asyncio
import time
import json


class Plugin:
    def __init__(self):
        """Start main loop"""
        depend_check = []
        try:
            for p in self.dependencies:
                for f in os.listdir(os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/plugins"):
                    f = f.strip(".py")
                    if p == f:
                        depend_check.append(p)
            if depend_check != self.dependencies:
                print(
                    f"Dependencies could not be found for \"{self.__class__}\".")
        except AttributeError:
            print("Dependencies is disabled for " + str(self.__class__))
        self.stopped = False
        loop = asyncio.new_event_loop()
        configpath = os.path.dirname(os.path.dirname(
            os.path.realpath(__file__))) + "/plugins/config"
        try:
            self.config = json.load(
                open(configpath + "/" + self.name + "/config.json", "r"))
        except AttributeError:
            print("Warning: Config is disabled for " + str(self.__class__))
        except FileNotFoundError:
            print("Warning: Config is disabled for " + str(self.__class__))
        if self.metadata == False:
            print(f"Warning: Plugin {self.__class__} has invalid metadata!")
        while True:
            if self.stopped:
                break
            loop.run_until_complete(self.loop())
            sleep(1)

    def create_config(self, template):
        """Create config for plugins"""
        configpath = os.path.dirname(os.path.dirname(
            os.path.realpath(__file__))) + "/plugins/config"
        if os.path.exists(configpath + "/" + self.name + "/config.json"):
            return
        if self.metadata == False:
            print("Warning: Config could not be created due to insufficent metadata.")
            return
        if not os.path.exists(configpath):
            os.mkdir(configpath)
        if not os.path.exists(configpath + "/" + self.name):
            os.mkdir(configpath + "/" + self.name)
        config = json.dump(template, open(
            configpath + "/" + self.name + "/config.json", "w"))

    def set_metadata(self, name="", author="", description="", version="", dependencies=[]):
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
