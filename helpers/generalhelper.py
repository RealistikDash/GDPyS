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

class UpdateQueryBuilder():
    """Makes it simple to work with long update queries."""
    def __init__(self, target_db : str):
        """Prepares that builder and sets tthe db."""
        self.TARGET_DB = target_db
        self.where_conditions = []
        self.where_params = []
        self.set_conds = []
        self.set_params =[]
    
    def set_equals(self, condition : str, equals : str, format_safe : bool = False):
        """Adds a coundition equals."""
        if format_safe:
            self.set_conds.append(f"{condition} = {equals}")
        else:
            self.set_conds.append(f"{condition} = %s")
            self.set_params.append(equals)
    
    def set_not_equals(self, condition : str, equals : str, format_safe : bool = False):
        """Adds a coundition equals."""
        if format_safe:
            self.set_conds.append(f"NOT {condition} = {equals}")
        else:
            self.set_conds.append(f"NOT {condition} = %s")
            self.set_params.append(equals)

    def where_equals(self, condition : str, equals : str, format_safe : bool = False):
        """Adds a where true condition."""
        if format_safe:
            self.where_conditions.append(f"{condition} = {equals}")
        else:
            self.where_conditions.append(f"{condition} = %s")
            self.where_params.append(equals)
    
    def where_not_equals(self, condition : str, equals : str, format_safe : bool = False):
        """Adds a where true condition."""
        if format_safe:
            self.where_conditions.append(f"NOT {condition} = {equals}")
        else:
            self.where_conditions.append(f"NOT {condition} = %s")
            self.where_params.append(equals)
    
    def get_query(self):
        """Returns the final query."""
        base_query = f"UPDATE {self.TARGET_DB} SET "
        sets = ""
        wheres = ""
        if len(self.where_conditions) != 0:
            wheres = "WHERE "
        
        for set_ in self.set_conds:
            sets += f"{set_},"
        sets = sets[:-1]

        for where_ in self.set_conds:
            wheres += f"{where_},"
        wheres = wheres[:-1]

        return f"{base_query}{sets} {wheres}"
