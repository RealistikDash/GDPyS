from functions import AIDToUID, HasPrivilege, mycursor, Bot, Xor, TimeAgoFromNow, GetBcryptPassword
from constants import *
from core.glob import glob
from core.mysqlconn import mydb
from config import UserConfig
from helpers.passwordhelper import CheckBcryptPw, CreateBcrypt
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
            isLDM,
            secret,
            hostname
            )
        VALUES      
            ( #hey mysql also uses hashtags for comments neat
            %s, #levelname
            %s, #gameversion
            27, #binary version
            'GDPyS Bot', #username
            %s, #description
            %s, #level ver
            %s, # length
            %s, # audiotrack
            0,  # auto
            %s, #password
            %s, #original
            %s, #twoplayer
            %s, #songid
            0,  #objects
            %s, #coins
            %s, #requested stars
            %s, #extra string
            %s, #level string
            0,  #level info
            %s, #upload date
            %s, #update date
            %s, #orignal reup
            %s, #userID
            %s, #extID
            0,  #unlisted
            %s,  #is ldm
            'blah its reupload',
            'MYSELF' #todo: change to users ip
            )  
    """, (
        level_dict["a2"], #level name
        game_version, #game ver
        level_dict["a3"], #description
        level_dict["a5"], #level ver
        level_dict["a15"], #length
        level_dict["a12"], #audiotrack
        password, #password
        level_dict["a1"], #original
        two_player,#twoplayer
        song_id,#songid
        coins,#coins
        req_stars, #req stars
        extra_str, #extra string
        level_string, #level str
        timestamp,#upload date
        timestamp,#update date
        level_dict["a1"], #original reup
        Bot.BotUserId,#user id
        Bot.BotID, #ext od
        ldm#ldm
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

def get_logs(page):
    """Fetches logs for a specific page."""
    offset = (int(page) - 1) * 100 #100 is the amount of logs to display
    mycursor.execute("SELECT * FROM adminlogs ORDER BY id DESC LIMIT 100 OFFSET %s", (offset,))
    resp = []
    usernames = {}
    for log in mycursor.fetchall():
        #get username for them
        if log[1] not in list(usernames.keys()): #for speed so all usernames dont have to be fetched
            mycursor.execute("SELECT userName FROM accounts WHERE accountID = %s LIMIT 1", (log[1],))
            username = mycursor.fetchone()
            if username == None:
                username="Deleted Account"
            else:
                username = username[0]
            usernames[log[1]] = username
        resp.append({
            "id" : log[0],
            "from_id" : log[1],
            "from_name" : usernames[log[1]],
            "message" : log[2],
            "timeago" : TimeAgoFromNow(log[3])
        })
    return resp

def change_password(post_data: dict, session: dict) -> dict:
    """Changes a user's password."""
    if not session["LoggedIn"]:
        return False
    new_password = post_data["password"]
    prev_bcrypt = GetBcryptPassword(session["AccountID"])
    old_password = post_data["oldpass"]
    if not CheckBcryptPw(prev_bcrypt, old_password):
        return False
    #change it here
    new_password = CreateBcrypt(new_password)
    mycursor.execute("UPDATE accounts SET password = %s WHERE accountID = %s LIMIT 1", (new_password,session["AccountID"],))
    mydb.commit()
    return True
