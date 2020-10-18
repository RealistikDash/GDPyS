# simple misc functions thaat aim to replace
import asyncio
import aiohttp
import logging
import json
import os
from typing import Union
from helpers.timehelper import Timer


def dict_keys(dictioary: dict) -> tuple:
    """Returns a tuple of all the dictionary keys."""
    return tuple(dictioary.keys())


def get_ip(request) -> str:
    """Gets IP address from request."""
    if request.headers.get("X-Real-IP"):  # I do this with nginx
        return request.headers.get("X-Real-IP")
    elif request.headers.get("x-forwarded-for"):
        return request.headers.get("x-forwarded-for")
    return request.remote


def create_offsets_from_page(page: int, amount_per_page: int = 10) -> int:
    """Calculates the offset of mysql query."""
    return int(page) * int(amount_per_page)


def joint_string(content: dict) -> str:
    """Builds a joint string out of a dict."""
    return_str = ""
    # iterating through dict
    for key in dict_keys(content):
        return_str += f":{key}:{content[key]}"
    return return_str[1:]


def pipe_string(content: dict) -> str:
    """Generates a pipe separated string."""
    return_str = ""
    for key in dict_keys(content):
        return_str += f"{key}~|~{content[key]}~|~"
    return return_str


def wave_string(content: dict) -> str:
    """Builds a wavy string used in gd responses."""
    return_str = ""
    for key in dict_keys(content):
        return_str += f"{key}~{content[key]}~"
    return return_str[:-1]


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


def string_bool(str_bool: str) -> bool:
    """Converts a string 1/0 to bool."""
    if int(str_bool):
        return True
    return False


def deprecated(func):
    """Decorator for deprecation warning"""
    raise DeprecationWarning("Function is deprecated!")


def paginate_list(list_to_paginate: list, page: int, elems_page: int = 10):
    """Gets a page from list."""
    offset = create_offsets_from_page(page, elems_page)
    return list_to_paginate[offset:offset+elems_page]


def select(table: list, column, where):
    """And SQL like select thing. Searches table param if column param == where param. If found, returns the list row. If not found, none is returned."""
    for i in table:
        if i[column] == where:
            return i

    return None


def select_obj_id(table: list, where):
    """select() function but for objects with .ID"""
    for i in table:
        if i.ID == where:
            return i

    return None


def time_function(function, args: tuple = ()):
    """Times and logs the execution of a function."""
    timer = Timer()
    timer.start()
    a = function(*args)
    timer.end()
    logging.debug(
        f"Execution of function {function.__name__} took {timer.ms_return()}")
    return a


async def time_coro(coro, args: tuple = ()):
    """Times the execution of a coroutine"""
    timer = Timer()
    timer.start()
    a = await coro(*args)
    timer.end()
    logging.debug(
        f"Execution of coroutine {coro.__name__} took {timer.ms_return()}")
    return a


class JsonFile():
    def __init__(self, file_name: str):
        self.file = None
        self.file_name = file_name
        if os.path.exists(file_name):
            with open(file_name) as f:
                self.file = json.load(f)

    def get_file(self) -> dict:
        """Returns the loaded JSON file as a dict."""
        return self.file

    def write_file(self, new_content: dict) -> None:
        """Writes a new dict to the file."""
        with open(self.file_name, 'w') as f:
            json.dump(new_content, f, indent=4)
        self.file = new_content


class UpdateQueryBuilder():
    """Makes it simple to work with long update queries."""

    def __init__(self, target_db: str):
        """Prepares that builder and sets the db."""
        self.TARGET_DB = target_db
        self.where_conditions = []
        self.where_params = []
        self.set_conds = []
        self.set_params = []

    def set_equals(self, condition: str, equals: str, format_safe: bool = False):
        """Adds a coundition equals."""
        if format_safe:
            self.set_conds.append(f"{condition} = {equals}")
        else:
            self.set_conds.append(f"{condition} = %s")
            self.set_params.append(equals)

    def set_not_equals(self, condition: str, equals: str, format_safe: bool = False):
        """Adds a coundition equals."""
        if format_safe:
            self.set_conds.append(f"NOT {condition} = {equals}")
        else:
            self.set_conds.append(f"NOT {condition} = %s")
            self.set_params.append(equals)

    def where_equals(self, condition: str, equals: str, format_safe: bool = False):
        """Adds a where true condition."""
        if format_safe:
            self.where_conditions.append(f"{condition} = {equals}")
        else:
            self.where_conditions.append(f"{condition} = %s")
            self.where_params.append(equals)

    def where_not_equals(self, condition: str, equals: str, format_safe: bool = False):
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


class SelectQueryBuilder():
    """FOr helping with the building of long and/or complex select queries."""

    def __init__(self, table: str):
        self.table = table
        self.selection = []
        self.where = []
        self.where_args = []
        self.order = "levelID"
        self.limit = 0
        self.offset = 0

    def select_add(self, selection: str):
        """Adds a select column."""
        if type(selection) == list:
            self.selection += selection
        else:
            self.selection.append(selection)

    def where_equals(self, column: str, value: str, format_safe: bool = False):
        """Adds a where equals condition"""
        if format_safe:
            self.where.append(F"{column} = {value}")
        else:
            self.where.append(f"{column} = %s")
            self.where_args.append(value)

    def where_not_equals(self, column: str, value: str, format_safe: bool = False):
        """Adds a where equals condition"""
        if format_safe:
            self.where.append(F"NOT {column} = {value}")
        else:
            self.where.append(f"NOT {column} = %s")
            self.where_args.append(value)

    def where_more_than(self, column: str, value: str, format_safe: bool = False):
        """Adds a where equals condition"""
        if format_safe:
            self.where.append(F"{column} > {value}")
        else:
            self.where.append(f"{column} > %s")
            self.where_args.append(value)

    def where_less_than(self, column: str, value: str, format_safe: bool = False):
        """Adds a where equals condition"""
        if format_safe:
            self.where.append(F"{column} < {value}")
        else:
            self.where.append(f"{column} < %s")
            self.where_args.append(value)

    def where_like_token(self, column: str, value: str, format_safe: bool = False):
        """Adds a where equals condition"""
        if format_safe:
            self.where.append(F"{column} LIKE %{value}%")
        else:
            self.where.append(f"{column} Like %s")
            self.where_args.append(f"%{value}%")

    def where_in_int_list(self, column: str, int_list: list) -> None:
        """Column in list of integers."""
        if type(int_list) == list:
            int_list = list_comma_string(int_list)
        the_list = safe_id_list(int_list)  # Sanetise input
        self.where.append(f"{column} IN ({the_list})")

    def build(self) -> str:
        """Builds the final query."""
        selection_str = list_comma_string(self.selection)
        base_query = f"SELECT {selection_str} FROM {self.table}"
        where = ""
        where_args = self.where_args
        limit = ""

        if len(self.where) > 0:
            where += " WHERE "
            for arg in self.where:
                where += f"{arg} AND"
            where = where[:-4]

        if self.limit > 0 and self.offset > 0:
            limit += f" LIMIT {self.limit} OFFSET {self.offset}"
        query = f"{base_query}{where} ORDER BY {self.order}{limit}"
        logging.debug(query)
        return query, where_args

    def build_count(self) -> str:
        """BUILDS COUNT QUERy"""
        base_query = f"SELECT COUNT(*) FROM {self.table}"
        where = ""
        where_args = self.where_args

        if len(self.where) > 0:
            where += " WHERE "
            for arg in self.where:
                where += f"{arg} AND"
            where = where[:-4]
        query = f"{base_query}{where}"
        logging.debug(query)
        return query, where_args

    def set_order(self, order: str):
        """Sets the order."""
        self.order = order
