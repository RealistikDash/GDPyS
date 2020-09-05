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
