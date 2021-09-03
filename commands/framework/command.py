from dataclasses import dataclass
from objects.user import User
from objects.level import Level
from typing import Optional
from const import Privileges
import traceback

CUSTOM_CHECK_FAIL_MSG = (
    "Sorry, but the conditions required for this command to run are not "
    "currently met. Try using !help to see which commands you may currently run."
)
PRIV_CHECK_FAIL_MSG = (
    "Sorry, but you are missing the required privileges to execute this "
    "command. Try using !help to see which commands you may currently run."
)
ARG_CHECK_MISMATCH = (
    "Sorry, but the arguments you've provided for this command are incorrect."
)

ERROR_MSG = (
    "An exception has occured while running this command! We have been notified "
    "of it!"
)

@dataclass
class CommandContext:
    """Context data provided regarding the current command execution."""

    user: User
    level: Level
    content: str
    # IGNORE. For future command groups.
    _processing_content: str = ""

class Command:
    def __init__(self, name: str, desc: str,
                 priv_req: Optional[Privileges] = None) -> None:
        """Creates an instance of command with specified attributes.
        
        Args:
            name (str): The name of the command, also the trigger word for the
                command (MUST BE ONE WORD, ELSE USE COMMANDGROUPS).
            desc (str): The description of what the command does (shown in the
                help command).
            priv_req (Optional Privileges): The privilege required for the command
                to be executed.
        """

        if " " in name:
            raise ValueError("Command names may not contain spaces!")

        self.name: str = name
        self.description: str = desc
        self.priv_req = priv_req
    
    @property
    def syntax_advice(self) -> str:
        """Formatted thing showing syntax advice."""

        return " ".join(
            [
                f"<{k} : {v.__name__}>" for k, v in self._args_actual()
            ]
        )
    
    async def execute(self, ctx: CommandContext) -> Optional[str]:
        """The actual execution of the command (the func commands write).
        All previous checks have to be passed to reach here, so no need
        for perm checks here. Returned string is the reply that is sent
        directly back.
        
        Args set to the function do actually matter (discord.py style).
        """

        return "Hello, world!"
    
    async def check_prior(self, ctx: CommandContext) -> bool:
        """Check (overidable by the Command implementation) prior to
        command execution. Has to return True or else the command is not
        executed."""

        return True
    
    # Internal checks.
    def _priv_check(self, ctx: CommandContext) -> bool:
        """Checks if the user has the permissions to run this command."""

        return True if self.priv_req is None else ctx.user.has_privilege(self.priv_req)

    # Messages sent on fails.
    def on_priv_check_fail(self, ctx: CommandContext) -> Optional[str]:
        """Func run on the fail of the privilege check. Return string is message
        sent back."""

        return PRIV_CHECK_FAIL_MSG
    
    def on_custom_check_fail(self, ctx: CommandContext) -> Optional[str]:
        """Func run on the fail of the custom check. Return string is message
        sent back."""

        return CUSTOM_CHECK_FAIL_MSG
    
    def on_arg_mismatch(self, ctx: CommandContext) -> Optional[str]:
        """Func ran on the mismatch of command content and args expected."""

        return ARG_CHECK_MISMATCH
    
    def on_error(self, ctx: CommandContext, tb: str) -> Optional[str]:
        """Function executed on exception in the command."""

        msg = ERROR_MSG

        if ctx.user.has_privilege(Privileges.DEV):
            # Show devs exceptions.
            msg += "\n" + tb
        return msg
    
    # Execution related
    def _args_actual(self) -> dict:
        """Returns a dict of arg: type for the command args."""

        return {
            k: v for k, v in self.execute.__annotations__.items()\
                if k not in ("self", "return") and v is not CommandContext
        }
    
    # TODO: Bit cursed...
    def _adapt_args(self, ctx: CommandContext) -> Optional[list]:
        """Adapts the args to the command so they can be directly passed to 
        `Command.execute`. Returns None on fail."""

        resp_args = []
        default_args = list(self.execute.__defaults__) if self.execute.__defaults__ else None

        untouched_args = ctx._processing_content.split(" ")
        for idx, (_, v) in enumerate(self._args_actual().items()):
            try: word = v(untouched_args[idx])
            except IndexError:
                # Check if we have a default, else error.
                try: word = default_args.pop(0) # Wished this was a dict.
                except (IndexError, AttributeError): return None
            except ValueError: return None
            
            resp_args.append(word)
        return resp_args
    
    async def handle(self, ctx: CommandContext) -> Optional[str]:
        """Handles the execution and checks of the command. Called by CommandManager."""

        # Do a weird thing that makes grouped commands work slightly better.
        if not ctx._processing_content: ctx._processing_content = ctx.content
        ctx._processing_content = ctx._processing_content.removeprefix(self.name)

        # Run checks first.
        if not self._priv_check(ctx): return self.on_priv_check_fail()
        if not await self.check_prior(ctx): return self.on_custom_check_fail()

        adapted_args = self._adapt_args(ctx)
        if adapted_args is None: return self.on_arg_mismatch(ctx)

        try:
            return await self.execute(ctx, *adapted_args)
        except Exception:
            return self.on_error(ctx, traceback.format_exc())

