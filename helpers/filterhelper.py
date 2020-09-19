USERNAME_ALLOWED_CHARS = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
USERNAME_CHAR_LIMIT = 16

def check_username(username: str) -> bool:
    """Checks if a given username can be made inside GD."""
    username = list(username) #easier to analyse

    if len(username) > USERNAME_CHAR_LIMIT:
        return False

    for char in username:
        if char not in USERNAME_ALLOWED_CHARS:
            return False
    
    return True
