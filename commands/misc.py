# Misc commands.
from __future__ import annotations

from typing import Optional

from .framework.command import Command
from .framework.command import CommandContext
from const import GDPyS


class PingCommand(Command):
    """A simple command that replies with a constant string."""

    def __init__(self) -> None:
        super().__init__(name="ping", desc=self.__doc__)

    async def handle(self, ctx: CommandContext) -> Optional[str]:
        return f"Pong! {GDPyS.NAME} {GDPyS.BUILD} is answering!"
