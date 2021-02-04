import aiohttp

async def post_request(url: str, params: dict) -> str:
    """Sends a post request to `url` and returns
    its contents as a `str`.
    
    Args:
        url (str): The URL the post request shall
            be sent to.
        params (dict): The post parameters.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params) as resp:
            return await resp.text()
