import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web

def index(request):
	return web.Response(body=b'<h1>Awesome,wangker</h1>',content_type='text/html',charset='utf-8')

@asyncio.coroutine
def init(loop):
	# 定义一个 webAPP;
	app = web.Application(loop=loop)
	# 添加 get 方法，router 路由器
	app.router.add_route('GET','/',index)
	# 用异步协程的方法创建一个网络服务
	srv = yield from loop.create_server(app.make_handler(),'127.0.0.1',9000)
	# 设置网络登陆信息
	logging.info('server started at http://127.0.0.1:9000...')
	return srv

loop = asyncio.get_event_loop()   # 获取异步 IO 的事件循环
loop.run_until_complete(init(loop))
loop.run_forever()