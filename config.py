#Taken from RealistikPanel
#the purpose of this file has changed to be a quick config fetcher
import json
from os import path
from colorama import init, Fore
from logger import logger
from datetime import datetime

dir_path = path.dirname(path.realpath(__file__))

init() #Colorama thing

DefaultConfig = {
    "Port" : 80,
    #SQL Info
    "SQLHost" : "localhost",
    "SQLUser" : "root",
    "SQLDatabase" : "GDPyS",
    "SQLPassword" : "",
    "Chest1Wait" : 60,
    "Chest2Wait" : 240,
    "CronThreadDelay" : 3600,
    "LocalServer" : False,
    "LegacyPasswords" : False, #cvolton gmdprivateserver passwords if true, bcrypt if false
    "MaxAccsPerIP" : 4,
    "MagicGivesCP" : True, #makes magic levels give cp
    "AwardGivesCP" : True, #makes awarded levels give cp
    "BannedLevelsHidden" : True,
    "LevelCacheSize" : 200, #will store levels in memory. CAN BE EXPENSIVE
    "CommandPrefix" : "/",
    "CheatlessAC" : True, #global switch
    "CheatlessExtremeDemonMinAttempts" : 100, #if a user submits an extreme demon score under this att count, they will be banned
    "CheatlessScoreCheck" : True,
    "CheatlessCronChecks" : True,
    "CheatlessMaxStars" : 5000
}

class JsonFile:
    @classmethod
    def SaveDict(self, Dict, File):
        """Saves a dict as a file"""
        with open(File, 'w') as json_file:
            json.dump(Dict, json_file, indent=4)

    @classmethod
    def GetDict(self, file):
        """Returns a dict from file name"""
        if not path.exists(file):
            return {}
        else:
            with open(file) as f:
                data = json.load(f)
            return data

UserConfig = JsonFile.GetDict(dir_path + "/config.json")
#Config Checks

if UserConfig == {}:
    logger.warning(Fore.YELLOW+"No config found! Generating!"+Fore.RESET)
    JsonFile.SaveDict(DefaultConfig, dir_path + "/config.json")
    logger.info(Fore.WHITE+"Config created! It is named config.json. Edit it accordingly and start the server again!")
    exit()
else:
    #config check and updater
    AllGood = True
    NeedSet = []
    for key in list(DefaultConfig.keys()):
        if key not in list(UserConfig.keys()):
            AllGood = False
            NeedSet.append(key)

    if AllGood:
        # setup logging
        logger.setLevel("INFO")
        logger.info(Fore.GREEN+"Configuration loaded successfully! Loading..." + Fore.RESET)
    else:
        #fixes config
        logger.info(Fore.BLUE+"Updating config..." + Fore.RESET)
        for Key in NeedSet:
            UserConfig[Key] = DefaultConfig[Key]
            logger.info(Fore.BLUE+f"Option {Key} added to config. Set default to '{DefaultConfig[Key]}'." + Fore.RESET)
        logger.info(Fore.GREEN+"Config updated! Please edit the new values to your liking." + Fore.RESET)
        JsonFile.SaveDict(UserConfig, dir_path + "/config.json")
        exit()
