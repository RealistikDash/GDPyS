from functions import AIDToUID, CheckBcryptPw, HasPrivilege, mycursor
from constants import *
from core.glob import glob
from config import UserConfig
import requests
import urllib.parse

def ToolLoginCheck(request) -> bool:
    """Handles the login checks for user tools. Returns new session if true"""
    #Return struct is (T/F based on result, Message)
    Username = request.form["username"]
    Password = request.form["password"]

    mycursor.execute("SELECT userName, password, accountID, privileges FROM accounts WHERE userName LIKE %s LIMIT 1", (Username,))
    User = mycursor.fetchone()
    if User == None:
        return (False, "User not found!")
    
    UserID = AIDToUID(User[2])
    #check if not banned
    mycursor.execute("SELECT isBanned FROM users WHERE userID = %s LIMIT 1", (UserID,))
    if mycursor.fetchone()[0]:
        return (False, "You are banned!")
    
    if not HasPrivilege(User[2], UserLogIn):
        return (False, "You do not have permission to log in!")

    # password check
    if not CheckBcryptPw(User[1], Password):
        return (False, "Incorrect password!")
    
    return (True, {
        "AccountID" : User[2],
        "Username" : User[0],
        "Privileges" : User[3],
        "LoggedIn" : True
    })

def levels_reuploaded_left() -> int:
    """Gets the percentage of reupload taken a day. Yeah that was worded weird."""
    return int(round((glob.reuploaded_levels/UserConfig["MaxReuploadedLevels24h"])*100, 2))

def reupload_level_api(level_id: str, server: str, session):
    """[NOT RESTFUL] Reuploads a level from an external source."""
    server = urllib.parse.unquote(server) #urldecode it
    if not HasPrivilege(session["AccountID"], ToolLevelReupload):
        return {
            "status" : 403,
            "message" : "You don't have sufficient privileges for this action!"
        }
    
    if glob.reuploaded_levels >= UserConfig["MaxReuploadedLevels24h"]:
        return {
            "status" : 403,
            "message" : "The limit for levels reuploaded a day has been reached!"
        }
    #fix link in case
    if server[-1] != "/":
        server += "/"
    try:
        level_data = requests.post(server + "downloadGJLevel22.php", {
            "gameVersion" : 21,
            "binaryVersion" : 35,
            "gdw" : 0,
            "levelID" : level_id,
            "secret" : "Wmfd2893gb7",
            "inc" : 1,
            "extras" : 0
        }).text
    except Exception:
        return {
            "status" : 500,
            "message" : "The request failed!"
        }
    if level_data in ["", "-1", "No no no"]:
        return {
            "status" : 403,
            "message" : "This server hates you." if not level_data == "-1" else "This level doesn't exist."
        }
    

    level = level_data.split("#")[0].split(":") #remove the hashes and divide the level values

    ### POST REUPLOAD STUFF
    glob.reuploaded_levels += 1 #bump
    return {
        "status" : 200,
        "levelID" : 69
    }
