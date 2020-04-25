from flask import Flask, render_template, request
from functions import *
from config import *
from console import *

app = Flask(__name__)

@app.route("/database///accounts/loginGJAccount.php", methods=["GET", "POST"])
@app.route("/database/accounts/loginGJAccount.php", methods=["GET", "POST"])
def LoginHandler():
    """Handles login requests"""
    Udid = request.form["udid"]
    Username = request.form["userName"]
    Password = request.form["password"]
    Log(f"{Username} attempts login...")
    answer = LoginCheck(Udid, Username, Password, request)
    return answer

@app.route("/database///accounts/registerGJAccount.php", methods=["GET", "POST"])
@app.route("/database/accounts/registerGJAccount.php", methods=["GET", "POST"])
def RegisterHandler():
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
    print(Comments)
    return Comments # fix later

@app.route("/database///uploadGJAccComment20.php", methods=["GET", "POST"])
@app.route("/database/uploadGJAccComment20.php", methods=["GET", "POST"])
def UploadAccComment():
    Result = InsertAccComment(request)
    return Result

@app.route("/database///updateGJAccSettings20.php", methods=["GET", "POST"])
@app.route("/database/updateGJAccSettings20.php", methods=["GET", "POST"])
def UpdateAccountSettings():
    return UpdateAccSettings(request)

@app.errorhandler(500)
def BadCodeError(error):
    return "-1"

if __name__ == "__main__":
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
    app.run("0.0.0.0", port=UserConfig["Port"])