from core.mysqlconn import mydb
from functions import HasPrivilege, Bot, AIDToUID

__name__ = "GDPyS-SDK"
cursor = mydb.cursor()

class SDK():
    """The GDPyS plugin SDK."""
    def __init__(self):
        pass
    @classmethod
    def has_privilege(self, AccountID, Privilege) -> bool:
        """Checks if the given userID has the privilege."""
        return HasPrivilege(AccountID, Privilege)
    
    def ban_user(self, UserID):
        """Bans the user with the given userID."""
        cursor.execute("UPDATE users SET isBanned = 1 WHERE userID = %s LIMIT 1", (UserID,))
        mydb.commit()
    
    def unban_user(self, user_id) -> None:
        """Unbans the user with the given userID"""
        cursor.execute("UPDATE users SET isBanned = 0 WHERE userID = %s LIMIT 1", (user_id,))
        mydb.commit()
    
    def accountid_to_userid(self, account_id) -> int:
        """Gets the userID from the accountID"""
        return AIDToUID(account_id)

    def message_user(self, account_id: int, title:str, message: str) -> None:
        """Sends a message to the user via the GDPyS bot."""
        Bot.SendMessage(account_id, message, title)

