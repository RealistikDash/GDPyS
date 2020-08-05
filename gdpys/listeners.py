import asyncio
from flask import Flask, request
import logging
import os
app = Flask(__name__)
logging.getLogger("werkzeug").disabled = True
os.environ["WERKZEUG_RUN_MAIN"] = "true"

class Listener: # this has taken many nights of sleep deprivation ~spook
    def __init__(self):
        self.coros = {}
        
    def event(self, coro):
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("event registered must be a coroutine function")
        setattr(self, coro.__name__, coro)
        return coro
    
    def run(self):
        app.run(host="0.0.0.0", port=75)
    
    @app.route("/login")
    def login(self):
        username = request.args.get("username")
        for name, coro in self.coros.items():
            if name=="on_login":
                asyncio.run(coro(username))
    @app.route("/register")
    def register(self):
        username = request.args.get("username")
        email = request.args.get("email")
        for name, coro in self.coros.items():
            if name=="on_register":
                asyncio.run(coro(username, email))
    @app.route("/level_upload")
    def level_upload(self):
        username = request.args.get("username")
        levelid = request.args.get("levelid")
        for name, coro in self.coros.items():
            if name=="on_level_upload":
                asyncio.run(coro(username, levelid))
    @app.route("/suggest_stars")
    def suggest_stars(self):
        levelid = request.args.get("levelid")
        stars = request.args.get("stars")
        featured = request.args.get("featured")
        for name, coro in self.coros.items():
            if name=="on_suggest_stars":
                asyncio.run(coro(levelid, stars, featured))
    @app.route("/send_friend_request")  
    def send_friend_request(self):
        accountid = request.args.get("accountid")
        toaccountid = request.args.get("toaccountid")
        comment = request.args.get("comment")
        for name, coro in self.coros.items():
            if name=="on_send_friend_request":
                asyncio.run(coro(accountid, toaccountid, comment))
    @app.route("/upload_account_comment")
    def upload_account_comment(self):
        username = request.args.get("username")
        comment = request.args.get("comment")
        for name, coro in self.coros.items():
            if name=="on_upload_account_comment":
                asyncio.run(coro(username, comment))
    @app.route("/delete_account_comment")
    def delete_account_comment(self):
        accountid = request.args.get("accountid")
        commentid = request.args.get("commentid")
        for name, coro in self.coros.items():
            if name=="on_delete_account_comment":
                asyncio.run(coro(accountid, commentid))
    @app.route("/delete_comment")
    def delete_comment(self):
        accountid = request.args.get("accountid")
        commentid = request.args.get("commentid")
        for name, coro in self.coros.items():
            if name=="on_delete_comment":
                asyncio.run(coro(accountid, commentid))
    @app.route("/upload_comment")
    def upload_comment(self):
        username = request.args.get("username")
        comment = request.args.get("comment")
        for name, coro in self.coros.items():
            if name=="on_upload_comment":
                asyncio.run(coro(username, comment))
    @app.route("/request_mod")
    def request_mod(self):
        userid = request.args.get("userid")
        for name, coro in self.coros.items():
            if name=="on_request_mod":
                asyncio.run(coro(userid))
    @app.route("/like")
    def like(self):
        print("like wow scoobs, someone just liked a level")
        like = request.args.get("like")
        for name, coro in self.coros.items():
            if name=="on_like":
                asyncio.run(coro(like))
    @app.route("/ready")
    def ready(self):
        for name, coro in self.coros.items():
           if name=="on_ready":
                asyncio.run(coro())
