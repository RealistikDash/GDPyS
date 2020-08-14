from functions import AIDToUID, CheckBcryptPw, HasPrivilege, mycursor, Bot, Xor
from constants import *
from core.glob import glob
from core.mysqlconn import mydb
from config import UserConfig
import requests
import urllib.parse
import time
import zlib
import base64

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
    if server[-4:] != ".php":
        if server[-1] != "/":
            server += "/downloadGJLevel22.php"
        else:
            server += "/downloadGJLevel22.php"
    try:
        level_data = requests.post(server, {
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
    ### OK THIS PART IS A PORT OF CVOLTONS LEVEL REUPLOAD AS IM TIRED AND NEED THIS QUICKLY
    ### DEADLINES, THEY SUCK
    # TODO: MAKE MY OWN

    def chk_array(src):
        return "0" if src == "" else src
    level_dict = {}
    for i in range(1, len(level) + 1):
        var = level[i-1]
        if i % 2 == 0:
            level_dict[f"a{arg_num}"] = var
        else:
            arg_num = var
    
    #check if level isnt just total emptyness (a4 is level str)
    if level_dict["a4"] == "":
        return {
            "status" : 500,
            "message" : "There is something wrong with the level!"
        }
    
    timestamp = round(time.time())
    level_string = chk_array(level_dict["a4"])
    game_version = chk_array(level_dict["a13"])

    if level_string[:2] == "eJ":
        level_string = level_string.replace("_", "/").replace("-", "+")
        level_string = zlib.decompress(level_string, zlib.MAX_WBITS|32).decode()
        if game_version > 18:
            game_version = 18
    
    mycursor.execute("SELECT COUNT(*) FROM levels WHERE originalReup = %s", (level_dict["a1"],))

    if mycursor.fetchone()[0] != 0:
        return {
            "status" : 403,
            "message" : "This level already exists"
        }
    
    two_player = chk_array(level_dict["a31"])
    song_id = chk_array(level_dict["a35"])
    extra_str = chk_array(level_dict["a36"])
    coins = chk_array(level_dict["a37"])
    req_stars = chk_array(level_dict["a39"])
    ldm = chk_array(level_dict["a40"])
    password_unxor = chk_array(level_dict["a27"])
    password = Xor(base64.b64decode(password_unxor.encode()).decode(), 26364)

    #this sql query is gonna make me cry...
    mycursor.execute("""
        INSERT INTO levels
            (
            levelName,
            gameVersion,
            binaryVersion,
            userName,
            levelDesc,
            levelVersion,
            levelLength,
            audioTrack,
            auto,
            password,
            original,
            twoPlayer,
            songID,
            objects,
            coins,
            requestedStars,
            extraString,
            levelString,
            levelInfo,
            uploadDate,
            updateDate,
            originalReup,
            userID,
            extID,
            unlisted,
            isLDM
            )
        VALUES      
            (
            %s,
            %s,
            27,
            'GDPyS Bot',
            %s,
            %s,
            %s,
            %s,
            0,
            %s,
            %s,
            %s,
            %s,
            0,
            %s,
            %s,
            %s,
            %s,
            0,
            %s,
            %s,
            %s,
            %s,
            0,
            %s
            )  
    """, (
        level_dict["a2"],
        game_version,
        level_dict["a3"],
        level_dict["a5"],
        level_dict["a15"],
        level_dict["a12"],
        password,
        level_dict["a1"],
        two_player,
        song_id,
        coins,
        req_stars,
        extra_str,
        level_string,
        timestamp,
        timestamp,
        level_dict["a1"],
        Bot.BotUserId,
        Bot.BotID,
        ldm
    ))
    mydb.commit()
    NewLevelID = mycursor.lastrowid
    #write level to file
    with open(f"./Data/Levels/{NewLevelID}", "w+") as File:
        File.write(level_string)
        File.close()

    ### POST REUPLOAD STUFF
    glob.reuploaded_levels += 1 #bump
    return {
        "status" : 200,
        "levelID" : NewLevelID,
        "percentage" : levels_reuploaded_left()
    }
