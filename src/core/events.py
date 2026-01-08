import asyncio

# 用于同步关闭的事件
shutdown_event = asyncio.Event()

# 用于日志流的消息队列
log_queue = asyncio.Queue()

# 全局事件循环引用
main_loop = None
