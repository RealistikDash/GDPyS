class XorKeys():
    password = 37526
    chk = 19847
    level_password = 26364
    quests = 19847
    chests = 59182

class Permissions():
    authenticate = 2<<0
    upload_level = 2<<1
    post_comment = 2<<2
    post_acc_comment = 2<<3
    mod_regular = 2<<6
    mod_elder = 2<<7

class Secrets():
    """All the GeometryDash secret values"""
    normal = "Wmfd2893gb7"

class ResponseCodes():
    """All the web response codes."""
    generic_fail = "-1"
    generic_success = "1"
    generic_fail2 = "-2"
    login_contact_rob = "-12"
    empty_list = "#0:0:0"

class Colours():
    """ALL THE COLOURS IN THE SKY"""
    reset = u"\u001b[0m"
    red = u"\u001b[31m"
    black = u"\u001b[30m"
    green = u"\u001b[32m"
    yellow = u"\u001b[33m"
    blue = u"\u001b[34m"
    magenta = u"\u001b[35m"
    cyan = u"\u001b[36m"
    white = u"\u001b[37m"
    all_col = [red, green, yellow, blue, magenta, cyan, white]
