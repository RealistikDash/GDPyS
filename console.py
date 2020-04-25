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
    print(f"{Fore.MAGENTA} [{FormattedTime()}] {Text} {Fore.RESET}")

def Success(Text):
    """Logs a thing in console."""
    print(f"{Fore.GREEN} [{FormattedTime()}] {Text} {Fore.RESET}")

def Fail(Text):
    """Logs a thing in console."""
    print(f"{Fore.RED} [{FormattedTime()}] {Text} {Fore.RESET}")