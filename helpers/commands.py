from __future__ import annotations


class CommandsAsync:
    """A commands framework for any usage. Its goal is to provide a simple
    way of adding a pathway for specific user input -> handler. This is an
    async handler only variant."""

    def __init__(self, prefix: str = "/") -> None:
        """Configures the commands framework with prefix.

        Args:
            prefix (str): The prefix all commands must start with to be
                handled by the framework.
        """

        self.prefix: str = prefix
        self.handlers: dict = {}

    @property
    def commands(self) -> tuple:
        """List of all the commands handled.

        Returns:
            tuple of all command names.
        """

        return tuple(self.handlers)

    def register(self, name: str, handler, priv: int) -> None:
        """Registers a handler into a list of commands to be handled.

        Args:
            name (str): The name of the command that triggers the handler.
            handler (coroutine): The coroutine of the command handler.
            priv (int): A bitwise privilege enum required for the command.
        """

        self.handlers[name] = {"handler": handler, "privilege": priv}

    def _handlable(self, input: str) -> bool:
        """Checks if the user input meets the prerequisites to be handled.
        Args:
            input (str): The input of the user.

        Returns:
            True if it is able, else False.
        """

        # This is simply a check for the prefix.
        if input.startswith(self.prefix):
            return True
        return False

    def _meets_privs(self, name: str, user: object) -> bool:
        """Checks if the user passed meets the privileges for the command.

        Args:
            name (str): The name of the command.
            user (any): The object to validate the privileges of (must have
                `has_privilege`) function!
        """

        return user.has_privilege(self.handlers[name]["privilege"])

    def _command_exists(self, name: str) -> bool:
        """Checks if the command name passed is registered with a handler."""

        return name in self.commands
