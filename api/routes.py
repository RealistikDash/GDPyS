#import aiohttp
#from helpers.userhelper import user_helper

#async def user_handler(request:aiohttp.web.Request):
#    user = request.match_info["userid"]
#    print(type(user))
#    return user_helper.get_object(user)