import mysql.connector
from config import *
from console import *
import time
import timeago

try:
    mydb = mysql.connector.connect(
        host=UserConfig["SQLHost"],
        user=UserConfig["SQLUser"],
        passwd=UserConfig["SQLPassword"],
        database=UserConfig['SQLDatabase']
    ) #connects to database
    print(f"{Fore.GREEN} Successfully connected to MySQL!")
except Exception as e:
    print(f"{Fore.RED} Failed connecting to MySQL! Aborting!\n Error: {e}{Fore.RESET}")
    exit()

mycursor = mydb.cursor() #creates a thing to allow us to run mysql commands

def VerifyGJP(AccountID: int, GJP: str):
    """Returns true if GJP is correct."""
    #NOT DONE YET!!!!!!
    return True

def FixUserInput(String):
    """Gets rid of potentially problematic user input."""
    String = String.replace("\0", "")
    String = String.replace("#", "")
    String = String.replace("|", "")
    String = String.replace("#", "")
    String = String.replace(":", "")
    String = String.replace("--", "")
    return String


def LoginCheck(Udid, Username, Password, request):
    """Checks login and password"""
    Username = FixUserInput(Username)
    mycursor.execute("SELECT accountID FROM accounts WHERE userName LIKE %s", (Username,))
    Accounts = mycursor.fetchall()
    if len(Accounts) == 0:
        #no accounts found
        Fail(f"Account {Username} not found!")
        return "-1" #idk the error codes
    AccountID = Accounts[0][0] #choosing the closes one

    #User ID
    mycursor.execute("SELECT userID FROM users WHERE extID = %s", (AccountID,))
    UserID = mycursor.fetchall()
    if len(UserID) == 0:
        TheIP = request.remote_addr
        mycursor.execute("INSERT INTO users (isRegistered, extID, userName, IP) VALUES (1, %s, %s, %s)", (AccountID, Username, TheIP))
        mydb.commit()
        #fetch again br uh
        mycursor.execute("SELECT userID FROM users WHERE extID = %s", (AccountID,))
        UserID = mycursor.fetchall()

    UserID = UserID[0][0]

    #insert password check here
    Success(f"Authentication for {Username} was successfull!")
    return f"{AccountID},{UserID}"

def HashPassword(PlainPassword: str):
    """Creates a hashed password to be used in database."""
    return PlainPassword #for now no hashing

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
    return 0

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
    #gets messages and friend requests (thanks cvolton again)
    if TargetAccid == FromAccid: #its the user checking themselves out
        FriendState = 0
        mycursor.execute("SELECT count(*) FROM friendreqs WHERE toAccountID = %s", (TargetAccid,))
        FreindReqs = mycursor.fetchall()[0]
        mycursor.execute("SELECT count(*) FROM messages WHERE toAccountID = %s AND isNew=0", (TargetAccid,))
        NewMessages = mycursor.fetchall()[0]
        mycursor.execute("SELECT count(*) FROM friendships WHERE (person1 = %s AND isNew2 = '1') OR  (person2 = %s AND isNew1 = '1')", (FromAccid, FromAccid,))
        NewFirends = mycursor.fetchall()[0]
        Append = f":38:{NewMessages}:39:{FreindReqs}:40:{NewFirends}"
    else:
        FriendState = 0
        Append = ""
        #check for incoming reqs
        mycursor.execute("SELECT count(*) FROM friendships WHERE (person1 = %s AND person2 = %s) OR (person2 = %s AND person1 = %s)", (TargetAccid, FromAccid, FromAccid, TargetAccid))
        if len(mycursor.fetchall()) > 0:
            FriendState = 1
        else:
            mycursor.execute("SELECT ID, comment, uploadDate FROM friendreqs WHERE accountID = %s AND toAccountID = %s", (TargetAccid, FromAccid))
            IncomingReq = len(mycursor.fetchall())
            if IncomingReq != 0:
                FriendState = 3
            else: #so other queries arent ran if we already found it
                #outgoing reqs
                mycursor.execute("SELECT ID, comment, uploadDate FROM friendreqs WHERE accountID = %s AND toAccountID = %s", (FromAccid, TargetAccid))
                IncomingReq = len(mycursor.fetchall())
                if IncomingReq != 0:
                    FriendState = 4

    mycursor.execute("SELECT * FROM users WHERE extID = %s LIMIT 1", (TargetAccid,))
    Userdata = mycursor.fetchall()[0]
    mycursor.execute("SELECT youtubeurl, twitter, twitch, frS, mS, cS FROM accounts WHERE accountID = %s LIMIT 1", (TargetAccid,))
    ExtraData = mycursor.fetchall()[0]
    Rank = GetRank(TargetAccid)
    #AAAAAAAA WHY DIDNT ROBTOP USE JSON
    #refrence taken from php gdps (thanks cvolton)
    TheStupidString = f"1:{Userdata[3]}:2:{Userdata[1]}:13:{Userdata[10]}:17:{Userdata[11]}:10:{Userdata[7]}:11:{Userdata[8]}:3:{Userdata[4]}:46:{Userdata[25]}:4:{Userdata[5]}:8:{Userdata[22]}:18:{ExtraData[4]}:19:{ExtraData[3]}:50:{ExtraData[5]}:20:{ExtraData[0]}:21:{Userdata[15]}:22:{Userdata[16]}:23:{Userdata[17]}:24:{Userdata[18]}:25:{Userdata[19]}:26:{Userdata[20]}:28:{Userdata[21]}:43:{Userdata[28]}:47:{Userdata[29]}:30:{Rank}:16:{Userdata[2]}:31:{FriendState}:44:{ExtraData[1]}:45:{ExtraData[2]}:29:1:49:0{Append}"
    Success(f"Got user data for {Userdata[3]} successfully!A")
    return TheStupidString

def Base64Encode(Text):
    return Text.encode("base64".strip())

def AIDToUID(AccountID: int):
    """Gets user ID from Account ID."""
    mycursor.execute("SELECT userID FROM users WHERE extID = %s LIMIT 1", (AccountID,))
    Thing = mycursor.fetchall()
    if len(Thing) == 0:
        return None
    return Thing[0][0]

def TimeAgoFromNow(Timestamp):
    """Returns a string of how long ago from now was a timestamp."""
    Time = datetime.fromtimestamp(Timestamp)
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
    
    CommentStr = ""
    for comment in UserComments:
        CommentStr += f"2~{comment[0]}~3~{comment[1]}~4~{comment[2]}~5~0~7~{comment[3]}~9~{TimeAgoFromNow(comment[5])}~6~{comment[4]}|"

    Success(f"Successfully got account comments for {TargetAccid}!")

    return CommentStr[:-1]

def InsertAccComment(request):
    """Adds an account comment."""
    Username = request.form["userName"]
    CommentContent = request.form["comment"]
    AccountID = request.form["accountID"]
    if not VerifyGJP(AccountID, request.form["gjp"]):
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
    #big boy query coming up....
    mycursor.execute(
        "UPDATE users SET stars = %s, diamonds = %s, color1 = %s, color2 = %s, iconType = %s, special = %s, accIcon = %s, accShip = %s, accBall = %s, accBird = %s, accDart = %s, accRobot = %s, accGlow = %s, accSpider = %s, accExplosion = %s, gameVersion = %s, secret = %s, coins=%s, userCoins = %s WHERE userID = %s LIMIT 1",
        (DataDict["stars"], DataDict["diamonds"], DataDict["color1"], DataDict["color2"], DataDict["iconType"], DataDict["special"], DataDict["accIcon"], DataDict["accShip"], DataDict["accBall"], DataDict["accBird"], DataDict["accDart"], DataDict["accRobot"], DataDict["accGlow"], DataDict["accSpider"], DataDict["accExplosion"], DataDict["gameVersion"], DataDict["secret"], DataDict["coins"], DataDict["userCoins"], UserID)
        )
    mydb.commit()
    Success(f"Successfully updated the user profile for {request.form['userName']}!")
    return "1"

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
    print(ReturnStr)
    Success("Leaderboards served!")
    return ReturnStr[:-1]

def IsMod(request):
    """Returns whether the user is a mod (has badge)."""
    Log(f"User {request.form['accountID']} is checking mod status.")
    if not VerifyGJP(request.form["accountID"], request.form["gjp"]):
        return "-1"
    #checking if user has role assigned
    mycursor.execute("SELECT roleID FROM roleassign WHERE accountID = %s", (request.form["accountID"],))
    Role = mycursor.fetchall()
    if len(Role) == 0:
        return "-1" #no role assigned, byebye
    Role = Role[0][0]
    #now we get the role badge
    mycursor.execute("SELECT actionRequestMod FROM roles WHERE roleID = %s", (Role,))
    BadgePriv = mycursor.fetchall()
    if len(BadgePriv) == 0:
        return "-1" #role not found
    BadgePriv = BadgePriv[0][0]
    if BadgePriv == 0:
        Success(f"User {request.form['accountID']} mod check fail!")
        return "-1"
    Success(f"User {request.form['accountID']} mod check success!")
    return str(BadgePriv)