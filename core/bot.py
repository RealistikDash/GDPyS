from functions import mycursor, HashPassword, RandomString
from core.mysqlconn import mydb
import time
import base64
from console import Log, Success

class GDPySBot:
    """This is the bot class for GDPyS. It is responsible for everything GDPyS related ranging from connecting and creating the bot to sending messages."""
    def __init__(self):
        """Sets up the GDPyS bot class for connection etc."""
        self.Connected = False
        self.BotID = 0
        self.BotUserId = 0

    def _CheckBot(self):
        """Checks if the bot account exists."""
        mycursor.execute("SELECT COUNT(*) FROM accounts WHERE isBot = 1")
        BotCount = mycursor.fetchone()[0]
        if BotCount == 0:
            return False
        return True

    def _FetchID(self):
        """Gets the bots accountID."""
        mycursor.execute("SELECT accountID FROM accounts WHERE isBot = 1 LIMIT 1")
        return mycursor.fetchone()[0]
    
    def _SetUserId(self):
        """Sets the user id for bot."""
        mycursor.execute("SELECT userID FROM users WHERE extID = %s LIMIT 1", (self.BotID,))
        self.BotUserId = mycursor.fetchone()[0]

    def _RegitsterBot(self, BotName="GDPySBot"):
        """Creates the bot account."""
        Timestamp = round(time.time())
        Password = HashPassword(RandomString(16)) #no one ever ever ever should access the bot account. if they do, you messed up big time
        mycursor.execute("INSERT INTO accounts (userName, password, email, secret, saveData, registerDate, isBot) VALUES (%s, %s, 'rel@es.to', '', '', %s, 1)", (BotName, Password, Timestamp))
        mydb.commit() #so the fetchid before works???
        mycursor.execute("INSERT INTO users (isRegistered, extID, userName, IP) VALUES (1, %s, %s, '1.1.1.1')", (self._FetchID(), BotName,))
        mydb.commit()
        Success(f"Created bot user ({BotName})!")
    
    def Connect(self):
        """Sets up the bot to be able to be used."""
        if not self._CheckBot():
            Log("Bot not found! Creating new account for it!")
            self._RegitsterBot()
        
        self.BotID = self._FetchID()
        self.Connected = True
        self._SetUserId()
    
    def GetID(self):
        """Returns the bot's account ID."""
        return self.BotID
    
    def SendMessage(self, Target: int, Body: str, Subject: str):
        """Sends a message from the bot."""
        #first we base64 encode the body and subject
        Subject = base64.b64encode(Subject.encode()).decode("ascii")
        Body = base64.b64encode(Body.encode()).decode("ascii")
        Timestamp = round(time.time())

        #and we create the message
        mycursor.execute("INSERT INTO messages (accID, toAccountID, userName, userID, subject, body, timestamp, isNew) VALUES (%s, %s, 'GDPyS Bot', %s, %s, %s, %s, 0)",
            (self.BotID, Target, self.BotUserId, Subject, Body, Timestamp)
        )
        mydb.commit()