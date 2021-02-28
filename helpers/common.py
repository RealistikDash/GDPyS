# Common functions related to simple python-related things.
from typing import Union
import os
try:
    from orjson import loads as json_load
    from json import dump as json_dump
except ImportError:
    # there is always one person in milion peoples that
    # orjson wont work for them so thats a backup
    from json import loads as json_load
    from json import dump as json_dump

class JsonFile:
    """Assists within working with simple JSON files."""

    def __init__(self, file_name: str):
        """Loads a Json file `file_name` from disk.
        
        Args:
            file_name (str): The path including the filename of the JSON file
                you would like to load.
        """

        self.file = None
        self.file_name = file_name
        if os.path.exists(file_name):
            with open(file_name) as f:
                self.file = json_load(f.read())

    def get_file(self) -> dict:
        """Returns the loaded JSON file as a dict.
        
        Returns:
            Contents of the file.
        """
        return self.file

    def write_file(self, new_content: Union[dict, list]) -> None:
        """Writes `new_content` to the target file.
        
        Args:
            new_content (dict, list): The new content that should be placed
                within the file.
        """

        with open(self.file_name, "w") as f:
            json_dump(new_content, f, indent=4)
        self.file = new_content

def dict_keys(d: dict) -> tuple:
    """Returns a `tuple` of all the keys present within the dictionary `d`.
    
    Args:
        d (dict): A dictionary to fetch all the keys of.
    """

    # I decided to use tuple as its immutable.
    return tuple(d)

def safe_username(uname: str) -> str:
    """Generates a "safe username" from a regular username.
    
    Args:
        uname (str): The username to convert to a safe variant.
    
    Returns:
        The username string that is lowercase and ` ` replaced with `_`.
    """

    return uname.lower().replace(" ", "_")


def paginate_list(list_to_paginate: list, page: int, elems_page: int = 10):
    """Grabs a 'page' out of the given `list_to_paginate` and returns a section
    `elems_page` large.
    
    Args:
        list_to_paginate (list): The list of items you would like to get the
            page of.
        page (int): The number of the page (starting with 0) you would like to
            fetch.
        elems_page (int): The number of elements that should be present within
            a page.
    
    Returns:
        A list of elements.
    """
    offset = page * elems_page
    return list_to_paginate[offset : offset + elems_page]

def is_numeric(digit: str) -> bool:
    """Kind of like `str.isdigit()` but works with checking for negative numbers
    too.
    
    Args:
        digit (str): A string to be checked for if it is a number.
    
    Returns:
        True if it is numeric, else false.
    """

    # Ugly but works.
    try:
        int(digit)
        return True
    except ValueError:
        return False
