from __future__ import annotations

import aiohttp

USER_AGENT = ""
HEADERS = {"User-Agent": USER_AGENT}


async def post_request(url: str, params: dict) -> str:
    """Sends a post request to `url` and returns its contents as a `str`.

    Args:
        url (str): The URL the post request shall be sent to.
        params (dict): The post parameters.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params, headers=HEADERS) as resp:
            return await resp.text()


async def simple_get(url: str) -> str:
    """Sends a simple GET request to the `url` and returns the contents
    of the body as `str`.

    Args:
        url (str): The URL the post request shall be sent to.
        params (dict): The post parameters.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as resp:
            return await resp.text()
