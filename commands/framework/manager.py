from .command import Command, CommandContext
from typing import Optional, Dict
from config import conf

COMMAND_NOT_EXIST = (
    "This command does not exist!  Try using !help to see a list of available "
    "commands."
)

class CommandManager:
    """The command manager class is responsible for registering commands,
    handling their storage and routing."""

    def __init__(self) -> None:
        """Configures a default instance of CommandManager."""

        self.cmd_idx: Dict[str, Command] = {}
    
    def register_command(self, c: Command) -> None:
        """Registers a command to the command index to be available when
        handling.
        
        Args:
            c (Command): The command `class` (not initialised) to register.
        """
        c = c()
        self.cmd_idx[c.name] = c
