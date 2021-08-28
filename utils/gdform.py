from const import GDCol
from typing import List, Dict, Union

def gd_dict_str(d: Dict[int, str], separator: str = ":") -> str:
    """Converts the dict `d` into a Geometry Dash-styled HTTP response.
    
    Args:
        d (dict): A dictionary of keys to convert. Should be in the format 
            key int: str`.
        separator (str): The character to separate all elements of the dict.
    
    Returns:
        Returns a string from the dict in the format `1:aaa:2:b`
    """
    
    a = [str(arg[i]) for arg in d.items() for i in (0, 1)]
    
    # Combine them all and send off.
    return separator.join(a)

def parse_to_dict(data: str, separator: str = "~|~") -> dict:
    """Parses a GeometryDash style keyed split response into an easy to work
    with Python dictionary object.
    
    Args:
        data (str): The data to be parsed into a dict.
    """

    # Bit ugly but reduces function calls and var alloc    
    return {
        key: val for key, val in zip(*[iter(
            data.split(separator)
        )] * 2)
    }


def col_tag(text: str, col: GDCol) -> str:
    """Formats the text using the Geometry Dash colour tags.
    
    Args:
        text (str): The text to be coloured through tags.
        col (GDCol): The Geometry Dash colour to wrap the text around with.
    
    Returns:
        Col formatted str.
    """

    return f"<c{col}>{text}</c>"

def tempban_instant(*text) -> str:
    """Formats a message to be in the format of a temporary comment ban with
    an instant finish time.

    Note:
        The text MAY NOT CONTAIN `_`. This is because it is used as a
            formatting character in this context, meaning it would absolutely
            mess up the response.
    
    Args:
        *text (str): Text elements to be merged separated by a space.
    
    Returns:
        A comment ban styled string similar to `temp_0_<text>`.
    """

    # Merge into single str.
    text_str = " ".join(text)
    return tempban(text_str, 0)
    
def tempban(reason: str, duration_left: int) -> str:
    """Builds a server response in the structure of a comment ban.
    
    Note:
        The text MAY NOT CONTAIN `_`. This is because it is used as a
            formatting character in this context, meaning it would absolutely
            mess up the response.
    
    Args:
        reason (str): The plaintext reason for the comment ban that will be
            displayed to the user.
        duration_left (int): The time left till the end of the user's comment
            ban.

    Returns:
        A comment ban styled string similar to `temp_0_<text>`.
    """

    # Invalid contents would mess this up big time.
    if "_" in reason:
        raise ValueError(
            "Comment ban contents may not include the underscore character!"
        )
    
    return f"temp_{duration_left}_{reason}"
