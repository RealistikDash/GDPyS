from const import GDCol
from typing import List, Dict, Union

def gd_builder(resp: List[Union[dict, str]], separator: str = "#") -> str:
    """Builds a Geometry Dash-styled response string out of
    the list `resp`.

    Note:
        Currently, the only object types to be supported within
            the builder list `resp` are dictionaries and strings.

    Args:
        resp (list): A list of objects to be converted into
            a response string. These objects will be parsed.
        separator (str): The character separating each sector
            of the response.
    
    Returns:
        A Geometry Dash response string. Each parsed list element
            is separated by a `separator` and follows the GD
            protocol.
    
    """

    # All parts of responses will be stored here.
    final_resp = []

    # Iterate through all resp sectors.
    for s in resp:
        # Check its type.
        typ = type(s)

        # Dict for handlers of all types. We are doing a budget switch statement.
        builder = {
            dict: gd_dict_str,
            str: str, # Doing this so it fits well in the system,
            int: str # Need this so we can work with them as strs.
        }.get(typ)

        # If none, give an error.
        if builder is None:
            raise ValueError(f"Building to str from type {typ} is not allowed!")

        # execute the builder and immidately add it to final resp.
        final_resp.append(
            builder(s)
        )

    # Combine all sectors, dividing them all by #
    return separator.join(final_resp)

def gd_dict_str(d: Dict[int, str], separator: str = ":") -> str:
    """Converts the dict `d` into a Geometry Dash-styled HTTP response.
    
    Args:
        d (dict): A dictionary of keys to convert. Should be in the format 
            key int: str`.
        separator (str): The character to separate all elements of the dict.
    
    Returns:
        Returns a string from the dict in the format `1:aaa:2:b`
    """

    # Idk how to make this efficient so here goes nothing.
    a = []

    # Iterate through all and add them to a list.
    for key, val in d.items():
        a += [key, val]
    
    # Combine them all and send off.
    return separator.join(str(i) for i in a)

def parse_to_dict(data: str, separator: str = "~|~") -> dict:
    """Parses a GeometryDash style keyed split response into an easy to work
    with Python dictionary object.
    
    Args:
        data (str): The data to be parsed into a dict.
    """

    # Create the dict we will be making
    resp = {}

    # Split the data by separator.
    d_s = data.split(separator)

    # Iterate every two.
    for key, val in zip(*[iter(d_s)] * 2):
        resp[int(key)] = val
    
    return resp


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
