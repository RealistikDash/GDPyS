import asyncio
import threading
import time

class Listener: # this has taken many nights of sleep deprivation ~spook
    def __init__(self):
        self.coros = {}
            
    def login(self, username):
        for name, coro in self.coros.items():
            if name=="on_login":
                asyncio.run(coro(username))

    def on_login(self, coro):
        self.coros["on_login"] = coro
        return coro
    
    def register(self, username, email):
        for name, coro in self.coros.items():
            if name=="on_register":
                asyncio.run(coro(username, email))

    def on_register(self, coro):
        self.coros["on_register"] = coro
        return coro
    
    def level_upload(self, username, levelid):
        for name, coro in self.coros.items():
            if name=="on_level_upload":
                asyncio.run(coro(username, levelid))

    def on_level_upload(self, coro):
        self.coros["on_level_upload"] = coro
        return coro
    
    def suggest_stars(self, levelid, stars, featured):
        for name, coro in self.coros.items():
            if name=="on_suggest_stars":
                asyncio.run(coro(levelid, stars, featured))

    def on_suggest_stars(self, coro):
        self.coros["on_suggest_stars"] = coro
        return coro
        
    def send_friend_request(self, accountid, toaccountid, comment):
        for name, coro in self.coros.items():
            if name=="on_send_friend_request":
                asyncio.run(coro(accountid, toaccountid, comment))

    def on_send_friend_request(self, coro):
        self.coros["on_send_friend_request"] = coro
        return coro

    def upload_account_comment(self, username, comment):
        for name, coro in self.coros.items():
            if name=="on_upload_account_comment":
                asyncio.run(coro(username, comment))

    def on_upload_account_comment(self, coro):
        self.coros["on_upload_account_comment"] = coro
        return coro
    
    def delete_account_comment(self, accountid, commentid):
        for name, coro in self.coros.items():
            if name=="on_delete_account_comment":
                asyncio.run(coro(accountid, commentids))

    def on_delete_account_comment(self, coro):
        self.coros["on_delete_account_comment"] = coro
        return coro
    
    def upload_comment(self, username, comment):
        for name, coro in self.coros.items():
            if name=="on_upload_comment":
                asyncio.run(coro(username, comment))

    def on_upload_comment(self, coro):
        self.coros["on_upload_comment"] = coro
        return coro
    
    def request_mod(self, userid):
        for name, coro in self.coros.items():
            if name=="on_request_mod":
                asyncio.run(coro(userid))

    def on_request_mod(self, coro):
        self.coros["on_request_mod"] = coro
        return coro
    
    def like(self, like):
        for name, coro in self.coros.items():
            if name=="on_like":
                asyncio.run(coro(like))

    def like(self, coro):
        self.coros["on_like"] = coro
        return coro