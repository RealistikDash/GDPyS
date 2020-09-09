#simple misc functions thaat aim to replace 
import aiohttp

def dict_keys(dictioary: dict) -> tuple:
    """Returns a tuple of all the dictionary keys."""
    return tuple(dictioary.keys())

def get_ip(request : aiohttp.web.Request) -> str:
    """Gets IP address from request."""
    if request.headers.get("x-forwarded-for"):
        return request.headers.get("x-forwarded-for")
    return request.remote

def create_offsets_from_page(page: int, amount_per_page : int = 10) -> int:
    """Calculates the offset of mysql query."""
    return int(page) * int(amount_per_page)

def joint_string(content: dict):
    """Builds a joint string out of a dict."""
    return_str = ""
    #iterating through dict
    for key in dict_keys(content):
        return_str += f":{key}:{content[key]}"
    return return_str[1:]

def pipe_string(content : dict) -> str:
    """Generates a pipe separated string."""
    return_str = ""
    for key in dict_keys(content):
        return_str += f"{key}~|~{content[key]}~|~"
    return return_str

def safe_id_list(string: str) -> str:
    """Returns a fomrattable comma string list with input hopefull sanetised."""
    string = string.split(",")
    new_list = []
    for a in string:
        try:
            new_list.append(int(a))
        except ValueError:
            pass
    return list_comma_string(new_list)

def list_comma_string(elem_list: list):
    """Converts a Python list to a comma separated string."""
    result = ""
    for elem in elem_list:
        result += f"{elem},"
    return result[:-1]

def empty(variable) -> bool:
    """Python ver of empty php function"""
    if variable and variable != "-" and variable != "0":
        return False
    return True
