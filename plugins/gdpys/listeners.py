import asyncio


class Listener:  # this has taken many nights of sleep deprivation ~spook
    def __init__(self):
        self.coros = {}

    def event(self, coro):
        self.coros[coro.__name__] = coro
        return coro

    def login(self, username):
        for name, coro in self.coros.items():
            if name == "on_login":
                asyncio.run(coro(username))

    def register(self, username, email):
        for name, coro in self.coros.items():
            if name == "on_register":
                asyncio.run(coro(username, email))

    def level_upload(self, username, levelid):
        for name, coro in self.coros.items():
            if name == "on_level_upload":
                asyncio.run(coro(username, levelid))

    def suggest_stars(self, levelid, stars, featured):
        for name, coro in self.coros.items():
            if name == "on_suggest_stars":
                asyncio.run(coro(levelid, stars, featured))

    def send_friend_request(self, accountid, toaccountid, comment):
        for name, coro in self.coros.items():
            if name == "on_send_friend_request":
                asyncio.run(coro(accountid, toaccountid, comment))

    def upload_account_comment(self, username, comment):
        for name, coro in self.coros.items():
            if name == "on_upload_account_comment":
                asyncio.run(coro(username, comment))

    def delete_account_comment(self, accountid, commentid):
        for name, coro in self.coros.items():
            if name == "on_delete_account_comment":
                asyncio.run(coro(accountid, commentid))

    def delete_comment(self, accountid, commentid):
        for name, coro in self.coros.items():
            if name == "on_delete_comment":
                asyncio.run(coro(accountid, commentid))

    def upload_comment(self, username, comment):
        for name, coro in self.coros.items():
            if name == "on_upload_comment":
                asyncio.run(coro(username, comment))

    def request_mod(self, userid):
        for name, coro in self.coros.items():
            if name == "on_request_mod":
                asyncio.run(coro(userid))

    def like(self, like):
        for name, coro in self.coros.items():
            if name == "on_like":
                asyncio.run(coro(like))

    def ready(self):
        for name, coro in self.coros.items():
            if name == "on_ready":
                asyncio.run(coro())


listener = Listener()
