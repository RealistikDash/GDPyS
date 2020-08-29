import bcrypt
import base64
import hashlib
import string
import random

def hash_sha1(text: str) -> str:
    """Hashes text in SHA1."""
    return hashlib.sha1(text.encode()).hexdigest()

def base64decode(text: str) -> str:
    """Decodes base64."""
    return base64.b64decode(text.encode()).decode()

def base64encode(text: str) -> str:
    """Encodes base64."""
    return base64.b64encode(text.encode()).decode()

def hash_bcrypt(text: str) -> str:
    """Hashes text using bcrypt."""
    return bcrypt.hashpw(text.encode("utf-8"), bcrypt.gensalt(10)).decode()

def compare_bcrypt(text1: str, text2: str) -> bool:
    """Compares two strings using bcrypt."""
    check : bool = False
    try:
        check = bcrypt.checkpw(text1.encode(), text2.encode())
    except ValueError:
        pass
    return check

def random_string(length = 8):
    """Generates a random string made of upper and lower case ascii characters of given length."""
    return "".join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for i in range(length))
