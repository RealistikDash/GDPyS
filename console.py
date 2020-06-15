from colorama import Fore, init
from datetime import datetime

init()

def FormattedTime(DateTimeObject = None):
    """Returns a formatted time string."""
    if DateTimeObject == None:
        DateTimeObject = datetime.now()
    return DateTimeObject.strftime("%H:%M:%S")

def Log(Text):
    """Logs a thing in console."""
    print(f"{Fore.MAGENTA} [GDPyS] [{FormattedTime()}] {Text} {Fore.RESET}")

def Success(Text):
    """Logs a thing in console."""
    print(f"{Fore.GREEN} [GDPyS] [{FormattedTime()}] {Text} {Fore.RESET}")

def Fail(Text):
    """Logs a thing in console."""
    print(f"{Fore.RED} [GDPyS] [{FormattedTime()}] {Text} {Fore.RESET}")

def CLCheck(Text):
    """Logs a CheatlessAC message to console."""
    print(f"{Fore.MAGENTA} [Cheatless] [{FormattedTime()}] {Text} {Fore.RESET}")

def CLBan(Text):
    """Logs when a person gets anticheat banned."""
    print(f"{Fore.RED} [Cheatless] [{FormattedTime()}] {Text} {Fore.RESET}")