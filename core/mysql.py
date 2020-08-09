from config import UserConfig
from logger import logger

try:
    mydb = mysql.connector.connect(
        host=UserConfig["SQLHost"],
        user=UserConfig["SQLUser"],
        passwd=UserConfig["SQLPassword"],
        database=UserConfig['SQLDatabase']
    ) #connects to database
    logger.info(f"{Fore.GREEN}[GDPyS] Successfully connected to MySQL!{Fore.RESET}")
except Exception as e:
    logger.error(f"{Fore.RED}[GDPyS] Failed connecting to MySQL! Aborting!\nError: {e}{Fore.RESET}")
    exit()