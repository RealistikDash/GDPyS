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
    if len(seed) != 10 or seed.isnumeric():
        return False
    
    # All checks passed.
    return True

def verify_textbox(text: str, extra_chars: tuple = ()) -> bool:
    """Verifies if textbox entry contains allowed characters to prevent the
    user entering bad characters.
    
    Args:
        text (str): The input to verify the characters of.
        extra_chars (tuple): Additional characters in case of spacial fields.
    """

    # Check if the length isn't absurd
    if len(text) > 32: return False

    # We iterate through every character in the `text`
    # and check if its in the allowed chars.
    for char in list(text):
        if char not in ALLOWED_CHARS + extra_chars:
            return False
    
    return True

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
