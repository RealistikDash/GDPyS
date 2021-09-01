# This helper is used for verifying some of the post
# args sent by some endpoints. To keep the handlers
# clean, these will be kept here.
from const import GDCol

# Local constants
ALLOWED_CHARS = list("abcdefghijklmnopqrstuvwxyz0123456789 ")

def verify_stats_seed(seed: str) -> bool:
    """Verifies if the seed sent in the `seed` post argument of the request is
    valid by performing several checks on it.
    
    Args:
        seed (str): The seed passed by Geometry Dash as part of the request.
    
    Returns:
        True if valid, else False.
    """

    # Currently, all I know is that this is a completely
    # random string that's 10 chars long.
    return not (len(seed) != 10 or seed.isnumeric())

def verify_textbox(text: str, extra_chars: list = [], char_count: int = 32) -> bool:
    """Verifies if textbox entry contains allowed characters to prevent the
    user entering bad characters.
    
    Args:
        text (str): The input to verify the characters of.
        extra_chars (list): Additional characters in case of spacial fields.
        char_count (int): The maximum size of the content.
    """
    
    return all(char in ALLOWED_CHARS + extra_chars for char in text) \
        and len(text) < char_count

ALLOWED_CHARS_COM = list("!@#$%^&*()-_=+\|~`")
def verify_comment(text: str) -> bool:
    """Verifies if the text provided in the comment is fully valid."""

    return verify_textbox(text, ALLOWED_CHARS_COM, 256)

def close_col_tags(text: str) -> str:
    """Fixes all unclosed colour tags, which are known to cause crashes in
    Geometry Dash.
    
    Args:
        text (str): The text to fix the tag closing for.
    
    Returns:
        A safe version of the text.
    """

    while text.count("<c") > text.count("</c>"):
        text += "</c>"

def remove_col_tags(text: str) -> str:
    """Removes all colour tags from the message. These tags are known to cause
    crashes in-game.
    
    Args:
        text (str): The text to fix the tag closing for.
    
    Returns:
        A safe version of the text.
    """

    for tag in GDCol.ALL:
        text.replace(f"<c{tag}>", "")
    
    text.replace("</c>", "")

    return text
