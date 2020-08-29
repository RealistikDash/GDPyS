from aiohttp import web

async def home_page(request):
    """Home page"""
    return web.Response(text="Running GDPyS 2")