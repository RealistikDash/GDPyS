import mysql.connector
from config import *
from console import *
import time
import timeago
import base64
import random
import hashlib
from itertools import cycle
import requests
import zlib
import os
import urllib.parse
import bcrypt
from threading import Thread
from constants import *
import string
from logger import logger
from datetime import datetime, timedelta

try:
    mydb = mysql.connector.connect(
        host=UserConfig["SQLHost"],
        user=UserConfig["SQLUser"],
        passwd=UserConfig["SQLPassword"],
        database=UserConfig['SQLDatabase']
    ) #connects to database
    logger.info(f"{Fore.GREEN}[GDPyS] Successfully connected to MySQL!{Fore.RESET}")
except Exception as e:
    logger.error(f"{Fore.RED}[GDPyS] Failed connecting to MySQL! Aborting!\nError: {e}{Fore.RESET}")
    exit()

mycursor = mydb.cursor(buffered=True) #creates a thing to allow us to run mysql commands

# TODO: Add SQL index creation

#caches
Ranks = {}
PrivilegeCache = {} # Privileges will be cached here
LevelDLCache = {} #the level data will be stored here so it doesnt have to be redownloaded
BrcyptCache = {} #so we dont call mysql in gjpchecks
UserIDCache = {} #caches user ids (1 less query!)

def CacheUserIDs():
    """Caches all UserIDs from table. Used to remove the query from AIDToUID."""
    Log("Caching UserIDs.")
    mycursor.execute("SELECT extID, userID FROM users")
    UserIDs = mycursor.fetchall()
    for a in UserIDs:
        UserIDCache[int(a[0])] = a[1]

def GetUIDFromCache(AccID: int) -> int:
    """Returns UID from cache if there. Caches it if not there."""
    AccID = int(AccID)
    try:
        return UserIDCache[AccID]
    except IndexError:
        mycursor.execute("SELECT userID FROM users WHERE extID = %s LIMIT 1", (AccID,))
        UserIDCache[AccID] = mycursor.fetchone()[0]
        Log(f"Cached UserID for {AccID}")
        return UserIDCache[AccID]
        

def GetBcryptPassword(AccountID):
    """Gets a users password from cache or gets it from db and caches it."""
    if AccountID not in list(BrcyptCache.keys()):
        mycursor.execute("SELECT password FROM accounts WHERE accountID = %s LIMIT 1", (AccountID,))
        BrcyptCache[AccountID] = mycursor.fetchone()[0]
        Log(f"Cached Bcrypt for {AccountID}")
    return BrcyptCache[AccountID]

def DecodeGJP(GJP) -> str:
    """Decodes the GJP sent by the client.
    
    NOTE: 
    DO NOT STORE THE RETURN OF THIS FUNCTION. THAT IS REALLY UNSAFE.
    
    CREDIT: 
    Taken from Cvolton's GMD private server
    https://github.com/Cvolton/GMDprivateServer/blob/master/incl/lib/GJPCheck.php
    This is just a python port of that function."""
    #TODO: this can be a one-liner
    GJP = GJP.replace("_", "/").replace("-", "+")
    GJP = base64.b64decode(GJP)
    return Xor(GJP.decode(), 37526)

def VerifyGJP(AccountID: int, GJP: str):
    """Returns true if GJP is correct."""
    return CheckBcryptPw(GetBcryptPassword(AccountID), DecodeGJP(GJP))

def FixUserInput(String):
    """[DEPRECATED] Gets rid of potentially problematic user input."""
    String = String.replace(r"\0", "")
    String = String.replace("#", "")
    String = String.replace("|", "")
    String = String.replace("#", "")
    String = String.replace(":", "")
    String = String.replace("--", "")
    return String

def GetServerIP():
    """Gets the server IP."""
    if UserConfig["LocalServer"]:
        CurrentIP = "127.0.0.1"
    else:
        Request = requests.get("https://ip.zxq.co/") #gets our ip
        CurrentIP = Request.json()["ip"]
    return CurrentIP

def LoginCheck(Udid, Username, Password, request):
    """Checks login and password"""
    mycursor.execute("SELECT accountID FROM accounts WHERE userName LIKE %s", (Username,))
    Accounts = mycursor.fetchall()
    if len(Accounts) == 0:
        #no accounts found
        Fail(f"Account {Username} not found!")
        return "-1" #idk the error codes
    AccountID = Accounts[0][0] #choosing the closes one

    #User ID
    mycursor.execute("SELECT userID, isBanned FROM users WHERE extID = %s", (AccountID,))
    UIDFetch = mycursor.fetchone()
    if UIDFetch == None:
        TheIP = request.remote_addr
        mycursor.execute("INSERT INTO users (isRegistered, extID, userName, IP) VALUES (1, %s, %s, %s)", (AccountID, Username, TheIP))
        mydb.commit()
        #fetch again br uh
        mycursor.execute("SELECT userID, isBanned FROM users WHERE extID = %s", (AccountID,))
        UIDFetch = mycursor.fetchone()

    UserID = UIDFetch[0]

    #we dont allow banned people to log in, tell them its disabled
    if UIDFetch[1]:
        return "-12"

    if not CheckPassword(AccountID, Password):
        return "-1"

    #lastly we check if they are allowed to log in
    if not HasPrivilege(AccountID, UserLogIn):
        return "-1"
    Success(f"Authentication for {Username} was successfull!")
    return f"{AccountID},{UserID}"

def HashPassword(PlainPassword: str):
    """Creates a hashed password to be used in database."""
    if not UserConfig["LegacyPasswords"]:
        return CreateBcrypt(PlainPassword)
    return PlainPassword #havent done legacy passwords

def CheckPassword(AccountID: int, Password: str):
    """Checks if the password passed matches the one in the database."""
    #getting password from db
    DBPassword = GetBcryptPassword(AccountID)
    if not UserConfig["LegacyPasswords"]:
        return CheckBcryptPw(DBPassword, Password)
    return True

def RegisterFunction(request):
    """Registers a user."""
    Log(f"Register attempt started for {request.form['userName']}")
    #check if username is taken
    mycursor.execute("SELECT userName FROM accounts WHERE userName LIKE %s LIMIT 1", (request.form["userName"],))
    Test = mycursor.fetchall()
    if len(Test) != 0:
        Fail(f"Cound not register {request.form['userName']}! (username taken)")
        return "-2"
    #aight lets go register them
    Username = FixUserInput(request.form["userName"])
    Password = HashPassword(request.form["password"])
    Email = FixUserInput(request.form["email"])
    RegisterTime = round(time.time())
    #Query Time
    mycursor.execute("INSERT INTO accounts (userName, password, email, secret, saveData, registerDate, saveKey) VALUES (%s, %s, %s, '', '', %s, '')", (Username, Password, Email, RegisterTime))
    mydb.commit()
    Success(f"User {Username} successfully registered!")
    return "1"

def GetRank(AccountID):
    """Gets rank for user."""
    try:
        Rank = Ranks[str(AccountID)]
    except:
        Rank = 0
    return Rank

def Xor(data, key):
    data = str(data)
    key = str(key)
    xored = ''.join(chr(ord(x) ^ ord(y)) for (x,y) in zip(data, cycle(key)))
    return xored

def GetUserDataFunction(request):
    """Gets the user data."""
    TargetAccid = request.form["targetAccountID"]
    FromAccid = request.form["accountID"]
    Log(f"Getting account data for {TargetAccid}")
    if not VerifyGJP(FromAccid, request.form["gjp"]):
        return "-1"
    #checking for blocks
    mycursor.execute("SELECT id FROM blocks WHERE (person1 = %s AND person2 = %s) OR (person1 = %s AND person2 = %s)", (TargetAccid, FromAccid, FromAccid, TargetAccid))
    Blocks = mycursor.fetchall()
    if len(Blocks) > 0:
        return "-1"
    Append = ""
    FriendState = 0
    #gets messages and friend requests (thanks cvolton again)
    if TargetAccid == FromAccid: #its the user checking themselves out
        mycursor.execute("SELECT count(*) FROM friendreqs WHERE toAccountID = %s AND isNew = 1", (TargetAccid,))
        FreindReqs = mycursor.fetchone()[0]
        mycursor.execute("SELECT count(*) FROM messages WHERE toAccountID = %s AND isNew = 0", (TargetAccid,))
        NewMessages = mycursor.fetchone()[0]
        mycursor.execute("SELECT count(*) FROM friendships WHERE (person1 = %s AND isNew2 = '1') OR  (person2 = %s AND isNew1 = '1')", (FromAccid, FromAccid,))
        NewFirends = mycursor.fetchone()[0]
        Append = f":38:{NewMessages}:39:{FreindReqs}:40:{NewFirends}"
    else:
        #check for incoming reqs
        mycursor.execute("SELECT count(*) FROM friendships WHERE (person1 = %s AND person2 = %s) OR (person2 = %s AND person1 = %s)", (TargetAccid, FromAccid, FromAccid, TargetAccid))
        if mycursor.fetchone()[0] > 0:
            FriendState = 1
        else:
            mycursor.execute("SELECT ID, comment, uploadDate FROM friendreqs WHERE accountID = %s AND toAccountID = %s", (TargetAccid, FromAccid))
            if len(mycursor.fetchall()):
                FriendState = 3
            else: #so other queries arent ran if we already found it
                #outgoing reqs
                mycursor.execute("SELECT ID, comment, uploadDate FROM friendreqs WHERE accountID = %s AND toAccountID = %s", (FromAccid, TargetAccid))
                if len(mycursor.fetchall()):
                    FriendState = 4

    mycursor.execute("SELECT * FROM users WHERE extID = %s LIMIT 1", (TargetAccid,))
    Userdata = mycursor.fetchall()[0]
    mycursor.execute("SELECT youtubeurl, twitter, twitch, frS, mS, cS FROM accounts WHERE accountID = %s LIMIT 1", (TargetAccid,))
    ExtraData = mycursor.fetchall()[0]
    Rank = GetRank(TargetAccid)
    ModBadgeLevel = GetModBadge(TargetAccid)
    #AAAAAAAA WHY DIDNT ROBTOP USE JSON
    #refrence taken from php gdps (thanks cvolton)
    TheStupidString = f"1:{Userdata[3]}:2:{Userdata[1]}:13:{Userdata[10]}:17:{Userdata[11]}:10:{Userdata[7]}:11:{Userdata[8]}:3:{Userdata[4]}:46:{Userdata[25]}:4:{Userdata[5]}:8:{Userdata[22]}:18:{ExtraData[4]}:19:{ExtraData[3]}:50:{ExtraData[5]}:20:{ExtraData[0]}:21:{Userdata[15]}:22:{Userdata[16]}:23:{Userdata[17]}:24:{Userdata[18]}:25:{Userdata[19]}:26:{Userdata[20]}:28:{Userdata[21]}:43:{Userdata[28]}:47:{Userdata[29]}:30:{Rank}:16:{Userdata[2]}:31:{FriendState}:44:{ExtraData[1]}:45:{ExtraData[2]}:29:1:49:{ModBadgeLevel}{Append}"
    Success(f"Got user data for {Userdata[3]} successfully!A")
    return TheStupidString

def AIDToUID(AccountID: int):
    """Gets user ID from Account ID."""
    return GetUIDFromCache(AccountID) #calls this function now

def TimeAgoFromNow(Timestamp):
    """Returns a string of how long ago from now was a timestamp."""
    Time = datetime.fromtimestamp(int(Timestamp))
    Now = datetime.now()
    return timeago.format(Time, Now)

def GetAccComments(request):
    """Gets account comments for person."""
    Page = int(request.form["page"])
    Offset = 10 * Page
    TargetAccid = request.form["accountID"]
    Log(f"Getting page {Page} of account comments for {TargetAccid}.")
    UserID = AIDToUID(TargetAccid)
    #getting the data we need
    mycursor.execute("SELECT comment, userID, likes, isSpam, commentID, timestamp FROM acccomments WHERE userID = %s ORDER BY timeStamp DESC LIMIT 10 OFFSET %s", (UserID, Offset))
    UserComments = mycursor.fetchall()
    if len(UserComments) == 0: #if no usercomments
        return "#0:0:0"
    
    #get comment count
    mycursor.execute("SELECT count(*) FROM acccomments WHERE userID = %s", (UserID,))
    CommentCount = mycursor.fetchall()[0][0]
    
    CommentStr = ""
    for comment in UserComments:
        CommentStr += f"2~{comment[0]}~3~{comment[1]}~4~{comment[2]}~5~0~7~{comment[3]}~9~{TimeAgoFromNow(comment[5])[:-4]}~6~{comment[4]}|"

    CommentStr = CommentStr[:-1]

    CommentStr = f"{CommentStr}#{CommentCount}:{Offset}:10"

    Success(f"Successfully got account comments for {TargetAccid}!")

    return CommentStr

def InsertAccComment(request):
    """Adds an account comment."""
    Username = request.form["userName"]
    CommentContent = request.form["comment"]
    AccountID = request.form["accountID"]
    if not VerifyGJP(AccountID, request.form["gjp"]):
        return "-1"
    #checking if they are allowed
    if not HasPrivilege(AccountID, UserPostAccComment):
        return "-1"
    USerID = AIDToUID(AccountID)
    Timestamp = round(time.time())
    mycursor.execute("INSERT INTO acccomments (comment, userID, timeStamp, userName) VALUES (%s, %s, %s, %s)", (CommentContent, USerID, Timestamp, Username))
    mydb.commit()
    return "1"

def UpdateAccSettings(request):
    """Updates the account settings for user."""
    AccountID = request.form["accountID"]
    Ms = request.form["mS"]
    Frs = request.form["frS"]
    Cs = request.form["cS"]
    AccountID = request.form["accountID"]
    YouTube = request.form["yt"]
    Twitter = request.form["twitter"]
    Twitch = request.form["twitch"]
    Log(f"Updating account settings for {AccountID}")
    if not VerifyGJP(AccountID, request.form["gjp"]):
        return "-1"
    
    #setting the things
    mycursor.execute("UPDATE accounts SET mS = %s, cS = %s, frS = %s, youtubeurl = %s, twitter = %s, twitch = %s WHERE accountID = %s", (Ms, Cs, Frs, YouTube, Twitter, Twitch, AccountID))
    mydb.commit()
    Success(f"Settings updated successfully for {AccountID}!")
    return "1"

def UpdateUserScore(request):
    """Updates the user page."""
    #ill do it this way as i can't be asked to write out a billion if statements
    #getting accid from name
    Log(f'Updating user settings for {request.form["userName"]}...')
    mycursor.execute("SELECT accountID FROM accounts WHERE userName LIKE %s", (request.form["userName"],))
    AccountID = mycursor.fetchall()
    if len(AccountID) == 0:
        return "-1"
    AccountID = AccountID[0][0]
    if not VerifyGJP(AccountID, request.form["gjp"]):
        return "-1"
    ToGet = ["userName", "stars", "demons", "icon", "diamonds", "color1", "color2", "iconType", "special", "accIcon", "accShip", "accBall", "accBird", "accDart", "accRobot", "accGlow", "accSpider", "accExplosion", "gameVersion", "secret", "coins", "userCoins"]
    DataDict = {}
    for Thing in ToGet:
        try:
            DataDict[Thing] = request.form[Thing]
        except:
            DataDict[Thing] = 0

    UserID = AIDToUID(AccountID)
    #hold on a minute, lets run the Cheatless check!
    if int(DataDict["stars"]) > UserConfig["CheatlessMaxStars"]:
        CheatlessBan(AccountID, "star count over max allowed stars")

    #big boy query coming up....
    mycursor.execute(
        "UPDATE users SET stars = %s, diamonds = %s, color1 = %s, color2 = %s, iconType = %s, special = %s, accIcon = %s, accShip = %s, accBall = %s, accBird = %s, accDart = %s, accRobot = %s, accGlow = %s, accSpider = %s, accExplosion = %s, gameVersion = %s, secret = %s, coins=%s, userCoins = %s, icon = %s WHERE userID = %s LIMIT 1",
        (DataDict["stars"], DataDict["diamonds"], DataDict["color1"], DataDict["color2"], DataDict["iconType"], DataDict["special"], DataDict["accIcon"], DataDict["accShip"], DataDict["accBall"], DataDict["accBird"], DataDict["accDart"], DataDict["accRobot"], DataDict["accGlow"], DataDict["accSpider"], DataDict["accExplosion"], DataDict["gameVersion"], DataDict["secret"], DataDict["coins"], DataDict["userCoins"], DataDict["icon"], UserID)
        )
    mydb.commit()
    Success(f"Successfully updated the user profile for {request.form['userName']}!")
    return str(UserID)

def JointStringBuilder(Content: dict):
    """Builds a joint string out of a dict."""
    ReturnString = ""
    #iterating through dict
    for key in list(Content.keys()):
        ReturnString += f":{key}:{Content[key]}"
    return ReturnString[1:]

def GetLeaderboards(request):
    """Gets the leaderboards."""
    AccID = request.form["accountID"]
    LeaderboardType = request.form["type"] #4 leaderboard types, realitive, creator, friends and top
    Log(f"Serving {LeaderboardType} leaderboards to {AccID}")

    #leaderboard data
    if LeaderboardType == "top":
        #probably the simplest one
        mycursor.execute("SELECT * FROM users WHERE isBanned = '0' AND stars > 0 ORDER BY stars DESC LIMIT 100")

    elif LeaderboardType == "creators":
        mycursor.execute("SELECT * FROM users WHERE isCreatorBanned = '0' AND isBanned = '0' ORDER BY creatorPoints DESC LIMIT 100")

    TheData = mycursor.fetchall()
    
    ReturnStr = ""
    Iteration = 0
    for User in TheData:
        Iteration += 1
        ReturnStr += JointStringBuilder({
            "1" : User[3], #username
            "2" : User[1], #user id
            "3" : User[4], #stars
            "4" : User[5], #demons
            "6" : Iteration, #rank
            "7" : User[2], #extid
            "8" : round(User[22]), #cp
            "9" : User[6], #icon
            "10" : User[7], #col1
            "11" : User[8], #col2
            "13" : User[10], #coins
            "14" : User[9], #icon type
            "15" : User[12], #special
            "16" : User[2], #another extid
            "17" : User[11], #usercoins
            "46" : User[25] #diamonds
        }) + "|"
    Success("Leaderboards served!")
    return ReturnStr[:-1]

def GetModBadge(AccountID):
    """Gets mod badge level"""
    HasElderMod = HasPrivilege(AccountID, ModElderBadge)
    if HasElderMod:
        return 2
    HasMod = HasPrivilege(AccountID, ModRegularBadge)
    if HasMod:
        return 1
    return 0

def IsMod(request):
    """Returns whether the user is a mod (has badge)."""
    Log(f"User {request.form['accountID']} is checking mod status.")
    if not VerifyGJP(request.form["accountID"], request.form["gjp"]):
        return "-1"
    if HasPrivilege(request.form["accountID"], ModReqMod):
        if HasPrivilege(request.form["accountID"], ModElderBadge):
            return "2"
        else:
            return "1"
    else:
        return "-1"

def Rewards(request):
    """Responsible for the chest rewards."""
    Log(f"Started getting chest data for {request.form['accountID']}")
    if not VerifyGJP(request.form["accountID"], request.form["gjp"]):
        return "-1"
    
    Timestamp = round(time.time())
    RewardType = request.form["rewardType"] #0 = get time, 1= small chest, 2 = big chest
    Chk = request.form["chk"]
    #chk things ported from cvoltons php thing
    EncodeChk = Xor(base64.b64decode(Chk[5:]), 59182)
    UserID = AIDToUID(request.form["accountID"])
    mycursor.execute("SELECT chest1count, chest1time, chest2count, chest2time FROM users WHERE userID = %s LIMIT 1", (UserID,)) #get chest 1 data
    ChestData = mycursor.fetchall()[0]
    Chest1Data = [ChestData[0], ChestData[1]]
    Chest2Data = [ChestData[2], ChestData[3]]
    if RewardType == 1:
        #smol chest
        if not (Chest1Data[0] - Timestamp) <= 0:
            return "-1"
        NewChestCount = Chest1Data[0] + 1
        NewChestTime = Timestamp + (UserConfig["Chest1Wait"] * 60)
        mycursor.execute("UPDATE users SET chest1count = %s, chest1time = %s WHERE userID = %s LIMIT 1", (NewChestCount, NewChestTime, UserID))

    if RewardType == 2:
        #big chest
        if not (Chest2Data[0] - Timestamp) <= 0:
            return "-1"
        NewChestCount = Chest2Data[0] + 1
        NewChestTime = Timestamp + (UserConfig["Chest2Wait"] * 60)
        mycursor.execute("UPDATE users SET chest2count = %s, chest2time = %s WHERE userID = %s LIMIT 1", (NewChestCount, NewChestTime, UserID))

    #generating chest stuff, work in progress
    Chest1orbs = random.randint(100, 1000)
    Chest1Diamonds = random.randint(0, 2)
    Chest1Shards = random.randint(0, 1)
    Chest1Keys = random.randint(0, 1)
    Chest1Str = f"{Chest1orbs},{Chest1Diamonds},{Chest1Shards},{Chest1Keys}"

    Chest2orbs = random.randint(100, 1000)
    Chest2Diamonds = random.randint(0, 2)
    Chest2Shards = random.randint(0, 1)
    Chest2Keys = random.randint(0, 1)
    Chest2Str = f"{Chest2orbs},{Chest2Diamonds},{Chest2Shards},{Chest2Keys}"

    Chest1Lest = Timestamp - Chest1Data[1]
    Chest2Lest = Timestamp - Chest2Data[1]

    #building return string
    #cant use joint string builder here due to a different nature of this return :/
    ReturnStr = f"1:{UserID}:{EncodeChk}:{request.form['udid']}:{request.form['accountID']}:{Chest1Lest}:{Chest1Str}:{Chest1Data[0]}:{Chest2Lest}:{Chest2Str}:{Chest2Data[0]}:{RewardType}"
    #the weird way gd encrypts this
    EncodedReturn = Xor(ReturnStr, 59182)
    EncodedReturn = base64.b64encode(EncodedReturn.encode("ascii")).decode("ascii")
    EncodedReturn = EncodedReturn.replace("/", "_")
    EncodedReturn = EncodedReturn.replace("+", "-")
    ShaReturn = Sha1It(EncodedReturn + "pC26fpYaQCtg")
    Success("Boom chest data done.")
    return f"bruhh{EncodedReturn}|{ShaReturn}"

def Sha1It(Text: str):
    """Hashes text in SHA1."""
    return hashlib.sha1(Text.encode()).hexdigest()

def CacheRanks():
    StartTime = time.time()
    logger.info("Caching ranks... ")
    mycursor.execute("SELECT extID FROM users WHERE isBanned = 0 ORDER BY stars")
    Leaderboards = mycursor.fetchall()
    Leaderboards.reverse()
    Ranks.clear()

    UserRank = 0

    for User in Leaderboards:
        UserRank += 1
        Ranks[str(User[0])] = UserRank
    logger.info(f"Done! {round((time.time() - StartTime) * 1000, 2)}ms")

def CronThread():
    Log("Cron thread started!")
    while True:
        Log("Running cron!")
        StartTime = time.time()
        CacheUserIDs()
        CacheRanks()
        CalculateCP()
        MaxStarCountBan()
        Log(f"Cron done! Took {round(time.time() - StartTime, 2)}s")
        time.sleep(UserConfig["CronThreadDelay"])

def GetAccountUrl(request):
    """Returns something for the account url?"""
    return request.url_root

def SaveUserData(request):
    """Saves the data of the user."""
    #ok so this is pretty much a direct port of cvoltons backupGJAccount to make sure the saves form the php server work with GDPyS
    Username = request.form["userName"] #whY is name capitalised smh
    Password = request.form["password"] #here word isnt capitalised smhmh
    Log(f"Beginning to save data for {Username}")

    SaveData = request.form["saveData"]

    #getting account id from username
    mycursor.execute("SELECT accountID FROM accounts WHERE userName LIKE %s", (Username,))
    AccountID = mycursor.fetchall()
    if len(AccountID) == 0:
        Log("User not found!")
        return "-1"
    AccountID = AccountID[0][0]
    if not CheckPassword(AccountID, Password):
        Fail("Password didn't match!")
        return "-1"
    
    #this is where we do the save ting, decrypting things
    SaveDataAttr = SaveData.split(";")
    SaveData = SaveDataAttr[0]
    SaveData = SaveData.replace("-", "+")
    SaveData = SaveData.replace("_", "/")
    SaveData = base64.b64decode(SaveData)
    SaveData = zlib.decompress(SaveData, zlib.MAX_WBITS|32).decode()

    #getting some variables from the save data
    OrbCount = SaveData.split("</s><k>14</k><s>")[1]
    OrbCount = OrbCount.split("</s>")[0]
    LevelCount = SaveData.split("<k>GS_value</k>")[1]
    LevelCount = LevelCount.split("</s><k>4</k><s>")[1]
    LevelCount = LevelCount.split("</s>")[0]
    mycursor.execute("UPDATE users SET orbs = %s, completedLvls = %s WHERE extID = %s", (OrbCount, LevelCount, AccountID))
    mydb.commit()

    #replacing  the user's password
    SaveData = SaveData.replace(f"<k>GJA_002</k><s>{Password}</s>", "<k>GJA_002</k><s>password go bye bye</s>")

    #guess what now we are encrypting it back
    SaveData = zlib.compress(SaveData.encode())
    SaveData = base64.b64encode(SaveData).decode("ascii")
    SaveData = SaveData.replace("+", "-")
    SaveData = SaveData.replace("/", "_")
    SaveData = f"{SaveData};{SaveDataAttr[1]}"

    #writing the save data to file
    with open(f"./Data/Saves/{AccountID}", "w+") as File:
        File.write(SaveData)
        File.close()

    Success(f"User data for {Username} saved!")
    return "1"

def LoadUserData(request):
    """Returns the user data to be loaded."""
    Username = request.form["userName"]
    Password = request.form["password"]

    Log(f"Starting loading user data for {Username}!")

    #getting account id from username
    mycursor.execute("SELECT accountID FROM accounts WHERE userName LIKE %s", (Username,))
    AccountID = mycursor.fetchall()
    if len(AccountID) == 0:
        Log("User not found!")
        return "-1"
    AccountID = AccountID[0][0]
    if not CheckPassword(AccountID, Password):
        Fail("Password didn't match!")
        return "-1"

    #getting the save data
    mycursor.execute("SELECT saveData FROM accounts WHERE accountID = %s", (AccountID,))
    try:
        DBSaveData = mycursor.fetchall()[0][0]
    except:
        Log("No user data found in db!")
        DBSaveData = "" #why did i do this in this way? idk.

    if os.path.exists(f"./Data/Saves/{AccountID}"):
        File = open(f"./Data/Saves/{AccountID}", "r")
        SaveData = File.read()
        File.close()
    else:
        Log("No save data found! Using the one saved in database!")
        SaveData = DBSaveData
    
    Success(f"Successfully returned load data to {Username}!")
    return f"{SaveData};21;30;a;a"

def LikeFunction(request):
    """Likes a comment/level/accomments."""
    # Type 1 | Levels
    # Type 2 | Commetns
    # Type 3 | Account Comments

    Type = int(request.form["type"])
    Like = int(request.form["like"])
    ItemID = request.form["itemID"]

    if Type == 1:
        #level
        Table = "levels"
        Column = "levelID"
    if Type == 2:
        Table = "comments"
        Column = "commentID"
    if Type == 3:
        Table = "acccomments"
        Column = "commentID"

    #ok so i usually dont do formats in sql queries because sql injection, but here we can trust variables
    mycursor.execute(f"SELECT likes FROM {Table} WHERE {Column} = %s LIMIT 1", (ItemID,))
    Likes = mycursor.fetchall()
    if len(Likes) == 0:
        return "-1"
    Likes = Likes[0][0]

    if Like == 1:
        Likes += 1
    else:
        Likes -= 1
    
    mycursor.execute(f"UPDATE {Table} SET likes = %s WHERE {Column} = %s", (Likes, ItemID))
    mydb.commit()
    return "1"

def UploadLevel(request):
    """Handles the level uploading part."""
    Username = request.form["userName"]
    GJP = request.form["gjp"]
    GameVersion = request.form["gameVersion"]
    Log(f"{Username} is trying to upload a level!")

    #i should make this a function... also on some versions the account id is not passed so to be safe i did this
    mycursor.execute("SELECT accountID FROM accounts WHERE userName LIKE %s", (Username,))
    AccountID = mycursor.fetchall()
    if len(AccountID) == 0:
        Log("User not found!")
        return "-1"
    AccountID = AccountID[0][0]

    if not VerifyGJP(AccountID, GJP):
        return "-1"
    if not HasPrivilege(AccountID, UserUploadLevel):
        return "-1"

    ToGet = ["levelID", "levelName", "levelDesc", "levelVersion", "levelLength", "audioTrack", "auto", "password", "original", "twoPlayer", "songID", "objects", "coins", "requestedStars", "extraString", "levelString", "levelInfo", "secret", "ldm", "udid", "binaryVersion", "unlisted"]
    DataDict = {}
    for Thing in ToGet:
        try:
            if Thing == "levelDesc" and GameVersion < 20:
                #encode it for the old folks (still debating whether to maintain compatibillity with the older versions or not)
                DataDict[Thing] = base64.b64encode(request.form[Thing]).decode("ascii")
            DataDict[Thing] = request.form[Thing]
        except:
            #special cases because YEAH
            if Thing == "extraString":
                DataDict[Thing] = "29_29_29_40_29_29_29_29_29_29_29_29_29_29_29_29"
            elif Thing == "password":
                DataDict[Thing] = 1
            else:
                DataDict[Thing] = 0

    #getting UserID
    mycursor.execute("SELECT userID FROM users WHERE extID = %s", (AccountID,))
    UserID = mycursor.fetchall()[0][0]

    #database stuff
    if DataDict["levelString"] != "" and DataDict["levelName"] != "":
        UploadDate = round(time.time())
        mycursor.execute(
            """INSERT INTO levels (levelName, gameVersion, binaryVersion, userName, levelDesc, levelVersion, levelLength, audioTrack, auto, password, original, twoPlayer, songID, objects, coins, requestedStars, extraString, levelString, levelInfo, secret, uploadDate, userID, extID, updateDate, unlisted, hostname, isLDM) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (DataDict["levelName"], GameVersion, DataDict["binaryVersion"], Username, DataDict["levelDesc"], DataDict["levelVersion"], DataDict["levelLength"], DataDict["audioTrack"], DataDict["auto"], DataDict["password"], DataDict["original"], DataDict["twoPlayer"], DataDict["songID"], DataDict["objects"], DataDict["coins"], DataDict["requestedStars"], DataDict["extraString"], DataDict["levelString"], DataDict["levelInfo"], DataDict["secret"], UploadDate, UserID, AccountID, UploadDate, DataDict["unlisted"], request.remote_addr, DataDict["ldm"])
        )
        mydb.commit()
        # TODO: Later add a case for updating the level like bruh
        LevelId = mycursor.lastrowid

        with open(f"./Data/Levels/{LevelId}", "w+") as File:
            File.write(DataDict["levelString"])
            File.close()
        
        Success(f"{Username} has uploaded level {DataDict['levelName']}!")
        return str(LevelId)
    else:
        return "-1"

def CheckForm(form, TheThing):
    """Checks if something in a form is set."""
    #I KNOW I CAN JUST CHECK IF THE THING IS IN THE KEYS BUT IM TOO LAZY TO DO THIS RN
    try:
        form[TheThing] = ""
        return True
    except:
        return False

def UserString(UserID: int):
    """Returns a user string."""
    mycursor.execute("SELECT userName, extID FROM users WHERE userID = %s", (UserID,))
    Data = mycursor.fetchall()
    if len(Data) == 0:
        return ""
    Data = list(Data[0])

    try:
        Data[1] = int(Data[1])
    except:
        Data[1] = 0
    
    return f"{UserID}:{Data[0]}:{Data[1]}"

def GenMulti(LevelMultiString):
    """
    Ported from GMDPrivateServer by Cvolton
    /incl/lib/generateHash.php
    Let me sleep
    """
    Levels = LevelMultiString.split("|")
    Hash = ""
    for Level in Levels:
        mycursor.execute("SELECT levelID, starStars, starCoins FROM levels WHERE levelID = %s", (Level,))
        Data = mycursor.fetchall()
        if len(Data) > 0:
            Data = Data[0]

            Hash += f"{str(Data[0])[0]}{str(Data[0])[len(str(Data[0]))-1]}{Data[1]}{Data[2]}"
    
    return Sha1It(Hash + "xI25fpAapCQg")

def GenSongString(SongID: int):
    """Generates a song string."""
    mycursor.execute("SELECT ID, name, authorID, authorName, size, isDisabled, download FROM songs WHERE ID = %s", (SongID,))
    SongData = mycursor.fetchall()
    if len(SongData) == 0:
        return ""
    SongData = SongData[0]
    if SongData[5]:
        #if DISABLED
        return ""
    
    SongURL = SongData[6]

    if ":" in SongURL:
        SongURL = urllib.parse.quote(SongURL)

    #clean up output
    SongName = SongData[1].replace("#", "")
    AuthorName = SongData[3].replace("#", "")
    
    return f"1~|~{SongData[0]}~|~2~|~{SongName}~|~3~|~{SongData[2]}~|~4~|~{AuthorName}~|~5~|~{SongData[4]}~|~6~|~~|~10~|~{SongURL}~|~7~|~~|~8~|~0"

def IsInt(TheThing):
    """Checks if the thing passed is a valid integer."""
    try:
        int(TheThing)
        return True
    except:
        return False


def GetLevels(request):
    """As the function states, this gets (get ready for it) levels!"""
    Log("Beginning to fetch levels!")
    #BRUH I HATE THIS SO MUCH SO SO SO MUCH
    #this is a partial port of cvoltons sorry i cant do this
    Form = request.form #so i dont have to write request.form

    Type = int(request.form.get("type", 0))

    #pages
    Offset = int(request.form.get("page", 0)) * 10

    Order = "uploadDate"
    SQLParams = []
    SQLFormats = [] #to prevent sql injection yeah

    #gauntlets
    Gauntlet = int(request.form.get("gauntlet", 0))
    if Gauntlet != 0:
        mycursor.execute("SELECT level1, level2, level3, level4, level5 FROM gauntlets WHERE ID = %s LIMIT 1", (Gauntlet,))
        GauntletLevels = mycursor.fetchone()
        if GauntletLevels == None:
            SQLParams.append("levelID IN (%s)")
            SQLFormats.append(f"{GauntletLevels[0]},{GauntletLevels[1]},{GauntletLevels[2]},{GauntletLevels[3]},{GauntletLevels[4]}")

    #SO MANY IF STATEMENTS I HATE THIS
    if CheckForm(Form, "featured") and Form["featured"]:
        SQLParams.append("starFeatured = 1")
    if CheckForm(Form, "original") and Form["original"]:
        SQLParams.append("original = 0")
    if CheckForm(Form, "coins") and Form["coins"]:
        SQLParams.append("starCoins = 1 AND NOT coins = 0")
    if CheckForm(Form, "epic") and Form["epic"]:
        SQLParams.append("starEpic = 1")
    if CheckForm(Form, "twoPlayer") and Form["twoPlayer"]:
        SQLParams.append("twoPlayer = 1")
    if CheckForm(Form, "star"):
        SQLParams.append("NOT starStars = 0")
    if CheckForm(Form, "noStar"):
        SQLParams.append("starStars = 0")
    if CheckForm(Form, "len"):
        SQLParams.append(f"levelLenght IN ({Form['len']})")

    if Type == 0 or Type == 15:
        Order = "likes"
        SearchStr = request.form.get("str", "")
        if SearchStr != "":
            #looking for level id
            if IsInt(SearchStr):
                SQLParams.append("levelID = %s")
                SQLFormats.append(SearchStr)
            #nope its a name
            else:
                #add % around search to find levels with that thing in the name
                #and btw this may be replaced with elasticsearch as i look further into it
                ThingSearchStr = f"%{SearchStr}%"
                SQLParams.append("levelName LIKE %s")
                SQLFormats.append(ThingSearchStr)
    if Type == 1:
        Order = "downloads"
    elif Type == 2:
        Order = "likes"
    elif Type == 3:
        SQLParams.append(f"uploadDate > {round(time.time()) - 604800}")
        Order = "likes"
    #no type 4 as it is already the default one
    elif Type == 5:
        Param5 = "levels.userID = %s"
        if not UserConfig["BannedLevelsHidden"]:
            Param5 = "userID = %s"
        SQLParams.append(Param5)
        SQLFormats.append(Form["str"])
    elif Type == 6:
        SQLParams.append("starFeatured = 1 OR starFeatured = 2")
        Order = "uploadDate, rateDate DESC"
    elif Type == 7:
        SQLParams.append("magic = 1")
    elif Type == 10: #mappacks
        SQLParams.append("levelID in (%s)")
        SQLFormats.append(Form["str"])
    elif Type == 11:
        SQLParams.append("awarded = 1")
    elif Type == 12:
        # TODO: Followed
        pass
    elif Type == 13:
        AccountID = request.form["accountID"]
        if not VerifyGJP(AccountID, request.form["gjp"]):
            return "-1"
        SQLParams.append("levels.extID in (%s)")
        SQLFormats.append(ListToCommaString(GetFriendsList(AccountID)))
    elif Type == 16:
        SQLParams.append("NOT starEpic = 0")
        Order = "rateDate DESC, uploadDate"

    #converting dict to sql
    if len(SQLParams) != 0:
        Conditions = "WHERE "
        for Condition in SQLParams:
            Conditions += f"{Condition} AND"
        if not UserConfig["BannedLevelsHidden"]:
            Conditions = Conditions[:-4]
    else:
        Conditions = "WHERE"
        if not UserConfig["BannedLevelsHidden"]:
            Conditions = "" #ngl this is messy

    Query = f"SELECT * FROM levels INNER JOIN users ON levels.userID = users.userID {Conditions} users.isBanned = 0 ORDER BY {Order} DESC LIMIT 10 OFFSET {Offset}"
    CountQuery = f"SELECT count(*) FROM levels INNER JOIN users ON levels.userID = users.userID {Conditions} users.isBanned = 0"

    #if the config for removing levels of banned people is disabled
    if not UserConfig["BannedLevelsHidden"]:
        Query = f"SELECT * FROM levels {Conditions} ORDER BY {Order} DESC LIMIT 10 OFFSET {Offset}"
        CountQuery = f"SELECT count(*) FROM levels {Conditions}"

    mycursor.execute(CountQuery, tuple(SQLFormats))
    LevelCount = mycursor.fetchall()[0][0]

    mycursor.execute(Query, tuple(SQLFormats))
    Levels = mycursor.fetchall()

    ReturnStr = ""
    UserStr = ""
    LevelMultiStr = ""
    SongString = ""

    for Level in Levels:
        ReturnStr += JointStringBuilder({
            "1" : Level[3],
            "2": Level[4],
            "3" : Level[5],
            "5" : Level[6],
            "6" : Level[35],
            "8" : "10",
            "9" : Level[21],
            "10" : Level[22],
            "12" : Level[8],
            "13" : Level[0],
            "14" : Level[23],
            "17" : Level[24],
            "43" : Level[34],
            "25" : Level[25],
            "18" : Level[26],
            "19" : Level[31],
            "42" : Level[33],
            "45" : Level[14],
            "15" : Level[7],
            "30" : Level[11],
            "31" : "0",
            "37" : Level[15],
            "38" : Level[30],
            "39" : Level[16],
            "46" : "1",
            "47" : "2",
            "40" : Level[42],
            "35" : Level[13]
        }) + "|"

        UserStr += UserString(Level[-8]) + "|"
        LevelMultiStr += str(Level[3]) + "|"

        if Level[13] != 0:
            SongString += GenSongString(Level[13]) + "~:~"
    
    ReturnStr = ReturnStr[:-1]
    UserStr = UserStr[:-1]
    LevelMultiStr = LevelMultiStr[:-1]
    SongString = SongString[:-3]

    TheFinalStr = f"{ReturnStr}#{UserStr}#{SongString}#{LevelCount}:{Offset}:10#{GenMulti(LevelMultiStr)}"
    Success("Level list served!")
    return TheFinalStr

def SoloGen(LevelString: str):
    """Port of genSolo from Cvolton's GMDPrivateServer."""
    Return = ""
    StrLen = len(LevelString) // 40
    for i in range(40):
        Return += LevelString[i * StrLen]
    return Sha1It(Return + "xI25fpAapCQg")

def SoloGen2(LevelString: str):
    """Port of genSolo2 from Cvolton's GMDPrivateServer."""
    return Sha1It(LevelString + "xI25fpAapCQg")

def CheckBcryptPw(dbpassword, painpassword):
    """
    Checks Bcrypt passwords. Taken from RealistikPanel (made by me)
    By: kotypey
    password checking...
    """

    painpassword = painpassword.encode('utf-8')
    dbpassword = dbpassword.encode('utf-8')
    try:
        check = bcrypt.checkpw(painpassword, dbpassword)
    except:
        Fail("Invalid password type (not Bcrypt)")
        return False

    return check

def CreateBcrypt(Password: str):
    """Creates hashed password."""
    BHashed = bcrypt.hashpw(Password.encode("utf-8"), bcrypt.gensalt(10))
    return BHashed.decode()

def GetSong(request):
    """A mix of getting the song info and adding it if it doesnt exist."""
    SongID = int(request.form["songID"])
    Log(f"Getting song {SongID}.")

    mycursor.execute("SELECT ID, name, authorID, authorName, size, isDisabled, download FROM songs WHERE ID = %s LIMIT 1", (SongID,))
    SongData = mycursor.fetchall()
    if len(SongData) == 0:
        if SongID > 5000000:
            return "-1" #dont ask gd for custom songs
        Log("Song not in database... Calling boomlings.")
        BoomlingsSongInfo = requests.post("http://www.boomlings.com/database/getGJSongInfo.php", data={
            "secret" : "Wmfd2893gb7",
            "songID" : SongID
        })
        Response = BoomlingsSongInfo.text
        Thread(target=AddSongToDB, args=(Response,)).start() #add to thread not to slow down
        Success("Served song from boomlings!")
        return Response

    Log("Song found in database! Serving...")
    SongData = SongData[0]

    if SongData[5]:
        return "-2"
    
    SongURL = SongData[6]

    Success("Song served!")
    return f"1~|~{SongData[0]}~|~2~|~{SongData[1]}~|~3~|~{SongData[2]}~|~4~|~{SongData[3]}~|~5~|~{SongData[4]}~|~6~|~~|~10~|~{SongURL}~|~7~|~"

def GetComments(request):
    """Gets comments for a level."""
    Data = {}
    #ok this is prob stupid but yolo
    #btw to explain how this works, first value is key, second value is the default one if not set
    # NOTE: This was before i found out about request.form.get
    ToGet = [["mode", 0], ["count", 10], ["page", 0], ["levelID", 0], ["userID", 0]]

    for Key in ToGet:
        try:
            Data[Key[0]] = int(request.form[Key[0]])
        except:
            Data[Key[0]] = Key[1]

    Offset = Data["page"] * Data["count"]
    Column = "likes"
    if Data["mode"] == 0:
        Column = "commentID"
    
    if Data["levelID"] == 0 or Data["levelID"] == "":
        #all comments
        DisplayID = True
        mycursor.execute(f"SELECT levelID, commentID, timestamp, comment, userID, likes, isSpam, percent FROM comments WHERE userID = %s ORDER BY {Column} DESC LIMIT %s OFFSET %s", (Data["userID"], Data['count'], Offset))
        Comments = mycursor.fetchall()
        mycursor.execute("SELECT count(*) FROM comments WHERE userID = %s", (Data["levelID"],))
        CommentCount = mycursor.fetchall()[0][0]
    else:
        DisplayID = False
        mycursor.execute(f"SELECT levelID, commentID, timestamp, comment, userID, likes, isSpam, percent FROM comments WHERE levelID = %s ORDER BY {Column} DESC LIMIT %s OFFSET %s", (Data["levelID"], Data['count'], Offset))
        Comments = mycursor.fetchall()
        mycursor.execute("SELECT count(*) FROM comments WHERE levelID = %s", (Data["levelID"],))
        CommentCount = mycursor.fetchall()[0][0]
    
    if len(Comments) == 0:
        return "-2"

    ReturnString = ""
    UserString = ""
    for Comment in Comments:
        if DisplayID:
            ReturnString += f"1~{Comment[0]}~"
        UploadAgo = TimeAgoFromNow(Comment[2])[:-4]
        mycursor.execute("SELECT userID, userName, icon, color1, color2, iconType, special, extID FROM users WHERE userID = %s LIMIT 1", (Comment[4],))
        UserData = mycursor.fetchone()
        if UserData == None:
            Fail(f"Failed to find data for user with the UserID of {Data['levelID']}! This will lead to a lot of bad things.")
        try:
            AccountID = int(UserData[-1])
        except:
            AccountID = 0
        RoleData = GetRoleForUser(AccountID)
        ReturnString += f"2~{Comment[3]}~3~{Comment[4]}~5~0~7~{Comment[6]}~9~{UploadAgo}~6~{Comment[1]}~10~{Comment[7]}~11~{RoleData['Badge']}~12~{RoleData['Colour']}:1~{UserData[1]}~7~1~9~{UserData[2]}~10~{UserData[3]}~11~{UserData[4]}~14~{UserData[5]}~15~{UserData[6]}~16~{UserData[7]}|"
    
    return f"{ReturnString[:-1]}#{CommentCount}:{Data['page']}:{Data['count']}"


def AddSongToDB(Response: str):
    """Adds song to database."""
    if Response == "-1" or Response == "" or Response == "-2":
        return
    Log("Adding song from Boomlings to database.")
    List = Response.split("|")
    SongID = List[1][1:-1]
    SongName = List[3][1:-1]
    AuthorID = List[5][1:-1]
    AuthorName = List[7][1:-1]
    SongSize = List[9][1:-1]
    SongURL = List[13][1:-1]

    mycursor.execute("INSERT INTO songs (ID, name, authorID, authorName, size, download) VALUES (%s, %s, %s, %s, %s, %s)", (SongID, SongName, AuthorID, AuthorName, SongSize, SongURL))
    mydb.commit()

def GetRoleForUser(AccountID):
    """Gets role data for account id."""
    Default = {
        "RoleID" : 0,
        "RoleName" : "User",
        "Badge" : 0,
        "Colour" : "256,256,256"
    }
    mycursor.execute("SELECT privileges FROM accounts WHERE accountID = %s LIMIT 1", (AccountID,))
    UserPriv = mycursor.fetchone()
    if UserPriv == None:
        return Default

    UserPriv = UserPriv[0]

    mycursor.execute("SELECT id, name, colour FROM privilegegroups WHERE privileges = %s LIMIT 1", (UserPriv,))
    PrivRole = mycursor.fetchone()
    if PrivRole == None:
        return Default

    #working out the badge
    Badge = 0
    if bool(UserPriv & ModElderBadge):
        Badge = 2
    elif bool(UserPriv & ModRegularBadge):
        Badge = 1
    
    return {
        "RoleID" : PrivRole[0],
        "RoleName" : PrivRole[1],
        "Badge" : Badge,
        "Colour" : PrivRole[2]
    }

def DeleteAccComment(request):
    """Handler for deleting a comment"""
    AccountID = request.form["accountID"]
    if not VerifyGJP(AccountID, request.form["gjp"]):
        return "-1"
    CommentID = request.form["commentID"]

    #getting the user id for later query so that a person cant delete anyone else's comments
    mycursor.execute("SELECT userID FROM users WHERE extID = %s", (AccountID,))
    UserID = mycursor.fetchone()
    if UserID is None:
        return "-1"
    UserID = UserID[0]
    mycursor.execute("DELETE FROM acccomments WHERE userID = %s AND commentID = %s LIMIT 1", (UserID, CommentID,))
    mydb.commit()
    return "1"

def CommentCommand(Comment: str, Extra: dict) -> bool:
    """Handles comment commands."""
    #Example extra dict
    #{
    #    "LevelID" : 432423,
    #    "AccountID" : 543534
    #}
    Command = Comment[len(UserConfig["CommandPrefix"]):].split(" ")
    ###I WANT SWITCH STATEMENTS
    if Command[0] == "setacc" and HasPrivilege(Extra["AccountID"], CommandSetAcc):
        mycursor.execute("SELECT userID, extID FROM users WHERE isRegistered = 1 AND userName LIKE %s LIMIT 1", (Command[1],))
        User = mycursor.fetchone()
        if User is None:
            return False
        mycursor.execute("UPDATE levels SET userName = %s, userID = %s, extID = %s WHERE levelID = %s LIMIT 1", (Command[1], User[0], User[1], Extra["LevelID"]))
        mydb.commit()
        return True
    elif Command[0] == "daily" and HasPrivilege(Extra["AccountID"], ModSetDaily):
        #port of cvoltons command as its his system
        Tmw = time.mktime((datetime.combine(datetime.today(), datetime.min.time()) + timedelta(days=1)).timetuple())
        mycursor.execute("SELECT timestamp FROM dailyfeatures WHERE timestamp >= %s AND type = 0 ORDER BY timestamp DESC LIMIT 1", (Tmw,))
        Timestamp = mycursor.fetchone()
        if Timestamp == None:
            NewTimestamp = Tmw #no prev up to date levels
        else:
            NewTimestamp = Timestamp + 86400 #add a day
        mycursor.execute("INSERT INTO dailyfeatures (levelID, timestamp) VALUES (%s, %s)", (Extra["LevelID"], NewTimestamp))
        mydb.commit()
        return True
    return False

def PostComment(request):
    """Posts a level comment."""
    Username = request.form["userName"] #why is this passed? idk... ill still use it
    Log(f"{Username} tries to post a comment...")
    AccountID = request.form.get("accountID") # WHY DIDNT I FIND OUT REQUEST.FORM.GET BEFORE THIS
    if not VerifyGJP(AccountID, request.form["gjp"]):
        return "-1"
    Percent = int(request.form.get("percent", 0))
    UserID = AIDToUID(AccountID)
    LevelID = request.form["levelID"]
    Comment = request.form["comment"]
    #Check if its not a command
    DeB64 = base64.b64decode(Comment).decode()
    if DeB64.startswith(UserConfig["CommandPrefix"]):
        return str(int(CommentCommand(DeB64, {
            "LevelID" : LevelID,
            "AccountID" : AccountID
        }))) #cursed
    Timestamp = round(time.time())
    #we finally add the comment
    mycursor.execute("INSERT INTO comments (levelID, userID, comment, timeStamp, percent, userName) VALUES (%s, %s, %s, %s, %s, %s)", (LevelID, UserID, Comment, Timestamp, Percent, Username))
    mydb.commit()
    Success("Comment posted!")
    return "1"

def HasPrivilege(AccountID: int, Privilege):
    """Checks if the given account has privilege."""
    #checking if the privilege has been cached
    if str(AccountID) in list(PrivilegeCache.keys()):
        #checking if the thing is not expired
        #and yes ik i could have done it in the same statement
        if PrivilegeCache[str(AccountID)]["Expiry"] > time.time():
            return bool(PrivilegeCache[str(AccountID)]["Privileges"] & Privilege)
    
    #username either not cached or expired
    #getting privs from db
    mycursor.execute("SELECT privileges FROM accounts WHERE accountID = %s LIMIT 1", (AccountID,))
    DBPriv = mycursor.fetchone()
    if DBPriv == None:
        return False
    DBPriv = DBPriv[0]

    #ok first we add them to the cache
    PrivilegeCache[str(AccountID)] = {
        "Privileges" : DBPriv,
        "Expiry" : round(time.time()) + 600
    }
    Log(f"Cached privileges for account {AccountID}")

    #and now alas we check if they have it
    return bool(DBPriv & Privilege)

def RandomString(Lenght=8):
    Chars = string.ascii_lowercase
    return ''.join(random.choice(Chars) for i in range(Lenght))

class GDPySBot:
    """This is the bot class for GDPyS. It is responsible for everything GDPyS related ranging from connecting and creating the bot to sending messages."""
    def __init__(self):
        """Sets up the GDPyS bot class for connection etc."""
        self.Connected = False
        self.BotID = 0
        self.BotUserId = 0

    def _CheckBot(self):
        """Checks if the bot account exists."""
        mycursor.execute("SELECT COUNT(*) FROM accounts WHERE isBot = 1")
        BotCount = mycursor.fetchone()[0]
        if BotCount == 0:
            return False
        return True

    def _FetchID(self):
        """Gets the bots accountID."""
        mycursor.execute("SELECT accountID FROM accounts WHERE isBot = 1 LIMIT 1")
        return mycursor.fetchone()[0]
    
    def _SetUserId(self):
        """Sets the user id for bot."""
        mycursor.execute("SELECT userID FROM users WHERE extID = %s LIMIT 1", (self.BotID,))
        self.BotUserId = mycursor.fetchone()[0]

    def _RegitsterBot(self, BotName="GDPySBot"):
        """Creates the bot account."""
        Timestamp = round(time.time())
        Password = HashPassword(RandomString(16)) #no one ever ever ever should access the bot account. if they do, you messed up big time
        mycursor.execute("INSERT INTO accounts (userName, password, email, secret, saveData, registerDate, isBot) VALUES (%s, %s, 'rel@es.to', '', '', %s, 1)", (BotName, Password, Timestamp))
        mydb.commit() #so the fetchid before works???
        mycursor.execute("INSERT INTO users (isRegistered, extID, userName, IP) VALUES (1, %s, %s, '1.1.1.1')", (self._FetchID(), BotName,))
        mydb.commit()
        Success(f"Created bot user ({BotName})!")
    
    def Connect(self):
        """Sets up the bot to be able to be used."""
        if not self._CheckBot():
            Log("Bot not found! Creating new account for it!")
            self._RegitsterBot()
        
        self.BotID = self._FetchID()
        self.Connected = True
        self._SetUserId()
    
    def GetID(self):
        """Returns the bot's account ID."""
        return self.BotID
    
    def SendMessage(self, Target: int, Body: str, Subject: str):
        """Sends a message from the bot."""
        #first we base64 encode the body and subject
        Subject = base64.b64encode(Subject.encode()).decode("ascii")
        Body = base64.b64encode(Body.encode()).decode("ascii")
        Timestamp = round(time.time())

        #and we create the message
        mycursor.execute("INSERT INTO messages (accID, toAccountID, userName, userID, subject, body, timestamp, isNew) VALUES (%s, %s, 'GDPyS Bot', %s, %s, %s, %s, 0)",
            (self.BotID, Target, self.BotUserId, Subject, Body, Timestamp)
        )
        mydb.commit()

#for now ill place the bot defenition her
Bot = GDPySBot()
Bot.Connect()

def CheatlessScoreCheck(Score: dict) -> bool:
    """Runs a score validity verification."""
    #ok here i will assume that the owner or mod of the gdps doesnt act stupid and rate free extremes.
    #this is an example score dict
    {
        "AccountID" : 1,
        "LevelID" : 222,
        "Percentage" : 100,
        "Attempts" : 10,
        "Coins" : 0
    }
    if UserConfig["CheatlessAC"] and UserConfig["CheatlessScoreCheck"]:
        if Score["Percentage"] > 100:
            CheatlessBan(Score["AccountID"], "invalid level score submission")
            return False
        elif Score["Percentage"] == 100:
            CLCheck(f"Running score check on a score on the level {Score['LevelID']}")
            #ok lads first we get the level data
            mycursor.execute("SELECT levelName, starStars, starDemonDiff, starCoins, coins FROM levels WHERE levelID = %s LIMIT 1", (Score['LevelID'],))
            LevelData = mycursor.fetchone()

            #first check! invalid score
            if LevelData == None:
                CheatlessBan(Score["AccountID"], "invalid level score submission")
                return False
            
            #next we do coin check
            if Score["Coins"] > LevelData[4]:
                CheatlessBan(Score["AccountID"], "unachievable coin count")
                return False

            #now we check if they beat the extreme in like 5 attempts. this will rely on the mods not being stupid and rating
            if LevelData[1] == 10 and LevelData[2] == 6 and Score["Attempts"] < UserConfig["CheatlessExtremeDemonMinAttempts"]:
                CheatlessBan(Score["AccountID"], "too quick demon completion")
                return False
            
            #if there are invalid values given
            if Score["Attempts"] < 0 or Score["Coins"] > 3 or Score["Coins"] < 0:
                CheatlessBan(Score["AccountID"], "invalid level score data")
                return False

        else: #checks for uncomplete levels
            #has coins when not completed level
            if Score["Coins"] > 0:
                CheatlessBan(Score["AccountID"], "coins on uncompleted level")
                return False
        
    return True

def CheatlessBan(AccountID: int, Offence: str):
    """Initiates and official CheatlessAC ban!"""
    CLBan(f"User {AccountID} has been banned by CheatlessAC for {Offence}.")
    Bot.SendMessage(AccountID, Subject="[CheatlessAC] You have been banned!", Body=f"You have been by the Cheatless AntiCheat! The reason for your ban is {Offence}. Please contact the staff team for more info and stop cheating.")
    mycursor.execute("UPDATE users SET isBanned = 1 WHERE extID = %s LIMIT 1", (AccountID,))
    mydb.commit()

def LevelSuggest(request):
    """Suggests/rates a level and handles the route."""
    AccountID = request.form["accountID"]
    if not VerifyGJP(AccountID, request.form["gjp"]):
        return "-1"
    
    #grab vars from post req
    LevelID = request.form["levelID"]
    Stars = int(request.form["stars"])
    FeatureStatus = request.form["feature"]

    #no switch statements in python so i attempted to do this
    RateData = [
        { # NA
            "StarDemon" : 0,
            "StarDifficulty" : 0,
            "StarStars" : 0,
            "StarDemonDiff" : 0,
            "StarAuto" : 0,
        },
        { # Auto
            "StarDemon" : 0,
            "StarDifficulty" : 0,
            "StarStars" : 1,
            "StarDemonDiff" : 0,
            "StarAuto" : 1
        },
        { # Easy
            "StarDemon" : 0,
            "StarDifficulty" : 10,
            "StarStars" : 2,
            "StarDemonDiff" : 0,
            "StarAuto" : 0
        },
        { # Normal
            "StarDemon" : 0,
            "StarDifficulty" : 20,
            "StarStars" : 3,
            "StarDemonDiff" : 0,
            "StarAuto" : 0
        },
        { # Hard 1
            "StarDemon" : 0,
            "StarDifficulty" : 30,
            "StarStars" : 4,
            "StarDemonDiff" : 0,
            "StarAuto" : 0
        },
        { # Hard 2
            "StarDemon" : 0,
            "StarDifficulty" : 30,
            "StarStars" : 5,
            "StarDemonDiff" : 0,
            "StarAuto" : 0
        },
        { # Harder 1
            "StarDemon" : 0,
            "StarDifficulty" : 40,
            "StarStars" : 6,
            "StarDemonDiff" : 0,
            "StarAuto" : 0
        },
        { # Harder 2
            "StarDemon" : 0,
            "StarDifficulty" : 40,
            "StarStars" : 7,
            "StarDemonDiff" : 0,
            "StarAuto" : 0
        },
        { # Insane 1
            "StarDemon" : 0,
            "StarDifficulty" : 50,
            "StarStars" : 8,
            "StarDemonDiff" : 0,
            "StarAuto" : 0
        },
        { # Insane 2
            "StarDemon" : 0,
            "StarDifficulty" : 50,
            "StarStars" : 9,
            "StarDemonDiff" : 0,
            "StarAuto" : 0
        },
        { # Demon
            "StarDemon" : 1,
            "StarDifficulty" : 0,
            "StarStars" : 10,
            "StarDemonDiff" : 4,
            "StarAuto" : 0
        }
    ][Stars]

    #we check whether they can suggest, rate or none
    if HasPrivilege(AccountID, ModRateLevel):
        #ok so first we will get the data for the thing
        mycursor.execute("""UPDATE levels SET 
                                starDemon = %s, 
                                starDifficulty = %s, 
                                starCoins = 1, 
                                starStars = %s, 
                                starDemonDiff = %s,
                                starFeatured = %s,
                                starAuto = %s
                            WHERE levelID = %s LIMIT 1
            """, (
                RateData["StarDemon"],
                RateData["StarDifficulty"],
                RateData["StarStars"],
                RateData["StarDemonDiff"],
                FeatureStatus,
                RateData["StarAuto"],
                LevelID
            ))
        mydb.commit()
        return "1"
    return "-1"

def DebugManualAddSong(Source, SongID):
    """[DEBUG] Manually add a custom song from a custom source."""
    SongInfo = requests.post(Source, data={
        "secret" : "Wmfd2893gb7",
        "songID" : SongID
    })
    AddSongToDB(SongInfo.text)

def DebugReupload(Source, LevelID):
    """[DEBUG] Reuploads level from source to GDPyS server."""
    Level = requests.post(Source, data = {
        "secret" : "Wmfd2893gb7",
        "gameVersion" : 22,
        "levelID" : LevelID,
        "binaryVersion" : 33,
        "gdw" : 0,
        "inc" : 1,
        "extras" : 0
    })

    Result = Level.text
    
    if Result == "" or Result == "-1" or Result == "No no no":
        Fail(f"Server error with response {Result}!")
        return
    
    # TODO FINISH THIS

def MessagePost(request):
    """Posts a message to user."""
    Log("Message send attempt!")
    AccountID = request.form["accountID"]
    if not VerifyGJP(AccountID, request.form["gjp"]):
        return "-1"

    Target = request.form["toAccountID"]
    #checks if not blocked
    mycursor.execute("SELECT COUNT(*) FROM blocks WHERE person1 = %s AND person2 = %s LIMIT 1", (Target, AccountID))
    ReturnThing = mycursor.fetchone()
    if ReturnThing[0] > 0:
        Fail("They were blocked...")
        return "-1" #they are blocked!
    
    mycursor.execute("SELECT mS, userName FROM accounts WHERE accountID = %s", (Target,)) #ill also squeeze the username in here
    ReturnThing = mycursor.fetchone()
    if ReturnThing[0] == 1:
        #ok lets check if they are friends
        # TODO Friend check
        Fail("Friend only messages!")
        return "-1" #dont accept messages!
    
    Secret = request.form["secret"]
    Subject = request.form["subject"]
    Body = request.form["body"]
    Timestamp = round(time.time())
    Username = ReturnThing[1]
    UserID = AIDToUID(AccountID)

    #add to db!
    mycursor.execute("""INSERT INTO messages 
                            (accID, toAccountID, userName, userID, secret, subject, body, timestamp, isNew)
                            VALUES
                            (%s, %s, %s, %s, %s, %s, %s, %s, 0)
                            """,
                            (
                                AccountID,
                                Target,
                                Username,
                                UserID,
                                Secret,
                                Subject,
                                Body,
                                Timestamp
                            ))
    mydb.commit()
    Success("Message sent!")
    return "1"

def UserSearchHandler(request):
    """Handles user searches."""

    Search = f"%{request.form['str']}%" #surrounding with % for the like search
    Offset = int(request.form.get("page", 0)) * 10
    #we get the user data now
    mycursor.execute("""SELECT
                        userName,
                        userID,
                        coins,
                        userCoins,
                        icon,
                        color1,
                        color2,
                        iconType,
                        special,
                        extID,
                        stars,
                        creatorPoints,
                        demons
                    FROM
                        users
                    WHERE
                        userName LIKE %s
                    LIMIT 10 OFFSET %s""", (Search, Offset))

    Users = mycursor.fetchall()
    ReturnString = ""

    UserCount = len(Users)

    if UserCount == 0:
        return "-1"

    #now we create on of those joint strings yeah
    for User in Users:
        ReturnString += JointStringBuilder({
            "1" : User[0],
            "2" : User[1],
            "13" : User[2],
            "17" : User[3],
            "9" : User[4],
            "10" : User[5],
            "11" : User[6],
            "14" : User[7],
            "15" : User[8],
            "16" : User[9],
            "3" : User[10],
            "4" : User[12],
            "8" : round(User[11])
        }) + "|"
    return ReturnString[:-1] + f"#{UserCount}:{Offset}:10"

def APIGetLevel(LevelID):
    """API handler that returns json for level info."""
    #ok here we get the level data from db
    mycursor.execute("SELECT userName, levelID, extID, userID, levelName, levelDesc, levelLength, audioTrack, songID, coins, starDifficulty, downloads, likes, starStars, uploadDate, awarded, magic, starDemon, starAuto, starFeatured, starEpic FROM levels WHERE isDeleted = 0 and levelID = %s LIMIT 1",
    (
        LevelID,
    ))
    LevelData = mycursor.fetchone()
    if LevelData == None:
        return {
            "status" : 204, #i think its 204
            "message" : "No levels found with the specified level id."
        }
    #i think this is a gdpys bug lmao
    if LevelData[5] == "0":
        Description = ""
    else:
        Description = base64.b64decode(LevelData[5]).decode()
    #changing the rate diff to words
    Difficulty = {
        0 : "na",
        10 : "easy",
        20 : "normal",
        30 : "hard",
        40 : "harder",
        50 : "insane"
    }[LevelData[10]]
    #manual exceptions
    if LevelData[17]:
        Difficulty = "demon"
    if LevelData[18]:
        Difficulty = "auto"
    Comments = []
    mycursor.execute("SELECT userID, userName, comment, timestamp, likes, percent FROM comments WHERE levelID = %s", (LevelID,))
    for Comment in mycursor.fetchall():
        Comments.append({
            "userID" : Comment[0],
            "username" : Comment[1],
            "comment" : base64.b64decode(Comment[2]).decode(),
            "timestamp" : Comment[3],
            "likes" : Comment[4],
            "percent" : Comment[5]
        })
    return {
        "status" : 200,
        "id" : LevelData[1],
        "name" : LevelData[4],
        "description" : Description,
        "likes" : LevelData[12],
        "downloads" : LevelData[11],
        "customsong" : bool(LevelData[8]),
        "songid" : LevelData[8], #custom songs
        "audiotrack" : LevelData[7], #in-game songs
        "uploaded" : LevelData[14],
        "coins" : LevelData[9],
        "length" : LevelData[6],
        "creator" : {
            "username" : LevelData[0],
            "userid" : LevelData[3],
            "accountid" : LevelData[2]
        },
        "rate" : {
            "difficulty" : Difficulty,
            "stars" : LevelData[13],
            "magic" : bool(LevelData[16]),
            "awarded" : bool(LevelData[15]),
            "featured" : bool(LevelData[19]),
            "epic" : bool(LevelData[20])
        },
        "comments" : Comments,
        "message" : "Success!"
    }

def GetMessages(request):
    """Gets messages for user."""
    GJP = request.form["gjp"]
    AccountID = request.form["accountID"]
    Offset = int(request.form["page"]) * 10
    Log(f"Getting messages for user {AccountID}.")

    if not VerifyGJP(AccountID, GJP):
        return "-1" 

    GetSent = int(request.form.get("getSent", 0)) #0 = msgs received, 1= msgs sent by the user

    SQLCondition = "toAccountID"

    if GetSent:
        SQLCondition = "accID"
    
    mycursor.execute(f"SELECT * FROM messages WHERE {SQLCondition} = %s ORDER BY timestamp DESC LIMIT 10 OFFSET %s", (AccountID, Offset))
    Messages = mycursor.fetchall()
    #count query
    mycursor.execute(f"SELECT COUNT(*) FROM messages WHERE {SQLCondition} = %s", (AccountID,))
    Count = mycursor.fetchone()[0]
    MessageString = ""

    for Message in Messages:
        UploadAgo = TimeAgoFromNow(Message[7])[:-4]
        #we get username and uid
        mycursor.execute("SELECT userName, userID FROM users WHERE extID = %s LIMIT 1", (Message[6 if GetSent else 4],))
        ExtraUserData = mycursor.fetchone()
        MessageString += JointStringBuilder({
            "1" : Message[5],
            "2" : Message[4],
            "3" : ExtraUserData[1],
            "4" : Message[3],
            "6" : ExtraUserData[0],
            "7" : UploadAgo,
            "8" : Message[9],
            "9" : GetSent
        })+"|"
    
    return f"{MessageString[:-1]}#{Count}:{Offset}:10" #the 10 is the limit

def GetMessage(request):
    """Returns message to client."""
    AccountID = request.form["accountID"]
    GJP = request.form["gjp"]
    MessageID = request.form["messageID"]
    Log(f"User {AccountID} tries to DL message.")

    if not VerifyGJP(AccountID, GJP):
        return "-1"
    
    #now we get message data
    mycursor.execute("SELECT * FROM messages WHERE messageID = %s AND (toAccountID = %s OR accID = %s) LIMIT 1", (MessageID, AccountID, AccountID))
    Message = mycursor.fetchone()

    if Message == None:
        return "-1" #if no message found and so other checks arent ran

    #we mark it as read if not already
    if not Message[9]:
        mycursor.execute("UPDATE messages SET isNew = 1 WHERE messageID = %s AND accID = %s LIMIT 1", (MessageID, AccountID))
        mydb.commit()
    
    GetSent = True if Message[4] else False
    
    mycursor.execute("SELECT userName, userID, extID FROM users WHERE extID = %s LIMIT 1", (Message[6 if GetSent else 4],))
    ExtraUserData = mycursor.fetchone()
    UploadAgo = TimeAgoFromNow(Message[7])[:-4]
    return JointStringBuilder({
        "1" : Message[5],
        "2" : ExtraUserData[2],
        "3" : ExtraUserData[1],
        "4" : Message[3],
        "5" : Message[2],
        "6" : ExtraUserData[0],
        "7" : UploadAgo,
        "8" : Message[9],
        "9" : int(GetSent)
    })

def DeleteCommentHandler(request):
    """Handles the comment deleting."""
    AccountID = request.form["accountID"]
    GJP = request.form["gjp"]
    if not VerifyGJP(AccountID, GJP):
        return "-1" #ignore green users,  they cant post comments anyways
    
    CommentID = request.form["commentID"]
    UserID = AIDToUID(AccountID)
    mycursor.execute("DELETE FROM comments WHERE userID = %s AND commentID = %s LIMIT 1", (UserID, CommentID)) #also squeezed a check that checks whether the person deleting the comment is that person into the query
    mydb.commit()
    return "1"

def MapPackHandelr(request):
    """Fetches the map packs and returns them to the gd client."""
    Log("Getting mappacks.")
    Offset = 10 * int(request.form.get("page", 0)) #turning page to an offset to be used in query below
    #mappack count
    mycursor.execute("SELECT COUNT(*) FROM mappacks")
    PackCount = mycursor.fetchone()[0]
    #Getting the mappacks
    mycursor.execute("SELECT * FROM mappacks LIMIT 10 OFFSET %s", (Offset,))
    MapPacks = mycursor.fetchall()
    PackStr = ""
    PackHash = ""
   
    for Mappack in MapPacks:
        PackStr += JointStringBuilder({
            "1" : Mappack[0], #pack id
            "2" : Mappack[1], #pack name
            "3" : Mappack[2], #pack levels
            "4" : Mappack[3], #stars
            "5" : Mappack[4], #coins
            "6" : Mappack[5], #difficulty
            "7" : Mappack[6], #colours (rgb)
            "8" : Mappack[6] #not gonna be using colors2. i dont even know what they are lmao
        }) + "|"
        MappackID = str(Mappack[0])
        PackHash += f"{MappackID[0]}{MappackID[len(MappackID)-1]}{Mappack[3]}{Mappack[4]}" #ok thas better
    
    PackHash = Sha1It(PackHash + "xI25fpAapCQg")
    return f"{PackStr[:-1]}#{PackCount}:{Offset}:10#{PackHash}"

def GetGauntletsHandler():
    """Returns all the gauntlet things to the gd client."""
    mycursor.execute("SELECT * FROM gauntlets")
    Gauntlets = mycursor.fetchall()
    GauntletReturn = ""
    HashReturn = ""

    for Gauntlet in Gauntlets:
        Levels = f"{Gauntlet[1]},{Gauntlet[2]},{Gauntlet[3]},{Gauntlet[4]},{Gauntlet[5]}"
        GauntletReturn += JointStringBuilder({
            "1" : Gauntlet[0],
            "3" : Levels
        }) + "|"
        HashReturn += f"{Gauntlet[0]}{Levels}" #screw adding
    
    return f"{GauntletReturn[:-1]}#{SoloGen2(HashReturn)}"

def CalculateCP():
    """Cron job that calculates CP for the whole server."""
    StartTime = time.time()
    logger.info("Beginning to calculate CP... ")
    #first we get all user ids
    mycursor.execute("SELECT userID FROM users")
    UserIDs = mycursor.fetchall()

    #fetching the counts and calculation total pp
    for UserID in UserIDs:
        UserCalcCP(UserID[0])
    mydb.commit()
    Finished = round((time.time() - StartTime) * 1000, 2)
    logger.info(f"Done! {Finished}ms")

def UserCalcCP(UserID : int):
    """Calculates CP for specified user id."""
    UserCP = 0
    #count rated levels
    mycursor.execute("SELECT COUNT(*) FROM levels WHERE starStars > 0 AND userID = %s", (UserID,))
    UserCP += mycursor.fetchone()[0]
    #count featured levels
    mycursor.execute("SELECT COUNT(*) FROM levels WHERE starFeatured > 0 AND userID = %s", (UserID,))
    UserCP += mycursor.fetchone()[0]
    #count epic levels
    mycursor.execute("SELECT COUNT(*) FROM levels WHERE starEpic > 0 AND userID = %s", (UserID,))
    UserCP += mycursor.fetchone()[0]
    #count magic levels
    if UserConfig["MagicGivesCP"]:
        mycursor.execute("SELECT COUNT(*) FROM levels WHERE magic > 0 AND userID = %s", (UserID,))
        UserCP += mycursor.fetchone()[0]
    #count awarded levels
    if UserConfig["AwardGivesCP"]:
        mycursor.execute("SELECT COUNT(*) FROM levels WHERE awarded > 0 AND userID = %s", (UserID,))
        UserCP += mycursor.fetchone()[0]
    
    #lastly we give the cp to them
    mycursor.execute("UPDATE users SET creatorPoints = %s WHERE userID = %s LIMIT 1", (UserCP, UserID))
    mydb.commit()

def ScoreSubmitHandler(request):
    """Handles the score submission request by the client."""
    # NOTE this will be slower but it will be better in a lot of ways
    #also this is used for submitting the score AND getting all of the scores
    
    ##### SCORE UPDATE #####
    Coins = int(request.form["s9"]) - 5819
    Atttempts = int(request.form["s1"]) - 8354 #bruh
    GJP = request.form["gjp"]
    LevelID = request.form["levelID"]
    AccountID = request.form["accountID"]
    Percent = int(request.form["percent"])

    Log(f"User {AccountID} tries to submit a score!")
    if not VerifyGJP(AccountID, GJP):
        return "-1"

    CheatlessStruct = {
        "AccountID" : AccountID,
        "LevelID" : LevelID,
        "Percentage" : Percent,
        "Attempts" : Atttempts,
        "Coins" : Coins
    }

    Timestamp = round(time.time())
    #get prev scores
    mycursor.execute("SELECT * FROM levelscores WHERE accountID = %s and levelID = %s LIMIT 1", (AccountID, LevelID))
    Score = mycursor.fetchone()
    #new scores
    if Score == None or Percent != 0: #no prev scores
        Log("New score on level!")
        #creting new score
        #dont thread the check
        if CheatlessScoreCheck(CheatlessStruct):
            mycursor.execute("INSERT INTO levelscores (accountID, levelID, percent, uploadDate, coins, attempts) VALUES (%s, %s, %s, %s, %s, %s)", (
                AccountID, LevelID, Percent, Timestamp, Coins, Atttempts
            ))
            mydb.commit()
    #dont do anything if the percentage is same or lower OR update it if percent is same and coin count is different
    elif Score[3] < Percent or (Score[3] == Percent and Coins > Score[6]):
        Log("Existing score updated.")
        if CheatlessScoreCheck(CheatlessStruct):
            mycursor.execute("UPDATE levelscores SET percent = %s, uploadDate = %s, attempts = %s, coins = %s WHERE scoreID = %s LIMIT 1", (
                Percent, Timestamp, Atttempts, Coins, Score[0]
                ))
            mydb.commit()
    
    #Get Scores
    Type = int(request.form.get("type", 1))

    #I WISH SWITCH STATEMENTS EXISTED and I might do something about this involving tuples
    if Type == 0:
        mycursor.execute("SELECT * FROM levelscores WHERE levelID = %s AND accountID in (%s) ORDER BY percent DESC LIMIT 50", (LevelID, ListToCommaString(GetFriendsList(AccountID))))
    elif Type == 1:
        mycursor.execute("SELECT * FROM levelscores WHERE levelID = %s ORDER BY percent DESC LIMIT 50", (LevelID,))
    
    elif Type == 2:
        AfterTime = Timestamp - 604800 #week ago
        mycursor.execute("SELECT * FROM levelscores WHERE levelID = %s AND uploadDate > %s ORDER BY percent DESC LIMIT 50", (LevelID, AfterTime))
    
    Scores = mycursor.fetchall()

    SQLList =""
    #so we can get all the user data in one query
    for Score in Scores:
        SQLList += f"{Score[1]},"
    
    if len(SQLList) != "":
        SQLList = SQLList[:-1]

    #get all the user date
    mycursor.execute("SELECT extID, userName, userID, icon, color1, color2, iconType, special FROM users WHERE extID in (%s) AND isBanned = 0", (SQLList,))
    AllUserData = mycursor.fetchall()

    ReturnStr = ""
    for i in range(0, len(Scores)):
        #in a for loop to also get places
        Score = Scores[i]
        UserData = Select(AllUserData, 0, str(Score[1])) #got userdata from prev query
        if not UserData == ():
            UserData = UserData[0]
            #skip users that are either banned or something weird had happened to them
            ReturnStr += JointStringBuilder({
                1 : UserData[1],
                2 : UserData[2],
                3 : Score[3],
                6 : i,
                9 : UserData[3],
                10 : UserData[4],
                11 : UserData[5],
                13 : Score[6],
                14 : UserData[6],
                15 : UserData[7],
                16 : UserData[0],
                42 : TimeAgoFromNow(Score[4])[:-4]
            }) + "|"
    
    if len(ReturnStr) == 0:
        return ""
    return ReturnStr[:-1]

def MaxStarCountBan() -> None:
    """[CheatlessAC Cron] Bans people who have a star count higher than the total starcount of the server."""
    # TODO : Make the same thing for usercoins and regular coins
    if UserConfig["CheatlessCronChecks"] and UserConfig["CheatlessAC"]:
        StartTime = time.time()
        logger.info("Running CheatlessAC Cron Starcount Check... ")
        TotalStars = 187 #from RobTop levels
        #get all star rated levels
        mycursor.execute("SELECT starStars FROM levels WHERE starStars > 0")
        StarredLevels = mycursor.fetchall()

        #add em all up
        for Level in StarredLevels:
            TotalStars += Level[0]
        
        #count query
        mycursor.execute("SELECT COUNT(*) FROM users WHERE stars > %s", (TotalStars,))
        BannedCount = mycursor.fetchone()[0]
        #ban em
        mycursor.execute("UPDATE users SET isBanned = 1 WHERE stars > %s", (TotalStars,))
        mydb.commit()

        logger.info(f"Done with {BannedCount} users banned! {round((time.time() - StartTime) * 1000, 2)}ms")

def Select(TheList: list, Position: int, Thing):
    """An SQL-like select thing.
    
    TheList: List to search through.
    Position: The position to look in. Can be index or dict key
    Thing: What position has to be to be added to the return.
    """

    ReturnList = []

    #look through the list
    """
    for i in range(0, len(TheList)):
        if TheList[i][Position] == Thing:
            ReturnList.append(TheList[i])
    """

    for ThingL in TheList:
        if ThingL[Position] == Thing:
            ReturnList.append(ThingL)
    
    #make it tuple as less mem usage idk
    TheReturn = tuple(ReturnList)
    del ReturnList #so we dont wait for garbage collection????
    return TheReturn

def DropCachedLevel(LevelID : int) -> None:
    """Removes level from cache."""
    del LevelDLCache[LevelID]

def LevelInCache(LevelID) -> bool:
    """Checks if level is already in cache."""
    return LevelID in list(LevelDLCache.keys())

def CacheLevel(LevelID: int) -> bool:
    """Caches level file. Stores in dict if level not already in cache. Returns bool based on whether successful or not."""
    if not os.path.exists(f"Data/Levels/{LevelID}"):
        #it may be levelString
        mycursor.execute("SELECT levelString FROM levels WHERE levelID = %s LIMIT 1", (LevelID,))
        Level = mycursor.fetchone()
        if Level is None:
            return False
        if Level[0] == "":
            return False
        LevelFiles = Level[0]
    else:
        LevelFiles = open(f"Data/Levels/{LevelID}", "r").readlines()[0]
    #if level is already in we will just overwrite it. no need for checks
    LevelDLCache[LevelID] = LevelFiles
    #remove level if too long
    if len(LevelDLCache) > UserConfig["LevelCacheSize"]:
        LevelDLCache.pop(0)
    Log(f"Cached level {LevelID}.")
    return True

def GetLevelDL(LevelID: int) -> str:
    """Gets level file from cache or loads it."""
    if not LevelInCache(LevelID):
        CacheLevel(LevelID) #cache it if not cached
    return LevelDLCache[LevelID] 

def GetUserString(UID):
    """Returns user string."""
    mycursor.execute("SELECT userName, extID, userID FROM users WHERE userID = %s LIMIT 1", (UID,))
    User = mycursor.fetchone() #assume it exist
    return f"{User[2]}:{User[0]}:{User[1]}"

def DLLevel(request):
    """Returns a stored level."""

    LevelID = int(request.form["levelID"])
    Log(f"Getting level {LevelID}!")
    IsDaily = False
    FeaID = 0
    if LevelID == -1: #would make into dict switch-like statement but it would be slower
        mycursor.execute("SELECT levelID, feaID FROM dailyfeatures WHERE timestamp < %s AND type = 0 ORDER BY timestamp DESC LIMIT 1", (round(time.time()),))
        a=mycursor.fetchone()
        LevelID = a[0]
        FeaID = a[1]
        IsDaily = True
    elif LevelID == -2: #would make into dict switch-like statement but it would be slower
        mycursor.execute("SELECT levelID, feaID FROM dailyfeatures WHERE timestamp < %s AND type = 1 ORDER BY timestamp DESC LIMIT 1", (round(time.time()),))
        a=mycursor.fetchone()
        LevelID = a[0]
        FeaID = a[1]+100001
        IsDaily = True

    #getting the level
    mycursor.execute("SELECT * FROM levels WHERE levelID = %s LIMIT 1", (LevelID,))
    Level = mycursor.fetchall()
    if len(Level) == 0:
        return "-1"

    Level = Level[0]

    #bump the downloads
    Downloads = Level[22] + 1
    mycursor.execute("UPDATE levels SET downloads = %s WHERE levelID = %s", (Downloads, LevelID))
    mydb.commit()

    UpdateAgo = TimeAgoFromNow(Level[28])[:-4]
    UploadAgo = TimeAgoFromNow(Level[27])[:-4]

    Password = Level[10]
    PasswordXor = 0
    if Level[10] != 0:
        PasswordXor = base64.b64encode(Xor(Level[10], 26364).encode("ascii")).decode("ascii")

    LevelFiles = GetLevelDL(LevelID)
    
    if LevelFiles[0:3] == "kS1":
        LevelFiles = base64.b64encode(zlib.compress(LevelFiles)).decode("ascii")
        LevelFiles = LevelFiles.replace("/", "_")
        LevelFiles = LevelFiles.replace("+", "-")
    
    ReturnStr = JointStringBuilder({
        "1" : LevelID,
        "2" : Level[4],
        "3" : Level[5],
        "4" : LevelFiles,
        "5" : Level[6],
        "6" : Level[35],
        "8" : "10",
        "9" : Level[21],
        "10" : Downloads,
        "11" : "1",
        "12" : Level[8],
        "13" : Level[0],
        "14" : Level[23],
        "15" : Level[7],
        "17" : Level[24],
        "18" : Level[26],
        "19" : Level[31],
        "25" : Level[25],
        "27" : PasswordXor,
        "28" : UploadAgo,
        "29" : UpdateAgo,
        "30" : Level[11],
        "31" : "1",
        "42" : Level[33],
        "43" : Level[34],
        "45" : Level[14],
        "35" : Level[13],
        "36" : Level[17],
        "37" : Level[15],
        "38" : Level[30],
        "39" : Level[16],
        "46" : "1",
        "47" : "2",
        "48" : "1",
        "40" : Level[42]
    })

    ReturnStr += f"#{SoloGen(LevelFiles)}#"
    CoolString = f"{Level[35]},{Level[26]},{Level[24]},{LevelID},{Level[30]},{Level[31]},{Password},{FeaID}"
    ReturnStr += SoloGen2(CoolString) + "#"
    if not IsDaily:
        ReturnStr += CoolString
    else:
        ReturnStr += GetUserString(Level[35])
    Success(f"Served level {LevelID}!")
    return ReturnStr

def RemoveMessageHandler(request):
    """Handles message remove request."""
    AccountID = request.form["accountID"]

    if not VerifyGJP(AccountID, request.form["gjp"]):
        return "-1"
    # TODO: Finish

def ListToCommaString(TheList: list):
    """Converts a Python list to a comma separated string."""
    Res = ""
    for Elem in TheList:
        Res += f"{Elem},"
    return Res[:-1]

def GetFriendsList(AccountID: int):
    """Returns a list of account ids of the users friends."""
    mycursor.execute("SELECT accountID FROM friendreqs WHERE toAccountID = %s", (AccountID,))
    Friends = mycursor.fetchall()
    mycursor.execute("SELECT toAccountID FROM friendreqs WHERE accountID = %s", (AccountID,))
    Friends1 = mycursor.fetchall()
    FriendsRetrun = []

    for Friend in (Friends + Friends1):
        FriendsRetrun.append(Friend[0])
    return FriendsRetrun

def SendFriendReq(request):
    """Handles the send friend req action."""
    AccountID = request.form["accountID"]
    if not VerifyGJP(AccountID, request.form["gjp"]):
        return "-1"
    TargetAccountID = request.form["toAccountID"]
    Message = request.form["comment"]

    #stupid checks
    mycursor.execute("SELECT COUNT(*) FROM blocks WHERE (person1 = %s AND person2 = %s) OR (person1 = %s AND person2 = %s)", (AccountID, TargetAccountID, TargetAccountID, AccountID))
    if mycursor.fetchone()[0]:
        return "-1"
    mycursor.execute("SELECT COUNT(*) FROM friendships WHERE (person1=%s AND person2=%s) OR (person1=%s AND person2=%s)", (AccountID, TargetAccountID, TargetAccountID, AccountID))
    if mycursor.fetchone()[0]:
        return "-1"
    mycursor.execute("SELECT COUNT(*) FROM accounts WHERE accountID = %s AND frS = 1", (TargetAccountID,))
    if mycursor.fetchone()[0]:
        return "-1" 
    mycursor.execute("SELECT COUNT(*) FROM friendreqs WHERE (accountID = %s AND toAccountID = %s) OR (accountID = %s AND toAccountID = %s)", (AccountID, TargetAccountID, TargetAccountID, AccountID))
    if mycursor.fetchone()[0]:
        return "-1" 
    mycursor.execute("INSERT INTO friendreqs (accountID, toAccountID, comment, uploadDate) VALUES (%s, %s, %s, %s)", (AccountID, TargetAccountID, Message, round(time.time())))
    mydb.commit()
    return "1"

def DeleteFriendRequest(request):
    """Handles friend request deletion."""
    AccountID = request.form["accountID"]
    if not VerifyGJP(AccountID, request.form["gjp"]):
        return "-1"
    Target = request.form["targetAccountID"]
    mycursor.execute("DELETE FROM friendreqs WHERE accountID = %s AND toAccountID = %s", ((AccountID, Target),(Target, AccountID))[0 if int(request.form.get("isSender", 0)) else 1])
    mydb.commit()
    return "1"

def GetFriendReqList(request):
    """Handles the friend req list request by the client."""
    AccountID = request.form["accountID"]
    if not VerifyGJP(AccountID, request.form["gjp"]):
        return "-1"
    
    Offset = int(request.form["page"]) * 10
    GetSent = bool(int(request.form.get("getSent", 0))) #FOR THE MEME
    Col = "accountID" if GetSent else "toAccountID"

    mycursor.execute("SELECT * FROM friendreqs WHERE {} = %s LIMIT 10 OFFSET %s".format(Col), (AccountID, Offset)) #never format except when you trust the input 1000%
    FriendReqs = mycursor.fetchall()
    #check right here. dont bother wiht the count query if there
    if len(FriendReqs) == 0:
        return "-2" #lonely
    mycursor.execute("SELECT COUNT(*) FROM friendreqs WHERE {} = %s ".format(Col), (AccountID,))
    Count = mycursor.fetchone()[0]
    if not GetSent:
        #mark em as read
        # I HATE EVERYTHING ABOUT THIS... SUBQUERIES DONT WORK AS THIS REQUIRES LIMIT AND OFFSETEHIO GFNWERIGUOWLHRWEFQUEHJFGRWOIJGRWIG
        mycursor.execute(f"SELECT id FROM friendreqs WHERE {Col} = %s LIMIT 10 OFFSET %s", (AccountID, Offset))
        AList = ""
        for x in mycursor.fetchall():
            AList+=f"{x[0]},"
        mycursor.execute("UPDATE friendreqs SET isNew = 0 WHERE id in (%s)", (AList[:-1],))
        mydb.commit()
    ReturnStr = ""
    for Request in FriendReqs:
        mycursor.execute("SELECT userName, userID, icon, color1, color2, iconType, special, extID FROM users WHERE extID = %s LIMIT 1", (Request[1] if GetSent else Request[0],)) #TODO: turn these individual requests and turn them into 
        UserData = mycursor.fetchone()
        ReturnStr += JointStringBuilder({
            "1" : UserData[0],
            "2" : UserData[1],
            "9" : UserData[2],
            "10" : UserData[3],
            "11" : UserData[4],
            "14" : UserData[5],
            "15" : UserData[6],
            "16" : UserData[7],
            "32" : Request[4],
            "35" : Request[2],
            "37" : TimeAgoFromNow(Request[3])[:-4],
            "41" : Request[5]
        }) + "|"
    
    return f"{ReturnStr[:-1]}#{Count}:{Offset}:10"

# TODO: MOVE TO OWN FILE
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

def GetDaily(request):
    """Responds with a daily or weekly level. Using Cvolton's system."""
    Weekly = int(request.form.get("weekly", 0))
    Timestamp = round(time.time())
    mycursor.execute("SELECT levelID FROM dailyfeatures WHERE timestamp < %s AND type = %s ORDER BY timestamp DESC LIMIT 1", (Timestamp, Weekly))
    LevelID = mycursor.fetchone()
    if LevelID == None:
        Fail("No daily level set!")
        return "-1"
    LevelID = LevelID[0]

    #calculate time till level change
    TimeToChange = 0
    if not Weekly:
        #this is big brain time
        now = datetime.now()
        SecondsSinceMidnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() #calculate time since midnight
        TimeToChange = 86400 - SecondsSinceMidnight #substract for seconds in day to get time til next midnight
    else:
        DayToday = datetime.today().weekday()
        EndTime = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(days=7-DayToday) #new level every monday
        TimeToChange = time.mktime(EndTime.timetuple())
        LevelID += 100001 #idk what he was thinking either
    return f"{LevelID}|{round(TimeToChange)}"
