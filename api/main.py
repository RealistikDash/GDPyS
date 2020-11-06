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

def text(**kwargs) -> aiohttp.web.Response:
    return aiohttp.web.Response(**kwargs, content_type="text/html")

async def home(request:web.Request):
    return web.HTTPOk()

app.router.add_get("/", home)

@routes.get("/user/{user}")
async def user(request:aiohttp.web.Request):
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