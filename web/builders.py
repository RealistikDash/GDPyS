# Extremely simple response builder.
from typing import List, Dict

def gd_builder(resp: List[dict, str], separator: str = "#") -> str:
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
    """Converts the dict `d` into a Geometry Dash-styled HTTP
    response.
    
    Args:
        d (dict): A dictionary of keys to convert. Should be in
            the format `key int: str`.
        separator (str): The character to separate all elements of
            the dict.
    
    Returns:
        Returns a string from the dict in the format `1:aaa:2:b`
    """

    # Idk how to make this efficient so here goes nothing.
    a = []

    # Iterate through all and add them to a list.
    for key, val in d.items():
        a += [key, val]
    
    # Combine them all and send off.
    return separator.join(a)
