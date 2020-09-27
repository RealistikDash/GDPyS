from exceptions import GDPySCommandError
from objects.comments import CommandContext

async def test_command(ctx : CommandContext):
    """GDPyS test command."""
    raise GDPySCommandError("Yes")
