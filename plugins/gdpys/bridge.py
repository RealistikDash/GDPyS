from . import listeners

l = listeners.listener

class Bridge: # this might be deleted later ~spook
    
    def login(self, username):
        l.login(username)
    
    def register(self, username, email):
        l.register(username, email)
    
    def level_upload(self, username, levelid):
        l.level_upload(username, levelid)
    
    def suggest_stars(self, levelid, stars, featured):
        l.suggest_stars(levelid, stars, featured)
    
    def send_friend_request(self, accountid, toaccountid, comment):
        l.send_friend_request(accountid, toaccountid, comment)
    
    def upload_account_comment(self, username, comment):
        l.upload_account_comment(username, comment)
    
    def delete_account_comment(self, accountid, commentid):
        l.delete_account_comment(accountid, commentid)
    
    def upload_comment(self, username, comment):
        l.upload_comment(username, comment)
    
    def request_mod(self, userid):
        l.request_mod(userid)
    
    def like(self, like):
        l.like(like)