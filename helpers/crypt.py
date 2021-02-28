# Common encryption/hashing related functions within GDPyS.
from itertools import cycle
from const import XorKeys
import hashlib
import bcrypt
import base64
import random
import string

def base64_encode(text: str) -> str:
    """Encodes the param `text` using url safe Base64.
    
    Args:
        text (str): The text that is to be encoded using Base64.
    
    Returns:
        Base64 encoded string.
    """

    # This is simply a wrapper around base64 functions.
    return base64.urlsafe_b64encode(text.encode()).decode()

def base64_decode(text: str) -> str:
    """Decodes param `text` from Base64 to regular string.
    
    Args:
        text (str): A Base64 encoded string.
    
    Return:
        Decoded string of the contents of the base64 encoded string.
    """

    return base64.urlsafe_b64decode(text.encode()).decode()

def bcrypt_hash(passw: str, difficulty: int = 10) -> str:
    """Hashes the pasword `passw` using the BCrypt hashing algorhythm.

    Args:
        passw (str): The password that is supposed to be hashed.
        difficulty (int): The amount of times the password should be salted
            (higher is more secure but slower).
    
    Returns:
        A string of the BCript hashed passwd.
    """

    return bcrypt.hashpw(
        passw.encode(),
        bcrypt.gensalt(difficulty)
    ).decode()

def bcrypt_check(plain_pass: str, bcrypt_pass: str) -> bool:
    """Compares a plain text password `plain_pass` to the BCrypt hashed
    password `bcrypt_pass`.
    
    Args:
        plain_pass (str): The plain text password to be compared to the BCrypt
            hashed one.
        bcrypt_pass (str): The BCrypt hashed password to be checked against
            the plain text one.
    
    Returns:
        Bool relating to whether the passwords
            match or not.
    """

    # This will be placed within a try statement as
    # non-bcryptable values will cause errors here
    # and we want that to count as auth failures.
    try:
        return bcrypt.checkpw(
            plain_pass.encode(),
            bcrypt_pass.encode()
        )
    # Bad bcrypt_pass would raise ValueError
    except ValueError:
        return False

def xor_cipher(text: str, key: int) -> str:
    """Encrypts the string `text` using the XOR cipher with the key `key`.
    
    Args:
        text (str): The text that is to be encrypted using the XOR cipher.
        key (int): The key to be used within the encryption process.
    
    Returns:
        An XOR encoded string of param `text` using the key `key`.
    """

    return "".join(chr(ord(x) ^ ord(y)) for (x, y) in zip(str(text), cycle(str(key))))

def gjp_decode(gjp: str) -> str:
    """Decodes the string `gjp` encoded using the "Geometry Jump Password"
    encryption method.

    Args:
        gjp (str): The Geometry Jump Password encoded string to be decoded.
    
    Returns:
        A decoded GJP string.
    """

    return xor_cipher(
        base64_decode(gjp),
        XorKeys.GJP
    )

def string_random(length: int = 8) -> str:
    """Generates a completely random string with the length of `length`.

    Note:
        The string generated will only contain ASCII upper case and lower case
            characters.
    
    Args:
        length (int): The length of the string to be generated.
    
    Returns:
        A randomly generated string.
    """

    return "".join(
        random.choice(string.ascii_lowercase + string.ascii_uppercase)
        for i in range(length)
    )
