from aiohttp import web


async def handle(request):
    d = {"mixers": [1]}
    # return web.json_response(d)
    peername = request.transport.get_extra_info('peername')
    return web.Response(text=str(peername))

app = web.Application()
app.add_routes([web.get('/', handle)])

if __name__ == '__main__':
    web.run_app(app, port=9000)
