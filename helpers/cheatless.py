from helpers.userhelper import user_helper
from helpers.levelhelper import level_helper
from config import user_config
from helpers.bot import gdpysbot

def CheatlessScoreCheck(score: dict) -> bool:
    """Runs a score validity verification."""
    # score example
    {
        "accountid" : 1,
        "levelid" : 222,
        "percentage" : 100,
        "attempts" : 10,
        "coins" : 0
    }
    if user_config["cheatless"]["enabled"]:
        if score["percentage"] > 100:
            cheatless_ban(score["AccountID"], "invalid level score submission")
            return False
        elif score["percentage"] == 100:
            print(f"Running score check on a score on the level {score['levelid']}")
            level_data = level_helper.get_level_obj(score["levelid"])

            if level_data == None:
                cheatless_ban(score["AccountID"], "invalid level score submission")
                return False
            
            if score["coins"] > level_data[4]:
                cheatless_ban(score["AccountID"], "unachievable coin count")
                return False

            if level_data[1] == 10 and level_data[2] == 6 and score["attempts"] < user_config["cheatless"]["minimum_attempts_extreme_demon"]:
                cheatless_ban(score["AccountID"], "too quick demon completion")
                return False
            
            if score["attempts"] < 0 or score["coins"] > 3 or score["coins"] < 0:
                cheatless_ban(score["accountid"], "invalid level score data")
                return False

        else:
            if score["coins"] > 0:
                cheatless_ban(score["AccountID"], "coins on uncompleted level")
                return False
        
    return True

def cheatless_ban(accountid: int, offence: str):
    """Initiates and official CheatlessAC ban!"""
    print(f"User {accountid} has been banned by CheatlessAC for {offence}.") # TODO: add lang
    gdpysbot.send_message(accountid, "[CheatlessAC] You have been banned!", 
    f"You have been by the Cheatless AntiCheat! The reason for your ban is {offence}. Please contact the staff team for more info."
    )
    #user_helper.ban_user(accountid, offence) # this function does not exist yet