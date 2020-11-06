from aiohttp import web
import aiohttp
from helpers.userhelper import user_helper
import platform
import json

app = web.Application()
routes = web.RouteTableDef()

def json_resp(*args, **kwargs) -> web.Response:
    actual_kwargs, json_kwargs = {}, {}

    for key, value in kwargs.items():
        actual_kwargs[key] = value
    return web.json_response(*args, **actual_kwargs)

def parse_string(string: str): # uwu thanks nekit
    if string is None:
        return {}

    current_section = ""
    current_content = None
    result = {}

    lines = [line for line in string.strip().splitlines() if line] + [""]
    result["method"], result["path"] = lines.pop(0).strip().split(maxsplit=1)

    for line in lines:
        line = line.strip(". ;")
        if line.endswith(":") or not line:
            if current_section:
                if isinstance(current_content, list):
                    current_content = "\n".join(current_content)

                result[current_section] = current_content
                current_content = None

            current_section = line.lower().rstrip(":").replace(" ", "_")

        else:
            key, sep, value = line.partition(": ")

            if sep:
                if current_content is None:
                    current_content = {}

                current_content[key] = value

            else:
                if current_content is None:
                    current_content = []

                current_content.append(line)

    return result

def parse_route_docs():
    for route in routes:
        info = dict(name=route.handler.__name__)
        info.update(parse_string(route.handler.__doc__))
        yield info

async def home(request:web.Request):
    payload = {
        "aiohttp": aiohttp.__version__,
        "python": platform.python_version(),
        "routes": list(parse_route_docs()),
    }
    return json_resp(payload)

app.router.add_get("/", home)

@routes.get("/user/{user}")
async def user(request:aiohttp.web.Request):
    """GET /api/user/{user}
    Description:
        Get a user by id
    Example:
        link: /api/user/2
    Returns:
        200: A user object
        404: User not found
    Return Type:
        application/json
    """
    user = request.match_info["user"]
    try: 
        int(user)
        is_int = True
    except ValueError:
        is_int = False
    if not is_int:
        user = user_helper.get_accountid_from_username(user)
    try:
        userobj = await user_helper.get_object(int(user))
    except AssertionError:
        return web.HTTPNotFound("User not found")
    return json_resp(json.dumps(userobj.__dict__))


app.add_routes(routes)