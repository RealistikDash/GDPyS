import asyncio
import threading
from bridge import Bridge

bridge = Bridge()

class Client:
    
    def login(self, username):
        pass
    
    def register(self, username, email):
        pass
    
    def level_upload(self, username, levelid):
        pass
    
    def suggest_stars(self, levelid, stars, featured):
        pass
    
    def send_friend_request(self, accountid, toaccountid, comment):
        pass
    
    def upload_account_comment(self, username, comment):
        pass
    
    def delete_account_comment(self, accountid, commentid):
        pass
    
    def upload_comment(self, username, comment):
        pass
    
    def request_mod(self, userid):
        pass
    
    def like(self, like):
        pass
