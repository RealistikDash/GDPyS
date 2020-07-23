from gdpys import listener
from gdpys.bridge import Bridge
import time

b = Bridge()
l = listener

@l.event
async def on_login(username):
    print(username)

time.sleep(2)

b.login("test")

time.sleep(2)