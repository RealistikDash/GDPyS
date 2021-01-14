from objects.user import User
from web.http import Request
from web.builders import gd_builder
from const import GenericResponse
from logger import info

async def register_account(req: Request) -> str:
    """Handles the account registration endpoint."""

    # Get variables and clean up from postdata.
    # TODO: some checks on this data.
    email = req.post_data["email"]
    username = req.post_data["userName"]
    password = req.post_data["password"] # Plaintext

    # This classmethod takes care of the majority of things such as rising GDException
    # that is later handled by the http server itself.
    u = await User.register(
        email= email,
        password= password,
        username= username
    )

    info(f"User {u.name} ({u.id}) registered successfully.")
    # They have been successfully registered.
    return GenericResponse.COMMON_SUCCESS
