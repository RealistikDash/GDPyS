import bcrypt
import base64
import hashlib
import string
import random
from itertools import cycle
from constants import XorKeys, CryptKeys
import logging


def hash_sha1(text: str) -> str:
    """Hashes text in SHA1."""
    return hashlib.sha1(text.encode()).hexdigest()


def decode_base64(text: str) -> str:
    """Decodes base64."""
    return base64.b64decode(text.encode()).decode()


def encode_base64(text: str) -> str:
    """Encodes base64."""
    return base64.b64encode(text.encode()).decode()


def hash_bcrypt(text: str) -> str:
    """Hashes text using bcrypt."""
    return bcrypt.hashpw(text.encode("utf-8"), bcrypt.gensalt(10)).decode()


def compare_bcrypt(text1: str, text2: str) -> bool:
    """Compares two strings using bcrypt.
    text1: Plain password
    text2: hashed password"""
    check: bool = False
    try:
        check = bcrypt.checkpw(text1.encode(), text2.encode())
    except ValueError:
        pass
    return check


def generate_random_string(length=8):
    """Generates a random string made of upper and lower case ascii characters of given length."""
    return "".join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for i in range(length))


def cipher_xor(data: str, key: str):
    xor = "".join(chr(ord(x) ^ ord(y))
                  for (x, y) in zip(str(data), cycle(str(key))))
    return xor


def decode_gjp(text: str) -> str:
    """Decodes GJP (Geometry Dash's password encryption method) and returns in plaintext."""
    return cipher_xor(decode_base64(text), XorKeys.password)


def encode_chk(text: str) -> str:
    """Encodes a Geometry Dash chunk."""
    return cipher_xor(encode_base64(text[5:]), XorKeys.chk)


def decode_chk(text: str) -> str:
    """Decodes a GD chunk."""
    return cipher_xor(decode_base64(text[5:]), XorKeys.chk)


def solo_gen3(string: str):
    """Port of genSolo3 from Cvolton's GMDPrivateServer."""
    return hash_sha1(string + CryptKeys.solo3)
