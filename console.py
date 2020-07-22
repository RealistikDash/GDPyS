from colorama import Fore, init
from datetime import datetime
from logger import logger
from config import UserConfig

init()

def Log(Text):
    """Logs a thing in console."""
    logger.info(f"{Fore.MAGENTA}[GDPyS] {Text}{Fore.RESET}")

def Success(Text):
    """Logs a thing in console."""
    logger.info(f"{Fore.GREEN}[GDPyS] {Text}{Fore.RESET}")

def Fail(Text):
    """Logs a thing in console."""
    logger.warning(f"{Fore.RED}[GDPyS] {Text}{Fore.RESET}") # might be changed to error later

def CLCheck(Text):
    """Logs a CheatlessAC message to console."""
    logger.info(f"{Fore.MAGENTA}[Cheatless] {Text}{Fore.RESET}")

def CLBan(Text):
    """Logs when a person gets anticheat banned."""
    logger.info(f"{Fore.RED}[Cheatless] {Text}{Fore.RESET}")