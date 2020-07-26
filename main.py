from flask import Flask, render_template, request, redirect, Blueprint, jsonify, session
from functions import *
from config import *
from console import *
import threading
from plugin import add_plugins
from plugins.gdpys.bridge import Bridge
from migrations import ImportGDPySDatabase
from constants import __version__

bridge = Bridge()
app = Flask(__name__)
APIBlueprint = Blueprint("api", __name__)
ToolBlueprint = Blueprint("tools", __name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = os.urandom(24).hex()

@app.route("/")
def Home():
    return redirect("/tools")

@app.route("/database///accounts/loginGJAccount.php", methods=["GET", "POST"])
@app.route("/database/accounts/loginGJAccount.php", methods=["GET", "POST"])
def LoginHandler():
    """Handles login requests"""
    Udid = request.form["udid"]
    Username = request.form["userName"]
    Password = request.form["password"]
    Log(f"{Username} attempts login...")
    bridge.login(Username)
    answer = LoginCheck(Udid, Username, Password, request)
    return answer

@app.route("/database///accounts/registerGJAccount.php", methods=["GET", "POST"])
@app.route("/database/accounts/registerGJAccount.php", methods=["GET", "POST"])
def RegisterHandler():
    bridge.register(request.form['userName'], FixUserInput(request.form["email"]))
    return RegisterFunction(request)


@app.route("/database///getGJUserInfo20.php", methods=["GET", "POST"])
@app.route("/database/getGJUserInfo20.php", methods=["GET", "POST"])
def GetUserData():
    Userdata = GetUserDataFunction(request)
    return Userdata

@app.route("/database///getGJAccountComments20.php", methods=["GET", "POST"])
@app.route("/database/getGJAccountComments20.php", methods=["GET", "POST"])
def AccountComments():
    Comments = GetAccComments(request)
    return Comments

@app.route("/database///uploadGJAccComment20.php", methods=["GET", "POST"])
@app.route("/database/uploadGJAccComment20.php", methods=["GET", "POST"])
def UploadAccComment():
    bridge.upload_account_comment(request.form["userName"], request.form["comment"])
    Result = InsertAccComment(request)
    return Result

@app.route("/database///updateGJAccSettings20.php", methods=["GET", "POST"])
@app.route("/database/updateGJAccSettings20.php", methods=["GET", "POST"])
def UpdateAccountSettings():
    return UpdateAccSettings(request)

@app.route("/database/updateGJUserScore22.php", methods=["GET", "POST"])
@app.route("/database///updateGJUserScore22.php", methods=["GET", "POST"])
#for older ver compatibillity i think
@app.route("/database/updateGJUserScore20.php", methods=["GET", "POST"])
@app.route("/database///updateGJUserScore20.php", methods=["GET", "POST"])
@app.route("/database/updateGJUserScore201php", methods=["GET", "POST"])
@app.route("/database///updateGJUserScore21.php", methods=["GET", "POST"])
def UpdateScore():
    return UpdateUserScore(request)

@app.route("/database///getGJScores20.php", methods=["GET", "POST"])
@app.route("/database/getGJScores20.php", methods=["GET", "POST"])
def GetScores():
    return GetLeaderboards(request)

@app.route("/database///requestUserAccess.php", methods=["GET", "POST"])
@app.route("/database/requestUserAccess.php", methods=["GET", "POST"])
def GetMod():
    bridge.request_mod(request.form["accountID"])
    return IsMod(request)

@app.route("/database///getGJRewards.php", methods=["GET", "POST"])
@app.route("/database/getGJRewards.php", methods=["GET", "POST"])
def GetRewards():
    return Rewards(request)

@app.route("/database///getAccountURL.php", methods=["GET", "POST"])
@app.route("/database/getAccountURL.php", methods=["GET", "POST"])
def GetAccUrl():
    return GetAccountUrl(request)

@app.route("//database/accounts/backupGJAccountNew.php", methods=["GET", "POST"])
@app.route("/database/accounts/backupGJAccountNew.php", methods=["GET", "POST"])
def SaveRoune():
    return SaveUserData(request)

#this is a bit of routes dont you think?
@app.route("//database/accounts/syncGJAccountNew.php", methods=["GET", "POST"])
@app.route("/database/accounts/syncGJAccountNew.php", methods=["GET", "POST"])
@app.route("//database/accounts/syncGJAccount20.php", methods=["GET", "POST"])
@app.route("/database/accounts/syncGJAccount20.php", methods=["GET", "POST"])
@app.route("//database/accounts/syncGJAccount.php", methods=["GET", "POST"])
@app.route("/database/accounts/syncGJAccount.php", methods=["GET", "POST"])
def LoadRoute():
    return LoadUserData(request)

@app.route("//database/likeGJItem211.php", methods=["GET", "POST"])
@app.route("/database/likeGJItem211.php", methods=["GET", "POST"])
def LikeRoute():
    bridge.like(bool(request.form["like"]))
    return LikeFunction(request)

@app.route("//database/uploadGJLevel21.php", methods=["GET", "POST"])
@app.route("/database/uploadGJLevel21.php", methods=["GET", "POST"])
def LevelUploadRoute():
    bridge.level_upload(request.form["userName"], request.form["levelID"])
    return UploadLevel(request)

@app.route("//database/getGJLevels21.php", methods=["GET", "POST"])
@app.route("/database/getGJLevels21.php", methods=["GET", "POST"])
def GetLevelsRoute():
    return GetLevels(request)

@app.route("//database/downloadGJLevel22.php", methods=["GET", "POST"])
@app.route("/database/downloadGJLevel22.php", methods=["GET", "POST"])
def DLLevelRoute():
    return DLLevel(request)

@app.route("//database/getGJSongInfo.php", methods=["GET", "POST"])
@app.route("/database/getGJSongInfo.php", methods=["GET", "POST"])
def SongRoute():
    return GetSong(request)

@app.route("//database/getGJComments21.php", methods=["GET", "POST"])
@app.route("/database/getGJComments21.php", methods=["GET", "POST"])
@app.route("/database/getGJCommentHistory.php", methods=["GET", "POST"])
def CommentGetRoute():
    return GetComments(request)

@app.route("//database/deleteGJAccComment20.php", methods=["GET", "POST"])
@app.route("/database/deleteGJAccComment20.php", methods=["GET", "POST"])
def DeleteAccCommentRoute():
    bridge.delete_account_comment(request.form["accountID"], request.form["commentID"])
    return DeleteAccComment(request)

@app.route("//database/uploadGJComment21.php", methods=["GET", "POST"])
@app.route("/database/uploadGJComment21.php", methods=["GET", "POST"])
def PostCommentRoute():
    bridge.upload_comment(request.form["userName"], request.form["comment"])
    return PostComment(request)

@app.route("//database/suggestGJStars20.php", methods=["GET", "POST"])
@app.route("/database/suggestGJStars20.php", methods=["GET", "POST"])
def LevelSuggestRoute():
    bridge.suggest_stars(request.form["levelID"], int(request.form["stars"]), request.form["feature"])
    return LevelSuggest(request)

@app.route("//database/uploadGJMessage20.php", methods=["GET", "POST"])
@app.route("/database/uploadGJMessage20.php", methods=["GET", "POST"])
def PostMessageRoute():
    return MessagePost(request)

@app.route("//database/getGJUsers20.php", methods=["GET", "POST"])
@app.route("/database/getGJUsers20.php", methods=["GET", "POST"])
def UserSearchRoute():
    return UserSearchHandler(request)

@app.route("//database/getGJMessages20.php", methods=["GET", "POST"])
@app.route("/database/getGJMessages20.php", methods=["GET", "POST"])
def GetMessagesRoute():
    return GetMessages(request)

@app.route("//database/downloadGJMessage20.php", methods=["GET", "POST"])
@app.route("/database/downloadGJMessage20.php", methods=["GET", "POST"])
def DownloadMessageRoute():
    return GetMessage(request)

@app.route("/database/deleteGJComment20.php", methods=["GET", "POST"])
def DeleteCommentRoute():
    bridge.delete_comment(request.form["accountID"], request.form["commentID"])
    return DeleteCommentHandler(request)

@app.route("/database/getGJMapPacks21.php", methods=["GET", "POST"])
def GetMapPacksRoute():
    return MapPackHandelr(request)

@app.route("/database/getGJGauntlets21.php", methods=["GET", "POST"])
def GauntletRoute():
    return GetGauntletsHandler()

@app.route("/database/getGJLevelScores211.php", methods=["GET", "POST"])
def LevelLBsRoute():
    return ScoreSubmitHandler(request)

@app.route("/database/uploadFriendRequest20.php", methods=["GET", "POST"])
def FriendReqRoute():
    bridge.send_friend_request(request.form["accountID"], request.form["toAccountID"], request.form["comment"])
    return SendFriendReq(request)

@app.route("/database/deleteGJFriendRequests20.php", methods=["GET", "POST"])
def DeleteFriendReqRoute():
    return DeleteFriendRequest(request)

@app.route("/database/getGJFriendRequests20.php", methods=["GET", "POST"])
def GetFriendReqRoute():
    return GetFriendReqList(request)

@app.route("/database/getGJDailyLevel.php", methods=["GET", "POST"])
def GetDailyRoute():
    return GetDaily(request)

##API ROUTES##
@APIBlueprint.route("/getlevel/<LevelID>")
def APILevelRount(LevelID):
    return jsonify(APIGetLevel(LevelID))

@app.route("/database/")
def DatabaseRoute():
    Log("Someone just got ricked!")
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

@app.errorhandler(500)
def BadCodeError(error):
    return "-1"

@APIBlueprint.errorhandler(500)
def APIBadCodeError(error):
    return jsonify({
        "status" : 500,
        "message" : "An internal server error has occured! Please report this to the owner or developer."
    })

@APIBlueprint.errorhandler(404)
def APINotFoundError(error):
    return jsonify({
        "status" : 404,
        "message" : "What you're looking for is not here."
    })
###########TOOLS
# TODO : Make separate file
ExampleSession = {
    "AccountID" : 0,
    "Username" : "",
    "Privileges" : 3,
    "LoggedIn" : False
}

def SetSession(NewSession: dict) -> None:
    """Sets the session to something new."""
    session.clear()
    for a in list(NewSession.keys()):
        session[a] = NewSession[a]

#fill session
@ToolBlueprint.before_request
def BeforeRequest(): 
    if "LoggedIn" not in list(dict(session).keys()): #we checking if the session doesnt already exist
        for x in list(ExampleSession.keys()):
            session[x] = ExampleSession[x]

@ToolBlueprint.route("/")
def HomeToolRoute():
    return render_template("home.html", session=session, title = "Home", ver=__version__)

@ToolBlueprint.route("/login", methods=["GET", "POST"])
def ToolsLoginRoute():
    if request.method == "GET":
        return render_template("login.html", session=session, title = "Login")
    #POST REQUEST
    A = ToolLoginCheck(request)
    if not A[0]: #login failed
        return render_template("login.html", session=session, title = "Login", BadAlert=A[1])
    #login success
    SetSession(A[1])
    return redirect("/")

@ToolBlueprint.errorhandler(500)
def Tool500():
    return render_template("500.html", session=session, title = "Code Broke")

@ToolBlueprint.errorhandler(404)
def Tool404():
    return render_template("404.html", session=session, title = "Page Missing")

app.register_blueprint(APIBlueprint, url_prefix='/api')
app.register_blueprint(ToolBlueprint, url_prefix='/tools')

if __name__ == "__main__":
    # this does not need to be logged as it should be on stdout
    print(rf"""{Fore.BLUE}   _____ _____  _____        _____ 
  / ____|  __ \|  __ \      / ____|
 | |  __| |  | | |__) |   _| (___
 | | |_ | |  | |  ___/ | | |\___ \
 | |__| | |__| | |   | |_| |____) |
  \_____|_____/|_|    \__, |_____/
                       __/ |
                      |___/
 {Fore.MAGENTA}Created by RealistikDash{Fore.RESET}
    """)
    add_plugins()
    bridge.ready()
    threading.Thread(target=CronThread).start()
    app.run("0.0.0.0", port=UserConfig["Port"])