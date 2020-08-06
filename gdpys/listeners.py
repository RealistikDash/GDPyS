import asyncio
from flask import Flask, request
import logging
import os
app = Flask(__name__)
logging.getLogger("werkzeug").disabled = True
os.environ["WERKZEUG_RUN_MAIN"] = "true"

class Listener: # this has taken many nights of sleep deprivation ~spook
    def __init__(self):
        self.funcs = {}
        
    def event(self, func):
        setattr(self, func.__name__, func)
        return func
    
    def run(self):
        app.run(host="0.0.0.0", port=75)
    
    @app.route("/login")
    def login(self):
        username = request.args.get("username")
        for name, func in self.funcs.items():
            if name=="on_login":
                func(username)
    @app.route("/register")
    def register(self):
        username = request.args.get("username")
        email = request.args.get("email")
        for name, func in self.funcs.items():
            if name=="on_register":
                func(username, email)
    @app.route("/level_upload")
    def level_upload(self):
        username = request.args.get("username")
        levelid = request.args.get("levelid")
        for name, func in self.funcs.items():
            if name=="on_level_upload":
                func(username, levelid)
    @app.route("/suggest_stars")
    def suggest_stars(self):
        levelid = request.args.get("levelid")
        stars = request.args.get("stars")
        featured = request.args.get("featured")
        for name, func in self.funcs.items():
            if name=="on_suggest_stars":
                func(levelid, stars, featured)
    @app.route("/send_friend_request")  
    def send_friend_request(self):
        accountid = request.args.get("accountid")
        toaccountid = request.args.get("toaccountid")
        comment = request.args.get("comment")
        for name, func in self.funcs.items():
            if name=="on_send_friend_request":
                func(accountid, toaccountid, comment)
    @app.route("/upload_account_comment")
    def upload_account_comment(self):
        username = request.args.get("username")
        comment = request.args.get("comment")
        for name, func in self.funcs.items():
            if name=="on_upload_account_comment":
                func(username, comment)
    @app.route("/delete_account_comment")
    def delete_account_comment(self):
        accountid = request.args.get("accountid")
        commentid = request.args.get("commentid")
        for name, func in self.funcs.items():
            if name=="on_delete_account_comment":
                func(accountid, commentid)
    @app.route("/delete_comment")
    def delete_comment(self):
        accountid = request.args.get("accountid")
        commentid = request.args.get("commentid")
        for name, func in self.funcs.items():
            if name=="on_delete_comment":
                func(accountid, commentid)
    @app.route("/upload_comment")
    def upload_comment(self):
        username = request.args.get("username")
        comment = request.args.get("comment")
        for name, func in self.funcs.items():
            if name=="on_upload_comment":
                func(username, comment)
    @app.route("/request_mod")
    def request_mod(self):
        userid = request.args.get("userid")
        for name, func in self.funcs.items():
            if name=="on_request_mod":
                func(userid)
    @app.route("/like")
    def like(self):
        print("like wow scoobs, someone just liked a level")
        like = request.args.get("like")
        for name, func in self.funcs.items():
            if name=="on_like":
                func(like)
    @app.route("/ready")
    def ready(self):
        for name, func in self.funcs.items():
           if name=="on_ready":
                func()
