import asyncio
from aiohttp.payload_streamer import streamer
from helpers.userhelper import user_helper
from helpers.levelhelper import level_helper
from helpers.generalhelper import dict_keys, deprecated
from helpers.timehelper import get_timestamp
from objects.comments import CommandContext, Comment, CommentBan
from constants import Permissions
from config import user_config
from exceptions import GDPySCommandError
from objects.levels import Level, Rating, DailyLevel

COMMANDS = {}


class Client:
    def __init__(self):
        self.permissions = Permissions

    ############################
    #           User           #
    ############################

    async def username_to_id(self, username: str) -> int:
        """Convert a username to an id"""
        return await user_helper.get_accountid_from_username(username)

    async def get_user_rank(self, id: int) -> int:
        """Get the rank of a user"""
        return await user_helper.get_rank(id)

    async def post_account_comment(self, id: int, comment: str) -> bool:
        """Post an account comment to a user's account"""
        return await user_helper.post_account_comment(id, comment, False, False)

    ############################
    #           Level          #
    ############################

    async def get_level(self, id: int) -> Level:
        """Get a level object"""
        return await level_helper.get_level_obj(id)

    async def star_to_difficulty(self, stars: int) -> int:
        """Convert star rating to a difficulty"""
        return await level_helper.star_to_difficulty(stars)

    async def like_level(self, id: int):
        """Bump a level's likes by one"""
        return await level_helper.bump_likes(id)

    async def upload_level(self, level: Level):
        """Uploads a level from a level object"""
        return await level_helper.upload_level(level)

    async def rate_level(self, rating: Rating):
        """Rates a level given a Rating object"""
        return await level_helper.rate_level(rating)

    async def get_daily_level(self) -> DailyLevel:
        """Get the current daily level"""
        return await level_helper.get_daily_level()

    # async def get_weekly_level(self) -> WeeklyLevel:
    #    """Get the current weekly level"""
    #    return await level_helper.get_weekly_level()

    ############################
    #         Commands         #
    ############################

    def command(self, name: str = None, permission: Permissions = None):
        """Decorator to create commands"""
        def decorator(coro):
            if not coro.__code__.co_flags & 0x0080 or getattr(coro, '_is_coroutine', False):
                raise Exception("Function is not a coroutine function!")
            if name is None:  # noqa
                name = coro.__name__.lower()  # noqa
                self.create_command(name, coro, permission)  # noqa

        return decorator

    def create_command(self, name: str, coro: asyncio.coroutine, permission: Permissions):
        """Create a command"""
        COMMANDS[name] = {
            "handler": coro,
            "permission": permission
        }

    def _command_exists(self, command: str) -> bool:
        """Checks if a given comment is a valid command."""
        command = command.split(" ")[0].lower()
        return command[len(user_config["command_prefix"]):] in dict_keys(COMMANDS)

    async def _create_context(self, comment: Comment) -> CommandContext:
        """Creates a context object for a command."""
        level = await level_helper.get_level_obj(comment.level_id)
        account = await user_helper.get_object(await user_helper.accid_userid(comment.user_id))
        return CommandContext(
            level,
            comment,
            account
        )

    async def _execute_command(self, command_obj: Comment):
        """Executes a GDPyS command comment command. Returns a bool or commentban object."""
        command_args = command_obj.comment[len(
            user_config["command_prefix"]):].split(" ")
        command = COMMANDS[command_args[0].lower()]
        ctx = await self._create_context(command_obj)
        # SHOULD be already cached.
        account = await user_helper.get_object(await user_helper.accid_userid(command_obj.user_id))
        # Create command args
        passed_args = command_args[1:]
        if not user_helper.has_privilege(account, command["permission"]):
            return False
        try:
            await command["handler"](ctx, *passed_args)
        except GDPySCommandError as e:
            return CommentBan(
                0,  # /shrug
                get_timestamp(),
                # Replace as _s mess up the response
                f"GDPyS Command Exception in {command['handler'].__name__.replace('_', '-')}:\n{e}"
            )
        return True


client = Client()

# Testing commands
# If this isnt removed and youre reading this i did forgot this. kindly mass tag me on discord https://discord.gg/Un42FEV RealistikDash#0077


async def rate(ctx: CommandContext, level: int, star: str):
    """Rates a level right??"""
    print(f"Level: {level}, stars: {star}")

client.create_command("rate", rate, None)
