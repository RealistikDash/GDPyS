from time import localtime, strftime
from colorama import Fore, Back
from helpers.time_helper import formatted_date
import sys
import os

CLEAR_FORE = Fore.RESET
CLEAR_BACK = Back.RESET

# Received permission directly from him to use it. Just figured it looks cool.
__name__ = "LoggerModule"
__author__ = "Lenforiee"

DEBUG = "debug" in sys.argv

# Windows support
# activated only when os name is nt (windows)
if os.name == "nt":
    from ctypes import windll
    windll.kernel32.SetConsoleMode(
        windll.kernel32.GetStdHandle(-11),
        7
    )

def logMessage(**kwargs):
    """Form message to be logged"""
    # Get kwargs
    content = kwargs.get('content')
    logType = kwargs.get('type')
    back_colour = kwargs.get('back_colour')

    # get our colours
    bg_colour = {
        "YELLOW": Back.YELLOW,
        "GREEN": Back.GREEN,
        "RED": Back.RED,
        "BLUE": Back.BLUE
    }.get(back_colour, Back.GREEN)
        
    # Output
    logConsole = f'{Fore.WHITE}{bg_colour}[{logType}]{CLEAR_BACK} - [{formatted_date()}] {content}{CLEAR_FORE}'
    print(logConsole)

def debug(message: str):
    if DEBUG:
        return logMessage(content=message, type="DEBUG", back_colour="YELLOW")

def info(message: str):
    return logMessage(content=message, type="INFO", back_colour="GREEN")
 
def error(message: str):
    return logMessage(content=message, type="ERROR", back_colour="RED")

def warning(message: str):
    return logMessage(content=message, type="WARNING", back_colour="BLUE")

