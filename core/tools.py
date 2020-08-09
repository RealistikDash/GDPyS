from functions import AIDToUID, CheckBcryptPw, HasPrivilege, mycursor
from constants import *

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