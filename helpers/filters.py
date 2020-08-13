username_allowed_chars = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_- ")
max_username_len = 22

def check_username(username: str) -> bool:
    """Checks if a given username can be made inside GD."""
    username = list(username) #easier to analyse

    if len(username) > max_username_len:
        return False

    for char in username:
        if char not in username_allowed_chars:
            return False
    
    return True