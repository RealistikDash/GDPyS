import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp_session import setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import fernet
import base64

__version__ = "v0.1.0"
app = aiohttp.web.Application()
templates = aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("./web/static/templates"))
app.router.add_static("/static/", path="./web/static/", name="static")
routes = aiohttp.web.RouteTableDef()

def render_template(template, **kwargs) -> aiohttp.web.Response:
    text = templates.get_template(template).render(**kwargs)
    return aiohttp.web.Response(text=text, content_type="text/html")

@routes.get("/")
async def tools_home(request):
    session = await get_session(request)
    ServerStatsCache = {
        "registered": 2000
    } # temp
    return render_template("home.html", title="Home", ver=__version__, session=session, stats=ServerStatsCache)

"""@routes.get("/login")
async def ToolsLoginRoute(request):
    session = await get_session(request)
    if not session["LoggedIn"]:
        return render_template("login.html", session=session, title = "Login")
    return aiohttp.web.HTTPFound("/tools")"""

@routes.get("/reupload/level")
def tools_level_reupload_route(request):
    return render_template("levelreupload.html", title="Level Reupload")

@routes.get("/reupload/song")
def tools_song_reupload_route(request):
    return render_template("songreupload.html", title="Song Reupload")

""" # not done / errors from port
@routes.get("/staff/admin-logs/<page>")
def tools_adminlogs_route(request, page):
    if not HasPrivilege(session["AccountID"], ModViewLogs):
        return render_template("403.html", session=session, title = "Missing Permissions!")
    return render_template("adminlogs.html", session=session, title="Admin Logs", logs = get_logs(page), page=page)

@routes.post("/account/change-password")
@routes.get("/account/change-password")
def tool_change_password_route(request):
    if request.method == "POST":
        a = change_password(request.form,session)
        if a:
            SetSession(ExampleSession)
            return render_template("passchange.html", session=session, title="Change Password", GoodAlert = "Password Changed Successfully!")
        return render_template("passchange.html", session=session, title="Change Password", BadAlert = "Password Change Failed!")
    return render_template("passchange.html", session=session, title="Change Password")

@routes.post("/staff/comment-ban")
@routes.get("/staff/comment-ban")
def tool_commentban_route(request):
    if not HasPrivilege(session["AccountID"], ModCommentBan):
        return render_template("403.html", session=session, title = "Missing Permissions!")
    
    if request.method == "GET":
        return render_template("commentban.html", session=session, title="Comment Ban")
    
    a = comment_ban(request)

    if not a[0]:
        return render_template("commentban.html", session=session, title="Comment Ban", BadAlert=a[1])
    return render_template("commentban.html", session=session, title="Comment Ban", GoodAlert=f"{a[1]} will next be able to comment {a[2]}")
"""

if __name__ == "__main__":
    app.add_routes(routes)
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(app, EncryptedCookieStorage(secret_key))
    aiohttp.web.run_app(app, port=82)