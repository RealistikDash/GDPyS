from helpers.userhelper import user_helper
from helpers.levelhelper import level_helper
from helpers.generalhelper import dict_keys
from helpers.timehelper import get_timestamp
from objects.comments import CommandContext, Comment, CommentBan
from constants import Permissions
from config import user_config
from exceptions import GDPySCommandError

COMMANDS = {}

class Client:
    def __init__(self):
        pass

    def ban(self, user):
        pass

    def unban(self, user):
        pass

    # commands

    def command_exists(self, command : str) -> bool:
        """Checks if a given comment is a valid command."""
        command = command.split(" ")[0].lower()
        return command[len(user_config["command_prefix"]):] in dict_keys(COMMANDS)
    
    async def create_context(self, comment : Comment) -> CommandContext:
        """Creates a context object for a command."""
        level = await level_helper.get_level_obj(comment.level_id)
        account = await user_helper.get_object(await user_helper.accid_userid(comment.user_id))
        return CommandContext(
            level,
            comment,
            account
        )

    async def execute_command(self, command_obj : Comment):
        """Executes a GDPyS command comment command. Returns a bool or commentban object."""
        command_args = command_obj.comment[len(user_config["command_prefix"]):].split(" ")
        command = COMMANDS[command_args[0].lower()]
        ctx = await self.create_context(command_obj)
        account = await user_helper.get_object(await user_helper.accid_userid(command_obj.user_id)) # SHOULD be already cached.
        if not user_helper.has_privilege(account, command["permission"]):
            return False
        try:
            await command["handler"](ctx)
        except GDPySCommandError as e:
            return CommentBan(
                0, # /shrug
                get_timestamp(),
                f"GDPyS Command Exception in {command['handler'].__name__.replace('_', '-')}:\n{e}" # Replace as _s mess up the response
            )
        return True

client = Client()