from objects import glob
from web.http import Request
from const import Privileges
from objects.user import User
from logger import info, debug
from utils.security import verify_textbox
from exceptions import GDPySHandlerException
from const import GenericResponse, HandlerTypes, DB_PREFIX

@glob.add_route(
    path= DB_PREFIX + "/accounts/registerGJAccount.php",
    status= HandlerTypes.PLAIN_TEXT,
    args= ("userName", "password", "email", "secret")
)
async def register_account(req: Request) -> str:
    """Handles the account registration endpoint."""

    # Get variables and clean up from postdata.
    # TODO: some checks on this data.
    email = req.post["email"]
    username = req.post["userName"]
    password = req.post["password"] # Plaintext

    # Verify post args.
    for arg in (email, username):
        if not verify_textbox(arg, ["@", "."]):
            # Arg does not match.
            debug("User sent invalid args!")
            raise GDPySHandlerException("-1")

    # This classmethod takes care of the majority of things such as rising GDPySHandlerException
    # that is later handled by the http server itself.
    u = await User.register(
        email= email,
        password= password,
        username= username
    )

    info(f"User {u.name} ({u.id}) registered successfully.")
    # They have been successfully registered.
    return GenericResponse.COMMON_SUCCESS

@glob.add_route(
    path= DB_PREFIX + "/accounts/loginGJAccount.php",
    status= HandlerTypes.PLAIN_TEXT,
    args= ("udid", "userName", "password", "secret", "sID")
)
async def login_account(req: Request) -> str:
    """Handles the action of user login.
    
    Note:
        Currently, bcrypt for this authentication is not cached due to it
        being in plain text, rather than GJP. This means that its slow as
        BCRYPT!!!
    """

    # Set all required post args to variables.
    name = req.post["userName"]
    password = req.post["password"]

    u = await User.from_name(name)

    # If they are none, return -1.
    if not u: raise GDPySHandlerException("-1")

    # Check if they are banned.
    if not u.has_privilege(Privileges.LOGIN):
        # They are banned!
        raise GDPySHandlerException("-12") # Account disabled.

    # Check their password last as this slow.
    if not u.check_pass(password): raise GDPySHandlerException("-1")

    info(f"{u} ({u.id}) has successfully authenticated!")
    # Since we do not have user ids, we just use the account ids.
    return f"{u.id},{u.id}"
