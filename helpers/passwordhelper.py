import bcrypt
import string
import random

def CreateBcrypt(Password: str):
    """Creates hashed password."""
    BHashed = bcrypt.hashpw(Password.encode("utf-8"), bcrypt.gensalt(10))
    return BHashed.decode()

def RandomString(Lenght=8):
    Chars = string.ascii_lowercase
    return ''.join(random.choice(Chars) for i in range(Lenght))

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
        return False

    return check
