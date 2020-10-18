USERNAME_ALLOWED_CHARS = list(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
)
USERNAME_CHAR_LIMIT = 16

COMMENT_CHAR_LIMIT = 100
COMMENT_ALLOWED_CHARS = list(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-/ "
)


def check_username(username: str) -> bool:
    """Checks if a given username can be made inside GD."""
    username = list(username)  # easier to analyse

    if len(username) > USERNAME_CHAR_LIMIT:
        return False

    for char in username:
        if char not in USERNAME_ALLOWED_CHARS:
            return False

    return True


def check_comment(comment: str) -> bool:
    """Checks if a given comment can be legitemately made inside GD."""
    comment = list(comment)  # easier to analyse

    if len(comment) > COMMENT_CHAR_LIMIT:
        return False

    for char in comment:
        if char not in COMMENT_ALLOWED_CHARS:
            return False

    return True
